#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 15:14:03 2019

@author: haoxiangyang
"""

# this is the deterministic optimization model for back checking
# the function will take in the score of that day. Input as 

from gurobipy import *
#import pdb
#pdb.set_trace()
import csv
import numpy as np

class player:
    def __init__(self,pID,name,pos,salary,team,status):
        self.ID = pID
        self.name = name
        self.pos = pos
        self.salary = salary
        self.team = team
        self.status = status
        
def subProblem(model,where):
    # if we see a MIP solution
    if where == GRB.Callback.MIPSOL:
        # for each scenario
        for i in range(model._N):
            sp = Model()
            z = sp.addVar(lb = 0, ub = 1, name = "z")
            x = {}
            varVal = {}
            for item in model._playerData:
                x[item.ID] = sp.addVar(vtype=GRB.BINARY, name = item.name)
                varTemp = model.getVarByName(item.name)
                varVal[item.ID] = model.cbGetSolution(varTemp)  # get xhat
            sp.update()
            # add the constraints
            zCon = sp.addConstr(model._W*z <= sum([model._sample[i][item.ID]*x[item.ID] for item in model._playerData]))
            capCon = sp.addConstr(sum([model._sample[i][item.ID]*x[item.ID] for item in model._playerData]) <= \
                         sum([model._sample[i][item.ID]*varVal[item.ID] for item in model._playerData]), name = "capCon")
            l1Con = sp.addConstrs((x[item.ID] <= varVal[item.ID] for item in model._playerData), name = "l1")
            l2Con = sp.addConstrs((x[item.ID] <= z for item in model._playerData), name = "l2")
            l3Con = sp.addConstrs((x[item.ID] >= z + varVal[item.ID] - 1 for item in model._playerData), name = "l3")
            sp.update()
            
            # set the objective function
            sp.addObjective(z, GRB.MAXIMIZE)
            sp.update()
            sp.optimize()
            
            # obtain the optimal solution and return the cut
            vhat = sp.ObjVal
            capConDual = capCon.Pi
            lambdahat = {}
            for indItem in range(len(model._playerData)):
                lambdahat[model._playerData[indItem].ID] = capConDual*model._sample[i][model._playerData[indItem].ID] + \
                    l1Con[indItem].Pi + l3Con[indItem].Pi
            model.cbLazy(model.getVarByName("theta[{}]".format(i)) <= vhat + sum((model.getVarByName(item.name) - \
                                            varVal[item.ID])*lambdahat[item.id] for item in model._playerData))
                
def readSample(sampleAdd):
    # read the sample information
    fi = open(sampleAdd,"r")
    csvReader = csv.reader(fi)
    data = []
    counter = 0
    for item in csvReader:
        if counter == 0:
            counter += 1
            N = len(list(item)) - 1
            for i in range(N):
                data.append({})
        else:
            for i in range(N):
                data[i][item[0]] = item[i+1]
    fi.close()
    return N,data

def readPD(pdAdd):
    # read the player data information
    fi = open(pdAdd,"r")
    csvReader = csv.reader(fi)
    playerData = []
    counter = 0
    for item in csvReader:
        if counter == 0:
            counter += 1
        else:
            pID = item[0]
            pPos = item[1]
            pName = item[3]
            pSalary = item[7]
            pTeam = item[9]
            pStatus = item[11]
            p = player(pID,pPos,pName,pSalary,pTeam,pStatus)
            playerData.append(p)
    fi.close()
    return playerData
            

def stoch_Opt(playerData,N,W,sample,threshold):
    # Input: 
    #       idList: the ID list of players
    #       positionList: the position of players
    #       samples: the samples of prediction for each player on idList
    #       threshold: the threshold we want to be above
    # Output:
    #       lineup: the list of players to select
    #       sList: the list of sample indices for which the threshold is met
    
    # set up the master
    mp = Model()
    # pass the data to the model struct
    mp._sample = sample
    mp._playerData = playerData
    mp._N = N
    mp._W = W
    # mp.params.outputflag = 0
    budget = 60000
    playertype = ["PG","SG","SF","PF","C"]
    playerQ = {"PG":2,"SG":2,"SF":2,"PF":2,"C":1}
    x = {}
    theta = mp.addVars(range(N),lb = 0, ub = 1, name = "theta")
    budgetexpr = 0
    posexprList = {}
    for pos in playertype:
        posexprList[pos] = 0
    for item in playerData:
        x[item.ID] = mp.addVar(vtype=GRB.BINARY, name = item.name)
        budgetexpr += item.salary*x[item.ID]
        posexprList[item.pos] += x[item.ID]
    mp.update()
    mp.setObjective(sum([theta[i] for i in theta.keys()]), GRB.MAXIMIZE)
    mp.addConstr(budgetexpr <= budget, name = "BudgetConstraint")
    for pos in playertype:
        mp.addConstr(posexprList[pos] == playerQ[pos])
    mp.update()
    
    # optimize the master problem with the callback function subProblem
    mp.optimize(subProblem)
    
    # obtain the solutions
    squadList = []
    for item in playerData:
        if x[item.ID].X == 1:
            squadList.append(item)
            
    return squadList
    