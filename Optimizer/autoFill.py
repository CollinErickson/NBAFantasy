#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 12:33:08 2017

@author: haoxiangyang
"""

#%%

# auto fill the brackets
def autoFill(lineObj,outAdd):
    fo = open(outAdd,"w",newline = "")
    csvWriter = csv.writer(fo,dialect = "excel")
    csvWriter.writerow(["PG","PG","SG","SG","SF","SF","PF","PF","C"])
    
    # for each generated lineup
    for lup in lineObj.pastLineup:
        # correct the sequence of the lineup
        lineOut = ["","","","","","","","",""]
        for playerNo in lup:
            player = lineObj.playerList[playerNo]
            # PG
            if player.pos == "PG":
                if lineOut[0] == "":
                    lineOut[0] = player.ID
                else:
                    lineOut[1] = player.ID
            # SG
            if player.pos == "SG":
                if lineOut[2] == "":
                    lineOut[2] = player.ID
                else:
                    lineOut[3] = player.ID
            # SF
            if player.pos == "SF":
                if lineOut[4] == "":
                    lineOut[4] = player.ID
                else:
                    lineOut[5] = player.ID
            # PF
            if player.pos == "PF":
                if lineOut[6] == "":
                    lineOut[6] = player.ID
                else:
                    lineOut[7] = player.ID
            # C
            if player.pos == "C":
                lineOut[8] = player.ID
        csvWriter.writerow(lineOut)
    fo.close()