#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 21:54:08 2018

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
        
#%%
        
