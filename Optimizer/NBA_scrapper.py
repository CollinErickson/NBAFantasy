# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 23:30:22 2016

@author: hyang89
"""

# NBA Scrapper

# List of Match: http://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate=07%2F05%2F2013
# Summary of a match: http://stats.nba.com/stats/boxscoresummaryv2?GameID=0021500525
# Traditional box score: http://stats.nba.com/stats/boxscoretraditionalv2?EndPeriod=10&EndRange=28800&GameID=0021500525&RangeType=0&Season=2015-16&SeasonType=Regular+Season&StartPeriod=1&StartRange=0
# Advanced box score: http://stats.nba.com/stats/boxscoreadvancedv2?EndPeriod=10&EndRange=28800&GameID=0021500525&RangeType=0&Season=2015-16&SeasonType=Regular+Season&StartPeriod=1&StartRange=0
# Four factors: http://stats.nba.com/stats/boxscorefourfactorsv2?EndPeriod=10&EndRange=28800&GameID=0021500525&RangeType=0&Season=2015-16&SeasonType=Regular+Season&StartPeriod=1&StartRange=0
# Player trackers: http://stats.nba.com/stats/boxscoreplayertrackv2?GameID=0021500525&Season=2015-16&SeasonType=Regular+Season
# Misc data: http://stats.nba.com/stats/boxscoremiscv2?EndPeriod=10&EndRange=34800&GameID=0021500523&RangeType=0&Season=2015-16&SeasonType=Regular+Season&StartPeriod=1&StartRange=0
# Scoring data: http://stats.nba.com/stats/boxscorescoringv2?EndPeriod=10&EndRange=34800&GameID=0021500523&RangeType=0&Season=2015-16&SeasonType=Regular+Season&StartPeriod=1&StartRange=0
# Usage data: http://stats.nba.com/stats/boxscoreusagev2?EndPeriod=10&EndRange=34800&GameID=0021500523&RangeType=0&Season=2015-16&SeasonType=Regular+Season&StartPeriod=1&StartRange=0

import os
import csv
import re
#import pdb
#pdb.set_trace()
import urllib.request
from selenium import webdriver
from urllib.request import FancyURLopener
import json
import datetime
import time
import bs4

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

class MyOpener(FancyURLopener):
    #version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
    version = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'

class NBAScraper:
    # Get the list of game ids
    def GetGameList(self):
        currentDate = self.start
        self.totalGameList = {}
        #browser = webdriver.Chrome("C:\\Documents\\Python_Files\\NBA\\chromedriver.exe")
        browser = webdriver.Chrome("/Users/haoxiangyang/Downloads/chromedriver")

        time.sleep(10)
        while currentDate <= self.end:
            # The previous version of scraping the IDs cannot work as the server
            # cannot be accessed.
        
            #dateAddress = 'http://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate=' \
            #+ str(currentDate.month) + '%2F' + str(currentDate.day) + '%2F' + str(currentDate.year)
            #dFile = self.myopener.open(dateAddress)        
            #dFile = urllib.request.urlopen(dateAddress)
            
            #dString = dFile.read()
            #dString = dString.decode('utf-8')
            
            #djson = json.loads(dString)
            #dgameID = []
            #for item in djson['resultSets'][0]['rowSet']:
            #    dgameID.append(item[2]) 
            #self.totalGameList[currentDate] = dgameID
            #currentDate = currentDate + datetime.timedelta(1)
            
            # Here we use selenium to obtain the list of the games
            if currentDate.month < 10:
                monthTemp = self.digTrans[currentDate.month]
            else:
                monthTemp = currentDate.month
            if currentDate.day < 10:
                dayTemp = self.digTrans[currentDate.day]
            else:
                dayTemp = currentDate.day
            browser.get('http://stats.nba.com/scores/#!/%s/%s/%s' % (monthTemp,dayTemp,currentDate.year))
            time.sleep(10)
            elemList = browser.find_elements_by_xpath("//*[@class='bottom-bar-container']//*[text() = 'Box Score']")
            dgameID = []
            for i in range(0,len(elemList)):
                address = elemList[i].get_attribute("href")
                dgameID.append(address[-11:-1])
            self.totalGameList[currentDate] = dgameID
            currentDate = currentDate + datetime.timedelta(1)
            
        browser.close()
            
     # Given the list of game ids, obtain the players' information
            
    def GetPlayersData(self):
        if self.existed:
            fi = open(self.fileOutput,'r')
            csvReader = csv.reader(fi,dialect = "excel")
            for item in csvReader:
                header = item
                break
            fi.close()
        else:
            header = []
        currentDate = self.start
        self.totalPlayerList = []
        browser = webdriver.Chrome("/Users/haoxiangyang/Downloads/chromedriver")
        while currentDate <= self.end:
            for igame in self.totalGameList[currentDate]:
                try:
                    sumAddress = 'http://stats.nba.com/stats/boxscoresummaryv2?GameID='+ igame
#                    sumFile = self.myopener.open(sumAddress)
#                    sumString = sumFile.read()
#                    sumString = sumString.decode('utf-8')
                    browser.get(sumAddress)
                    time.sleep(1)
                    elem = browser.find_element_by_xpath("//*[pre]")
                    sumString = elem.text
                    sumData = json.loads(sumString)
                    
                    boxAddress = 'http://stats.nba.com/stats/boxscoretraditionalv2?EndPeriod=10&EndRange=100000&GameID='+ igame +'&RangeType=0&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'
#                    boxFile = self.myopener.open(boxAddress)
#                    boxString = boxFile.read()
#                    boxString = boxString.decode('utf-8')
                    browser.get(boxAddress)
                    time.sleep(1)
                    elem = browser.find_element_by_xpath("//*[pre]")
                    boxString = elem.text
                    boxData = json.loads(boxString)
                    
                    aboxAddress = 'http://stats.nba.com/stats/boxscoreadvancedv2?EndPeriod=10&EndRange=100000&GameID='+ igame +'&RangeType=0&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'
#                    aboxFile = self.myopener.open(aboxAddress)
#                    aboxString = aboxFile.read()
#                    aboxString = aboxString.decode('utf-8')
                    browser.get(aboxAddress)
                    time.sleep(1)
                    elem = browser.find_element_by_xpath("//*[pre]")
                    aboxString = elem.text
                    aboxData = json.loads(aboxString)
                    
                    fourFacAddress = 'http://stats.nba.com/stats/boxscorefourfactorsv2?EndPeriod=10&EndRange=28800&GameID='+ igame +'&RangeType=0&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'
#                    fourFacFile = self.myopener.open(fourFacAddress)
#                    fourFacString = fourFacFile.read()
#                    fourFacString = fourFacString.decode('utf-8')
                    browser.get(fourFacAddress)
                    time.sleep(1)
                    elem = browser.find_element_by_xpath("//*[pre]")
                    fourFacString = elem.text
                    fourFacData = json.loads(fourFacString)
                    
                    plTrackAddress = 'http://stats.nba.com/stats/boxscoreplayertrackv2?GameID='+ igame +'&SeasonType=Regular+Season'
#                    plTrackFile = self.myopener.open(plTrackAddress)
#                    plTrackString = plTrackFile.read()
#                    plTrackString = plTrackString.decode('utf-8')
                    browser.get(plTrackAddress)
                    time.sleep(1)
                    elem = browser.find_element_by_xpath("//*[pre]")
                    plTrackString = elem.text
                    plTrackData = json.loads(plTrackString)
                    
                    miscAddress = 'http://stats.nba.com/stats/boxscoremiscv2?EndPeriod=10&EndRange=100000&GameID='+ igame +'&RangeType=0&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'
#                    miscFile = self.myopener.open(miscAddress)
#                    miscString = miscFile.read()
#                    miscString = miscString.decode('utf-8')
                    browser.get(miscAddress)
                    time.sleep(1)
                    elem = browser.find_element_by_xpath("//*[pre]")
                    miscString = elem.text
                    miscData = json.loads(miscString)
                    
                    scoringAddress = 'http://stats.nba.com/stats/boxscorescoringv2?EndPeriod=10&EndRange=100000&GameID='+ igame +'&RangeType=0&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'
#                    scoringFile = self.myopener.open(scoringAddress)
#                    scoringString = scoringFile.read()
#                    scoringString = scoringString.decode('utf-8')
                    browser.get(scoringAddress)
                    time.sleep(1)
                    elem = browser.find_element_by_xpath("//*[pre]")
                    scoringString = elem.text
                    scoringData = json.loads(scoringString)
                    
                    usageAddress = 'http://stats.nba.com/stats/boxscoreusagev2?EndPeriod=10&EndRange=34800&GameID='+ igame +'&RangeType=0&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'
#                    usageFile = self.myopener.open(usageAddress)
#                    usagestring = usageFile.read()
#                    usagestring = usagestring.decode('utf-8')
                    browser.get(usageAddress)
                    time.sleep(1)
                    elem = browser.find_element_by_xpath("//*[pre]")
                    usageString = elem.text
                    usageData = json.loads(usageString)
                    
                    if header == []:
                        headerSet = set(boxData['resultSets'][0]['headers'])
                        headerSet = headerSet.union(aboxData['resultSets'][0]['headers'])
                        headerSet = headerSet.union(fourFacData['resultSets'][0]['headers'])
                        headerSet = headerSet.union(plTrackData['resultSets'][0]['headers'])
                        headerSet = headerSet.union(miscData['resultSets'][0]['headers'])
                        headerSet = headerSet.union(scoringData['resultSets'][0]['headers'])
                        headerSet = headerSet.union(usageData['resultSets'][0]['headers'])
                        headerSet = headerSet.union({'GAME_DATE_EST','GAME_SEQUENCE','GAME_ID','HOME_TEAM_ID','VISITOR_TEAM_ID',\
                        'SEASON','ATTENDANCE','GAME_TIME'})
                        header = list(headerSet)
                        header.append('FDScore')
                        self.totalPlayerList.append(header)
                    
                    for player in range(len(boxData['resultSets'][0]['rowSet'])):
                        playerData = []
                        FDscore = 0
                        for item in header:
                            if item in boxData['resultSets'][0]['headers']:
                                indexx = boxData['resultSets'][0]['headers'].index(item)
                                playerData.append(boxData['resultSets'][0]['rowSet'][player][indexx])
                            else:
                                if item in aboxData['resultSets'][0]['headers']:
                                    indexx = aboxData['resultSets'][0]['headers'].index(item)
                                    playerData.append(aboxData['resultSets'][0]['rowSet'][player][indexx])
                                else:
                                    if item in fourFacData['resultSets'][0]['headers']:
                                        indexx = fourFacData['resultSets'][0]['headers'].index(item)
                                        playerData.append(fourFacData['resultSets'][0]['rowSet'][player][indexx])
                                    else:                                    
                                        if item in plTrackData['resultSets'][0]['headers']:
                                            indexx = plTrackData['resultSets'][0]['headers'].index(item)
                                            playerData.append(plTrackData['resultSets'][0]['rowSet'][player][indexx])
                                        else:
                                            if item in miscData['resultSets'][0]['headers']:
                                                indexx = miscData['resultSets'][0]['headers'].index(item)
                                                playerData.append(miscData['resultSets'][0]['rowSet'][player][indexx])
                                            else:
                                                if item in scoringData['resultSets'][0]['headers']:
                                                    indexx = scoringData['resultSets'][0]['headers'].index(item)
                                                    playerData.append(scoringData['resultSets'][0]['rowSet'][player][indexx])
                                                else:
                                                    if item in usageData['resultSets'][0]['headers']:
                                                        indexx = usageData['resultSets'][0]['headers'].index(item)
                                                        playerData.append(usageData['resultSets'][0]['rowSet'][player][indexx])
                                                    else:
                                                        if item in sumData['resultSets'][0]['headers']:
                                                            indexx = sumData['resultSets'][0]['headers'].index(item)
                                                            playerData.append(sumData['resultSets'][0]['rowSet'][0][indexx])
                                                        else:
                                                            if item in sumData['resultSets'][4]['headers']:
                                                                indexx = sumData['resultSets'][4]['headers'].index(item)
                                                                playerData.append(sumData['resultSets'][4]['rowSet'][0][indexx])
                            if item == "PTS" and playerData[-1] != None:
                                FDscore += float(playerData[-1])
                            elif item == "AST" and playerData[-1] != None:
                                FDscore += float(playerData[-1])*1.5
                            elif item == "BLK" and playerData[-1] != None:
                                FDscore += float(playerData[-1])*3
                            elif item == "STL" and playerData[-1] != None:
                                FDscore += float(playerData[-1])*3
                            elif item == "REB" and playerData[-1] != None:
                                FDscore += float(playerData[-1])*1.2
                            elif item == "TO" and playerData[-1] != None:
                                FDscore += float(playerData[-1])*(-1)
                        playerData.append(FDscore)
                        self.totalPlayerList.append(playerData)
                except:
                    pass
            currentDate = currentDate + datetime.timedelta(1)
        browser.close()
            
    def InjuryScraper(self,startDate,endDate,InjuryOut):
        # Input format: YYYY-MM-DD
        # Team name dictrionary
        teamIDTrans = {"ATL":"1610612737","BOS":"1610612738","BKN":"1610612751","CHA":"1610612766","CHI":"1610612741",\
        "CLE":"1610612739","DET":"1610612765","DAL":"1610612742","DEN":"1610612743","GS":"1610612744","HOU":"1610612745","IND":"1610612754",\
        "LAC":"1610612746","LAL":"1610612747","MEM":"1610612763","MIA":"1610612748","MIL":"1610612749","MIN":"1610612750",\
        "NO":"1610612740","NY":"1610612752","OKC":"1610612760","PHI":"1610612755","PHO":"1610612756","POR":"1610612757","SAC":"1610612758",\
        "SA":"1610612759","TOR":"1610612761","UTA":"1610612762","WAS":"1610612764","ORL":"1610612753"}
        
        teamNameTrans = {"Hawks":"ATL","Celtics":"BOS","Nets":"BKN","Hornets":"CHA","Bulls":"CHI"\
                        ,"Cavaliers":"CLE","Pistons":"DET","Mavericks":"DAL","Nuggets":"DEN","Warriors":"GS"\
                        ,"Rockets":"HOU","Pacers":"IND","Clippers":"LAC","Lakers":"LAL","Grizzlies":"MEM"\
                        ,"Heat":"MIA","Bucks":"MIL","Timberwolves":"MIN","Pelicans":"NO","Knicks":"NY"\
                        ,"Thunder":"OKC","76ers":"PHI","Suns":"PHO","Blazers":"POR","Kings":"SAC"\
                        ,"Spurs":"SA","Raptors":"TOR","Jazz":"UTA","Wizards":"WAS","Magic":"ORL"}
                        
        injuryNameChange = {'Gerald Green (b)': 'Gerald Green', 'Gerald Henderson (b)': 'Gerald Henderson', 'Tony Wroten Jr.': 'Tony Wroten', 'Norris Cole (a)': 'Norris Cole',\
            '(William) Tony Parker': 'Tony Parker', 'Reggie Jackson (b)': 'Reggie Jackson', 'Jonathon Simmons / Jonathan Simmons': 'Jonathon Simmons', \
            "Amare Stoudemire / Amar'e Stoudemire": "Amar'e Stoudemire", 'Louis Williams / Lou Williams': 'Louis Williams', 'James Michael McAdoo / James McAdoo (Michael)': 'James Michael McAdoo',\
            'Louis Amundson / Lou Amundson': 'Louis Amundson', 'Ray McCallum (b)': 'Ray McCallum', 'Wesley Matthews / Wes Matthews Jr.': 'Wesley Matthews', 'Ed Davis (a)': 'Ed Davis', \
            'Nene / Nene Hilario / Maybyner Hilario': 'Nene Hilario', 'Matthew Dellavedova / Matt Dellavedova': 'Matthew Dellavedova', 'Emanuel Ginobili / Manu Ginobili': 'Manu Ginobili',\
            'Metta World Peace / Ron Artest': 'Metta World Peace', 'Walter Tavares / Edy Tavares': 'Walter Tavares', 'Jose Juan Barea / Jose Barea / J.J. Barea': 'Jose Juan Barea',\
            'Matthew Dellavedova (CBC CBS NBA P)  / Matt Dellavedova (R)': 'Matthew Dellavedova', 'Wesley Johnson (CBC CBS P R S) / Wes Johnson (E NBA)': 'Wesley Johnson', 'Mike Dunleavy Jr.': 'Mike Dunleavy',\
            'Wesley Johnson / Wes Johnson': 'Wesley Johnson', 'Maurice Williams / Mo Williams': 'Mo Williams', 'John Wall (a)': 'John Wall', 'Zaur Pachulia / Zaza Pachulia': 'Zaza Pachulia',\
            'Alexis Ajinca / Alex Ajinca': 'Alexis Ajinca', 'Roy Devyn Marble / Roy Marble (Devyn)': 'Roy Devyn Marble', 'R.J. Hunter': 'RJ Hunter'}
        
        # read in the injury file and compile to a csv file
        InjuryFirstPage = "http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate="+startDate\
                    +"&EndDate="+endDate+"&ILChkBx=yes&InjuriesChkBx=yes&Submit=Search"
        InjuryFile = urllib.request.urlopen(InjuryFirstPage)
        InjuryStr = InjuryFile.read()
        InjuryStr = InjuryStr.decode('utf-8')
        InjurySoup = bs4.BeautifulSoup(InjuryStr,'html.parser')
        
        trList = InjurySoup.find_all("tr")
        trLast = trList[-1]
        lastPage = re.findall('>([0-9]+)</a></p></td>',str(trLast))
        lastPage = int(lastPage[0])
        
        totalData = [["Date","Team","Acquired","Relinquished"]]
        
        for i in range(lastPage):
            InjuryPage = "http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate="+startDate+\
                        "&EndDate="+endDate+"&ILChkBx=yes&InjuriesChkBx=yes&Submit=Search&start="+str(i*25)
            InjuryFile = urllib.request.urlopen(InjuryPage)
            InjuryStr = InjuryFile.read()
            InjuryStr = InjuryStr.decode('utf-8')
            InjurySoup = bs4.BeautifulSoup(InjuryStr,'html.parser')
            trList = InjurySoup.find_all("tr")
            trList = trList[1:-1]
            # search each item in 
            for item in trList:
                tdItem = item.findAll("td")
                if not("fine" in tdItem[4].text):
                    dateEntry = tdItem[0].text.strip()
                    teamEntry = teamIDTrans[teamNameTrans[tdItem[1].text.strip()]]
                    backEntry = tdItem[2].text.replace(' • ','')
                    backEntry = backEntry.strip()
                    goneEntry = tdItem[3].text.replace(' • ','')
                    goneEntry = goneEntry.strip()
                    notesEntry = tdItem[4].text.strip()
                    if backEntry in injuryNameChange.keys():
                        backEntry = injuryNameChange[backEntry]
                    if goneEntry in injuryNameChange.keys():
                        goneEntry = injuryNameChange[goneEntry]
                    totalData.append([dateEntry,teamEntry,backEntry,goneEntry,notesEntry])
                            
        fo = open(InjuryOut,"w",newline ="")
        csvWriter = csv.writer(fo)
        csvWriter.writerows(totalData)
        fo.close()        
        
    # Output the data to the spread sheet
    def Output(self):
        title = []
        if self.existed:
            self.fo = open(self.fileOutput,'a',newline = '')
            self.csvWriter = csv.writer(self.fo,dialect = 'excel')
            self.csvWriter.writerow(title)
        else:
            self.fo = open(self.fileOutput,'w',newline = '')
            self.csvWriter = csv.writer(self.fo,dialect = 'excel')
        self.csvWriter.writerows(self.totalPlayerList)
        self.fo.close()   
            
        
    def __init__(self,start,end,fileOutput):
        # date format: YYYY.MM.DD
        startList = start.split(".")
        endList = end.split(".")
        self.fileOutput = fileOutput
        self.start = datetime.date(int(startList[0]),int(startList[1]),int(startList[2]))
        self.end = datetime.date(int(endList[0]),int(endList[1]),int(endList[2]))
        if os.path.exists(self.fileOutput):
            self.existed = True
        else:
            self.existed = False
        self.myopener = MyOpener()
        self.digTrans = {1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09'}
        
class SalaryScraper:
    def SalaryIDScraper(self,salaryIDadd,salaryOutput):
        # scrape the salary information from Rotoguru
        salaryFI = open(salaryIDadd,'r')
        IDstring = salaryFI.read()
        IDList = re.findall('<option value=([0-9]+)>([A-Za-z\- ,.\']+)',IDstring)
        SalaryTot = [['Player Name','Date','Salary']]
        for item in IDList:
            playerID = item[0]
            playerName = item[1].strip().split(',')
            playerFN = playerName[1].strip()
            playerLN = playerName[0].strip()
            playerAdd = 'http://rotoguru1.com/cgi-bin/playrh.cgi?'+ playerID +'x'
            playerFile = self.myopener.open(playerAdd)
            playerStr = playerFile.read()
            playerStr = playerStr.decode('utf-8')
            soup = bs4.BeautifulSoup(playerStr,'html.parser')
            listsalary = soup.find_all('td', bgcolor = 'CCFFFF',align = "right")
            listtimeAll = soup.find_all('td', bgcolor = 'FFCC99',align = "center")
            listtime = []
            for item1 in listtimeAll:
                timeitem = re.findall('([0-9]+\-[0-9]+)',str(item1))
                if not(timeitem == []):
                    listtime.append(timeitem[0])
            for i in range(len(listtime)):
                salaryString = str(listsalary[i].contents)
                salary = re.findall('\$([0-9,]+)',salaryString)
                if not(salary==[]):
                    salary = salary[0].replace(",","")
                    playerInfo = [playerFN+' '+playerLN,listtime[i],salary]
                    SalaryTot.append(playerInfo)
        fo = open(salaryOutput,'w',newline = '')
        csvWriter = csv.writer(fo,dialect = "excel")
        csvWriter.writerows(SalaryTot)
        fo.close()
        
    def SalaryDayScraper(self):
        # use urlrequest to obtain data from RotoGuru
        currentDate = self.start
        
        # from the start to the end
        while currentDate <= self.end:
            # read the day's data (csv format option on)
            try:
                salaryAdd = "http://rotoguru1.com/cgi-bin/hyday.pl?mon=%s&day=%s&year=%s&game=fd" % (currentDate.month,currentDate.day,currentDate.year)
                aRaw = urllib.request.urlopen(salaryAdd)
                aString = aRaw.read()
                aString = aString.decode("ISO-8859-1")
                
                # use regEx to extract information & obtain a csv file
                playerList = re.findall('<!--([0-9]+)--><tr><td>([A-Z]+)</td><td><a href=".+" target="_blank" >(.+)</a>([\^]*)</td><td align=center>([0-9\.]+)</td><td align=right>([0-9\$\,]+)</td><td align=center>([a-z]+)</td><td>([a-z\ \@]+)</td><td align=right>&nbsp;([0-9\-]+)</td><td align=right>([0-9\:A-Z]+)</td><td align=left> &nbsp; (.*)</td></tr>',aString)
                salaryData = []
                title = ["Player ID","Position","First Name","Last Name","Starter","FDPoints","Salary",\
                         "Team","Opponent","Home","Team Score","Opponent Score",]
                for item in playerList:
                    itemL = list(item)
                    nameList = itemL[2].split(',')
                    lastName = nameList[0].strip()
                    firstName = nameList[1].strip()
                    itemL = itemL[:2] + [firstName,lastName] + itemL[3:]
                    if itemL[4] == '^':
                        itemL[4] = 1
                    else:
                        itemL[4] = 0
                    itemL[6] = itemL[6].replace("$","")
                    itemL[6] = itemL[6].replace(",","")
                    if 'v' in itemL[8]:
                        homeInd = 1
                        itemL[8] = itemL[8].replace("v","")
                        itemL[8] = itemL[8].strip()
                    else:
                        homeInd = 0
                        itemL[8] = itemL[8].replace("@","")
                        itemL[8] = itemL[8].strip()
                    itemL = itemL[:9] + [homeInd] + itemL[9:]
                    scoreList = itemL[10].split('-')
                    itemL = itemL[:10] + [scoreList[0],scoreList[1]] + itemL[11:]
                        
                    salaryData.append(itemL)
                    
#                dailySoup = bs4.BeautifulSoup(aString,'html.parser')
#                csvOut = dailySoup.find("pre")
#                csvOut = csvOut.find("pre")
#                csvContent = csvOut.contents
#                csvContentStr = str(csvContent[0])
#                csvContentList = csvContentStr.split('\n')
#                title = csvContentList[0].split(';')
#                title = title[:3] + ["First Name","Last Name"] + title[4:]
#                
#                # split the data 
#                salaryData = []
#                for item in csvContentList[1:-1]:
#                    itemList = item.split(';')
#                    # split the first name and the last name
#                    nameList = itemList[3].split(',')
#                    lastName = nameList[0].strip()
#                    firstName = nameList[1].strip()
#                    itemList = itemList[:3] + [firstName,lastName] + itemList[4:]
#                    
#                    # transform the salary format to a number format
#                    itemList[7] = itemList[7].replace("$","")
#                    itemList[7] = itemList[7].replace(",","")
#                    salaryData.append(itemList)
                
                # output the salary information to the outPath folder
                if currentDate.month < 10:
                    monthTemp = self.digTrans[currentDate.month]
                else:
                    monthTemp = currentDate.month
                if currentDate.day < 10:
                    dayTemp = self.digTrans[currentDate.day]
                else:
                    dayTemp = currentDate.day
                outAdd = self.outPath + "%s%s%s.csv" % (currentDate.year, monthTemp, dayTemp)
                fo = open(outAdd,'w',newline = '')
                csvWriter = csv.writer(fo,dialect = 'excel')
                csvWriter.writerow(title)
                csvWriter.writerows(salaryData)
                fo.close()
            except:
                print(currentDate)
            
            currentDate = currentDate + datetime.timedelta(1)
    
    def __init__(self,start,end,outPath):
        self.outPath = outPath
        startList = start.split(".")
        endList = end.split(".")
        self.start = datetime.date(int(startList[0]),int(startList[1]),int(startList[2]))
        self.end = datetime.date(int(endList[0]),int(endList[1]),int(endList[2]))
        self.digTrans = {1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09'}
        
class projectionScraper:
    def ProjectionDayScraper(self):
        # use urlrequest to obtain data from RotoGuru
        currentDate = self.start
        title = ["Player Name","Predicted Point"]
        self.dayDict = {}
        
        # from the start to the end
        while currentDate <= self.end:
            monthTemp = self.monthStr[currentDate.month]
            wkDayTemp = self.wkDays[currentDate.weekday()]
            if currentDate.day < 10:
                dayTemp = self.digTrans[currentDate.day]
            else:
                dayTemp = currentDate.day
            
            self.browser.get('https://dailyfantasynerd.com/projections/fanduel/nba?d={}%20{}%20{}%20{}'.format(wkDayTemp,monthTemp,dayTemp,currentDate.year))
            time.sleep(10)
            self.dayDict[currentDate] = {}
            
            
            nameList = self.browser.find_elements_by_name("n")
            nameList = nameList[1:]
            elemList = self.browser.find_elements_by_xpath("//*[@class='text-center'][@name='dfn']")
            listlen = len(elemList)
            projData = []
            
            for i in range(listlen):
                self.dayDict[currentDate][nameList[i].text] = float(elemList[i].text)
                projData.append([nameList[i].text,elemList[i].text])
            
            outAdd = self.outPath + dateConvert(currentDate) + ".csv"
            fo = open(outAdd,'w',newline = '')
            csvWriter = csv.writer(fo,dialect = 'excel')
            csvWriter.writerow(title)
            csvWriter.writerows(projData)
            fo.close()
            
            currentDate = currentDate + datetime.timedelta(1)
            
    
    def __init__(self,start,end,outPath):
        self.outPath = outPath
        startList = start.split(".")
        endList = end.split(".")
        self.start = datetime.date(int(startList[0]),int(startList[1]),int(startList[2]))
        self.end = datetime.date(int(endList[0]),int(endList[1]),int(endList[2]))
        self.digTrans = {1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09'}
        self.wkDays = {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}
        self.monthStr = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        
        # work around: input the username and password manually
        self.browser = webdriver.Chrome("/Users/haoxiangyang/Downloads/chromedriver")
        self.browser.get('https://dailyfantasynerd.com/login')