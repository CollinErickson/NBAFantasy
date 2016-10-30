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
import pdb
pdb.set_trace()

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
        theta = thetaprob.addVar(lb = -numpy.inf, name = "theta")
        lamb = {}
        for k in pList:
            lamb[k] = thetaprob.addVar(lb = -L, ub = L, name = "lambda_{}".format(k))
        thetaprob.update()
        # set up the objective function for the theta problem
        thetaprob.setObjective(theta, GRB.MINIMIZE)
        thetaprob.update()
        # set up the initial constraint
        # start with y = 0, z = 0
        rhsExpr = 0
        for k in pList:
            rhsExpr += lamb[k]*(-xhat[k])
        thetaprob.addConstr(theta >= rhsExpr)
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
                        # if the lambda is greater than or equal to 0 but the w is less than 0
                        # then we need to decide which z should be added first
                        # this is decided by ordering the ratio between lambda and w since local copy z is continuous between 0 and 1
                        ratioL.append(lagranMul[i,k]/(-scenList[i][pIDList.index(k)]))
                        ratioK.append(k)
            if ratioL != []:
                sortedind = list(numpy.argsort(ratioL)).reverse()
            else:
                sortedind = []
            startind = 0
            
            while (tsum >= 0)and(startind < len(sortedind)):
                if tsum <= scenList[i][pIDList.index(ratioK[sortedind[startind]])]:
                    ztrial[ratioK[sortedind[startind]]] = tsum/scenList[i][pIDList.index(ratioK[sortedind[startind]])]
                    tsum = 0
                else:
                    ztrial[ratioK[sortedind[startind]]] = 1
                    tsum -= scenList[i][pIDList.index(ratioK[sortedind[startind]])]
                startind += 1
            
            rhsExpr = 0
            for k in pList:
                if k in ztrial.keys():
                    rhsExpr += lamb[k]*(ztrial[k]-xhat[k])
                else:
                    rhsExpr += lamb[k]*(-xhat[k])
            thetaprob.addConstr(theta >= ytrial + rhsExpr)
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
                            # if lambda is greater than/equal to 0 but w is smaller than 0
                            # record the ratio between lambda and w
                            ratioL1.append(lagranMul[i,k]/(-scenList[i][pIDList.index(k)]))
                            ratioK1.append(k)
                    else:
                        # if lambda is less than 0
                        # record the ratio between lambda and w
                        ratioL2.append(-lagranMul[i,k]/scenList[i][pIDList.index(k)])
                        ratioK2.append(k)
                if ratioL1 != []:
                    sortedind1 = list(numpy.argsort(ratioL1)).reverse()
                else:
                    sortedind1 = []
                if ratioL2 != []:
                    sortedind2 = list(numpy.argsort(ratioL2))
                else:
                    sortedind2 = []
                startind = 0
                if tsum >= T:
                    # if the summed weight is over threshold
                    # then add positive lambda with negative w until tsum = T
                    # according to the order in sortedind1
                    while (tsum >= T)and(startind < len(sortedind1)):
                        if (tsum - T) <= scenList[i][pIDList.index(ratioK1[sortedind1[startind]])]:
                            ztrial[ratioK1[sortedind1[startind]]] = (tsum - T)/scenList[i][pIDList.index(ratioK1[sortedind1[startind]])]
                            tsum = T
                        else:
                            ztrial[ratioK1[sortedind1[startind]]] = 1
                            tsum -= scenList[i][pIDList.index(ratioK1[sortedind1[startind]])]
                        startind += 1
                else:
                    # if the summed weight is less than threshold
                    # then add positive w with negative lambda until tsum = T
                    # according to the order in sortedind2
                    while (tsum < T):
                        if (T - tsum) <= scenList[i][pIDList.index(ratioK2[sortedind2[startind]])]:
                            ztrial[ratioK2[sortedind2[startind]]] = (T - tsum)/scenList[i][pIDList.index(ratioK2[sortedind2[startind]])]
                            tsum = T
                        else:
                            ztrial[ratioK2[sortedind2[startind]]] = 1
                            tsum += scenList[i][pIDList.index(ratioK2[sortedind2[startind]])]
                        startind += 1
                
                rhsExpr = 0
                for k in pList:
                    if k in ztrial.keys():
                        rhsExpr += lamb[k]*(ztrial[k]-xhat[k])
                thetaprob.addConstr(theta >= ytrial + rhsExpr)
                thetaprob.update()
            
            prevTheta = currentTheta
            thetaprob.optimize()
            currentTheta = theta.x
            for k in pList:
                lagranMul[i,k] = lamb[k].x
        thetaList.append(currentTheta)
    return lagranMul,thetaList
    
def fakeInput(salaryF,playerDAdd,N,outputF):
    # this function is used to generate random input to test the algorithm
    playerDict = numpy.load(playerDAdd)[0]
    fi = open(salaryF,"r")
    csvReader = csv.reader(fi,dialect = "excel")
    title = [""]
    meansP = []
    counter = 0
    for item in csvReader:
        if counter == 0:
            counter += 1
        else:
            title.append(playerDict[item[2] + ' ' + item[3]])
            meansP.append(float(item[4]))
    fi.close()
    fo = open(outputF,"w",newline = "")
    csvWriter = csv.writer(fo,dialect = "excel")
    csvWriter.writerow(title)
    for i in range(N):
        outputList = [i+1] + list(numpy.random.normal(meansP,list(0.01+numpy.multiply(0.2,meansP))))
        csvWriter.writerow(outputList)
    fo.close()
    
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
            pIDList = list(map(int,item[1:]))
            counter += 1
        else:
            pData.append(list(map(float,item[1:])))
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
#    z = {}
    obj = 0
    # define the objective function
#    for i in range(N):
#        z[i] = master.addVar(lb = 0, ub = 1, name = "Z_{}".format(i))
#        obj += 1/N*z[i]
    z = master.addVar(lb = 0, name = "Z")
    obj = z
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
    for item in posList:
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
            pi,v = genLagrangian(xtemp,master,N,playerList,pData,pIDList,threshold)
            pitotal = {}
            vtotal = 0
            for k in playerList:
                pitotal[k] = 0 
                for i in range(N):
                    pitotal[k] += pi[i,k]/N
                    vtotal += v[i]/N
            piTerm = 0
            for k in playerList:
                piTerm += pitotal[k]*(x[k] - xtemp[k])
            master.addConstr(z <= vtotal + piTerm, name = "LagrangianCut_{}".format(l))
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
        