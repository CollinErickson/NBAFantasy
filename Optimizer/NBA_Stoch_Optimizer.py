# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 22:36:20 2016

@author: haoxi
"""

# this is the stochastic optimization model for back checking
# the function will take in the score of that day and type of the Fantasy ("FD"
# for FanDuel and "DK" for DraftKings.

# Right now it is only applicable to FanDuel

from gurobipy import *
import numpy
import csv

# the input is the salary file, the simulated scenario file and the player dictionary
def stoch_opt(salaryF,distrnF,playerDAdd):
    # load the dictionary that maps players' names to their IDs
    playerDict = numpy.load(playerDAdd)[0]
    # load the simulated scenarios
    fi = open(distrnF,"r")
    csvReader = csv.reader(fi,dialect = "excel")
    counter = 0
    pData = []
    for item in csvReader:
        if counter == 0:
            pIDList = item
        else:
            pData.append(item[1:])
    fi.close()
    pData = numpy.array(pData)
    N = numpy.size(pData,0)
    
    # load the salary/position information
    fi = open(salaryF,"r")
    csvReader = csv.reader(fi,dialect = "excel")
    counter = 0
    posList = ["C","PG","SG","PF","SF"]
    posReq = {"C":1,"PG":2,"SG":2,"PF":2,"SF":2}
    
    master = Model()
    # define the decision variable
    x = {}
    z = {}
    obj = 0
    # define the objective function
    for i in range(N):
        z[i] = master.addVar(lb = 0, ub = 1, name = "Z_{}".format(i))
        obj += 1/N*z[i]
    playerList = []
    totalS = 0
    posC = {}
    B = 60000
    for item in posList:
        posC[item] = 0
    
    for item in csvReader:
        if counter == 0:
            counter += 1
        else:
            # read in player's name and obtain their corresponding ID
            playerName = item[2] + ' ' + item[3]
            playerID = playerDict[playerName]
            playerList.append(playerID)
            x[playerID] = master.addVar(vtype=GRB.BINARY, name = playerName)
            # append the position information
            posC[item[1]] += x[playerID]
            # append the salary information
            totalS += float(item[6])*x[playerID]
    
    fi.close()
    # finish building the master program
    master.update()
    master.setObjective(obj, GRB.MAXIMIZE)
    master.addConstr(totalS <= B, name = "BudgetConstraint")
    for item in posList.keys():
        master.addConstr(posC[item] == posReq[item], name = "PositionConstraint_{}".format(item))