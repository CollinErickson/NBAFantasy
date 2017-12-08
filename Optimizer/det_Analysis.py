# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 23:59:54 2017

@author: haoxi
"""

 # deterministic optimization analysis: check what players are among the most picked
import datetime
from gurobipy import *
from NBA_Det_Optimizer import *
import csv
#import pdb
#pdb.set_trace()
#%%
# first generate the top 500 picks of each day
start = datetime.date(2017,10,17)
end = datetime.date(2017,12,3)
currentDate = start
salaryPath = "C:/Documents/PhD/Sports/FD/Salary/"
lineupPath = "C:/Documents/PhD/Sports/FD/Lineups/"
N = 2000

digTrans = {1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09'}
 
while currentDate <= end:
    # for every single day print out the top 500 lineups in csv format
    try:
        if currentDate.month < 10:
            monthTemp = digTrans[currentDate.month]
        else:
            monthTemp = str(currentDate.month)
        if currentDate.day < 10:
            dayTemp = digTrans[currentDate.day]
        else:
            dayTemp = str(currentDate.day)
            
        c = detOptimizer(str(currentDate.year)+monthTemp+dayTemp,salaryPath,lineupPath,N)
        c.mainN()
        c.outputLineups()
    except:
        print(currentDate)
    currentDate = currentDate + datetime.timedelta(1)
     
#%%
# After hand draw the trend of position of top human player's, $75 winner's order in the list of best options
# Collect the information of how many times a player has shown up in the top 2000?1000?
    
snapshotPath = "C:/Documents/PhD/Sports/FD/Snapshot/"
    
currentDate = start
playerList = []
pBaseDict = {}
pActDict = {}
while currentDate <= end:
    if currentDate.month < 10:
        monthTemp = digTrans[currentDate.month]
    else:
        monthTemp = str(currentDate.month)
    if currentDate.day < 10:
        dayTemp = digTrans[currentDate.day]
    else:
        dayTemp = str(currentDate.day)
    
    # first generate a list of players
    fi = open(salaryPath + str(currentDate.year) + monthTemp + dayTemp + ".csv","r")
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
    fi = open(lineupPath + str(currentDate.year) + monthTemp + dayTemp + ".csv","r")
    csvReader = csv.reader(fi)
    counter = 0
    for item in csvReader:
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
    fi.close()
    
    # make a snapshot
    fo = open(snapshotPath + str(currentDate.year) + monthTemp + dayTemp + ".csv","w",newline = '')
    csvWriter = csv.writer(fo,dialect = 'excel')
    for pl in playerList:
        csvWriter.writerow([pl,pActDict[pl],pBaseDict[pl],pActDict[pl]/pBaseDict[pl]])
    fo.close()
    
    currentDate = currentDate + datetime.timedelta(1)
    