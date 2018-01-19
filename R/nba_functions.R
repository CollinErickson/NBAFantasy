library(magrittr)
library(plyr)
#' Takes in the raw data file name and does all the data cleaning
convert.raw.nba <- function(file.path.in,write.out=F,file.path.out) {browser()
  #nba <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\2015Season2.csv",stringsAsFactors=F)
  # Read in the data
  nba <- read.csv(file.path.in,stringsAsFactors=F)
  #over10 <- nba14[nba14$SEC>600,]
  #' Find players that played at all
  played <- nba$MIN!=''
  # Remove players that didn't play
  nba <- nba[played,] # Remove those who didn't play, loses injury comments
  #browser()
  # Convert playing time to seconds, fixes some issues
  nba$SEC <- sapply((nba$MIN), #   this wont work, fix this
                    function(xxx) {
                      strspl <- as.numeric(strsplit(xxx,':')[[1]])
                      if (length(strspl)==2) {
                        return(sum(strspl*c(60,1)))
                      } else if (length(strspl)==3) {
                          return(sum(strspl*c(60,1,0)))
                      } else if (length(strspl)==1) {
                        #browser() # Paul Pierce LAC 10/28/15 played 24 minutes but MIN is "1". 2 others with  "1".
                        return((strspl*1))
                      } else {
                        print(strspl)
                        print(xxx)
                        return(stop('messed up error 352329393'))
                      }
                    }
  )
  # Calculates Fan Duel points
  if (is.character(nba$REB[1])) {nba$REB <- as.numeric(nba$REB)}
  nba$FanDuelPts <- nba$PTS + 1.2*nba$REB + 1.5*nba$AST + 3*nba$BLK + 3*nba$STL - 1*nba$TO
  nba$IS_HOME <- (nba$TEAM_ID == nba$HOME_TEAM_ID)
  nba$OPP_TEAM_ID <- ifelse(nba$IS_HOME,nba$VISITOR_TEAM_ID,nba$HOME_TEAM_ID)

  # Change team abbrev to standardized
  nba$TEAM_ABBREVIATION <- convert.teamname.to.stdteamname(nba$TEAM_ABBREVIATION)

  # Get OPP_TEAM_ABBREVIATION
  unique.teams <- unique.data.frame(nba[,c('TEAM_ID', 'TEAM_ABBREVIATION')])
  teammap <- unique.teams[,2]
  names(teammap) <- unique.teams[,1]
  nba$OPP_TEAM_ABBREVIATION <- teammap[as.character(nba$OPP_TEAM_ID)]

  # Order the columns alphabetically
  nba <- nba[,order(names(nba))]
  if (write.out) { # Write out clean data
    write.csv(nba,file.path.out)
  }
  return(nba)
}
if (F) {
  #nba15 <- convert.raw.nba("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\2015Season20160211.csv")
  nba15 <- convert.raw.nba("data\\2015Season20160211.csv")
  nba <- convert.raw.nba("data\\2015Season20160211.csv")
}

