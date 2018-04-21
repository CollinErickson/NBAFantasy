#' Predict using a tree
#'
#' Was worse than LM
#'
#' @param dftrain
#' @param dftest
#'
#' @return
#' @export
#'
#' @examples
nba_tree1 <- function(dftrain, dftest) {
  browser()
  print(dim(dftrain))
  print(dim(dftest))

  # Use FanDuelPts or FDScore (from nba) instead of FanDuelPts (from blank)
  # Opponent (from blank) not good, should get it from nba
  tr1 <- rpart::rpart(FanDuelPts ~ stdname + IS_HOME + OPP_TEAM_ABBREVIATION, data=dftrain, na.action=na.omit, method="anova")
  plot(tr1$model$FanDuelPts, tr1$fitted.values, main="Fitted vs actual FanDuelPts on training")
  abline(a=0,b=1,col=2)

  inboth <- (dftrain$stdname %in% (tr1$model$stdname)) & !is.na(dftrain$DFN.Projection) & !is.na(dftrain$FanDuelPts)
  myproj <- predict(tr1, dftrain[inboth,])

  plot(dftrain[inboth,]$FanDuelPts, myproj)
  plot(dftrain[inboth,]$FanDuelPts, dftrain[inboth,]$DFN.Projection)
  myrmse <- sqrt(mean((dftrain[inboth,]$FanDuelPts - myproj)^2))
  DFNrmse <- sqrt(mean((dftrain[inboth,]$FanDuelPts - dftrain[inboth,]$DFN.Projection)^2))

  print(c(myrmse, DFNrmse))


  inboth <- (dftest$stdname %in% (tr1$model$stdname)) & !is.na(dftest$DFN.Projection) & !is.na(dftest$FanDuelPts)
  myproj <- predict(tr1, dftest[inboth,])

  plot(dftest[inboth,]$FanDuelPts, myproj)
  plot(dftest[inboth,]$FanDuelPts, dftest[inboth,]$DFN.Projection)
  myrmse <- sqrt(mean((dftest[inboth,]$FanDuelPts - myproj)^2))
  DFNrmse <- sqrt(mean((dftest[inboth,]$FanDuelPts - dftest[inboth,]$DFN.Projection)^2))

  print(c(myrmse, DFNrmse))



  return()
}
if (F) {

  df1 <- join_data(nba, "20171128", "20171219")
  df2 <- join_data(nba, "20171220", "20180104")
  nba_tree1(dftrain=df1, dftest=df2)
}
