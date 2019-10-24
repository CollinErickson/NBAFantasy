# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 23:59:54 2017

@author: haoxi
"""

 # deterministic optimization analysis: check what players are among the most picked
import os
os.chdir("/Users/haoxiangyang/Desktop/Git/NBAFantasy/Optimizer/")
 
import datetime
from gurobipy import *
from NBA_Det_Optimizer import *
import csv
from NBA_scrapper import *
#import pdb
#pdb.set_trace()
salaryPath = "/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/Salary/"
lineupPath = "/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/Lineups/"
snapshotPath = "/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/Snapshot/"
blankPath = "/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/Blank/"
projPath = "/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/Projections/"

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

#%%
# first generate the top 2000 picks of each day
start = datetime.date(2018,1,4)
end = datetime.date(2018,1,4)
currentDate = start
#salaryPath = "C:/Documents/PhD/Sports/FD/Salary/"
#lineupPath = "C:/Documents/PhD/Sports/FD/Lineups/"
N = 2000
M = 1
# 
while currentDate <= end:
    # for every single day print out the top 500 lineups in csv format
#    try:
    dateStr = dateConvert(currentDate) 
    c = detOptimizer(dateStr,salaryPath,lineupPath,N,M)
    c.mainN()
    c.outputLineups()
#    except:
#        print(currentDate)
    currentDate = currentDate + datetime.timedelta(1)
#
#%%
# After hand draw the trend of position of top human player's, $75 winner's order in the list of best options
# Collect the information of how many times a player has shown up in the top 2000?1000?
    
#snapshotPath = "C:/Documents/PhD/Sports/FD/Snapshot/"
    
currentDate = start
playerList = []
pBaseDict = {}
pActDict = {}
N = 2000
while currentDate <= end:
    try:
        dateStr = dateConvert(currentDate) 
        # first generate a list of players
        fi = open(salaryPath + dateStr + ".csv","r")
        csvReader = csv.reader(fi)
        # read in the data from the salary file
        counter = 0
        for item in csvReader:
            if counter == 0:
                counter += 1
            else:
                # if the player is not in the player list, append the player's name to the list
                name = item[2] + " " + item[3]
                if not(name in playerList):
                    playerList.append(name)
                    pBaseDict[name] = N
                    pActDict[name] = 0
                else:
                    pBaseDict[name] += N
        # finish reading the salary data            
        fi.close()
        
        # read in the N best lineup file
        fi = open(lineupPath + dateStr + "_" + str(N) + ".csv","r")
        csvReader = csv.reader(fi)
        counter = 0
        for item in csvReader:
            try:
                if counter == 0:
                    counter += 1
                else:
                    # record the players
                    PG1name = item[1].replace("_"," ")
                    pActDict[PG1name] += 1
                    PG2name = item[4].replace("_"," ")
                    pActDict[PG2name] += 1
                    SG1name = item[7].replace("_"," ")
                    pActDict[SG1name] += 1
                    SG2name = item[10].replace("_"," ")
                    pActDict[SG2name] += 1
                    PF1name = item[13].replace("_"," ")
                    pActDict[PF1name] += 1
                    PF2name = item[16].replace("_"," ")
                    pActDict[PF2name] += 1
                    SF1name = item[19].replace("_"," ")
                    pActDict[SF1name] += 1
                    SF2name = item[22].replace("_"," ")
                    pActDict[SF2name] += 1
                    Cname = item[25].replace("_"," ")
                    pActDict[Cname] += 1
            except:
                print(currentDate,item)
        fi.close()
        
        # make a snapshot
        fo = open(snapshotPath + dateStr + ".csv","w",newline = '')
        csvWriter = csv.writer(fo,dialect = 'excel')
        for pl in playerList:
            csvWriter.writerow([pl,pActDict[pl],pBaseDict[pl],pActDict[pl]/pBaseDict[pl]])
        fo.close()
        
        currentDate = currentDate + datetime.timedelta(1)
    except:
        print(currentDate)
        currentDate = currentDate + datetime.timedelta(1)
        
#%%
# After creating all the snapshot, use probability as a reward 
testRunAdd = "/Users/haoxiangyang/Desktop/NBA/testRun_20171213.csv"
fi = open(testRunAdd,"r")
csvReader = csv.reader(fi)
model = Model()
counter = 0
obj = 0
budgetexpr = 0
x = {}
j = 0
playertype = ["PG","SG","SF","PF","C"]
playerQ = {"PG":2,"SG":2,"SF":2,"PF":2,"C":1}
posexprList = {}
budget = 60000
for pos in playertype:
    posexprList[pos] = 0
for item in csvReader:
    if counter == 0:
        counter += 1
    else:
        fullname = item[3]
        j += 1
        x[j] = model.addVar(vtype=GRB.BINARY, name = fullname)
        prob = float(item[13])
        obj += prob*x[j]
        salary = float(item[7])
        budgetexpr += salary*x[j]
        posexprList[item[1]] += x[j]
        
model.update()
model.setObjective(obj, GRB.MAXIMIZE)
model.addConstr(budgetexpr <= budget, name = "BudgetConstraint")
for pos in playertype:
    model.addConstr(posexprList[pos] == playerQ[pos])
model.update()
model.optimize()
for v in model.getVars():
    if v.x == 1:
        print(v.varName,"\n")
        
fi.close()