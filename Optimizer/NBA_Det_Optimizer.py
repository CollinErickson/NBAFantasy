# -*- coding: utf-8 -*-
"""
Created on Wed Feb 03 19:37:55 2016

@author: hyang89
"""

# this is the deterministic optimization model for back checking
# the function will take in the score of that day and type of the Fantasy ("FD"
# for FanDuel and "DK" for DraftKings.

# Right now it is only applicable to FanDuel

from gurobipy import *
#import pdb
#pdb.set_trace()
import csv

def det_Opt(scoreInput,gameType):
    fi = open(scoreInput,"r")
    csvReader = csv.reader(fi)
    data = []
    model = Model()
    for item in csvReader:
        data.append(item)
    if gameType == "FD":
        budget = 60000
        playertype = ["PG","SG","SF","PF","C"]
        playerQ = {"PG":2,"SG":2,"SF":2,"PF":2,"C":1}
        #injury = {"O":0,'':1,'GTD':1}
        x = {}
        j = 0
        obj = 0
        budgetexpr = 0
        posexprList = {}
        for pos in playertype:
            posexprList[pos] = 0
        playerInfo = {}
        for item in data[1:]:
            j = j+1
            playerInfo[item[1].replace(" ","_")] = (item[5],item[2],item[3],item[4])
            if item[4] != 'O':
                x[j] = model.addVar(vtype=GRB.BINARY, name = item[1].replace(" ","_"))
                obj += item[5]*x[j]
                budgetexpr += item[2]*x[j]
                posexprList[item[3]] += x[j]
        model.update()
        model.setObjective(obj, GRB.MAXIMIZE)
        model.addConstr(budgetexpr <= budget, name = "BudgetConstraint")
        for pos in playertype:
            model.addConstr(posexprList[pos] == playerQ[pos])
        model.update()
        #model.write('NBA_Det_Optimize.lp')
        model.optimize()
        #model.write('NBA_Det_Optimize.sol')
        total_salary_used = 0
        for v in model.getVars():
            if v.x == 1:
                print(v.varName,playerInfo[v.varName])
                total_salary_used += int(playerInfo[v.varName][1])
        print(total_salary_used)
    else:
        budget = 50000
        playertype = ["PG","SG","SF","PF","C","G","F","UTIL"]
        playerQ = [1,1,1,1,1,1,1,1]
    fi.close()
        