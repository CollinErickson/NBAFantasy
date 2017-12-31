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
projPath = "/Users/haoxiangyang/Desktop/NBA_Data/Projections/"

# function to convert the datetime date to a YYYYMMDD string
def dateConvert(currentDate):
    digTrans = {1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09'}
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
                "J.J. Barea":"Jose Barea",\
                "Wesley Matthews":"Wes Matthews",\
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
                "Wade Baldwin IV": "Wade Baldwin",\
                "Timothe Luwawu-Cabarrot": "Timothe Luwawu",\
                "Ish Smith":"Ishmael Smith",\
                "Wesley Matthews":"Wes Matthews",\
                "JR Smith":"J.R. Smith",\
                "Joe Young":"Joseph Young"}

class playerData:
    def __init__(self,ID,name,pos,fppg,played,salary,team,oppo,inj,topProb):
        self.ID = ID
        self.name = name
        self.pos = pos
        self.fppg = fppg
        self.played = played
        self.salary = salary
        self.team = team
        self.oppo = oppo
        self.inj = inj
        self.topProb = topProb
        
N = 300
M = 2
opt = 500
pairBar = 300

predictDate = datetime.date(2017,12,30)
#%%

class detOptimizer_d:
    def addLineup(self):
        self.model.optimize()
        lineupN = []
        for v in self.model.getVars():
            if abs(v.x - 1) <= 1e-6:
                lineupN.append(self.playerIndex[v.varName])
                # add the past lineups
        self.addCon[self.counter] = self.model.addConstr(quicksum(self.x[j] for j in lineupN) <= 9 - self.M)
        self.model.update()
        return lineupN
    
    def addLineup_pair(self):
        self.model.optimize()
        lineupN = []
        for v in self.model.getVars():
            if abs(v.x - 1) <= 1e-6:
                lineupN.append(self.playerIndex[v.varName])
                # add the past lineups
        
        # update the pair information
        for (i,j) in self.expPair.keys():
            if (i in lineupN)and(j in lineupN):
                self.expPair[(i,j)] += 1
            if self.expPair[(i,j)] == self.pairBar:
                self.expPair[(i,j)] += 1
                self.model.addConstr(self.x[i] + self.x[j] <= 1)
        
        lineupLP = quicksum(self.x[j] for j in lineupN)
        self.addCon[self.counter] = self.model.addConstr(lineupLP <= 9 - self.M)
        self.model.update()
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
        self.addCon = {}
        j = 0
        self.obj = 0
        self.budgetexpr = 0
        self.posexprList = {}
        self.playerIndex = {}
        self.playerIndexRev = {}
        self.expensive = []
        self.expPair = {}
        self.team = {}
        for pos in self.playertype:
            self.posexprList[pos] = 0
        for item in self.playerList:
            # only non-injured players are included
            if item.inj == '':
                self.playerIndex[item.name] = j
                self.playerIndexRev[j] = item.name
                self.x[j] = self.model.addVar(vtype=GRB.BINARY, name = item.name)
                if item.name in self.zeroList:
                    self.model.addConstr(self.x[j] == 0)
                self.obj += item.topProb*self.x[j]
                self.budgetexpr += item.salary*self.x[j]
                if item.team in self.team.keys():
                    self.team[item.team] += self.x[j]
                else:
                    self.team[item.team] = self.x[j]
                if item.salary >= 3500:
                    self.expensive.append(j)
                self.posexprList[item.pos] += self.x[j]
            j += 1
        
        # pair up the expensive players
        for i in range(len(self.expensive)):
            for j in range(i+1,len(self.expensive)):
                self.expPair[(i,j)] = 0
                
        # no more than four players in the same team
        for teamKey in self.team.keys():
            self.model.addConstr(self.team[teamKey] <= 4)
            
        self.model.update()
        self.model.setObjective(self.obj, GRB.MAXIMIZE)
        self.model.addConstr(self.budgetexpr <= self.budget, name = "BudgetConstraint")
        for pos in self.playertype:
            self.model.addConstr(self.posexprList[pos] == self.playerQ[pos])
        self.model.update()
        
        # reduce the probability of players that are frequently selected
        for i in range(N):
            self.counter = i
            #lineupN = self.addLineup()
            lineupN = self.addLineup_pair()
            for item in lineupN:
                self.playerN[self.playerIndexRev[item]][0] += 1
                if self.playerN[self.playerIndexRev[item]][0] >= self.opt:
                    self.playerN[self.playerIndexRev[item]][0] = 0
                    self.obj -= 1/3*self.playerN[self.playerIndexRev[item]][1]*self.x[item]
            self.model.setObjective(self.obj, GRB.MAXIMIZE)
            self.model.update()
            #print(i,lineupN)
            self.pastLineup.append(lineupN)
            
        
    def __init__(self,playerList,N,M,opt,pairBar,zeroList):
        self.playerList = playerList
        self.playerN = {}
        # initialize with the number of selection
        for item in self.playerList:
            self.playerN[item.name] = [0,item.topProb]
        self.N = N
        self.M = M
        self.opt = opt
        self.pairBar = pairBar
        self.zeroList = zeroList

# automatic generate N1 lineups from the blank file, the last snapshot from the predicted date
# & the list of players excluded