#' Create a table matching the players from the game data and salary data
create.id.conversion.table <- function(nba,sal) {
  # NBA is full nba data table
  # sal is the Fan Duel salary table

  # Conversion bs
  # Some names don't agree between the two
  conversion.all.names <- c('Bradley Beal', 'Brad Beal',
                            'Lou Williams', 'Louis Williams',
                            'JJ Redick', 'J.J. Redick',
                            'Bryce Dejean-Jones', 'Bryce Jones',
                            'PJ Tucker', 'P.J. Tucker',
                            'CJ Watson', 'C.J. Watson',
                            'Luc Mbah a Moute', 'Luc Richard Mbah a Moute',
                            'KJ McDaniels', 'K.J. McDaniels',
                            'Lou Amundson', 'Louis Amundson',
                            'PJ Hairston', 'P.J. Hairston',
                            'CJ McCollum', 'C.J. McCollum',
                            'Ish Smith', 'Ishmael Smith',
                            'Phil Pressey', 'Phil (Flip) Pressey',
                            'JaKarr Sampson', 'Jakarr Sampson',
                            'Patty Mills', 'Patrick Mills',
                            'Nene', 'Nene Hilario')
  evens <- (1:(length(conversion.all.names)/2))*2
  odds <- evens-1
  conversion.FD.names <- conversion.all.names[evens]
  conversion.nba.names <- conversion.all.names[odds]
  # Check with grep to find player row
  #nba$PLAYER_NAME[grep("Michael",nba$PLAYER_NAME)]

  # Need map between FD player ids and NBA
  # Creates the data frame, will add rows to it in loop below
  FD.nba.conversion <- data.frame(FD.Id=numeric(0),FD.Paste.Name=numeric(0),
                                  FD.First.Name=numeric(0),FD.Last.Name=numeric(0),
                                  FD.Team=numeric(0),nba.ID=numeric(0),nba.PLAYER_NAME=numeric(0),
                                  nba.TEAM_ABBREVIATION=numeric(0))

  # Some won't match up, need to figure out a conversion by hand
  no.conversion <- c()

  # Loop over players in salary table
  for(i in 1:(dim(sal)[1])) {
    prow <- sal[i,] # player row
    #print(prow)
    #print(i)
    pname <- paste(prow$First,prow$Last)
    nbaind <- which(pname == nba$PLAYER_NAME)[1]
    if (is.na(nbaind)) {
      conversion.FD.names.index <- which(pname==conversion.FD.names)
      if (length(conversion.FD.names.index)==0) {# No easy or hard conversion
        print(paste('Cant convert',pname,'error 57823'))
        #no.conversion <- c(no.conversion,pname)
      } else {
        conversion.nba.name <- conversion.nba.names[conversion.FD.names.index]
        nbaind <- which(conversion.nba.name == nba$PLAYER_NAME)[1]
        if(is.na(nbaind))
          stop(paste('Double name fail error 2623482'))
      }
    }
    if (!is.na(nbaind)) {
      FD.nba.conversion <- rbind(FD.nba.conversion,
                                 data.frame(FD.Id=prow$Id,FD.Paste.Name=pname,FD.First.Name=prow$First,FD.Last.Name=prow$Last,FD.Team=prow$Team,
                                            nba.PLAYER_ID=nba$PLAYER_ID[nbaind],nba.PLAYER_NAME=nba$PLAYER_NAME[nbaind],nba.TEAM_ABBREVIATION=nba$TEAM_ABBREVIATION[nbaind]))
    } else {
      no.conversion <- c(no.conversion,pname)
      # Going to write out NAs
      FD.nba.conversion <- rbind(FD.nba.conversion,
                                 data.frame(FD.Id=prow$Id,FD.Paste.Name=pname,FD.First.Name=prow$First,FD.Last.Name=prow$Last,FD.Team=prow$Team,
                                            nba.PLAYER_ID=NA,nba.PLAYER_NAME=NA,nba.TEAM_ABBREVIATION=NA))
    }
  }


  # Write out conversion file

  return(FD.nba.conversion)

  write.csv(FD.nba.conversion,"data\\FD_nba_conversion_csv")
}
if (F) {
  create.id.conversion.table(nba,sal)
  #FD.nba.conversion <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FD.nba.conversion.csv")
  FD.nba.conversion <- read.csv("data\\FD_nba_conversion.csv")
}

#' Fit a simple linear model to the data
fit.LM.1 <- function(nba,sal,res) {
  mod1 <- lm(FanDuelPts ~ factor(PLAYER_ID),data = nba)
  # Predict for single row to test (Cousins)

  #FD.nba.conversion <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FD.nba.conversion.csv",stringsAsFactors=F)
  FD.nba.conversion <- read.csv("data\\FD_nba_conversion.csv",stringsAsFactors=F)
  FD.Id.to.NBA.PLAYER_ID <- FD.nba.conversion$nba.PLAYER_ID
  names(FD.Id.to.NBA.PLAYER_ID) <- FD.nba.conversion$FD.Id
  sal$PLAYER_ID <- FD.Id.to.NBA.PLAYER_ID[sal$Id]


  sal$LM.1.pred <- predict(mod1,newdata = sal)
  # Get coefficient for specific player
  #mod3$coefficients['factor(PLAYER_ID)202326']
  plot(sal$FPPG,sal$LM.)
}

