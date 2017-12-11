# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 09:42:40 2016

@author: hyang89
"""

# NBA Prediction Spreadsheet Builder

import os
import csv
#import pdb
#pdb.set_trace()
import datetime
import time

class spreadsheetBuilder:
    def dateTransformer(self,strInput):
        gameDate = strInput.split("T")[0]
        gameDateList = gameDate.split("-")
        return gameDateList
        
    def distanceCal(self,fileIn):
        fi = open(fileIn,"r")
        csvReader = csv.reader(fi,dialect = "excel")
        counter = 0
        distList = []
        ori = []
        for item in csvReader:
            if counter == 0:
                dest = item[1:]
            else:
                distList.append(item[1:])
                ori.append(item[0])
        dist = {}
        for item in range(len(ori)):
            dist[ori[item]] = {}
            for item1 in range(len(dest)):
                dist[ori[item]][dest[item1]] = distList[item][item1]
        
    def buildTeam(self):
        self.fullteamData = {}
        for item in self.teamGame.keys():
            self.fullteamData[item] = {"Name":self.teamName[item],"Game_Info":[]}
            sortedKeys = sorted(self.teamGame[item].keys())
            t = 0
            for game in sortedKeys:
                t += 1
                gameEntries = self.teamGame[item][game]
                opponentEntries = self.teamGame[self.rawData[gameEntries[0]][self.title.index("VISITOR_TEAM_ID")]][game]
                gameInfo = {"Game_Id":game}
                
                # Is the team home team?
                if self.rawData[gameEntries[0]][self.title.index("HOME_TEAM_ID")] == item:
                    gameInfo["Home_Team"] = 1
                else:
                    gameInfo["Home_Team"] = 0
                gameInfo["Court"] = self.teamName[self.rawData[gameEntries[0]][self.title.index("HOME_TEAM_ID")]]
                    
                # What is the date?
                gameInfo["Date"] = self.rawData[gameEntries[0]][self.title.index("GAME_DATE_EST")][:10]
                gameInfo["Round"] = t
                
                # Game statistics:
                gameInfo["FGM"] = 0
                gameInfo["FGA"] = 0
                gameInfo["FG3M"] = 0
                gameInfo["FG3A"] = 0
                gameInfo["FTM"] = 0
                gameInfo["FTA"] = 0
                gameInfo["OREB"] = 0
                gameInfo["DREB"] = 0
                gameInfo["AST"] = 0
                gameInfo["TO"] = 0
                gameInfo["BLKA"] = 0
                gameInfo["PFD"] = 0
                gameInfo["PTS_2ND_CHANCE"] = 0
                gameInfo["PTS_FB"] = 0
                gameInfo["PTS_PAINT"] = 0
                gameInfo["PACE"] = 0
                gameInfo["MIN"] = 0
                for player in opponentEntries:
                    if self.rawData[player][self.title.index("COMMENT")] == '':
                        for attr in self.attributeList1:
                            gameInfo[attr] += float(self.rawData[player][self.title.index(attr)])
                        if ":" in self.rawData[player][self.title.index("MIN")]:
                            minList = self.rawData[player][self.title.index("MIN")].split(":")
                            minutes = int(minList[0]) + int(minList[1])/60
                        else:
                            minutes = float(self.rawData[player][self.title.index("MIN")])*24
                        gameInfo["PACE"] += float(self.rawData[player][self.title.index("PACE")])/48*minutes
                        gameInfo["MIN"] += minutes
                self.fullteamData[item]["Game_Info"].append(gameInfo)
                
    def hardPlayer(self):
        self.playerGame = {}
        for item in self.rawData:
            if not(item[self.title.index("PLAYER_ID")] in self.playerGame.keys()):
                self.playerGame[item[self.title.index("PLAYER_ID")]] = {}
                self.playerGame[item[self.title.index("PLAYER_ID")]]["Game_Id"] = [item[self.title.index("GAME_ID")]]
                if (item[self.title.index("COMMENT")] == ''):
                    self.playerGame[item[self.title.index("PLAYER_ID")]]["Injury"] = [0]
                    for attr in self.attributeList:
                        self.playerGame[item[self.title.index("PLAYER_ID")]][attr] = [float(item[self.title.index(attr)])]
                else:
                    if ("DNP" in item[self.title.index("COMMENT")]):
                        self.playerGame[item[self.title.index("PLAYER_ID")]]["Injury"] = [0]
                    else:
                        self.playerGame[item[self.title.index("PLAYER_ID")]]["Injury"] = [1]
                    for attr in self.attributeList:
                        self.playerGame[item[self.title.index("PLAYER_ID")]][attr] = [0]
            else:
                self.playerGame[item[self.title.index("PLAYER_ID")]]["Game_Id"].append(item[self.title.index("GAME_ID")])
                if (item[self.title.index("COMMENT")] == ''):
                    self.playerGame[item[self.title.index("PLAYER_ID")]]["Injury"].append(0)
                    for attr in self.attributeList:
                        self.playerGame[item[self.title.index("PLAYER_ID")]][attr].append(float(item[self.title.index(attr)]))
                else:
                    if ("DNP" in item[self.title.index("COMMENT")]):
                        self.playerGame[item[self.title.index("PLAYER_ID")]]["Injury"].append(0)
                    else:
                        self.playerGame[item[self.title.index("PLAYER_ID")]]["Injury"].append(1)
                    for attr in self.attributeList:
                        self.playerGame[item[self.title.index("PLAYER_ID")]][attr].append(0)                
#        for item in self.playerGame.keys():
#            self.playerGame[item] = sorted(self.playerGame[item])
                
        for item in self.rawData:
            self.playerInfo = {}
            self.playerInfo["ID"] = item[self.title.index("PLAYER_ID")]
            if item[self.title.index("COMMENT")] == "":
                self.playerInfo["FDPoints"] = float(item[self.title.index("PTS")]) + 1.5*float(item[self.title.index("AST")]) + \
                2*float(item[self.title.index("BLK")]) + 1.2*float(item[self.title.index("REB")]) +\
                2*float(item[self.title.index("STL")]) - float(item[self.title.index("TO")])
            else:
                self.playerInfo["FDPoints"] = 0
            self.playerInfo["Team"] = item[self.title.index("TEAM_ID")]
            if item[self.title.index("TEAM_ID")] == item[self.title.index("HOME_TEAM_ID")]:
                self.playerInfo["Opponent"] = item[self.title.index("VISITOR_TEAM_ID")]
                self.playerInfo["Home"] = 1
            else:
                self.playerInfo["Opponent"] = item[self.title.index("HOME_TEAM_ID")]
                self.playerInfo["Home"] = 0
            gameNo = item[self.title.index("GAME_ID")]
            self.playerInfo["Game_Id"] = gameNo
            self.playerInfo["playerRound"] = self.playerGame[self.playerInfo["ID"]]["Game_Id"].index(gameNo)
            sortedKeys = sorted(self.teamGame[self.playerInfo["Team"]].keys())
            self.playerInfo["teamRound"] = sortedKeys.index(gameNo)
            
            # Last 7 days data
            gameDateList = self.dateTransformer(item[self.title.index("GAME_DATE_EST")])
            currentDate = datetime.date(int(gameDateList[0]),int(gameDateList[1]),int(gameDateList[2]))
            self.playerInfo["last3Game"] = 0
            self.playerInfo["last3Away"] = 0
            self.playerInfo["last3Injury"] = 0
            for attr in self.attributeList:
                self.playerInfo["last3_"+attr] = 0
            for game in self.fullteamData[self.playerInfo["Team"]]['Game_Info']:
                tempDateList = self.dateTransformer(game["Date"])
                tempDate = datetime.date(int(tempDateList[0]),int(tempDateList[1]),int(tempDateList[2]))
                if (game["Game_Id"] in self.playerGame[self.playerInfo["ID"]]["Game_Id"])and(tempDate >= currentDate - datetime.timedelta(5))and(tempDate < currentDate):
                    self.playerInfo["last3Game"] += 1
                    self.playerInfo["last3Away"] += 1-game["Home_Team"]
                    for attr in self.attributeList:
                        self.playerInfo["last3_"+attr] += self.playerGame[self.playerInfo["ID"]][attr][self.playerGame[self.playerInfo["ID"]]["Game_Id"].index(game["Game_Id"])]
                    if game["Game_Id"] in self.playerGame[self.playerInfo["ID"]]:
                        self.playerInfo["last3Injury"] += self.playerGame[self.playerInfo["ID"]]["Injury"][self.playerGame[self.playerInfo["ID"]]["Game_Id"].index(game["Game_Id"])]
                    else:
                        self.playerInfo["last3Injury"] += 1
            self.playerInfo["oppo_last3Game"] = 0
            for attr in self.attributeList1:
                self.playerInfo["oppo_last3_"+attr] = 0
            for game in self.fullteamData[self.playerInfo["Opponent"]]['Game_Info']:
                tempDateList = self.dateTransformer(game["Date"])
                tempDate = datetime.date(int(tempDateList[0]),int(tempDateList[1]),int(tempDateList[2]))
                if (tempDate >= currentDate - datetime.timedelta(5))and(tempDate < currentDate):
                    self.playerInfo["oppo_last3Game"] += 1
                    for attr in self.attributeList1:
                        self.playerInfo["oppo_last3_"+attr] += game[attr]
            if self.playerInfo["last3Game"] > 0:
                for attr in self.attributeList:
                    self.playerInfo["last3_"+attr] = self.playerInfo["last3_"+attr]/self.playerInfo["last3Game"]
            if self.playerInfo["oppo_last3Game"] > 0:
                for attr in self.attributeList1:
                    self.playerInfo["oppo_last3_"+attr] = self.playerInfo["oppo_last3_"+attr]/self.playerInfo["oppo_last3Game"]
            
            self.totalData.append(self.playerInfo)
                    
    def loadData(self):
        fi = open(self.fileIn,"r")
        csvReader = csv.reader(fi,dialect = "excel")
        counter = 0
        self.rawData = []
        self.teamGame = {}
        self.teamName = {}
        for item in csvReader:
            if counter == 0:
                self.title = item
                counter += 1
            else:
                if item != []:
                    if (item[self.title.index("GAME_ID")] != ''):
                        # rawData contains all entries from the season data
                        # build the profile of each team
                        teamID = item[self.title.index("TEAM_ID")]
                        if item[self.title.index("GAME_ID")][:2] != "00":
                            item[self.title.index("GAME_ID")] = "00"+item[self.title.index("GAME_ID")]
                        if teamID in self.teamGame.keys():
                            # append the game info to the existing team
                            if item[self.title.index("GAME_ID")] in self.teamGame[teamID].keys():
                                self.teamGame[teamID][item[self.title.index("GAME_ID")]].append(counter-1)
                            else:
                                self.teamGame[teamID][item[self.title.index("GAME_ID")]] = [counter-1]
                        else:
                            # create the team
                            self.teamGame[teamID] = {}
                            self.teamGame[teamID][item[self.title.index("GAME_ID")]] = [counter-1]
                            self.teamName[teamID] = item[self.title.index("TEAM_CITY")]
                        self.rawData.append(item)
                        counter += 1
        fi.close()
    
    def predGenerator(self,fileIn,filenameID,date,fileOut):
        fiId = open(filenameID,"r")
        csvReader1 = csv.reader(fiId,dialect = "excel")
        nameID = {}
        for item in csvReader1:
            nameID[item[0]] = item[1]
        fiId.close()
        fi = open(fileIn,"r");
        csvReader = csv.reader(fi,dialect = "excel")
        counter = 0
        self.fdData = [self.playerTitle]
        for item in csvReader:
            if counter == 0:
                counter += 1
            else:
                if item[10] != 'O':
                    name = item[2]+" "+item[3]
                    if name in self.changeName.keys():
                        name = self.changeName[name]
                    playerID = nameID[name]
                    team = self.teamNameTrans[item[8]]
                    opponent = self.teamNameTrans[item[9]]
                    if (item[8] in item[7].split("@")[1]):
                        home = 1
                    else:
                        home = 0
                    playerRound = item[5]
                    teamRound = 0
                    for item1 in self.fullteamData[team]["Game_Info"]:
                        if item1["Date"] < date:
                            teamRound += 1
                    
                    gameDateList = date.split("-")
                    currentDate = datetime.date(int(gameDateList[0]),int(gameDateList[1]),int(gameDateList[2]))
                    playerInfo = {}                    
                    playerInfo["last3Game"] = 0
                    playerInfo["last3Away"] = 0
                    playerInfo["last3Injury"] = 0
                    for attr in self.attributeList:
                        playerInfo["last3_"+attr] = 0
                    for game in self.fullteamData[team]['Game_Info']:
                        tempDateList = self.dateTransformer(game["Date"])
                        tempDate = datetime.date(int(tempDateList[0]),int(tempDateList[1]),int(tempDateList[2]))
                        if (game["Game_Id"] in self.playerGame[playerID]["Game_Id"])and(tempDate >= currentDate - datetime.timedelta(5))and(tempDate < currentDate):
                            playerInfo["last3Game"] += 1
                            playerInfo["last3Away"] += 1-game["Home_Team"]
                            for attr in self.attributeList:
                                playerInfo["last3_"+attr] += self.playerGame[playerID][attr][self.playerGame[playerID]["Game_Id"].index(game["Game_Id"])]
                            if game["Game_Id"] in self.playerGame[playerID]:
                                playerInfo["last3Injury"] += self.playerGame[playerID]["Injury"][self.playerGame[playerID]["Game_Id"].index(game["Game_Id"])]
                            else:
                                playerInfo["last3Injury"] += 1
                    playerInfo["oppo_last3Game"] = 0
                    for attr in self.attributeList1:
                        playerInfo["oppo_last3_"+attr] = 0
                    for game in self.fullteamData[opponent]['Game_Info']:
                        tempDateList = self.dateTransformer(game["Date"])
                        tempDate = datetime.date(int(tempDateList[0]),int(tempDateList[1]),int(tempDateList[2]))
                        if (tempDate >= currentDate - datetime.timedelta(5))and(tempDate < currentDate):
                            playerInfo["oppo_last3Game"] += 1
                            for attr in self.attributeList1:
                                playerInfo["oppo_last3_"+attr] += game[attr]
                    if playerInfo["last3Game"] > 0:
                        for attr in self.attributeList:
                            playerInfo["last3_"+attr] = playerInfo["last3_"+attr]/playerInfo["last3Game"]
                    if playerInfo["oppo_last3Game"] > 0:
                        for attr in self.attributeList1:
                            playerInfo["oppo_last3_"+attr] = playerInfo["oppo_last3_"+attr]/playerInfo["oppo_last3Game"]
                    outputList = ['',playerID,team,opponent,home,playerRound,teamRound,playerInfo["last3Game"],playerInfo["last3Away"],playerInfo["last3Injury"]]
                    for attr in self.attributeList:
                        outputList.append(playerInfo["last3_"+attr])
                    outputList.append(playerInfo["oppo_last3Game"])
                    for attr in self.attributeList1:
                        outputList.append(playerInfo["oppo_last3_"+attr])
                    outputList.append(item[1])
                    outputList.append(item[6])
                    self.fdData.append(outputList)
        fo = open(fileOut,"w",newline = "")
        csvWriter = csv.writer(fo,dialect = "excel")
        csvWriter.writerows(self.fdData)
        fo.close()
    
    def Output(self):
        fo = open(self.fileOut,"w",newline = "")
        csvWriter = csv.writer(fo,dialect = "excel")
        csvWriter.writerow(self.playerTitle)
        for item in self.totalData:
            outList = []
            for i in self.playerTitle:
                outList.append(item[i])
            csvWriter.writerow(outList)
        fo.close()
                
    def __init__(self,fileIn,fileOut):
        self.fileIn = fileIn
        self.fileOut = fileOut
        self.attributeList = ["FGM","FGA","FG3M","FG3A","FTM","FTA","OREB","DREB","AST","TO","BLK","STL"]
        self.attributeList1 = ["FGM","FGA","FG3M","FG3A","FTM","FTA","OREB","DREB","AST","TO","BLKA","PFD","PTS_2ND_CHANCE","PTS_FB","PTS_PAINT"]
        self.totalData = []
        self.playerTitle = ["FDPoints","ID","Team","Opponent","Home","playerRound","teamRound","last3Game","last3Away","last3Injury"]
        for attr in self.attributeList:
            self.playerTitle.append("last3_"+attr)
        self.playerTitle.append("oppo_last3Game")
        for attr in self.attributeList1:
            self.playerTitle.append("oppo_last3_"+attr)
        self.playerTitle.append("Position")
        self.playerTitle.append("Salary")
        self.changeName = {'Brad Beal':'Bradley Beal','Louis Williams':'Lou Williams','J.J. Redick':'JJ Redick',\
        'Bryce Jones':'Bryce Dejean-Jones','P.J. Tucker':'PJ Tucker','C.J. Watson':'CJ Watson','Luc Richard Mbah a Moute':'Luc Mbah a Moute',\
        'K.J. McDaniels':'KJ McDaniels','Louis Amundson':'Lou Amundson','P.J. Hairston':'PJ Hairston','C.J. McCollum':'CJ McCollum',\
        'Ishmael Smith':'Ish Smith','Phil (Flip) Pressey':'Phil Pressey','Jakarr Sampson':'JaKarr Sampson','Patrick Mills':'Patty Mills',\
        'Nene Hilario':'Nene'}
        self.teamNameTrans = {"ATL":"1610612737","BOS":"1610612738","BKN":"1610612751","CHA":"1610612766","CHI":"1610612741",\
        "CLE":"1610612739","DET":"1610612765","DAL":"1610612742","DEN":"1610612743","GS":"1610612744","HOU":"1610612745","IND":"1610612754",\
        "LAC":"1610612746","LAL":"1610612747","MEM":"1610612763","MIA":"1610612748","MIL":"1610612749","MIN":"1610612750",\
        "NO":"1610612740","NY":"1610612752","OKC":"1610612760","PHI":"1610612755","PHO":"1610612756","POR":"1610612757","SAC":"1610612758",\
        "SA":"1610612759","TOR":"1610612761","UTA":"1610612762","WAS":"1610612764","ORL":"1610612753"}
        self.injuryNamechange = {'Alexis Ajinca / Alex Ajinca': 'Alexis Ajinca', 'Patrick Mills (NBA S) / Patty Mills (CBC CBS E F P R)': 'Patty Mills',\
                                'R.J. Hunter': 'RJ Hunter', 'Nene / Nene Hilario / Maybyner Hilario': 'Nene Hilario', 'Louis Amundson / Lou Amundson': 'Louis Amundson',\
                                'Luc Richard Mbah a Moute / Luc Mbah a Moute': 'Luc Richard Mbah a Moute', 'Dennis Schroder (CBC E NBA P) / Dennis Schroeder (R)': 'Dennis Schroder',\
                                'Reggie Jackson (b)': 'Reggie Jackson', 'Otto Porter Jr.': 'Otto Porter', 'Tony Wroten Jr.': 'Tony Wroten', \
                                'James Michael McAdoo / James McAdoo (Michael)': 'James Michael McAdoo', 'Norris Cole (a)': 'Norris Cole', 'Mike Conley Jr.': 'Mike Conley', \
                                'Jose Juan Barea / Jose Barea / J.J. Barea': 'Jose Juan Barea', 'Matthew Dellavedova / Matt Dellavedova': 'Matthew Dellavedova', \
                                'Wesley Johnson / Wes Johnson': 'Wesley Johnson', 'Emanuel Ginobili / Manu Ginobili': 'Manu Ginobili', 'Wesley Matthews / Wes Matthews Jr.': 'Wesley Matthews',\
                                'Maurice Williams / Mo Williams': 'Mo Williams', 'Ishmael Smith / Ish Smith': 'Ish Smith', 'Zaur Pachulia / Zaza Pachulia': 'Zaza Pachulia', \
                                '(William) Tony Parker': 'Tony Parker', "Amare Stoudemire / Amar'e Stoudemire": "Amar'e Stoudemire", 'Mike Dunleavy Jr.': 'Mike Dunleavy'}