#' Linear model test 3
#'
#' Fit LM with stdname, IS_HOME, and Opponent
#'
#' @param df
#'
#' @return
#' @export
#'
#' @examples
nba_lm3 <- function(df) {
  browser()
  print(dim(df))

  lm3 <- lm(FDPoints ~ stdname + IS_HOME + Opponent, data=df, na.action=na.omit)
  plot(lm3$model$FDPoints, lm3$fitted.values, main="Fitted vs actual FDPoints on training")
  abline(a=0,b=1,col=2)

  inboth <- (df$stdname %in% (lm3$model$stdname)) & !is.na(df$DFN.Projection) & !is.na(df$FDPoints)
  myproj <- predict(lm3, df[inboth,])
  inbothandnotNA <- !is.na(myproj)

  plot(df[inboth,][inbothandnotNA,]$FDPoints, myproj[inbothandnotNA])
  plot(df[inboth,][inbothandnotNA,]$FDPoints, df[inboth,][inbothandnotNA,]$DFN.Projection)
  myrmse <- sqrt(mean((df[inboth,][inbothandnotNA,]$FDPoints - myproj[inbothandnotNA])^2))
  DFNrmse <- sqrt(mean((df[inboth,][inbothandnotNA,]$FDPoints - df[inboth,][inbothandnotNA,]$DFN.Projection)^2))
  c(myrmse, DFNrmse)



  return()
}

if (F) {
  nba_lm3(df=df1)
}
nba_lm4 <- function(dftrain, dftest) {
  browser()
  print(dim(dftrain))
  print(dim(dftest))

  lm3 <- lm(FanDuelPts ~ stdname + IS_HOME + OPP_TEAM_ABBREVIATION, data=dftrain, na.action=na.omit)
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
  nba <- convert.raw.nba(year_file_name)
  source('~/GitHub/NBAFantasy/R/aggregate_data.R')
  source('~/GitHub/NBAFantasy/R/convert_nickname_to_stdname.R')
  source('~/GitHub/NBAFantasy/R/convert_teamname_to_stdteamname.R')
  df1 <- join_data(nba, "20171128", "20171219")
  df2 <- join_data(nba, "20171220", "20180104")
  nba_lm4(dftrain=df1, dftest=df2)
}
