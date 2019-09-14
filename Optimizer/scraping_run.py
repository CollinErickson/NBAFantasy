#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 14:14:12 2017

@author: haoxiangyang
"""
from NBA_scrapper import *

yearList = [2010,2011,2012,2013,2014,2015,2016,2017]
seasonDict = {2010:("2010.10.26","2011.04.13"),
              2011:("2011.12.25","2012.04.26"),
              2012:("2012.10.30","2013.04.17"),
              2013:("2013.10.29","2014.04.16"),
              2014:("2014.10.28","2015.04.15"),
              2015:("2015.10.27","2016.04.13"),
              2016:("2016.10.25","2017.04.12"),
              2017:("2017.10.17","2018.01.11")}

for yr in yearList:
    start = seasonDict[yr][0]
    end = seasonDict[yr][1]
    a = NBAScraper(start,end,"/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/%s.csv" % yr);
    a.GetGameList()
    a.GetPlayersData()
    a.Output()
    
for yr in range(2017,2013,-1):
    start = seasonDict[yr][0]
    end = seasonDict[yr][1]
    b = SalaryScraper(start,end,"/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/Salary/")
    b.SalaryDayScraper()
    
for yr in range(2017,2013,-1):
    start = seasonDict[yr][0]
    end = seasonDict[yr][1]
    pS = projectionScraper(start,end,"/Users/haoxiangyang/Google Drive/Sports Analytics Stuff/Sports Analytics/NBA/Data/Projections/")
    pS.ProjectionDayScraper()