# -*- coding: utf-8 -*-
"""
Created on Sun Jun 05 00:16:03 2016

@author: hyang89
"""
import csv
import numpy
import datetime
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import AdaBoostClassifier
from sklearn import linear_model
from sklearn import neighbors
from otherML import *

# main program
trainS = datetime.date(2015,11,10)
testS = datetime.date(2016,3,1)
testE = datetime.date(2016,4,1)

currentDate = testS
base = numpy.array([20,23,26,36,50,53,90,94,105,109])
subSet = range(7,14) + list(base) + list(base+101) + list(base+202) + list(base+303) + range(418,976)

modelNameList = ["LinearReg","Boosted","KNN","Boosted_Class","KNN_Class","LogisticReg"]
modelParamList = [[],[7,10,"exponential"],[5,'distance'],[7,10],[5,'distance'],['l2','lbfgs',1000,'multinomial',True]]
modelOutput = [[],[],[],[],[],[]]
modelHighOutput = [[],[],[],[],[],[]]
classRightRate = []
while currentDate < testE:
    trainE = currentDate + datetime.timedelta(-1)
    testE1 = currentDate + datetime.timedelta(1)
    Xtrain,XtrainSmall,Ytrain,YtrainClass,Xtest,XtestSmall,Ytest,YtestClass,title = \
        readIn("PredictorSS.csv",trainS,trainE,currentDate,testE1,subSet)
    for i in range(3):
        modelRegLarge = modelTrain(Xtrain,Ytrain,modelNameList[i],modelParamList[i])
        modelRegSmall = modelTrain(XtrainSmall,Ytrain,modelNameList[i],modelParamList[i])
        modelClassLarge = modelTrain(Xtrain,YtrainClass,modelNameList[i+3],modelParamList[i+3])
        modelClassSmall = modelTrain(XtrainSmall,YtrainClass,modelNameList[i+3],modelParamList[i+3])
        # Obtain the MSE
        MSErrorRegLarge,MSErrorRegLargeH = modelRegTest(Xtest,Ytest,modelRegLarge)
        MSErrorRegSmall,MSErrorRegSmallH = modelRegTest(XtestSmall,Ytest,modelRegSmall)
        MSErrorClassLarge,MSErrorClassLargeH,RateClassLarge = modelClassTest(Xtest,Ytest,YtestClass,modelClassLarge)
        MSErrorClassSmall,MSErrorClassSmallH,RateClassSmall = modelClassTest(XtestSmall,Ytest,YtestClass,modelClassSmall)
        # Output
        modelOutput[i].append((MSErrorRegLarge,MSErrorRegSmall))
        modelHighOutput[i].append((MSErrorRegLargeH,MSErrorRegSmallH))
        modelOutput[i+3].append((MSErrorClassLarge,MSErrorClassSmall,RateClassLarge,RateClassSmall))
        modelHighOutput[i+3].append((MSErrorClassLargeH,MSErrorClassSmallH))
    currentDate = currentDate + datetime.timedelta(1)
    
fo = open("otherML.csv","wb")
csvWriter = csv.writer(fo,dialect = "excel")
for i in range(6):
    csvWriter.writerow([modelNameList[i]])
    csvWriter.writerows(modelOutput[i])
for i in range(6):
    csvWriter.writerow([modelNameList[i]])
    csvWriter.writerows(modelHighOutput[i])
fo.close()