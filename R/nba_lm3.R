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

  # Use FanDuelPts or FDScore (from nba) instead of FDPoints (from blank)
  # Opponent (from blank) not good, should get it from nba
  lm3 <- lm(FDPoints ~ stdname + IS_HOME + Opponent, data=dftrain, na.action=na.omit)
  plot(lm3$model$FDPoints, lm3$fitted.values, main="Fitted vs actual FDPoints on training")
  abline(a=0,b=1,col=2)

  inboth <- (dftrain$stdname %in% (lm3$model$stdname)) & !is.na(dftrain$DFN.Projection) & !is.na(dftrain$FDPoints)
  myproj <- predict(lm3, dftrain[inboth,])
  inbothandnotNA <- !is.na(myproj)

  plot(dftrain[inboth,][inbothandnotNA,]$FDPoints, myproj[inbothandnotNA])
  plot(dftrain[inboth,][inbothandnotNA,]$FDPoints, dftrain[inboth,][inbothandnotNA,]$DFN.Projection)
  myrmse <- sqrt(mean((dftrain[inboth,][inbothandnotNA,]$FDPoints - myproj[inbothandnotNA])^2))
  DFNrmse <- sqrt(mean((dftrain[inboth,][inbothandnotNA,]$FDPoints - dftrain[inboth,][inbothandnotNA,]$DFN.Projection)^2))
  c(myrmse, DFNrmse)


  inboth <- (dftest$stdname %in% (lm3$model$stdname)) & !is.na(dftest$DFN.Projection) & !is.na(dftest$FDPoints)
  myproj <- predict(lm3, dftest[inboth,])
  inbothandnotNA <- !is.na(myproj)

  plot(dftest[inboth,][inbothandnotNA,]$FDPoints, myproj[inbothandnotNA])
  plot(dftest[inboth,][inbothandnotNA,]$FDPoints, dftest[inboth,][inbothandnotNA,]$DFN.Projection)
  myrmse <- sqrt(mean((dftest[inboth,][inbothandnotNA,]$FDPoints - myproj[inbothandnotNA])^2))
  DFNrmse <- sqrt(mean((dftest[inboth,][inbothandnotNA,]$FDPoints - dftest[inboth,][inbothandnotNA,]$DFN.Projection)^2))
  c(myrmse, DFNrmse)



  return()
}
if (F) {
  df1 <- join_data(nba, "20171128", "20171219")
  df2 <- join_data(nba, "20171220", "20180104")
  nba_lm4(dftrain=df1, dftest=df2)
}
