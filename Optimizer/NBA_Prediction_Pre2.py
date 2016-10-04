# -*- coding: utf-8 -*-
"""
Created on Fri May 27 10:59:00 2016

@author: hyang89
"""

import csv
import datetime
from operator import add

#import pdb
#pdb.set_trace()

# This is the code to build up the predictor spreadsheet: try No. 2
# The spreadsheet should have columns: Name, team, last three games stats, home court information

class predictionPre:
    # the general function to read in the data
    def readinData(self,address):
        fi = open(address,"r")
        csvReader = csv.reader(fi)
        counter = 0
        data = []
        for item in csvReader:
            if counter == 0:
                title = item
                counter = counter + 1
            else:
                data.append(item)
        fi.close()
        return title,data
        
    # Generate the spreadsheet
    # given: - the starting date of the season
    #        - the prediction date
    def generateSpreadsheet(self,startDate,endDate):
        # transform the startDate and the endDate
        startD = datetime.datetime.strptime(startDate,"%Y-%m-%d")
        startD = startD.date()
        endD = datetime.datetime.strptime(endDate,"%Y-%m-%d")
        endD = endD.date()
        
        # build the title
        title = ["Date","FDPoints","Player_ID","Name","Game_ID","Team","Opponent","Home_Game","Last5Game","Last5Away","OnIL","ILLast5","ILLast10","ILLast30"]
        aset = set(range(len(self.matchTitle)))
        bset = set([0,25,27,56,59,67,68,74,80,81,89,94,109,114])
        cList = list(aset - bset)
        GameTitle = [self.matchTitle[index] for index in cList]
        GameTitleTemp = GameTitle.copy()
        for j in range(len(GameTitleTemp)):
            GameTitleTemp[j] = GameTitleTemp[j] + "_AVG"
        title = title + GameTitleTemp
        for i in range(3):
            GameTitleTemp = GameTitle.copy()
            for j in range(len(GameTitleTemp)):
                GameTitleTemp[j] = GameTitleTemp[j] + str(i+1)
            title = title + GameTitleTemp
        
        # Only pick the data before the endDate - 1
        dataUsed = []
        playerDict = {}
        playerList = []
        teamList = []
        dateIndex = self.matchTitle.index("GAME_DATE_EST")
        nameIndex = self.matchTitle.index("PLAYER_NAME")
        playerIndex = self.matchTitle.index("PLAYER_ID")
        self.playerLast1 = {}
        self.playerLast2 = {}
        self.playerLast3 = {}
        self.playerGame = {}
        self.playerAVG = {}
        for item in self.matchData:
            dateEntry = datetime.datetime.strptime(item[dateIndex],"%Y-%m-%dT00:00:00")
            dateEntry = dateEntry.date()
            if dateEntry <= endD + datetime.timedelta(-1):
                entry = item.copy()
                entry[dateIndex] = dateEntry
                for iB in cList:
                    if (entry[iB] == '')and(iB != 90):
                        entry[iB] = 0
                try:
                    minPlayed = entry[7].split(":")
                    minPlayed = float(minPlayed[0])+(float(minPlayed[1])/60.0)
                except:
                    minPlayed = float(entry[7])*24
                entry[7] = minPlayed
                dataUsed.append(entry)
                # Append the player's ID into the list of players we could predict
                if not(item[nameIndex] in playerDict.keys()):
                    playerDict[item[nameIndex]] = item[playerIndex]
                    playerList.append(item[playerIndex])
                    self.playerLast1[item[playerIndex]] = [0]*len(GameTitle)
                    self.playerLast2[item[playerIndex]] = [0]*len(GameTitle)
                    self.playerLast3[item[playerIndex]] = [0]*len(GameTitle)
                    self.playerGame[item[playerIndex]] = 0
                    self.playerAVG[item[playerIndex]] = [0]*len(GameTitle)
                if not(item[-1] in teamList):
                    teamList.append(item[-1])
        teamListOppo = teamList.copy()
        for i in range(len(teamListOppo)):
            teamListOppo[i] = teamListOppo[i]+"_Oppo"
        title = title + playerList + teamList + teamListOppo
        # collect the injury data before the endDate - 1
        InjdataUsed = []
        for item in self.injuryData:
            dateStr = item[0].split("/")
            dateEntry = datetime.date(int(dateStr[2]),int(dateStr[0]),int(dateStr[1]))
            if dateEntry <= endD:
                entry = [dateEntry] + item[1:]
                InjdataUsed.append(entry)
        
        # Scan the date
        self.teamInjList = {}
        self.playerInjList = {}
        currentDate = startD
        self.teamLastList = {}
        self.teamLastAway = {} 
        missedInfo = {}
        for item in teamList:
             self.teamLastList[item] = []
             self.teamLastAway[item] = []
             missedInfo[item] = []
             
        self.spreadSheet = [title]
        self.injInd = {}
        self.restInd = {}
        for item in playerList:
            self.injInd[item] = 0
            self.restInd[item] = 0
        while currentDate <= endD + datetime.timedelta(-1):
            matchDate = [i for i in dataUsed if i[dateIndex] == currentDate]
            injDate = [i for i in InjdataUsed if i[0] == currentDate]
            teamRestList = {}
            for item in teamList:
                teamRestList[item] = []
            
            # put player on the injury list
            for iK in self.playerInjList.keys():
                if self.injInd[iK] == 1:
                    self.playerInjList[iK] = currentDate
            for item in injDate:
                if (item[3] in playerDict.keys())or(item[2] in playerDict.keys()):
                    if not("rest (DTD)" in item[4]):
                        if (not(item[1] in self.teamInjList.keys()))and(item[3] != ''):
                            self.teamInjList[item[1]] = [playerDict[item[3]]]
                            self.playerInjList[playerDict[item[3]]] = item[0]
                            self.injInd[playerDict[item[3]]] = 1
                        elif (item[1] in self.teamInjList.keys())and(item[3] != ''):
                            if not(playerDict[item[3]] in self.teamInjList[item[1]]):
                                self.teamInjList[item[1]].append(playerDict[item[3]])
                            self.playerInjList[playerDict[item[3]]] = item[0]
                            self.injInd[playerDict[item[3]]] = 1
                        elif (item[1] in self.teamInjList.keys())and(item[2] != ''):
                            if playerDict[item[2]] in self.teamInjList[item[1]]:
                                self.teamInjList[item[1]].remove(playerDict[item[2]])
                            self.playerInjList[playerDict[item[2]]] = currentDate + datetime.timedelta(-1)
                            self.injInd[playerDict[item[2]]] = 0
                        else:
                            pass
                    else:
                        self.restInd[playerDict[item[3]]] = 1
                        teamRestList[item[1]].append(playerDict[item[3]])                   
                    
            # scan each entry
            playedPlayer = []
            playedTeam = []
            for item in matchDate:
                # 94: PLAYER_NAME, 27: PLAYER_ID, -1: TEAM_ID, 80: VISITOR_TEAM_ID, 25: HOME_TEAM_ID, 56: GAME_ID
                # fdPoints = 1*pts + 1.2*rebounds + 1.5*assists + 2*blocks + 2*steals - 1*turnovers
                fdPointsP = int(item[86]) + 1.2*int(item[91]) + 1.5*(int(item[42])) + 2*(int(item[23])+int(item[39])) - int(item[103])
                nameP = item[94]
                idP = item[27]
                self.playerGame[idP] += 1
                gameP = item[56]
                teamP = item[-1]
                last5GameP = len([i for i in self.teamLastList[teamP] if i >= currentDate + datetime.timedelta(-5) and i < currentDate])
                last5AwayP = len([i for i in self.teamLastAway[teamP] if i >= currentDate + datetime.timedelta(-5) and i < currentDate])
                if item[-1] == item[25]:
                    homeP = 1
                    oppoP = item[80]
                    if not(currentDate in self.teamLastList[teamP]):
                        self.teamLastList[teamP].append(currentDate)
                else:
                    homeP = 0
                    oppoP = item[25]
                    if not(currentDate in self.teamLastList[teamP]):
                        self.teamLastList[teamP].append(currentDate)
                    if not(currentDate in self.teamLastAway[teamP]):
                        self.teamLastAway[teamP].append(currentDate)
                    
                missedInfo[teamP] = [gameP,teamP,oppoP,homeP,last5GameP,last5AwayP,item[90]]
                playedPlayer.append(idP)
                playedTeam.append(teamP)
                gameData = [item[index] for index in cList]
                OnILP = 0
                IL5P = 0
                IL10P = 0
                IL30P = 0
                if idP in self.playerInjList.keys():
                    if (self.injInd[idP] == 1):
                        OnILP = 1
                    elif self.playerInjList[idP] >= currentDate + datetime.timedelta(-5):
                        IL5P = 1
                    elif self.playerInjList[idP] >= currentDate + datetime.timedelta(-10):
                        IL10P = 1
                    elif self.playerInjList[idP] >= currentDate + datetime.timedelta(-30):
                        IL30P = 1
                if self.restInd[idP] == 1:
                    OnILP = 1
                playerIndList = [0]*len(playerList)
                teamIndList = [0]*len(teamList)
                oppoIndList = [0]*len(teamList)
                playerIndList[playerList.index(idP)] = 1
                teamIndList[teamList.index(teamP)] = 1
                oppoIndList[teamList.index(oppoP)] = 1
                entry = [str(currentDate),fdPointsP,idP,nameP,gameP,teamP,oppoP,homeP,last5GameP,last5AwayP,OnILP,IL5P,IL10P,IL30P] + self.playerAVG[idP].copy() +\
                        self.playerLast1[idP].copy() + self.playerLast2[idP].copy() + self.playerLast3[idP].copy() + playerIndList + teamIndList + oppoIndList
                self.spreadSheet.append(entry)
                
            # edit the player past three game data
                self.playerLast3[idP] = self.playerLast2[idP].copy()
                self.playerLast2[idP] = self.playerLast1[idP].copy()
                self.playerLast1[idP] = gameData
                self.playerAVG[idP] = [(float(gameData[i])+float(self.playerAVG[idP][i])*(self.playerGame[idP] - 1))/self.playerGame[idP] for i in range(len(gameData))]
            
            injPl = [i for i in self.injInd.keys() if self.injInd[i] == 1]
            for item in injPl:
                if not(item in playedPlayer):
                    nameL = [i for i in playerDict.keys() if playerDict[i] == item]
                    nameL = nameL[0]
                    teamL = [i for i in self.teamInjList.keys() if item in self.teamInjList[i]]
                    teamL = teamL[0]
                    if (teamL in playedTeam):
                        playerIndList = [0]*len(playerList)
                        playerIndList[playerList.index(item)] = 1
                        teamIndList = [0]*len(teamList)
                        oppoIndList = [0]*len(teamList)
                        teamIndList[teamList.index(teamL)] = 1
                        oppoIndList[teamList.index(missedInfo[teamL][2])] = 1
                        entry = [str(currentDate),0,item,nameL] + missedInfo[teamL][:-1] + [1,0,0,0] + self.playerAVG[item].copy() + self.playerLast1[item].copy() + self.playerLast2[item].copy()\
                                + self.playerLast3[item].copy() + playerIndList + teamIndList + oppoIndList
                        gameData = []
                        for i in cList:
                            if i != 90:
                                gameData.append(0)
                            else:
                                gameData.append(missedInfo[teamL][-1])
                        self.playerLast3[idP] = self.playerLast2[idP].copy()
                        self.playerLast2[idP] = self.playerLast1[idP].copy()
                        self.playerLast1[idP] = gameData
                        self.spreadSheet.append(entry)
            restPl = [j for j in self.restInd.keys() if self.restInd[j] == 1]
            for item in restPl:
                if not(item in playedPlayer):
                    nameL = [i for i in playerDict.keys() if playerDict[i] == item]
                    nameL = nameL[0]
                    teamL = [i for i in teamRestList.keys() if item in teamRestList[i]]
                    teamL = teamL[0]
                    if (teamL in playedTeam):
                        playerIndList = [0]*len(playerList)
                        playerIndList[playerList.index(item)] = 1
                        teamIndList = [0]*len(teamList)
                        oppoIndList = [0]*len(teamList)
                        teamIndList[teamList.index(teamL)] = 1
                        oppoIndList[teamList.index(missedInfo[teamL][2])] = 1
                        entry = [str(currentDate),0,item,nameL] + missedInfo[teamL][:-1] + [1,0,0,0] + self.playerAVG[item].copy() + self.playerLast1[item].copy() + self.playerLast2[item].copy()\
                                + self.playerLast3[item].copy() + playerIndList + teamIndList + oppoIndList
                        gameData = []
                        for i in cList:
                            if i != 90:
                                gameData.append(0)
                            else:
                                gameData.append(missedInfo[teamL][-1])
                        self.playerLast3[idP] = self.playerLast2[idP].copy()
                        self.playerLast2[idP] = self.playerLast1[idP].copy()
                        self.playerLast1[idP] = gameData
                        self.spreadSheet.append(entry)
                self.restInd[item] = 0
            currentDate = currentDate + datetime.timedelta(1)
        
    def Output(self):
        fo = open(self.outAdd,"w",newline = "")
        csvWriter = csv.writer(fo,dialect = "excel")
        csvWriter.writerows(self.spreadSheet)
        fo.close()
                            
    def __init__(self,matchDataAdd,injuryDataAdd,outAdd):
        # read in the match data and the injury data
        self.matchAdd = matchDataAdd
        self.injuryAdd = injuryDataAdd
        self.outAdd = outAdd
        self.injuryTitle,self.injuryData = self.readinData(self.injuryAdd)
        self.matchTitle,self.matchData = self.readinData(self.matchAdd)
        