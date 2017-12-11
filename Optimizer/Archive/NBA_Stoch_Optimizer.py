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
    lagranMul = {}
    L = 99999
    thetaList = {}
        
    # for each scenario
    for i in range(N):
        for j in pList:
            # initialize with lambda = 0
            lagranMul[i,j] = 0

        # build the lagrangian relaxation problem
        lrm = Model()
        zlr = {}
        ylr = lrm.addVar(vtype = GRB.BINARY, name = "y")
        for j in pList:
            zlr[j] = lrm.addVar(lb = 0, ub = 1, name = "z_{}".format(j))
        lrm.update()
        lrm.addConstr(T*ylr<=quicksum([scenList[i][pIDList.index(j)]*zlr[j] for j in pList]))
        lrm.update()
        
        stopBool = False
        k = 0
        # until stop criterion is met, solve the lagrangian relaxation with the current multiplier
        while (not(stopBool))and(k <= 50):
            # update the objective function and solve the lagrangian relaxation problem
            lrm.setObjective(ylr+quicksum([lagranMul[i,j]*(xhat[j] - zlr[j]) for j in pList]),GRB.MAXIMIZE)
            lrm.update()
            lrm.optimize()
            
            # update the indicator whether the iteration should stop
            stopBool = True
            for j in pList:
                if abs(zlr[j].x - xhat[j]) >= 1e-5:
                    stopBool = False
            if not(stopBool):
                # calculate the step size
                gamma = 1/(k+2)
                for j in pList:
                    lagranMul[i,j] -= gamma*(xhat[j] - zlr[j].x)
            k += 1
        lrm.setObjective(ylr+quicksum([lagranMul[i,j]*(xhat[j] - zlr[j]) for j in pList]),GRB.MAXIMIZE)
        lrm.update()
        lrm.optimize()
        sumScore = sum([zlr[j].x*scenList[i][pIDList.index(j)] for j in pList])
        thetaList[i] = lrm.objVal
                
        
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
            meansP.append(float(item[4])+10)
    fi.close()
    fo = open(outputF,"w",newline = "")
    csvWriter = csv.writer(fo,dialect = "excel")
    csvWriter.writerow(title)
    for i in range(N):
        outputList = [i+1] + list(numpy.random.normal(meansP,list(0.01+numpy.multiply(0.5,meansP))))
        csvWriter.writerow(outputList)
    fo.close()
    
# the input is the salary file, the simulated scenario file and the player dictionary
def stoch_opt(salaryF,distrnF,playerDAdd,totalTeam):
    # load the dictionary that maps players' names to their IDs
    solColl = []
    playerDict = numpy.load(playerDAdd)[0]
    # load the simulated scenarios: each row is one scenario, first row contains the ID
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
    posPlayer = {"C":[],"PG":[],"SG":[],"PF":[],"SF":[]}
    
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
            posPlayer[item[1]].append(playerID)
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
            for i in range(N):
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
        solPG = []
        solSG = []
        solSF = []
        solPF = []
        solC = []
        for k in playerList:
            if abs(xtemp[k] - 1) <= 1e-4:
                xSol.append(k)
                if k in posPlayer["PG"]:
                    solPG.append(k)
                elif k in posPlayer["SG"]:
                    solSG.append(k)
                elif k in posPlayer["SF"]:
                    solSF.append(k)
                elif k in posPlayer["PF"]:
                    solPF.append(k)
                elif k in posPlayer["C"]:
                    solC.append(k)
        solColl.append(solPG+solSG+solSF+solPF+solC)
        currentT = 0
        for item in xSol:
            currentT += x[item]
        morig.addConstr(currentT <= 8)
        morig.update()
    return solColl
        
        