#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 23:27:20 2017

@author: haoxiangyang
"""

import os
os.chdir("/Users/haoxiangyang/Desktop/Git/NBAFantasy/Optimizer/")
 
import datetime
from gurobipy import *
from NBA_Det_Optimizer import *
import csv
from NBA_scrapper import *
#import pdb
#pdb.set_trace()
salaryPath = "/Users/haoxiangyang/Desktop/NBA_Data/Salary/"
lineupPath = "/Users/haoxiangyang/Desktop/NBA_Data/Lineups/"
snapshotPath = "/Users/haoxiangyang/Desktop/NBA_Data/Snapshot/"
blankPath = "/Users/haoxiangyang/Desktop/NBA_Data/Blank/"

# function to convert the datetime date to a YYYYMMDD string
def dateConvert(currentDate):
    if currentDate.month < 10:
        monthTemp = digTrans[currentDate.month]
    else:
        monthTemp = str(currentDate.month)
    if currentDate.day < 10:
        dayTemp = digTrans[currentDate.day]
    else:
        dayTemp = str(currentDate.day)
    return str(currentDate.year)+monthTemp+dayTemp

playerNameDict = {"Lou Williams":"Louis Williams",\
                "TJ Warren":"T.J. Warren",\
                "Otto Porter Jr.":"Otto Porter",\
                "CJ McCollum":"C.J. McCollum",\
                "Kelly Oubre Jr.":"Kelly Oubre",\
                "CJ Miles":"C.J. Miles",\
                "PJ Tucker":"P.J. Tucker",\
                "CJ Wilcox":"C.J. Wilcox",\
                "James Ennis III":"James Ennis",\
                "PJ Dozier":"P.J. Dozier",\
                "Gary Payton II":"Gary Payton",\
                "AJ Hammons":"A.J. Hammons",\
                "Nene":"Nene Hilario",\
                "Matt Williams Jr.": "Matt Williams",\
                "Johnny O'Bryant III": "Johnny O'Bryant",\
                "Wade Baldwin IV": "Wade Baldwin"}

class playerData:
    def __init__(self,name,pos,fppg,played,salary,team,oppo,inj,topProb):
        self.name = name
        self.pos = pos
        self.fppg = fppg
        self.played = played
        self.salary = salary
        self.team = team
        self.oppo = oppo
        self.inj = inj
        self.topProb = topProb

class detOptimizer_d:
    def addLineup(self):
        self.model.optimize()
        lineupN = []
        for v in self.model.getVars():
            if v.x == 1:
                lineupN.append(self.playerIndex[v.varName])
                # add the past lineups
        self.model.addConstr(quicksum(self.x[j] for j in lineupN) <= 9 - self.M)
        return lineupN
    
    def mainOpt(self):
        # deterministic optimizer to generate N lineups with M difference between each lineup
        self.model = Model()
        self.pastLineup = []
        self.model.params.outputflag = 0
        self.budget = 60000
        self.playertype = ["PG","SG","SF","PF","C"]
        self.playerQ = {"PG":2,"SG":2,"SF":2,"PF":2,"C":1}
        self.x = {}
        j = 0
        self.obj = 0
        self.budgetexpr = 0
        self.posexprList = {}
        self.playerIndex = {}
        self.playerIndexRev = {}
        for pos in self.playertype:
            self.posexprList[pos] = 0
        for item in self.playerList:
            # only non-injured players are included
            if item.inj == '':
                self.playerIndex[item.name] = j
                self.playerIndexRev[j] = item.name
                self.x[j] = self.model.addVar(vtype=GRB.BINARY, name = item.name)
                self.obj += item.topProb*self.x[j]
                self.budgetexpr += item.salary*self.x[j]
                self.posexprList[item.pos] += self.x[j]
                j += 1
        
        self.model.update()
        self.model.setObjective(self.obj, GRB.MAXIMIZE)
        self.model.addConstr(self.budgetexpr <= self.budget, name = "BudgetConstraint")
        for pos in self.playertype:
            self.model.addConstr(self.posexprList[pos] == self.playerQ[pos])
        self.model.update()
        
        for i in range(N):
            lineupN = self.addLineup()
            print(i,lineupN)
            self.pastLineup.append(lineupN)
            
        
    def __init__(self,playerList,N,M):
        self.playerList = playerList
        self.N = N
        self.M = M

# automatic generate N1 lineups from the blank file, the last snapshot from the predicted date
# & the list of players excluded

N = 300
M = 3

predictDate = datetime.date(2017,12,17)
prepreDate = predictDate - datetime.timedelta(1)
dateStr = dateConvert(predictDate)
# readin the snapshot
fi = open(snapshotPath + dateConvert(prepreDate) + ".csv","r")
csvReader = csv.reader(fi)
snapDict = {}
for item in csvReader:
    name = item[0]
    if name in snapDict.keys():
        print(name)
    else:
        snapDict[name] = float(item[3])
fi.close()

# read in the blank file
fi = open(blankPath + dateStr + ".csv","r")
csvReader = csv.reader(fi)
counter = 0
playerList = []
for item in csvReader:
    if counter == 0:
        counter += 1
    else:
        # read in the item and decide whether it is going to be included in the lineup consideration
        name = item[3]
        pos = item[1]
        fppg = float(item[5])
        played = int(item[6])
        salary = float(item[7])
        team = item[9]
        oppo = item[10]
        inj = item[11]
        if name in snapDict.keys():
            topProb = snapDict[name]
            player = playerData(name,pos,fppg,played,salary,team,oppo,inj,topProb)
            playerList.append(player)
        elif name in playerNameDict.keys():
            if playerNameDict[name] in snapDict.keys():
                topProb = snapDict[playerNameDict[name]]
                player = playerData(playerNameDict[name],pos,fppg,played,salary,team,oppo,inj,topProb)
                playerList.append(player)
            else:
                player = playerData(name,pos,fppg,played,salary,team,oppo,inj,0.0)
                playerList.append(player)
        else:
            player = playerData(name,pos,fppg,played,salary,team,oppo,inj,0.0)
            playerList.append(player)
fi.close()

# optimize using the playerList
d = detOptimizer_d(playerList,N,M)
d.mainOpt()