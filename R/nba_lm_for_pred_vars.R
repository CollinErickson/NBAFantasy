nba_lm_for_pred_vars <- function(dftrain, dftest, pred_vars) {
  # browser()
  print(dim(dftrain))
  print(dim(dftest))

  f <- paste("FanDuelPts", "~", paste((pred_vars), collapse=" + "))

  # lm3 <- lm(FanDuelPts ~ stdname + IS_HOME + OPP_TEAM_ABBREVIATION, data=dftrain, na.action=na.omit)
  lm3 <- lm(f, data=dftrain, na.action=na.omit)
  plot(lm3$model$FanDuelPts, lm3$fitted.values, main="Fitted vs actual FanDuelPts on training")
  abline(a=0,b=1,col=2)

  # inboth <- (dftrain$stdname %in% (lm3$model$stdname)) & !is.na(dftrain$DFN.Projection) & !is.na(dftrain$FanDuelPts)
  # myproj <- predict(lm3, dftrain[inboth,])
  myproj <- predict(lm3, dftrain)

  plot(dftrain$FanDuelPts, myproj)
  plot(dftrain$FanDuelPts, dftrain$DFN.Projection)
  myrmsetr <- sqrt(mean((dftrain$FanDuelPts - myproj)^2))
  DFNrmsetr <- sqrt(mean((dftrain$FanDuelPts - dftrain$DFN.Projection)^2))

  print(c(myrmsetr, DFNrmsetr))


  # inboth <- (dftest$stdname %in% (lm3$model$stdname)) & !is.na(dftest$DFN.Projection) & !is.na(dftest$FanDuelPts)
  # myproj <- predict(lm3, dftest[inboth,])
  myproj <- predict(lm3, dftest)

  plot(dftest$FanDuelPts, myproj)
  plot(dftest$FanDuelPts, dftest$DFN.Projection)
  myrmsete <- sqrt(mean((dftest$FanDuelPts - myproj)^2))
  DFNrmsete <- sqrt(mean((dftest$FanDuelPts - dftest$DFN.Projection)^2))

  print(c(myrmsete, DFNrmsete))


  c(myrmse.train=myrmsetr, DFNrmse.train=DFNrmsetr, myrmse.test=myrmsete, DFNrmse.test=DFNrmsete)

}
if (F) {
  year <- 2017
  year_file_name <- paste0("data/Player/", year, ".csv")
  source('~/GitHub/NBAFantasy/R/nba_functions.R')
  nba <- convert.raw.nba(year_file_name)
  source('~/GitHub/NBAFantasy/R/aggregate_data.R')
  source('~/GitHub/NBAFantasy/R/convert_nickname_to_stdname.R')
  source('~/GitHub/NBAFantasy/R/convert_teamname_to_stdteamname.R')
  df1all <- join_data(nba, "20171128", "20171219")
  df2all <- join_data(nba, "20171220", "20180104")
  df1 <- df1all[df1all$in.spbn=="SPBN",]
  df2 <- df2all[df2all$in.spbn=="SPBN",]
  nba_lm_for_pred_vars(dftrain=df1, dftest=df2, pred_vars=c("IS_HOME"))
  nba_lm_for_pred_vars(dftrain=df1, dftest=df2, pred_vars=c("IS_HOME"))
}
