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
start = datetime.date(2016,10,25)
end = datetime.date(2017,4,12)
currentDate = start
salaryPath = "/home/haoxiang/FD/Salary/"
lineupPath = "/home/haoxiang/FD/Lineups/"
N = 20

digTrans = {1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09'}

def run_date(currentDate):
    digTrans = {1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09'}
#    salaryPath = "/Users/haoxiangyang/Desktop/NBA_Data/Salary/"
#    lineupPath = "/Users/haoxiangyang/Desktop/NBA_Data/Lineups/"
    salaryPath = "/home/haoxiang/FD/Salary/"
    lineupPath = "/home/haoxiang/FD/Lineups/"
    N = 2000
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

currentDateSet = []
while currentDate <= end:
    # for every single day print out the top 500 lineups in csv format
    currentDateSet.append(currentDate)
    currentDate = currentDate + datetime.timedelta(1)
     
if __name__ == '__main__':
    p = Pool(10)
    p.map(run_date, currentDateSet)