# Predict using Daily Fantasy Nerd as an input
nba_lm_pwDFN <- function(dftrain0, dftest0) {
  dftrain <- dftrain0[dftrain0$in.spbn == "SPBN",]
  dftest <- dftest0[dftest0$in.spbn == "SPBN",]
  browser()
  print(dim(dftrain))
  print(dim(dftest))

  lm3 <- lm(FanDuelPts ~ stdname + IS_HOME + OPP_TEAM_ABBREVIATION + DFN.Projection, data=dftrain, na.action=na.omit)
  plot(lm3$model$FanDuelPts, lm3$fitted.values, main="Fitted vs actual FanDuelPts on training")
  abline(a=0,b=1,col=2)

  inboth <- (dftrain$stdname %in% (lm3$model$stdname)) & !is.na(dftrain$DFN.Projection) & !is.na(dftrain$FanDuelPts)
  myproj <- predict(lm3, dftrain[inboth,])

  plot(dftrain[inboth,]$FanDuelPts, myproj)
  plot(dftrain[inboth,]$FanDuelPts, dftrain[inboth,]$DFN.Projection)
  myrmse <- sqrt(mean((dftrain[inboth,]$FanDuelPts - myproj)^2))
  DFNrmse <- sqrt(mean((dftrain[inboth,]$FanDuelPts - dftrain[inboth,]$DFN.Projection)^2))

  print(c(myrmse, DFNrmse))


  inboth <- (dftest$stdname %in% (lm3$model$stdname)) & !is.na(dftest$DFN.Projection) & !is.na(dftest$FanDuelPts)
  myproj <- predict(lm3, dftest[inboth,])

  plot(dftest[inboth,]$FanDuelPts, myproj)
  plot(dftest[inboth,]$FanDuelPts, dftest[inboth,]$DFN.Projection)
  myrmse <- sqrt(mean((dftest[inboth,]$FanDuelPts - myproj)^2))
  DFNrmse <- sqrt(mean((dftest[inboth,]$FanDuelPts - dftest[inboth,]$DFN.Projection)^2))

  print(c(myrmse, DFNrmse))



  return()
}
if (F) {
  year <- 2017
  year_file_name <- paste0("data/Player/", year, ".csv")
  source('~/GitHub/NBAFantasy/R/nba_functions.R')
  source('~/GitHub/NBAFantasy/R/convert_nickname_to_stdname.R')
  source('~/GitHub/NBAFantasy/R/convert_teamname_to_stdteamname.R')
  nba <- convert.raw.nba(year_file_name)
  source('~/GitHub/NBAFantasy/R/aggregate_data.R')
  df1 <- join_data(nba, "20171128", "20171219")
  df2 <- join_data(nba, "20171220", "20180104")
  nba_lm_pwDFN(dftrain=df1, dftest=df2)
}
