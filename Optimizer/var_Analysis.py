#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 16:13:35 2017

@author: haoxiangyang
"""

# variance analysis of the daily fantasy nerd predictions

import os
os.chdir("/Users/haoxiangyang/Desktop/Git/NBAFantasy/Optimizer/")
 
import datetime
from gurobipy import *
from NBA_Det_Optimizer import *
import csv
from NBA_scrapper import *
import matplotlib.pyplot as plt
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
                "JR Smith":"J.R. Smith"}

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
  

def readSalary(salaryAdd):
    # return a dictionary of fd points
    fi = open(salaryAdd,"r")
    csvReader = csv.reader(fi)
    counter = 0
    salaryDict = {}
    for item in csvReader:
        if counter == 0:
            counter += 1
        else:
            playerName = item[2] + " " + item[3]
            salaryDict[playerName] = float(item[5])
    return salaryDict

      
def compareProj(start,end,projPath,salaryPath):
    # record the predicted point difference and the normalized point difference
    startList = start.split(".")
    endList = end.split(".")
    start = datetime.date(int(startList[0]),int(startList[1]),int(startList[2]))
    end = datetime.date(int(endList[0]),int(endList[1]),int(endList[2]))
    
    currentDate = start
    totalDiff = []
    while currentDate <= end:
        try:
            dateStr = dateConvert(currentDate)
            # read the salary data of the day
            salaryDict = readSalary(salaryPath + dateStr + ".csv")
            
            # read the projected FD scores
            fi = open(projPath + dateStr + ".csv","r")
            csvReader = csv.reader(fi)
            counter = 0
            for item in csvReader:
                if counter == 0:
                    counter += 1
                else:
                    namePl = item[0]
                    projV = float(item[1])
                    if namePl in salaryDict.keys():
                        diff = projV - salaryDict[namePl]
                    else:
                        if namePl in playerNameDict.keys():
                            if playerNameDict[namePl] in salaryDict.keys():
                                diff = projV - salaryDict[playerNameDict[namePl]]
                            else:
                                diff = projV - 0
                    totalDiff.append([projV,diff])
        except:
            print(currentDate)
        
        currentDate = currentDate + datetime.timedelta(1)
    return totalDiff

def comparePlayerProj(start,end,projPath,salaryPath):
    # record the predicted point difference for every player
    # examine which player has the largest variance
    startList = start.split(".")
    endList = end.split(".")
    start = datetime.date(int(startList[0]),int(startList[1]),int(startList[2]))
    end = datetime.date(int(endList[0]),int(endList[1]),int(endList[2]))
    
    currentDate = start
    playerDiff = {}
    
    while currentDate <= end:
        try:
            dateStr = dateConvert(currentDate)
            # read the salary data of the day
            salaryDict = readSalary(salaryPath + dateStr + ".csv")
            
            # read the projected FD scores
            fi = open(projPath + dateStr + ".csv","r")
            csvReader = csv.reader(fi)
            counter = 0
            for item in csvReader:
                if counter == 0:
                    counter += 1
                else:
                    namePl = item[0]
                    projV = float(item[1])
                    if namePl in salaryDict.keys():
                        diff = projV - salaryDict[namePl]
                        if namePl in playerDiff.keys():
                            playerDiff[namePl].append([projV,diff])
                        else:
                            playerDiff[namePl] = [[projV,diff]]
                    else:
                        if namePl in playerNameDict.keys():
                            if playerNameDict[namePl] in salaryDict.keys():
                                diff = projV - salaryDict[playerNameDict[namePl]]
                            else:
                                diff = projV - 0
                            if namePl in playerDiff.keys():
                                playerDiff[namePl].append([projV,diff])
                            else:
                                playerDiff[namePl] = [[projV,diff]]
        except:
            print(currentDate)
        
        currentDate = currentDate + datetime.timedelta(1)
    return playerDiff