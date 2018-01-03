# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 10:06:54 2016

@author: haoxi
"""

import csv
import numpy

# generate the player name-id dictionary

fi = open("C:\\Documents\\PhD\\Sports\\Sports Analytics\\Sports Analytics Stuff\\Sports Analytics\\NBA\\Archive\\IDdict1.csv","r")
csvReader = csv.reader(fi,dialect = "excel")

idDict = {}

counter = 0

for item in csvReader:
    if counter == 0:
        title = item
        counter += 1
    else:
        idDict[item[1]] = int(item[0])

fi.close()
numpy.save("C:\\Documents\\PhD\\Sports\\Sports Analytics\\Sports Analytics Stuff\\Sports Analytics\\NBA\\Archive\\idDict.npy",[idDict])