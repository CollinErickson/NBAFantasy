# -*- coding: utf-8 -*-
"""
Created on Sat Jun 04 21:49:52 2016

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
#import matplotlib.pyplot as plt
#from operator import add

# read-in the data
def transDate(dateStr):
    dateList = dateStr.split("-")
    dateReturn = datetime.date(int(dateList[0]),int(dateList[1]),int(dateList[2]))
    return dateReturn

def readIn(address,startDateTrain,endDateTrain,startDateTest,endDateTest,subset):
    fi = open(address,"r")
    csvReader = csv.reader(fi,dialect = "excel")
    ytrain = []
    xtrain = []
    xtrainSmall = []
    ytest = []
    xtest = []
    xtestSmall = []
    ytrainclass = []
    ytestclass = []
    counter = 0
    #zeroClass = [0]*11
    ytrainclass = []
    ytestclass = []
    for item in csvReader:
        if counter != 0:
            if (transDate(item[0]) >= startDateTrain) and (transDate(item[0]) < endDateTrain):
                fdPoints = float(item[1])
                ytrain.append(fdPoints)
                #tempClass = zeroClass[:]
                if fdPoints <= 5:
                    #tempClass[0] = 1
                    ytrainclass.append(0)
                elif fdPoints <= 10:
                    #tempClass[1] = 1
                    ytrainclass.append(1)
                elif fdPoints <= 15:
                    #tempClass[2] = 1
                    ytrainclass.append(2)
                elif fdPoints <= 20:
                    #tempClass[3] = 1
                    ytrainclass.append(3)
                elif fdPoints <= 25:
                    #tempClass[4] = 1
                    ytrainclass.append(4)
                elif fdPoints <= 30:
                    #tempClass[5] = 1
                    ytrainclass.append(5)
                elif fdPoints <= 35:
                    #tempClass[6] = 1
                    ytrainclass.append(6)
                elif fdPoints <= 40:
                    #tempClass[7] = 1
                    ytrainclass.append(7)
                elif fdPoints <= 45:
                    #tempClass[8] = 1
                    ytrainclass.append(8)
                elif fdPoints <= 50:
                    #tempClass[9] = 1
                    ytrainclass.append(9)
                else:
                    #tempClass[10] = 1
                    ytrainclass.append(10)
                #ytrainClass.append(tempClass)
                xtrain.append(map(float,item[7:]))
                xtrainSmall.append(map(float,[item[i] for i in subset]))
            if (transDate(item[0]) >= startDateTest) and (transDate(item[0]) < endDateTest):
                fdPoints = float(item[1])
                ytest.append(fdPoints)
                #tempClass = zeroClass[:]
                if fdPoints <= 5:
                    #tempClass[0] = 1
                    ytestclass.append(0)
                elif fdPoints <= 10:
                    #tempClass[1] = 1
                    ytestclass.append(1)
                elif fdPoints <= 15:
                    #tempClass[2] = 1
                    ytestclass.append(2)
                elif fdPoints <= 20:
                    #tempClass[3] = 1
                    ytestclass.append(3)
                elif fdPoints <= 25:
                    #tempClass[4] = 1
                    ytestclass.append(4)
                elif fdPoints <= 30:
                    #tempClass[5] = 1
                    ytestclass.append(5)
                elif fdPoints <= 35:
                    #tempClass[6] = 1
                    ytestclass.append(6)
                elif fdPoints <= 40:
                    #tempClass[7] = 1
                    ytestclass.append(7)
                elif fdPoints <= 45:
                    #tempClass[8] = 1
                    ytestclass.append(8)
                elif fdPoints <= 50:
                    #tempClass[9] = 1
                    ytestclass.append(9)
                else:
                    #tempClass[10] = 1
                    ytestclass.append(10)
                xtest.append(map(float,item[7:]))
                xtestSmall.append(map(float,[item[i] for i in subset]))
        else:
            counter += 1
            title = item
    return xtrain,xtrainSmall,ytrain,ytrainclass,xtest,xtestSmall,ytest,ytestclass,title

# training boosted tree, knn, svr, linear regression for regression
def modelTrain(xtrain,ytrain,modelName,modelParams):
    if modelName == "Boosted":
        predictor = AdaBoostRegressor(DecisionTreeRegressor(max_depth = modelParams[0]),n_estimators = modelParams[1],loss = modelParams[2])
        predictor.fit(xtrain,ytrain)
    elif modelName == "KNN":
        predictor = neighbors.KNeighborsRegressor(modelParams[0],weights = modelParams[1])
        predictor.fit(xtrain,ytrain)
    elif modelName == "LinearReg":
        predictor = linear_model.LinearRegression()
        predictor.fit(xtrain,ytrain)
    elif modelName == "Boosted_Class":
        predictor = AdaBoostClassifier(DecisionTreeClassifier(max_depth = modelParams[0]),n_estimators = modelParams[1])
        predictor.fit(xtrain,ytrain)
    elif modelName == "KNN_Class":
        predictor = neighbors.KNeighborsClassifier(modelParams[0],weights = modelParams[1])
        predictor.fit(xtrain,ytrain)
    elif modelName == "LogisticReg":
        predictor = linear_model.LogisticRegression(penalty=modelParams[0],solver = modelParams[1],max_iter = modelParams[2],multi_class = modelParams[3],warm_start= modelParams[4])
        predictor.fit(xtrain,ytrain)
    return predictor

# testing program for regression
def modelRegTest(xtest,ytest,predictor):
    ytest = numpy.array(ytest)
    ybar = numpy.array(predictor.predict(xtest))
    yerror = ybar - ytest
    MSE = numpy.mean(numpy.square(yerror))
    yerrorH = numpy.array([yerror[i] for i in range(len(ytest)) if ytest[i]>=30])
    MSEH = numpy.mean(numpy.square(yerrorH))
    return MSE,MSEH
    
# testing program for classification
def modelClassTest(xtest,ytest,ytestClass,predictor):
    ytest = numpy.array(ytest)
    ybar = predictor.predict(xtest)
    rate = sum(ytestClass == ybar)
    ybarProb = predictor.predict_proba(xtest)
    yestimation = ybarProb[:,0]*2 + ybarProb[:,1]*7.5 + ybarProb[:,2]*12.5 + ybarProb[:,3]*17.5 + ybarProb[:,4]*22.5 + ybarProb[:,5]*27.5\
        + ybarProb[:,6]*32.5 + ybarProb[:,7]*37.5+ybarProb[:,8]*42.5+ybarProb[:,9]*47.5+ybarProb[:,10]*60
    yerror = yestimation - ytest
    MSE = numpy.mean(numpy.square(yerror))
    yerrorH = numpy.array([yerror[i] for i in range(len(ytest)) if ytest[i]>=30])
    MSEH = numpy.mean(numpy.square(yerrorH))
    
    return MSE,MSEH,rate