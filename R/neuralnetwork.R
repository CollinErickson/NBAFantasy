library(neuralnet)
train5 <- read.csv('data/train5.csv')
test5 <- read.csv('data/test5.csv')
n <- names(train5)
f <- as.formula(paste("FDPoints ~", paste(n[!n %in% "FDPoints"], collapse = " + ")))
nn <- neuralnet(f, data=train5, hidden=c(1))

preds <- prediction(nn, test5) # doesn't work, can't allocate memory
plot(preds, test5$FDPoints)



# try on simpler model
nba2 <- nba[,c('FanDuelPts','PLAYER_ID','IS_HOME','OPP_TEAM_ID')]

nba3 <- model.matrix(~ FanDuelPts + factor(PLAYER_ID) + factor(IS_HOME) + factor(OPP_TEAM_ID) -1,data=nba2)
n2 <- colnames(nba3)
n2 <- gsub("[(]","",n2)
n2 <- gsub("[)]","",n2)
colnames(nba3) <- n2
nba3 <- as.data.frame(nba3)
#f2 <- as.formula('FanDuelPts ~ factor(PLAYER_ID) + factor(IS_HOME) + factor(OPP_TEAM_ID)')
f2 <- as.formula(paste("FanDuelPts ~ ", paste(n2[!n2 %in% "FanDuelPts"], collapse = " + ")))
nn2 <- neuralnet(f2, data=nba3, hidden=c(1))
pr2 <- prediction(nn, nba3) # not working


# try nnet package
library(nnet)
nn2 <- nnet(f2, data=nba3, size=c(1))
pr2 <- prediction(nn2, nba3) # also gives error


nn2 <- nnet(FanDuelPts ~ PLAYER_ID + IS_HOME + OPP_TEAM_ID, data=nba2, size=c(1), linout=TRUE)
pr2 <- predict(nn2, nba2) # also gives error

nn2 <- nnet(f2, data=nba3, size=c(2), linout=TRUE)
pr2 <- predict(nn2, nba3) # also gives error
plot(pr2, nba3$FanDuelPts)