#' If you have two corresponding vectors, this creates a dictionary
#'  allowing you to map keys to values.
get.converter <- function(keys,values) {
  conv <- values#FD.Id.to.NBA.PLAYER_ID <- FD.nba.conversion$nba.PLAYER_ID
  names(conv) <- keys#names(FD.Id.to.NBA.PLAYER_ID) <- FD.nba.conversion$FD.Id
  return(conv)
}
#' Create a converter that removes duplicates
get.converter.unique <- function(dat,key.name,value.name) {#browser()
  uniq <- ddply(dat,key.name,function(xx){xx[1,]})
  return(get.converter(uniq[,key.name],uniq[,value.name]))#ukeys,uvalues))
}
if (F) {
  get.converter(FD.nba.conversion$nba.PLAYER_ID,FD.nba.conversion$FD.Id)
  #team.abb.to.TEAM_ID.conv <- get.converter.unique(nba,'TEAM_ABBREVIATION','TEAM_ID')
  #TEAM_ID.to.team.abb.conv <- get.converter.unique(nba,'TEAM_ID','TEAM_ABBREVIATION')
  #write.csv(team.abb.to.TEAM_ID.conv, 'data//team_abb_to_TEAM_ID_conv.csv')
  #saveRDS(team.abb.to.TEAM_ID.conv, 'data//team_abb_to_TEAM_ID_conv.rds')
  #saveRDS(team.abb.to.TEAM_ID.conv, 'data//TEAM_ID_to_team_abb_conv.rds')
  team.abb.to.TEAM_ID.conv <- readRDS('data//team_abb_to_TEAM_ID_conv.rds')
}

