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

def getLB(xinc,playerList,pIDList,pData,N,T):
    lb = 0
    for i in range(N):
        pt = 0
        for item in playerList:
            pt += pData[i,pIDList.index(item)]*(xinc[item].x)
        if pt >= T:
            lb += 1
    return lb

# the input is the salary file, the simulated scenario file and the player dictionary
def stoch_opt(salaryF,distrnF,playerDAdd,totalTeam):
    # load the dictionary that maps players' names to their IDs
    playerDict = numpy.load(playerDAdd)[0]
    # load the simulated scenarios
    fi = open(distrnF,"r")
    csvReader = csv.reader(fi,dialect = "excel")
    counter = 0
    pData = []
    for item in csvReader:
        if counter == 0:
            pIDList = item[1:]
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
    detFirst = Model()
    # define the decision variable
    x = {}
    xdet = {}
    z = {}
    obj = 0
    # define the objective function
    for i in range(N):
        z[i] = master.addVar(lb = 0, ub = 1, name = "Z_{}".format(i))
        obj += 1/N*z[i]
    playerList = []
    totalS = 0
    totalSdet = 0
    posC = {}
    posCdet = {}
    B = 60000
    threshold = 360
    FDPointDet = 0
    for item in posList:
        posC[item] = 0
        posCdet[item] = 0
    
    for item in csvReader:
        if counter == 0:
            counter += 1
        else:
            # read in player's name and obtain their corresponding ID
            playerName = item[2] + ' ' + item[3]
            playerID = playerDict[playerName]
            playerList.append(playerID)
            x[playerID] = master.addVar(vtype=GRB.BINARY, name = playerName)
            xdet[playerID] = detFirst.addVar(vtype = GRB.BINARY, name = playerName + "Det")
            # append the position information
            posC[item[1]] += x[playerID]
            posCdet[item[1]] += xdet[playerID]
            # append the salary information
            totalS += float(item[6])*x[playerID]
            totalSdet += float(item[6])*xdet[playerID]
            # append average points
            FDPointDet += float(item[4])*xdet[playerID]
    
    fi.close()
    # finish building the master program
    master.update()
    detFirst.update()
    master.setObjective(obj, GRB.MAXIMIZE)
    detFirst.setObjective(FDPointDet, GRB.MAXIMIZE)
    master.addConstr(totalS <= B, name = "BudgetConstraint")
    detFirst.addConstr(totalSdet <= B, name = "BCon_Det")
    for item in posList.keys():
        master.addConstr(posC[item] == posReq[item], name = "PositionConstraint_{}".format(item))
        detFirst.addConstr(posCdet[item] == posReq[item], name = "PCon_Det_{}".format(item))
    master.update()
    detFirst.update()
    # solve the deterministic expected problem, obtain solutions
    detFirst.optimize()
    
    k = 1
    l = 1
    # obtain a lower bound for the current expected solution
    lb = getLB(xdet,playerList,pIDList,pData,N,threshold)
    ub = N
            
    # generate cuts around the incumbent lower bound solution!!!!!!!!
    
    solColl = []
    for j in range(totalTeam):
        # start the iteration to solve the decomposed problem!!!!!!!!!
        while lb < numpy.floor(ub):
            xSol = []
            master.optimize()
            # update the upper bound
            if ub > master.objVal:
                ub = master.objVal
            lb = getLB(x,playerList,pIDList,pData,N,threshold)
            for iKey in x.keys():
                if abs(x[iKey].x - 1) <= 0.000001:
                    xSol.append(iKey)
            # add the integer L-shaped cuts!!!!!!
            k += 1
            master.update()
            # add the Lagrangian cuts!!!!!!!
            l += 1
            master.update()
        
        # record the xSol, add the constraint to remove this team, repeat the process
        solColl.append(xSol)
        currentT = 0
        for item in xSol:
            currentT += x[item]
        master.addConstr(currentT <= 8)
        master.update()
        
        