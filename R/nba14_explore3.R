nba <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\2015Season2.csv",stringsAsFactors=F)
sal <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FDSalaryNow_2_8_16.csv",stringsAsFactors=F)
#sal <- read.table("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FDSalaryNow_2_8_16.csv.xlsx",
#                  stringsAsFactors=F,header=T)
#sal <- readTable("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FDSalaryNow_2_8_16.csv.xlsx",
#                  header=T)

library(plyr)
nba.IDs <- ddply(nba,.(PLAYER_ID),function(x){x[1,]})

# Need map between FD player ids and NBA
FD.nba.conversion <- data.frame(FD.Id=numeric(0),FD.Paste.Name=numeric(0),
                                FD.First.Name=numeric(0),FD.Last.Name=numeric(0),
                                FD.Team=numeric(0),nba.ID=numeric(0),nba.PLAYER_NAME=numeric(0),
                                nba.TEAM_ABBREVIATION=numeric(0))

# Some won't match up, need to figure out a conversion by hand
no.conversion <- c()

for(i in 1:(dim(sal)[1])) {
  prow <- sal[i,]
  #print(prow)
  #print(i)
  pname <- paste(prow$First,prow$Last)
  nbaind <- which(pname == nba$PLAYER_NAME)[1]
  if (is.na(nbaind)) {
    conversion.FD.names.index <- which(pname==conversion.FD.names)
    if (length(conversion.FD.names.index)==0) {# No easy or hard conversion
      print(paste('Cant convert',pname,'error 57823'))
      #no.conversion <- c(no.conversion,pname)
    } else {
      conversion.nba.name <- conversion.nba.names[conversion.FD.names.index]
      nbaind <- which(conversion.nba.name == nba$PLAYER_NAME)[1]
      if(is.na(nbaind))
        stop(paste('Double name fail error 2623482'))
      }
  }
  if (!is.na(nbaind)) {
    FD.nba.conversion <- rbind(FD.nba.conversion,
      data.frame(FD.Id=prow$Id,FD.Paste.Name=pname,FD.First.Name=prow$First,FD.Last.Name=prow$Last,FD.Team=prow$Team,
                 nba.PLAYER_ID=nba$PLAYER_ID[nbaind],nba.PLAYER_NAME=nba$PLAYER_NAME[nbaind],nba.TEAM_ABBREVIATION=nba$TEAM_ABBREVIATION[nbaind]))
  } else {
      no.conversion <- c(no.conversion,pname)  
  }
}


# Conversion bs
conversion.all.names <- c('Bradley Beal', 'Brad Beal',
'Lou Williams', 'Louis Williams',
'JJ Redick', 'J.J. Redick',
 'Bryce Dejean-Jones', 'Bryce Jones',
'PJ Tucker', 'P.J. Tucker',
'CJ Watson', 'C.J. Watson',
'Luc Mbah a Moute', 'Luc Richard Mbah a Moute',
'KJ McDaniels', 'K.J. McDaniels',
'Lou Amundson', 'Louis Amundson',
'PJ Hairston', 'P.J. Hairston',
'CJ McCollum', 'C.J. McCollum',
'Ish Smith', 'Ishmael Smith',
'Phil Pressey', 'Phil (Flip) Pressey',
'JaKarr Sampson', 'Jakarr Sampson',
'Patty Mills', 'Patrick Mills',
'Nene', 'Nene Hilario')
evens <- (1:(length(conversion.all.names)/2))*2
odds <- evens-1
conversion.FD.names <- conversion.all.names[evens]
conversion.nba.names <- conversion.all.names[odds]
# Check with grep to find player row
nba$PLAYER_NAME[grep("Michael",nba$PLAYER_NAME)]

# Write out conversion file

# Create linear model that predicts based on player, nothing else yet
#mod3 <- lm(FanDuelPts ~ factor(PLAYER_NAME) + factor(IS_HOME) + factor(OPP_TEAM_ID),data = nba)
mod1 <- lm(FanDuelPts ~ factor(PLAYER_ID),data = nba)
# Predict for single row to test (Cousins)
predict(mod1,newdata = data.frame(PLAYER_ID=202326))
# Get coefficient for specific player
mod3$coefficients['factor(PLAYER_ID)202326'] 

# Create dictionary
FD.Id.to.nba.ID <- FD.nba.conversion$nba.PLAYER_ID
names(FD.Id.to.nba.ID) <- FD.nba.conversion$FD.Id
# Add nba PLAYER_ID to salary
sal$PLAYER_ID <- FD.Id.to.nba.ID[as.character(sal$Id)]
head(sal)



# Add column for prediction from mod1
sal$mod1 <- predict(mod1,newdata = sal)

# Read in results
res <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FDResults_2_8_16.csv",stringsAsFactors=F)

plot(res$FDPt,sal$mod1)
plot(res$FDPt,sal$FPPG)
# My linear model was just predicting the average, will need to add more to the model to get useful
plot(sal$mod1,sal$FPPG)
