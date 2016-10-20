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

# the input is the incumbent solution and the master program
def genLagrangian(xhat,m,N,pList,scenList,pIDList,T):
    # initialize with lambda = 0
    lagranMul = {}
    L = 99999
    thetaList = []
    # for each scenario
    for i in range(N):
        # initialize the theta problem to solve for lambda
        ztrial = {}
        for k in pList:
            ztrial[k] = 0
        thetaprob = Model()
        theta = thetaprob.addVar(name = "theta")
        lamb = {}
        for k in pList:
            lamb[k] = thetaprob.addVar(lb = -L, ub = L, name = "lambda_{}".format(k))
        thetaprob.update()
        # set up the objective function for the theta problem
        thetaprob.setObjective(theta, GRB.MINIMIZE)
        thetaprob.update()
        # set up the initial constraint
        thetaprob.addConstr(theta >= sum([lamb[k]*(-xhat[k]) for k in pList]))
        thetaprob.update()
        
        prevTheta = -numpy.infty
        thetaprob.optimize()
        currentTheta = theta.x
        for k in pList:
            lagranMul[i,k] = lamb[k].x
        while currentTheta != prevTheta:
            # start the iteration to obtain lambda, split into y = 0 or y = 1!!!!!!!!!
            
            # y = 0
            ytrial = 0
            ztrial = {}
            ratioL = []
            ratioK = []
            for k in pList:
                if (lagranMul[i,k] >= 0):
                    tsum = 0
                    if (scenList[i][pIDList.index(k)] >= 0):
                        tsum += scenList[i][pIDList.index(k)]
                        ztrial[k] = 1
                    else:
                        ratioL.append(lagranMul[i,k]/(-scenList[i][pIDList.index(k)]))
                        ratioK.append(k)
            sortedind = list(numpy.argsort(ratioL)).reverse()
            startind = 0
            while (tsum >= 0)and(startind < len(sortedind)):
                if tsum <= scenList[i][pIDList.index(ratioK[sortedind[startind]])]:
                    ztrial[pIDList.index(ratioK[sortedind[startind]])] = tsum/scenList[i][pIDList.index(ratioK[sortedind[startind]])]
                    tsum = 0
                else:
                    ztrial[pIDList.index(ratioK[sortedind[startind]])] = 1
                    tsum -= scenList[i][pIDList.index(ratioK[sortedind[startind]])]
                startind += 1
            
            thetaprob.addConstr(theta >= ytrial + sum([lamb[k]*(ztrial[k]-xhat[k]) for k in pList]))
            thetaprob.update()
                
            # y = 1
            ytrial = 1
            ztrial = {}
            ratioL1 = []
            ratioK1 = []
            ratioL2 = []
            ratioK2 = []
            if sum([scenList[i][pIDList.index(k)] for k in pList]) >= T:
                for k in pList:
                    if (lagranMul[i,k] >= 0):
                        tsum = 0
                        if (scenList[i][pIDList.index(k)] >= 0):
                            tsum += scenList[i][pIDList.index(k)]
                            ztrial[k] = 1
                        else:
                            ratioL1.append(lagranMul[i,k]/(-scenList[i][pIDList.index(k)]))
                            ratioK1.append(k)
                    else:
                        ratioL2.append(-lagranMul[i,k]/scenList[i][pIDList.index(k)])
                        ratioK2.append(k)
                sortedind1 = list(numpy.argsort(ratioL1)).reverse()
                sortedind2 = list(numpy.argsort(ratioL2))
                startind = 0
                if tsum >= T:
                    while (tsum >= T)and(startind < len(sortedind1)):
                        if (tsum - T) <= scenList[i][pIDList.index(ratioK1[sortedind1[startind]])]:
                            ztrial[pIDList.index(ratioK1[sortedind1[startind]])] = (tsum - T)/scenList[i][pIDList.index(ratioK1[sortedind1[startind]])]
                            tsum = T
                        else:
                            ztrial[pIDList.index(ratioK1[sortedind1[startind]])] = 1
                            tsum -= scenList[i][pIDList.index(ratioK1[sortedind1[startind]])]
                        startind += 1
                else:
                    while (tsum < T):
                        if (T - tsum) <= scenList[i][pIDList.index(ratioK2[sortedind2[startind]])]:
                            ztrial[pIDList.index(ratioK2[sortedind2[startind]])] = (T - tsum)/scenList[i][pIDList.index(ratioK2[sortedind2[startind]])]
                            tsum = T
                        else:
                            ztrial[pIDList.index(ratioK2[sortedind2[startind]])] = 1
                            tsum += scenList[i][pIDList.index(ratioK2[sortedind2][startind])]
                        startind += 1
                        
                thetaprob.addConstr(theta >= ytrial + sum([lamb[k]*(ztrial[k]-xhat[k]) for k in pList]))
                thetaprob.update()
            
            prevTheta = currentTheta
            thetaprob.optimize()
            currentTheta = theta.x
            for k in pList:
                lagranMul[i,k] = lamb[k].x
        thetaList.append(theta)
    return lagranMul,thetaList
    
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
    
    morig = master
    for j in range(totalTeam):
        master = morig
        detFirst.update()
        # solve the deterministic expected problem, obtain solutions
        detFirst.optimize()
        
        l = 1
        # obtain a lower bound for the current expected solution
        lb = getLB(xdet,playerList,pIDList,pData,N,threshold)
        ub = N
        xtemp = {}
        for k in playerList:
            xtemp[k] = xdet[k].x
        # start the iteration to solve the decomposed problem
        while lb < numpy.floor(ub):
            # generate cuts around the incumbent lower bound solution!!!!!!!!
            pi,v = genLagrangian(xtemp,master,playerList,pData,pIDList,threshold)
            pitotal = {}
            vtotal = 0
            for k in playerList:
                pitotal[k] 
                for i in range(N):
                    pitotal[k] += pi[i,k]/N
                    vtotal += v[i]/N
            tempS = sum([pitotal[k]*(x[k] - xtemp[k]) for k in playerList])
            master.addConstr(z >= vtotal + tempS, name = "LagrangianCut_{}".format(l))
            master.update()
            master.optimize()
            # update the upper bound
            if ub > master.objVal:
                ub = master.objVal
            lb = getLB(x,playerList,pIDList,pData,N,threshold)
            for k in playerList:
                xtemp[k] = x[k].x
            # new iteration
            l += 1
        
        # record the xSol, add the constraint to remove this team, repeat the process
        xSol = []
        for k in playerList:
            if abs(xtemp[k] - 1) <= 1e-4:
                xSol.append(k)
        solColl.append(xSol)
        currentT = 0
        for item in xSol:
            currentT += x[item]
        morig.addConstr(currentT <= 8)
        morig.update()
        