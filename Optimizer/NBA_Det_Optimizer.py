# -*- coding: utf-8 -*-
"""
Created on Wed Feb 03 19:37:55 2016

@author: hyang89
"""

# this is the deterministic optimization model for back checking
# the function will take in the score of that day. Input as 

from gurobipy import *
#import pdb
#pdb.set_trace()
import csv

class detOptimizer:
    
    def det_Opt(self):
        
        self.model.optimize()
        lineupN = []
        for v in self.model.getVars():
            if v.x == 1:
                lineupN.append(self.playerIndex[v.varName])
                # add the past lineups
        self.model.addConstr(quicksum(self.x[j] for j in lineupN) <= 9 - self.M)
        return lineupN
    
    def mainN(self):
        # set up the lineups that have already been picked
        self.pastLineup = []
        
        # set up the model
        self.model = Model()
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
        self.playerInfo = {}
        for item in self.SalaryScoreData:
            j = j+1
            fullname = item[2] + "_" + item[3]
            # item: 1 as position, 2 as first name, 3 as last name, 5 as FD score, 6 as salary
            fdscore = float(item[5])
            salary = float(item[6])
            self.playerInfo[fullname] = (fdscore,salary,item[1])
            self.playerIndex[fullname] = j
            self.playerIndexRev[j] = fullname
            self.x[j] = self.model.addVar(vtype=GRB.BINARY, name = fullname)
            self.obj += fdscore*self.x[j]
            self.budgetexpr += salary*self.x[j]
            self.posexprList[item[1]] += self.x[j]
            
        self.model.update()
        self.model.setObjective(self.obj, GRB.MAXIMIZE)
        self.model.addConstr(self.budgetexpr <= self.budget, name = "BudgetConstraint")
        for pos in self.playertype:
            self.model.addConstr(self.posexprList[pos] == self.playerQ[pos])
        self.model.update()
        for i in range(self.N):
            lineupN = self.det_Opt()
            self.pastLineup.append(lineupN)
            
    def outputLineups(self):
        fo = open(self.outAdd,"w",newline = '')
        csvWriter = csv.writer(fo,dialect = 'excel')
        title = ["Lineup No.","PG","FD Score","Salary","PG","FD Score","Salary","SG","FD Score","Salary",\
                 "SG","FD Score","Salary","PF","FD Score","Salary","PF","FD Score","Salary","SF","FD Score","Salary",\
                 "SF","FD Score","Salary","C","FD Score","Salary","Total Score","Total Salary"]
        csvWriter.writerow(title)
        
        counter = 0
        for lineup in self.pastLineup:
            outList = [0]*len(title)
            counter += 1
            outList[0] = counter
            totalScore = 0
            totalSalary = 0
            
            for item in lineup:
                
                # fill first PG
                if self.playerInfo[self.playerIndexRev[item]][2] == "PG":
                    if outList[1] == 0:
                        outList[1] = self.playerIndexRev[item]
                        outList[2] = self.playerInfo[self.playerIndexRev[item]][0]
                        totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                        outList[3] = self.playerInfo[self.playerIndexRev[item]][1]
                        totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                    else:
                        outList[4] = self.playerIndexRev[item]
                        outList[5] = self.playerInfo[self.playerIndexRev[item]][0]
                        totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                        outList[6] = self.playerInfo[self.playerIndexRev[item]][1]
                        totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                elif self.playerInfo[self.playerIndexRev[item]][2] == "SG":
                    if outList[7] == 0:
                        outList[7] = self.playerIndexRev[item]
                        outList[8] = self.playerInfo[self.playerIndexRev[item]][0]
                        totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                        outList[9] = self.playerInfo[self.playerIndexRev[item]][1]
                        totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                    else:
                        outList[10] = self.playerIndexRev[item]
                        outList[11] = self.playerInfo[self.playerIndexRev[item]][0]
                        totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                        outList[12] = self.playerInfo[self.playerIndexRev[item]][1]
                        totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                elif self.playerInfo[self.playerIndexRev[item]][2] == "PF":
                    if outList[13] == 0:
                        outList[13] = self.playerIndexRev[item]
                        outList[14] = self.playerInfo[self.playerIndexRev[item]][0]
                        totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                        outList[15] = self.playerInfo[self.playerIndexRev[item]][1]
                        totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                    else:
                        outList[16] = self.playerIndexRev[item]
                        outList[17] = self.playerInfo[self.playerIndexRev[item]][0]
                        totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                        outList[18] = self.playerInfo[self.playerIndexRev[item]][1]
                        totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                elif self.playerInfo[self.playerIndexRev[item]][2] == "SF":
                    if outList[19] == 0:
                        outList[19] = self.playerIndexRev[item]
                        outList[20] = self.playerInfo[self.playerIndexRev[item]][0]
                        totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                        outList[21] = self.playerInfo[self.playerIndexRev[item]][1]
                        totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                    else:
                        outList[22] = self.playerIndexRev[item]
                        outList[23] = self.playerInfo[self.playerIndexRev[item]][0]
                        totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                        outList[24] = self.playerInfo[self.playerIndexRev[item]][1]
                        totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                else:
                    outList[25] = self.playerIndexRev[item]
                    outList[26] = self.playerInfo[self.playerIndexRev[item]][0]
                    totalScore += self.playerInfo[self.playerIndexRev[item]][0]
                    outList[27] = self.playerInfo[self.playerIndexRev[item]][1]
                    totalSalary += self.playerInfo[self.playerIndexRev[item]][1]
                    
            outList[28] = totalScore
            outList[29] = totalSalary
            csvWriter.writerow(outList)
            
        fo.close()
            
    
    def __init__(self,date,inPath,outPath,N,M):
        # create the input path and the output path
        self.inAdd = inPath + date + ".csv"
        self.outAdd = outPath + date + "_" + str(N) + ".csv"
        self.N = N
        self.M = M
        
        fi = open(self.inAdd,"r")
        csvReader = csv.reader(fi)
        data = []
        counter = 0
        for item in csvReader:
            if counter == 0:
                counter += 1
            else:
                data.append(item)
        fi.close()
        self.SalaryScoreData = data