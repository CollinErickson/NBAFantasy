nba <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\2015Season2.csv",stringsAsFactors=F)
View(nba)

require(plyr)

# Split into list by player
players <- dlply(nba,'PLAYER_ID')

# Select those who played enough
played.enoughTF <- sapply(players,function(x){(dim(x)[1]>50 & mean(x$FanDu)>30)})
players.enough <- players[played.enoughTF] # list of 42


#rp <- ps[[sample(1:492,1)]]
#plot(rp$FanDu)

# plot single player, usually don't see big trend
plot(players.enough[[sample(1:length(players.enough),1)]]$FanDu,type='l')

# plot all players, looks awful
plot(NULL,NULL,xlim=c(0,83),ylim=c(5,85))
sapply(players.enough,function(x){points(x$FanDu,type='l',col=sample(1:20,1))})

# Add columns for if player is home and for opponent team id
nba$IS_HOME <- (nba$TEAM_ID == nba$HOME_TEAM_ID)
nba$OPP_TEAM_ID <- ifelse(nba$IS_HOME,nba$VISITOR_TEAM_ID,nba$HOME_TEAM_ID)
table(nba$OPP_TEAM_ID==nba$TEAM_ID)

# See points against each team
# Looks wrong, GSW high, MIN and PHI low. 
# Maybe playoff games add more? 20% more games, makes sense
ddply(nba,'OPP_TEAM_ID',function(x)sum(x$FanDu)/82)
ddply(nba,'OPP_TEAM_ID',function(x)sum(x$FanDu)/length(unique(x$GAME_ID)))

# Get map from TEAM_ID and TEAM_ABBREV
ddply(nba,'OPP_TEAM_ID',function(x)x$TEAM_ABB[1])
cbind(ddply(nba,'OPP_TEAM_ID',function(x)x$TEAM_ABB[1]), ddply(nba,'OPP_TEAM_ID',function(x)sum(x$FanDu)/length(unique(x$GAME_ID))),ddply(nba,'TEAM_ID',function(x)sum(x$FanDu)/length(unique(x$GAME_ID))))


# Try to do a LM
# First one exactly replicates the FDP formula
mod1 <- lm(FanDuelPts ~ PTS + REB + AST + STL + BLK + TO,data = nba)
mod1


mod2 <- lm(FanDuelPts ~ factor(PLAYER_NAME),data = nba)
mean(nba$FanDu[nba$PLAYER_NAME=='Zoran Dragic'])
mean(nba$FanDu[nba$PLAYER_NAME=='Zach Randolph'])


mod3 <- lm(FanDuelPts ~ factor(PLAYER_NAME) + factor(IS_HOME) + factor(OPP_TEAM_ID),data = nba)


# Want to check covariance between players
teamply <- dlply(nba,'TEAM_CITY',identity)
t1 <- teamply[[1]]
# Want columns for players, rows for games, entries are FDP
player.names <- unique(t1$PLAYER_NAME)
game.ids <- unique(t1$GAME_ID)
t1.FDP <- matrix(NA,length(game.ids),length(player.names),dimnames = list(game.ids,player.names))
for(i in 1:length(t1$GAME_ID)) {
  x <- t1[i,]
  t1.FDP[as.character(x$GAME_ID),x$PLAYER_NAME] <- x$FanDuelP
}
View(t1.FDP)
# Find correlations, leave out pairwise NAs
cor(t1.FDP,use='pairwise.complete.obs')
summary(as.numeric(cor(t1.FDP,use='pairwise.complete.obs')))
hist(as.numeric(cor(t1.FDP,use='pairwise.complete.obs')))