#' This does all steps of fitting the linear model
fit.LM.2 <- function(nba,sal,res) {browser()
  # Fit the model
  mod2 <- lm(FanDuelPts ~ factor(PLAYER_ID) + factor(IS_HOME) + factor(OPP_TEAM_ID),data = nba) # + factor(OPP_TEAM_ID)

  FD.nba.conversion <- read.csv("data\\FD_nba_conversion.csv",stringsAsFactors=F)
  FD.Id.to.NBA.PLAYER_ID <- FD.nba.conversion$nba.PLAYER_ID
  names(FD.Id.to.NBA.PLAYER_ID) <- FD.nba.conversion$FD.Id
  sal$PLAYER_ID <- FD.Id.to.NBA.PLAYER_ID[sal$Id]
  sal$IS_HOME <- apply(sal,1,function(xxx){
    strsplit(xxx['Game'],'@')[[1]][2] == xxx['Team']
    })
  sal$OPP_TEAM_ABBREVIATION <- sal$Opponent
  sal$OPP_TEAM_ABBREVIATION[sal$OPP_TEAM_ABBREVIATION=='PHO'] <- 'PHX'
  sal$OPP_TEAM_ABBREVIATION[sal$OPP_TEAM_ABBREVIATION=='NO'] <- 'NOP'
  #team.abb.to.TEAM_ID.conv <- get.converter.unique(nba,'TEAM_ABBREVIATION','TEAM_ID')
  team.abb.to.TEAM_ID.conv<- readRDS('data//team_abb_to_TEAM_ID_conv.rds')
  sal$OPP_TEAM_ID <- team.abb.to.TEAM_ID.conv[sal$OPP_TEAM_ABBREVIATION]

  # Getting Error in model.frame.default(Terms, newdata, na.action = na.action, xlev = object$xlevels) :
              # factor factor(PLAYER_ID) has new levels 202343
  # Try to fix by setting to NA those that don't player_id in nba
  sal$PLAYER_ID[!(sal$PLAYER_ID %in% nba$PLAYER_ID)] <- NA

  sal$LM.2.pred <- predict(mod2,newdata = sal)
  sal$LM.2.pred[sal$Injury.Indicator=='O'] <- 0
  # Get coefficient for specific player
  #mod3$coefficients['factor(PLAYER_ID)202326']
  plot(sal$FPPG,sal$LM.2)
  #points(sal$FPPG,sal$LM.2,col='red')
  plot(res$FDPt,sal$LM.2)
  plot(res$FDPt,sal$LM.2,col=ifelse(sal$Injury.Ind=='GTD','red','black'))
}
if (F) {
  # Does everything
  #library(plyr)
  nba <- convert.raw.nba("data\\2015Season20160211.csv")
  FD.nba.conversion <- read.csv("data\\FD_nba_conversion.csv")
  sal <- read.csv("data\\FDSalaryNow_2_8_16.csv",stringsAsFactors=F)
  res <- read.csv("data\\FDResults_2_8_16.csv",stringsAsFactors=F)
  fit.LM.2(nba,sal,res)
  # Standard errors of coeffs coef(summary(mod2))[,2]
  #nas <- which(is.na(sal$LM.2.pred)) # Fixed PHO and NO, just 3 nobodies giving NA
}
if (F) { # Finds correlation of teammates, will use later for random sampling
  # Correlation on same team
  atl <- nba[nba$TEAM_ABB=='ATL',]
  atlpn <- length(unique(atl$PLAYER_NAME))
  atlp <- matrix(NA,length(unique(atl$GAME_ID)),atlpn,dimnames = list(unique(atl$GAME_ID),unique(atl$PLAYER_NAME)))
  for (gid in unique(atl$GAME_ID)) {
    for (plr in unique(atl$PLAYER_NAME)) {
      #print('  --')
      #print(atl$FanDuelPts[atl$GAME_ID==gid & atl$PLAYER_NAME==plr])
      atlind <- which(atl$GAME_ID==gid & atl$PLAYER_NAME==plr)
      if(length(atlind)==1)
        atlp[as.character(gid),plr] <- atl$FanDuelPts[atlind]
    }
  }
  atlc <- cor(atlp,use = 'pairwise.complete.obs')
  # Find # of games both played in together
  atlcg <- atlc
  atlcg <- ifelse(atlcg>-10,0,0)
  for (plr1 in unique(atl$PLAYER_NAME)) {
    for (plr2 in unique(atl$PLAYER_NAME)) {
      atlcg[plr1,plr2] <- sum(ddply(atl,.(GAME_ID),function(xx){return(data.frame(bth=(plr1 %in% xx$PLAYER_NAME & plr2 %in% xx$PLAYER_NAME)))})$bth)
    }
  }
  # TURNED INTO A FUNCTION BELOW
}
get.cor.and.cg.from.team <- function(atl) {
  #browser()
  # Correlation on same team
  # atl <- nba[nba$TEAM_ABB=='ATL',] calling it atl since it worked on just the team first
  # atl should be the df of nba with only atl players
  atlpn <- length(unique(atl$PLAYER_ID))
  atlp <- matrix(NA,length(unique(atl$GAME_ID)),atlpn,dimnames = list(unique(atl$GAME_ID),as.character(unique(atl$PLAYER_ID))))
  for (gid in unique(atl$GAME_ID)) { # loop to get matrix of players FDP in each game
    for (plr in unique(atl$PLAYER_ID)) {
      #print('  --')
      #print(atl$FanDuelPts[atl$GAME_ID==gid & atl$PLAYER_NAME==plr])
      atlind <- which(atl$GAME_ID==gid & atl$PLAYER_ID==plr)
      if(length(atlind)==1)
        atlp[as.character(gid),as.character(plr)] <- atl$FanDuelPts[atlind]
    }
  }
  atlc <- cor(atlp,use = 'pairwise.complete.obs') # Get correlation, only need pairs
  # Find # of games both played in together
  atlcg <- atlc
  atlcg <- ifelse(atlcg>-10,0,0) # Get matrix with zeros for each pair of players
  for (plr1 in as.character(unique(atl$PLAYER_ID))) {
    for (plr2 in as.character(unique(atl$PLAYER_ID))) {
      #atlcg[plr1,plr2] <- sum(ddply(atl,.(GAME_ID),function(xx){return(data.frame(bth=(plr1 %in% xx$PLAYER_NAME & plr2 %in% xx$PLAYER_NAME)))})$bth)
      atlcg[plr1,plr2] <- sum(!is.na(atlp[,plr1]) & !is.na(atlp[,plr2]))
    }
  }
  # Return correlation matrix and
  return(list(cor=atlc,cg=atlcg))
}
get.cor.and.cg.all <- function(nbaa){
  return(dlply(nbaa,.(TEAM_ID),get.cor.and.cg.from.team))
}
if (F) {
  # Find how FDP varies with FDP
  sal2 <- fit.LM.2.w.error(nba,sal,res)

}
fit.LM.2.w.error <- function(nba,sal,res) {
  mod2 <- lm(FanDuelPts ~ factor(PLAYER_ID) + factor(IS_HOME) + factor(OPP_TEAM_ID),data = nba) # + factor(OPP_TEAM_ID)
  # Predict for single row to test (Cousins)

  FD.nba.conversion <- read.csv("data\\FD_nba_conversion.csv",stringsAsFactors=F)
  FD.Id.to.NBA.PLAYER_ID <- FD.nba.conversion$nba.PLAYER_ID
  names(FD.Id.to.NBA.PLAYER_ID) <- FD.nba.conversion$FD.Id
  sal$PLAYER_ID <- FD.Id.to.NBA.PLAYER_ID[sal$Id]
  sal$IS_HOME <- apply(sal,1,function(xxx){
    strsplit(xxx['Game'],'@')[[1]][2] == xxx['Team']
  })

  # Get abbreviation and id for team and opponent
  sal$OPP_TEAM_ABBREVIATION <- sal$Opponent
  sal$OPP_TEAM_ABBREVIATION[sal$OPP_TEAM_ABBREVIATION=='PHO'] <- 'PHX'
  sal$OPP_TEAM_ABBREVIATION[sal$OPP_TEAM_ABBREVIATION=='NO'] <- 'NOP'
  team.abb.to.TEAM_ID.conv <- get.converter.unique(nba,'TEAM_ABBREVIATION','TEAM_ID')
  team.abb.to.TEAM_ID.conv <- readRDS('data/team_abb_to_TEAM_ID_conv.rds')
  sal$OPP_TEAM_ID <- team.abb.to.TEAM_ID.conv[sal$OPP_TEAM_ABBREVIATION]
    # for own team
  sal$TEAM_ABBREVIATION <- sal$Team
  sal$TEAM_ABBREVIATION[sal$TEAM_ABBREVIATION=='PHO'] <- 'PHX'
  sal$TEAM_ABBREVIATION[sal$TEAM_ABBREVIATION=='NO'] <- 'NOP'
  #team.abb.to.TEAM_ID.conv <- get.converter.unique(nba,'TEAM_ABBREVIATION','TEAM_ID')
  sal$TEAM_ID <- team.abb.to.TEAM_ID.conv[sal$TEAM_ABBREVIATION]

  LM.2.pred <- predict(mod2,newdata = sal,se.fit = T)
  sal$LM.2.pred <- LM.2.pred$fit
  sal$LM.2.pred[sal$Injury.Indicator=='O'] <- 0
  sal$LM.2.pred.se <- LM.2.pred$se.fit
  sal$LM.2.pred.se[sal$Injury.Indicator=='O'] <- 1 # to avoid numerical issues later
  # Get coefficient for specific player
  #mod3$coefficients['factor(PLAYER_ID)202326']
  plot(sal$FPPG,sal$LM.2.pred)
  points(sal$FPPG,sal$LM.2.pred+2*sal$LM.2.pred.se,col=5)
  points(sal$FPPG,sal$LM.2.pred-2*sal$LM.2.pred.se,col=5)
  #points(sal$FPPG,sal$LM.2,col='red')
  #plot(res$FDPt,sal$LM.2.pred)
  #plot(res$FDPt,sal$LM.2.pred,col=ifelse(sal$Injury.Ind=='GTD','red','black'))
  return(sal)
}
if (F) {
  # Get multivariate samples
  sal2a <- fit.LM.2.w.error(nba,sal,res)
  sal2 <- sal2a[-which(is.na(sal2a$PLAYER_ID)),]
  sal2.get.cor <- function(x,nba.cor.cg) {
    # Test: x <- sal2[sal2$Team=='ATL',]
    TEAM_ID <- x$TEAM_ID[1]
    #browser()
    nms <- x$PLAYER_ID # Names of players on team
    #cm <- diag(length(nms))
    #matrix(0,length(nms),length(nms),dimnames = list(nms,nms)) # correlation matrix
    #dimnames(cm) <- list(nms,nms)
    nms.cor <- dimnames(nba.cor.cg[[as.character(TEAM_ID)]][[1]])[[1]]
    min.games.played.together = 5
    while(T) {
      cm <- diag(length(nms))
      dimnames(cm) <- list(nms,nms)
      for(i in 1:(length(nms)-1)) {
        for (j in (i+1):length(nms)) {
          if(nms[i]%in%nms.cor  & nms[j]%in%nms.cor) {
            if(nba.cor.cg[[as.character(TEAM_ID)]][[2]][as.character(nms[i]),as.character(nms[j])]>=min.games.played.together){
              newval <- nba.cor.cg[[as.character(TEAM_ID)]][[1]][as.character(nms[i]),as.character(nms[j])]
              cm[i,j] <- newval
              cm[j,i] <- newval
            }
          }
        }
      }
      if(min(eigen(cm)$val) >=0) {
        break
      } else {
        print(c(min.games.played.together,min(eigen(cm)$val)))
        min.games.played.together <- min.games.played.together + 5
        if (min.games.played.together>50) {
          break
        }
      }
    }
    return(cm)
  }
  nbacor <- get.cor.and.cg.all(nba)
  # Gives correlation matrices for fan dual
  sal2.cms <- dlply(sal2,.(TEAM_ID),sal2.get.cor,nbacor)
  library(MASS)
  # DOESNT WORK, has 1 neg e-val, -.5, needs to be pos def
  MASS::mvrnorm(1,rep(0,15),sal2.cms[[1]])
  tmat <- sal2.cms[[1]]
  eigen(tmat)$val
  eigen(tmat+diag(.52,15))$val
  tmat.cov <- tmat
  tmat.cov.nms <- dimnames(tmat)[[1]]
  for (i in 1:length(tmat.cov.nms)) {
    tmat.cov[i,] <- tmat.cov[i,] * sal2$LM.2.pred.se[sal2$PLAYER_ID==tmat.cov.nms[i]]
    tmat.cov[,i] <- tmat.cov[,i] * sal2$LM.2.pred.se[sal2$PLAYER_ID==tmat.cov.nms[i]]
  }
  eigen(tmat.cov)$val
  MASS::mvrnorm(1,rep(0,15),tmat.cov)
  cor.to.cov <- function(tmat,sal2) {
    tmat.cov <- tmat
    tmat.cov.nms <- dimnames(tmat)[[1]]
    for (i in 1:length(tmat.cov.nms)) {
      tmat.cov[i,] <- tmat.cov[i,] * sal2$LM.2.pred.se[sal2$PLAYER_ID==tmat.cov.nms[i]]
      tmat.cov[,i] <- tmat.cov[,i] * sal2$LM.2.pred.se[sal2$PLAYER_ID==tmat.cov.nms[i]]
    }
    return(tmat.cov)
  }
  all.covs <- lapply(sal2.cms,cor.to.cov,sal2)
}
if (F) {
  # Trying to do everything here, including predictions (function)
  # First get data
  library(plyr)
  nba <- convert.raw.nba("data\\2015Season20160211.csv")
  FD.nba.conversion <- read.csv("data\\FD.nba.conversion.csv")
  sal <- read.csv("data\\FDSalaryNow_2_8_16.csv",stringsAsFactors=F)
  res <- read.csv("data\\FDResults_2_8_16.csv",stringsAsFactors=F)

  sal2a <- fit.LM.2.w.error(nba,sal,res)
  sal2 <- sal2a[-which(is.na(sal2a$PLAYER_ID)),]
  sal2.get.cor <- function(x,nba.cor.cg,sal2) {
    # Takes in a sal for a team along with nba.cor.cg
    # and returns a correlation matrix for those players
    # Test: x <- sal2[sal2$Team=='ATL',]
    TEAM_ID <- x$TEAM_ID[1]
    #browser()
    nms <- x$PLAYER_ID # Names of players on team
    #cm <- diag(length(nms))
    #matrix(0,length(nms),length(nms),dimnames = list(nms,nms)) # correlation matrix
    #dimnames(cm) <- list(nms,nms)
    nms.cor <- dimnames(nba.cor.cg[[as.character(TEAM_ID)]][[1]])[[1]]
    min.games.played.together = 5
    while(T) {
      cm <- diag(length(nms))
      dimnames(cm) <- list(nms,nms)
      for(i in 1:(length(nms)-1)) {
        for (j in (i+1):length(nms)) {
          if(nms[i]%in%nms.cor  & nms[j]%in%nms.cor) {
            if(nba.cor.cg[[as.character(TEAM_ID)]][[2]][as.character(nms[i]),as.character(nms[j])]>=min.games.played.together){
              newval <- nba.cor.cg[[as.character(TEAM_ID)]][[1]][as.character(nms[i]),as.character(nms[j])]
              cm[i,j] <- newval
              cm[j,i] <- newval
            }
          }
        }
      }
      if(min(eigen(cm)$val) >=0) {
        break
      } else {
        print(c(min.games.played.together,min(eigen(cm)$val)))
        min.games.played.together <- min.games.played.together + 5
        if (min.games.played.together>50) {
          break
        }
      }
    }
    # Then create covariance matrix
    tmat.cov <- cm
    tmat.cov.nms <- dimnames(cm)[[1]]
    for (i in 1:length(tmat.cov.nms)) {
      tmat.cov[i,] <- tmat.cov[i,] * sal2$LM.2.pred.se[sal2$PLAYER_ID==tmat.cov.nms[i]]
      tmat.cov[,i] <- tmat.cov[,i] * sal2$LM.2.pred.se[sal2$PLAYER_ID==tmat.cov.nms[i]]
    }
    # Get predicted mean from sal2, column is LM.2.pred
    means <- numeric(length(tmat.cov.nms))
    names(means) <- tmat.cov.nms
    for(i in 1:length(tmat.cov.nms)) {
      nm.this <- as.character(tmat.cov.nms[i])
      means[nm.this] <- sal2$LM.2.pred[as.character(sal2$PLAYER_ID)==nm.this]
    }
    return(list(mu=means,cor=cm,cov=tmat.cov))
  }
  nbacor <- get.cor.and.cg.all(nba)
  # Gives correlation matrices for fan dual
  sal2.cor.and.cov <- dlply(sal2,.(TEAM_ID),sal2.get.cor,nbacor,sal2)
  library(MASS)
  get.samples <- function(mcc.team,n) {
    MASS::mvrnorm(n=n,mu=mcc.team[[1]],Sigma=mcc.team[[3]])
  }
  get.samples(sal2.cor.and.cov[[1]],2)
  # Gets all the samples
  lapply(sal2.cor.and.cov,get.samples,2)
  # DOESNT WORK, has 1 neg e-val, -.5, needs to be pos def
  #MASS::mvrnorm(1,rep(0,15),sal2.cms[[1]])
  #tmat <- sal2.cms[[1]]
  #all.covs <- lapply(sal2.cms,cor.to.cov,sal2)
}
# Turning the above section into a function
write.out.nba.samples <- function(n.samples) {
  # Trying to do everything here, including predictions (function)
  # First get data
  require(plyr)
  nba <- convert.raw.nba("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\2015Season20160211.csv")
  FD.nba.conversion <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FD.nba.conversion.csv")
  sal <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FDSalaryNow_2_8_16.csv",stringsAsFactors=F)
  #res <- read.csv("C:\\Users\\cbe117\\School\\SportsAnalytics\\NBA\\FDResults_2_8_16.csv",stringsAsFactors=F)

  sal2a <- fit.LM.2.w.error(nba,sal,res=NULL)
  sal2 <- sal2a[-which(is.na(sal2a$PLAYER_ID)),]
  sal2.get.cor <- function(x,nba.cor.cg,sal2) {
    # Takes in a sal for a team along with nba.cor.cg
    # and returns a correlation matrix for those players
    # Test: x <- sal2[sal2$Team=='ATL',]
    TEAM_ID <- x$TEAM_ID[1]
    #browser()
    nms <- x$PLAYER_ID # Names of players on team
    #cm <- diag(length(nms))
    #matrix(0,length(nms),length(nms),dimnames = list(nms,nms)) # correlation matrix
    #dimnames(cm) <- list(nms,nms)
    nms.cor <- dimnames(nba.cor.cg[[as.character(TEAM_ID)]][[1]])[[1]]
    min.games.played.together = 5
    while(T) {
      cm <- diag(length(nms))
      dimnames(cm) <- list(nms,nms)
      for(i in 1:(length(nms)-1)) {
        for (j in (i+1):length(nms)) {
          if(nms[i]%in%nms.cor  & nms[j]%in%nms.cor) {
            if(nba.cor.cg[[as.character(TEAM_ID)]][[2]][as.character(nms[i]),as.character(nms[j])]>=min.games.played.together){
              newval <- nba.cor.cg[[as.character(TEAM_ID)]][[1]][as.character(nms[i]),as.character(nms[j])]
              cm[i,j] <- newval
              cm[j,i] <- newval
            }
          }
        }
      }
      if(min(eigen(cm)$val) >=0) {
        break
      } else {
        print(c(min.games.played.together,min(eigen(cm)$val)))
        min.games.played.together <- min.games.played.together + 5
        if (min.games.played.together>50) {
          break
        }
      }
    }
    # Then create covariance matrix
    tmat.cov <- cm
    tmat.cov.nms <- dimnames(cm)[[1]]
    for (i in 1:length(tmat.cov.nms)) {
      tmat.cov[i,] <- tmat.cov[i,] * sal2$LM.2.pred.se[sal2$PLAYER_ID==tmat.cov.nms[i]]
      tmat.cov[,i] <- tmat.cov[,i] * sal2$LM.2.pred.se[sal2$PLAYER_ID==tmat.cov.nms[i]]
    }
    # Get predicted mean from sal2, column is LM.2.pred
    means <- numeric(length(tmat.cov.nms))
    names(means) <- tmat.cov.nms
    for(i in 1:length(tmat.cov.nms)) {
      nm.this <- as.character(tmat.cov.nms[i])
      means[nm.this] <- sal2$LM.2.pred[as.character(sal2$PLAYER_ID)==nm.this]
    }
    return(list(mu=means,cor=cm,cov=tmat.cov))
  }
  nbacor <- get.cor.and.cg.all(nba)
  # Gives correlation matrices for fan dual
  sal2.cor.and.cov <- dlply(sal2,.(TEAM_ID),sal2.get.cor,nbacor,sal2)
  library(MASS)
  get.samples <- function(mcc.team,n) {
    MASS::mvrnorm(n=n,mu=mcc.team[[1]],Sigma=mcc.team[[3]])
  }
  #browser()
  #get.samples(sal2.cor.and.cov[[1]],2)
  # Gets all the samples
  sampleslist = lapply(sal2.cor.and.cov,get.samples,n.samples)
  samplesout = sampleslist[[1]]
  for(i in 2:length(sampleslist)) {
    samplesout <- cbind(samplesout,sampleslist[[i]])
  }
  write.csv(x=samplesout,file=file.choose())
}
if (F) {
  write.out.nba.samples(n.samples = 500)
}
