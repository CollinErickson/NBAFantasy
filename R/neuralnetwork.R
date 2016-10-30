library(neuralnet)
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
pr2 <- prediction(nn, nba3)
