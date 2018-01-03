#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 13:45:07 2017

@author: haoxiangyang
"""
import os
os.chdir("/Users/haoxiangyang/Desktop/Git/NBAFantasy/Optimizer/")
 
import datetime
from gurobipy import *
from NBA_Det_Optimizer import *
import csv
from NBA_scrapper import *
from det_Predict import *
from det_Validation import *
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

# read in last winning position data
lastWin = {}
fi = open("/Users/haoxiangyang/Desktop/NBA_Data/lastWinning.csv","r")
csvReader = csv.reader(fi,dialect = "excel")
for item in csvReader:
    dateList = item[0].split("/")
    cDate = datetime.date(2000+int(dateList[2]),int(dateList[0]),int(dateList[1]))
    lastWin[cDate] = float(item[1])
fi.close()

#%%

#salaryAdd = salaryPath + "20171216.csv"
#blankAdd = blankPath + "20171216.csv"
#teamList = ["okc","phi","por","orl","det","ind","mia","cha","lac","was","bkn","tor","uta","bos","chi","mil","atl","mem","nor","den","sas","hou"]
#convertBlank(salaryAdd,teamList,blankAdd)

predictDate = datetime.date(2017,12,30)
d2 = preNerd(predictDate,blankPath,projPath,snapshotPath,N,2,opt,50,1e-5)
salaryDict = readSalary(salaryPath + "20171230.csv")
FDScoreList = optValidation(d2.pastLineup,salaryDict,d2.playerIndexRev)
print(max(FDScoreList))
print(sum([i >= 303.7 for i in FDScoreList]))

#%%

# test out the no feature, changing the gap M
predictDate = datetime.date(2017,11,28)
maxResult_M = {}
sumResult_M = {}
MList = [1,2,3,4]
for i in MList:
    maxResult_M[i] = {}
    sumResult_M[i] = {}
end = datetime.date(2017,12,29)
while predictDate <= end:
    try:
        for i in MList:
            d3 = preNerd(predictDate,blankPath,projPath,snapshotPath,N,i,opt,50,1e-5)
            salaryDict = readSalary(salaryPath + dateConvert(predictDate) + ".csv")
            FDScoreList = optValidation(d3.pastLineup,salaryDict,d3.playerIndexRev)
            maxResult_M[i][predictDate] = max(FDScoreList)
            if predictDate in lastWin.keys():
                sumResult_M[i][predictDate] = sum([pl >= lastWin[predictDate] for pl in FDScoreList])
            print("Date {} Run {} finished".format(predictDate,i))
    except:
        print("Date {} Error".format(predictDate))
    
    predictDate = predictDate + datetime.timedelta(1)
#%%

# test out different lineup base pair change
predictDate = datetime.date(2017,12,29)
maxResult_P = {}
sumResult_P = {}
pList = [10,30,50,70,90,110]
for i in pList:
    maxResult_P[i] = {}
    sumResult_P[i] = {}
end = datetime.date(2017,12,29)
while predictDate <= end:
    try:
        for i in pList:
            d4 = preNerd(predictDate,blankPath,projPath,snapshotPath,N,1,opt,i,1e-5)
            salaryDict = readSalary(salaryPath + dateConvert(predictDate) + ".csv")
            FDScoreList = optValidation(d4.pastLineup,salaryDict,d4.playerIndexRev)
            maxResult_P[i][predictDate] = max(FDScoreList)
            if predictDate in lastWin.keys():
                sumResult_P[i][predictDate] = sum([pl >= lastWin[predictDate] for pl in FDScoreList])
            print("Date {} Run {} finished".format(predictDate,i))
    except:
        print("Date {} Error".format(predictDate))
    
    predictDate = predictDate + datetime.timedelta(1)
#%%
    
# print the output
#fo = open("/Users/haoxiangyang/Desktop/NBA_Data/Pcomp.csv","w",newline = "")
fo = open("/Users/haoxiangyang/Desktop/NBA_Data/Mcomp_C.csv","w",newline = "")
csvWriter = csv.writer(fo,dialect = "excel")
csvWriter.writerow(["",1,2,3,4])
#csvWriter.writerow(["",10,30,50,70,90,110])
predictDate = datetime.date(2017,11,28)
while predictDate <= end:
    dateOut = [predictDate]
    for i in MList:
#    for i in pList:
        #if predictDate in maxResult_P[i].keys():
        if predictDate in maxResult_M[i].keys():
            dateOut.append(maxResult_M[i][predictDate])
            # dateOut.append(maxResult_P[i][predictDate])
    csvWriter.writerow(dateOut)
    predictDate += datetime.timedelta(1)
predictDate = datetime.date(2017,11,28)
while predictDate <= end:
    dateOut = [predictDate]
    for i in MList:
#    for i in pList:
#        if predictDate in sumResult_P[i].keys():
#            dateOut.append(sumResult_P[i][predictDate])
        if predictDate in sumResult_M[i].keys():
            dateOut.append(sumResult_M[i][predictDate])
    csvWriter.writerow(dateOut)
    predictDate += datetime.timedelta(1)
    
fo.close()

#%%

# combine the P50-M3 and P50-M4
predictDate = datetime.date(2017,11,28)
end = datetime.date(2017,12,29)
maxResult_C = {}
sumResult_C = {}
luNo = {}
# record how many lineups are filled
while predictDate <= end:
    pastLineup = []
    try:
        d5 = preNerd(predictDate,blankPath,projPath,snapshotPath,N,3,opt,50,1e-5)
        d6 = preNerd(predictDate,blankPath,projPath,snapshotPath,N,4,opt,50,1e-5)
        # combine the past lineups from d5 and d6
        for item in d5.pastLineup:
            if not(item in pastLineup):
                pastLineup.append(item)
        for item in d6.pastLineup:
            if not(item in pastLineup):
                pastLineup.append(item)
        salaryDict = readSalary(salaryPath + dateConvert(predictDate) + ".csv")
        luNo[predictDate] = len(pastLineup)
        FDScoreList = optValidation(pastLineup,salaryDict,d5.playerIndexRev)
        maxResult_C[predictDate] = max(FDScoreList)
        if predictDate in lastWin.keys():
            sumResult_C[predictDate] = sum([pl >= lastWin[predictDate] for pl in FDScoreList])
    except:
        print("Date {} Error".format(predictDate))
    
    predictDate = predictDate + datetime.timedelta(1)

fo = open("/Users/haoxiangyang/Desktop/NBA_Data/Mcomp_C.csv","w",newline = "")
csvWriter = csv.writer(fo,dialect = "excel")
csvWriter.writerow(["","No. of Lineups","Max Score","No. of Earning Entries"])
#csvWriter.writerow(["",10,30,50,70,90,110])
predictDate = datetime.date(2017,11,28)
while predictDate <= end:
    try:
        dateOut = [predictDate,luNo[predictDate]]
        if predictDate in maxResult_C.keys():
            dateOut.append(maxResult_C[predictDate])
        if predictDate in sumResult_C.keys():
            dateOut.append(sumResult_C[predictDate])
        csvWriter.writerow(dateOut)
    except:
        aaa = 1
    predictDate += datetime.timedelta(1)
fo.close()