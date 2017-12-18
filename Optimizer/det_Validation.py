#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 23:45:43 2017

@author: haoxiangyang
"""
import os
os.chdir("/Users/haoxiangyang/Desktop/Git/NBAFantasy/Optimizer/")
 
import datetime
from gurobipy import *
from NBA_Det_Optimizer import *
import csv
from NBA_scrapper import *
salaryPath = "/Users/haoxiangyang/Desktop/NBA_Data/Salary/"

# deterministic optimization obtained N lineups
# validate against the salary info of that day to check the quality of generated lineups
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

def optValidation(lineupList,salaryDict,playerDict):
    # print the lineup and the FD score of that lineup, return a list of FD scores
    FDScoreList = []
    for item in lineupList:
        try:
            FDtotScore = 0
            for it in item:
                playerName = playerDict[it]
                #print(playerName)
                FDtotScore += salaryDict[playerName]
            FDScoreList.append(FDtotScore)
        except:
            print(item)
    return FDScoreList
        # print the information to test
        #print(FDtotScore)