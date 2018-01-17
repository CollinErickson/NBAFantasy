nba_lm3 <- function(df) {
  browser()
  print(dim(df))

  lm3 <- lm(FDPoints ~ stdname + IS_HOME + Opponent, data=df, na.action=na.omit)
  plot(lm3$model$FDPoints, lm3$fitted.values, main="Fitted vs actual FDPoints on training")
  abline(a=0,b=1,col=2)

  inboth <- (df1$stdname %in% (lm3$model$stdname)) & !is.na(df1$DFN.Projection) & !is.na(df1$FDPoints)
  myproj <- predict(lm3, df1[inboth,])
  inbothandnotNA <- !is.na(myproj)

  plot(df1[inboth,][inbothandnotNA,]$FDPoints, myproj[inbothandnotNA])
  plot(df1[inboth,][inbothandnotNA,]$FDPoints, df1[inboth,][inbothandnotNA,]$DFN.Projection)
  myrmse <- sqrt(mean((df1[inboth,][inbothandnotNA,]$FDPoints - myproj[inbothandnotNA])^2))
  DFNrmse <- sqrt(mean((df1[inboth,][inbothandnotNA,]$FDPoints - df1[inboth,][inbothandnotNA,]$DFN.Projection)^2))
  c(myrmse, DFNrmse)



  return()
}

if (F) {
  nba_lm3(df=df1)
}
