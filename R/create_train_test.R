#setwd("C:/Users/cbe117/School/IEMS490/Project")
library(caret)
set.seed(0)
#dat <- read.csv('nbaout_mm.csv')
dat.in <- read.csv('data/PredictorSS.csv')
drop.cols <- c('Date','Player_ID','Name','Game_ID','Team','Opponent')
dat <- dat.in[,!(names(dat.in)%in%drop.cols)] # remove date
if (F) {
  # First partition just does 70/30
  partit1 <- createDataPartition(dat$FDP,p=.7,list=F)
  train1 <- dat[partit1,]
  test1 <- dat[-partit1,]
  write.csv(train1,'train1.csv',row.names=F)
  write.csv(test1,'test1.csv',row.names=F)
}
if (F) {
  # train2 removes first 14 days, training is beginning of season
  dat2 <- dat[3081:dim(dat)[1],]
  indices2 <- floor(1:((dim(dat2)[1])*.7))
  train2 <- dat2[indices2,]
  test2  <- dat[-indices2,]
  fit2 <- lm(FDPoints~.,train2)
  pred.test2 <- predict(fit2,test2)
  plot(train2$FDP,fit2$fitted)
  plot(test2$FDP,pred.test2)
  sqrt(mean((train2$FDP-fit2$fitted)^2))
  sqrt(mean((test2$FDP-pred.test2)^2))
}
if(F) {
  # write out residuals as train3
  train3 <- train2
  train3$FDPoints <- fit2$residuals
  test3 <- test2
  test3$FDPoints <- test2$FDPoints - pred.test2
  write.csv(train3,'train3.csv',row.names=F)
  write.csv(test3,'test3.csv',row.names=F)
}
if (F) {
  # train4 does classes
  dat2 <- dat[3081:dim(dat)[1],]
  num.classes <- 8

  indices2 <- floor(1:((dim(dat2)[1])*.7))
  train2 <- dat2[indices2,]
  test2  <- dat[-indices2,]
  write.csv(train4,'train4.csv',row.names=F)
  write.csv(test4,'test4.csv',row.names=F)

}
if (F) {
  # 5 removes first 14 days and does random 70/30 split with rest
  dat5 <- dat[3081:dim(dat)[1],]
  partit5 <- createDataPartition(dat5$FDP,p=.7,list=F)
  train5 <- dat[partit5,]
  test5 <- dat[-partit5,]
  write.csv(train5,'data/train5.csv',row.names=F)
  write.csv(test5,'data/test5.csv',row.names=F)
}
