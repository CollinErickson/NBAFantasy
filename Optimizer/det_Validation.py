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
salaryPath = "/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/Salary/"

# recover the blank file from the salary file by giving the date and the match info
# match info input as a list with team name xxx
def convertBlank(salaryAdd,teamList,blankAdd):
    # can't have the injury info, list all DNP and NA players as ineligible
    fi = open(salaryAdd,"r")
    csvReader = csv.reader(fi)
    # read in the players
    counter = 0
    playerOut = [["Id","Position","First Name","Nickname","Last Name","FPPG","Played","Salary","Game","Team","Opponent","Injury Indicator","Injury Details"]]
    for item in csvReader:
        if counter == 0:
            counter += 1
        else:
            if (item[7] in teamList) or (item[8] in teamList):
                if (item[12] != "DNP") and (item[12] != "NA"):
                    playerData = [item[0],item[1],item[2],item[2]+" "+item[3],item[3],0,0,item[6],"",item[7],item[8],"",""]
                else:
                    playerData = [item[0],item[1],item[2],item[2]+" "+item[3],item[3],0,0,item[6],"",item[7],item[8],"O",""]
                playerOut.append(playerData)
    fi.close()
    
    fo = open(blankAdd,"w",newline = "")
    csvWriter = csv.writer(fo, dialect = "excel")
    csvWriter.writerows(playerOut)
    fo.close()
    

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
#        try:
        FDtotScore = 0
        for it in item:
            playerName = playerDict[it]
            #print(playerName)
            FDtotScore += salaryDict[playerName]
        FDScoreList.append(FDtotScore)
#        except:
#            print(item)
    return FDScoreList
        # print the information to test
        #print(FDtotScore)