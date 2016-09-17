#choose.files()
#nba14 <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\2014Season.csv",stringsAsFactors=F)
#nba14 <- nba14[!is.na(nba14$PTS),]
#nba14$SEC <- sapply((nba14$MIN),function(xxx)sum(as.numeric(strsplit(xxx,':')[[1]])*c(60,1)))
#nba14$FanDuelPts <- nba14$PTS + 1.2*nba14$REB + 1.5*nba14$AST + 2*nba14$BLK + 2*nba14$STL - 1*nba14$TO

#nba14o <- nba14[,order(names(nba14))]
# write.csv(nba14o,"C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\2014Season2.csv")

nba14 <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\2014Season.csv",stringsAsFactors=F)


hist(nba14$REB)
hist(nba14$PTS)
plot(nba14$PTS+runif(31437,-.5,.5),nba14$REB+runif(31437,-.5,.5),pch=19,cex=.1)

nba14$REBZ <- (nba14$REB-mean(nba14$REB))/sd(nba14$REB)
nba14$PTSZ <- (nba14$PTS-mean(nba14$PTS))/sd(nba14$PTS)
nba14$ASTZ <- (nba14$AST-mean(nba14$AST))/sd(nba14$AST)
km5 <- kmeans(x = nba14[,c('REB','PTS','AST')],5,10,10)
kmz5 <- kmeans(x = nba14[,c('REBZ','PTSZ','ASTZ')],5,10,10)

plot(nba14$PTS+runif(length(nba14$PTS),-.5,.5),nba14$REB+runif(length(nba14$REB),-.5,.5),pch=19,cex=.1,col=km5$cluster)
plot(nba14$AST+runif(length(nba14$AST),-.5,.5),nba14$REB+runif(length(nba14$REB),-.5,.5),pch=19,cex=.1,col=km5$cluster)
plot(nba14$PTS+runif(length(nba14$PTS),-.5,.5),nba14$AST+runif(length(nba14$AST),-.5,.5),pch=19,cex=.1,col=km5$cluster)

plot(nba14$PTSZ+runif(length(nba14$PTS),-.05,.05),nba14$REBZ+runif(length(nba14$REB),-.15,.15),pch=19,cex=.1,col=kmz5$cluster)
plot(nba14$ASTZ+runif(length(nba14$AST),-.25,.25),nba14$REBZ+runif(length(nba14$REB),-.15,.15),pch=19,cex=.1,col=kmz5$cluster)
plot(nba14$PTSZ+runif(length(nba14$PTS),-.05,.05),nba14$ASTZ+runif(length(nba14$AST),-.25,.25),pch=19,cex=.1,col=kmz5$cluster)

# Add SEC column which puts seconds played in game instead of minutes as string
#sec.from.min.char <- function(xxx)sum(as.numeric(strsplit(xxx,':')[[1]])*c(60,1))
#nba14$SEC <- nba14$MIN
#nba14$SEC <- sapply((nba14$MIN),sec.from.min.char)
nba14$SEC <- sapply((nba14$MIN),
                    function(xxx) {
                      strspl <- as.numeric(strsplit(xxx,':')[[1]])
                      if (length(strspl==2)) {
                        return(sum(strspl*c(60,1)))
                      } else if {
                        (length(strspl==3)) {
                          return(sum(strspl*c(60,1,0)))
                        }
                      } else return(stop('messed up error 352329393'))
                    }
  )
#nba14$SEC <- as.numeric(nba14$SEC)
summary(nba14$SEC)
head(cbind(nba14$MIN,nba14$SEC))


# Add column for Fanduel points
nba14$FanDuelPts <- nba14$PTS + 1.2*nba14$REB + 1.5*nba14$AST + 2*nba14$BLK + 2*nba14$STL - 1*nba14$TO
hist(nba14$FanDuelPts,freq=F)
curve(dlnorm(x,30,100),add=T,col='red')
curve(dgamma(x,1,.05),add=T,col='red')
stripchart(nba14$FanDuelPts ~ nba14$TEAM_ABBREVIATION)
stripchart(nba14$FanDuelPts ~ nba14$START_POSITION)

# Select games where ten minutes + played
over10 <- nba14[nba14$SEC>600,]
hist(over10$PTS)

#Get points by player
library(plyr)
FDP <- ddply(nba14,.(PLAYER_NAME),function(x) data.frame(sum=sum(x$FanDuelPts),mean=mean(x$FanDuelPts)))
hist(FDP$V1)
FDP.sort <- FDP[order(FDP$V1,decreasing = T),]
head(FDP.sort)

FDP10 <- FDP[FDP$mean>10,]
head(FDP10)

# See correlation between first n-1 games and last game
FDP_2 <- ddply(nba14,.(PLAYER_NAME),
             function(x) {
               LG <- which.max(x$GAME_ID)
               data.frame(sum=sum(x$FanDuelPts),mean=mean(x$FanDuelPts),
                          meantolast=mean(x$FanDuelPts[-LG]),last=x$FanDuelPts[LG])
               }
             )
plot(FDP_2$meantolast,FDP_2$last)
fit <- lm(FDP_2$last~FDP_2$meantolast)
summary(fit)