def zeroPlayers(predictDate,snapshotPath,epsilon):
    # exclude the players that will never make the cut    
    prepreDate = predictDate - datetime.timedelta(1)
    fileExist = False
    while not(fileExist):
        try:
            # readin the snapshot
            fi = open(snapshotPath + dateConvert(prepreDate) + ".csv","r")
            fileExist = True
        except:
            prepreDate -= datetime.timedelta(1)
    csvReader = csv.reader(fi)
    zeroList = []
    for item in csvReader:
        name = item[0]
        if float(item[3]) <= epsilon:
            zeroList.append(name)
    fi.close()
    return zeroList

def preFreq(predictDate,blankPath,snapshotPath,N,M,opt,pairBar):
    prepreDate = predictDate - datetime.timedelta(1)
    fileExist = False
    while not(fileExist):
        try:
            dateStr = dateConvert(predictDate)
            # readin the snapshot
            fi = open(snapshotPath + dateConvert(prepreDate) + ".csv","r")
            fileExist = True
        except:
            prepreDate -= datetime.timedelta(1)
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
            ID = item[0]
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
                player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,topProb)
                playerList.append(player)
            elif name in playerNameDict.keys():
                if playerNameDict[name] in snapDict.keys():
                    topProb = snapDict[playerNameDict[name]]
                    player = playerData(ID,playerNameDict[name],pos,fppg,played,salary,team,oppo,inj,topProb)
                    playerList.append(player)
                else:
                    player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,0.0)
                    playerList.append(player)
            else:
                player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,0.0)
                playerList.append(player)
    fi.close()
    # optimize using the playerList
    d = detOptimizer_d(playerList,N,M,opt,pairBar)
    d.mainOpt()
    return d
    
def preNerd(predictDate,blankPath,projPath,snapshotPath,N,M,opt,pairBar,epsilon):
    # read in the projection data from Daily Fantasy Nerd
    dateStr = dateConvert(predictDate)
    fi = open(projPath + dateStr + ".csv","r")
    csvReader = csv.reader(fi)
    projDict = {}
    counter = 0
    for item in csvReader:
        if counter == 0:
            counter += 1
        else:
            name = item[0]
            if name in projDict.keys():
                print(name)
            else:
                projDict[name] = float(item[1])
    fi.close()
    
    zeroList = zeroPlayers(predictDate,snapshotPath,epsilon)
    
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
            ID = item[0]
            name = item[3]
            pos = item[1]
            fppg = float(item[5])
            played = int(item[6])
            salary = float(item[7])
            team = item[9]
            oppo = item[10]
            inj = item[11]
            if name in projDict.keys():
                topProj = projDict[name]
                if name in playerNameDict.keys():
                    name = playerNameDict[name]
                player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,topProj)
                playerList.append(player)
            elif name in playerNameDict.keys():
                if playerNameDict[name] in projDict.keys():
                    topProj = projDict[playerNameDict[name]]
                    player = playerData(ID,playerNameDict[name],pos,fppg,played,salary,team,oppo,inj,topProj)
                    playerList.append(player)
                else:
                    player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,0.0)
                    playerList.append(player)
            else:
                player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,0.0)
                playerList.append(player)
    fi.close()
    # optimize using the playerList
    d = detOptimizer_d(playerList,N,M,opt,pairBar,zeroList)
    d.mainOpt()
    return d

def preEnsemble(predictDate,blankPath,projPath,snapshotPath,N,M,opt,pairBar,epsilon,beta):
     # read in the projection data from Daily Fantasy Nerd
    dateStr = dateConvert(predictDate)
    fi = open(projPath + dateStr + ".csv","r")
    csvReader = csv.reader(fi)
    projDict = {}
    counter = 0
    for item in csvReader:
        if counter == 0:
            counter += 1
        else:
            name = item[0]
            if name in projDict.keys():
                print(name)
            else:
                projDict[name] = float(item[1])
    fi.close()
    
    # read in the snapshot data from generated csv
    prepreDate = predictDate - datetime.timedelta(1)
    fileExist = False
    while not(fileExist):
        try:
            dateStr = dateConvert(predictDate)
            # readin the snapshot
            fi = open(snapshotPath + dateConvert(prepreDate) + ".csv","r")
            fileExist = True
        except:
            prepreDate -= datetime.timedelta(1)
    csvReader = csv.reader(fi)
    snapDict = {}
    for item in csvReader:
        name = item[0]
        if name in snapDict.keys():
            print(name)
        else:
            snapDict[name] = float(item[3])
    fi.close()
    
    zeroList = zeroPlayers(predictDate,snapshotPath,epsilon)
    
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
            ID = item[0]
            name = item[3]
            pos = item[1]
            fppg = float(item[5])
            played = int(item[6])
            salary = float(item[7])
            team = item[9]
            oppo = item[10]
            inj = item[11]
            if name in projDict.keys():
                topProj = projDict[name]
                if name in playerNameDict.keys():
                    name = playerNameDict[name]
                player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,topProj + beta*snapDict[name])
                playerList.append(player)
            elif name in playerNameDict.keys():
                if playerNameDict[name] in projDict.keys():
                    topProj = projDict[playerNameDict[name]]
                    player = playerData(ID,playerNameDict[name],pos,fppg,played,salary,team,oppo,inj,topProj + beta*snapDict[playerNameDict[name]])
                    playerList.append(player)
                else:
                    player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,0.0)
                    playerList.append(player)
            else:
                player = playerData(ID,name,pos,fppg,played,salary,team,oppo,inj,0.0)
                playerList.append(player)
    fi.close()
    # optimize using the playerList
    d = detOptimizer_d(playerList,N,M,opt,pairBar,zeroList)
    d.mainOpt()
    return d