#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 07:16:52 2017

@author: haoxiangyang
"""

# Read in a FanDuel blank spreadsheet, check the most recent snapshot and append
# the probability information to it and make the selection

import os
os.chdir("/Users/haoxiangyang/Desktop/Git/NBAFantasy/Optimizer/")
import datetime
from gurobipy import *
from NBA_Det_Optimizer import *
import csv
import pdb
pdb.set_trace()

#%%
# need a function to recover the daily blank file by giving the list of games played that day

def blankRecover(date,gameList):
    # gameList should have a format of "xxx at "

#%%

# N is the number of lineups selected
# M is the difference between two lineups
N = 300
M = 2