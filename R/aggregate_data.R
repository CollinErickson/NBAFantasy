# This file contains functions to load data from different sources
# (NBA results, DFN projections, FD salaries)
# and put them all into one big data.frame.
# Created 2017-18.

# Gather all Salary, Projections, and Blank to single df
#
# This function gathers all Salary, Projections, or ? data into one big df.
# Each is stored in a separate .csv file, so this loops over them.
#' @param folder Name of folder. One of Salary, Projection, ?
#' @param datelow Begin date in format "YYYYMMDD".
#' @param datehigh End date in format "YYYYMMDD".
#' @return data.frame with all data
put_all_fromdates_in_one_df <- function(folder, datelow, datehigh) {#browser()
  library(readr)
  if (nchar(datelow) != 8 || nchar(datehigh)!=8) {stop("date must have length 8 #982357")}
  datelowformat <- as.Date(datelow, format='%Y%m%d')
  datehighformat <- as.Date(datehigh, format='%Y%m%d')
  datei <- datelowformat
  all_salary <- NULL
  while (datei <= datehighformat) {
    filenamei <- paste0("data//",folder,"//", as.character.Date(datei, format="%Y%m%d"), ".csv")
    if (file.exists(filenamei)) {
      # salaryi <- read.csv(filenamei, colClasses=c(NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA))
      if (folder=="Salary") {
        salaryi <- readr::read_csv(filenamei, col_types = cols_only(`Player ID`="i", Position=col_character(), `First Name`=col_character(), `Last Name`=col_character(), Starter="i", FDPoints=col_double(), Salary="i",  Team=col_character(), Opponent=col_character(),  Home="i", `Team Score`="i", `Opponent Score`="i"))
      } else if (folder=="Projections") {
        salaryi <- readr::read_csv(filenamei, col_types = cols(`Player Name`=col_character(), `Predicted Point`=col_double()))
      } else if (folder=="Blank") {
        salaryi <- readr::read_csv(filenamei, col_types = cols_only(`Id`="i", Position=col_character(), `First Name`=col_character(), `Nickname`=col_character(), `Last Name`=col_character(), FPPG=col_double(), Played="i", Salary="i", Game=col_character(), Team=col_character(), Opponent=col_character(), `Injury Indicator`=col_character(), `Injury Details`=col_character()))
      } else {stop("#328721")}
      salaryi$Date <- datei
      if (is.null(all_salary)) {all_salary <- salaryi}
      else {all_salary <- rbind(all_salary, salaryi)}
    }
    datei <- datei + 1
  }
  if (folder=="Salary") {
    all_salary$Team <- toupper(all_salary$Team)
    all_salary$Opponent <- toupper(all_salary$Opponent)
    names(all_salary)[1] <- "FD.Id"
    names(all_salary)[c(3,4)] <- c("FD.First.Name", "FD.Last.Name")
    all_salary$FD.NamePaste <- paste(all_salary$FD.First.Name, all_salary$FD.Last.Name)
    all_salary$FD.Nickname.NoDot <- gsub("[.]","",all_salary$FD.NamePaste)
    # browser()
    all_salary$stdname <- convert.nickname.to.standard.name(all_salary$FD.NamePaste)
    all_salary$FD.First.Name <- NULL
    all_salary$FD.Last.Name <- NULL
    all_salary$FD.NamePaste <- NULL
  } else if (folder=="Projections") {#browser()
    names(all_salary)[c(1,2)] <- c("DFN.Name", "DFN.Projection")
    # Convert names to FD names
    namedf <- read.csv("data//FD_DFN_name_conversion.csv", stringsAsFactors = F)
    # DFN_to_FD <- all_salary$DFN.Name #namedf[,2]
    # names(DFN_to_FD) <- all_salary$DFN.Name #namedf[,1]
    DFN_to_FD <- namedf$FD.Nickname
    names(DFN_to_FD) <- namedf$DFN.Name
    all_salary$FD.Nickname <- sapply(all_salary$DFN.Name, function(i) {if (i %in% namedf$DFN.Name) {DFN_to_FD[i]} else {i}})
    all_salary$DFN.Name <- NULL
    all_salary$FD.Nickname.NoDot <- gsub("[.]","",all_salary$FD.Nickname)
    all_salary$stdname <- convert.nickname.to.standard.name(all_salary$FD.Nickname)
    # browser()
    all_salary$FD.Nickname <- NULL
    all_salary$FD.Nickname.NoDot <- NULL
  } else if (folder=="Blank") {
    all_salary$Team <- toupper(all_salary$Team)
    all_salary$Opponent <- toupper(all_salary$Opponent)
    names(all_salary)[1] <- "FD.Id"
    names(all_salary)[c(3,5,4)] <- c("FD.First.Name", "FD.Last.Name", "FD.Nickname")
    all_salary$FD.Nickname.NoDot <- gsub("[.]","",all_salary$FD.Nickname)
    all_salary$stdname <- convert.nickname.to.standard.name(all_salary$FD.Nickname)
    # browser()
    all_salary$FD.First.Name <- NULL
    all_salary$FD.Last.Name <- NULL
    all_salary$FD.Nickname <- NULL
    all_salary$FD.Nickname.NoDot <- NULL
    all_salary$Team <- convert.teamname.to.stdteamname(all_salary$Team)
    all_salary$Opponent <- convert.teamname.to.stdteamname(all_salary$Opponent)
    # Convert Injury Indicators that are NA to "None"
    all_salary$`Injury Indicator`[is.na(all_salary$`Injury Indicator`)] <- "None"
  } else {stop("#328722")}
  all_salary
}
if (F) {
  sal <- put_all_fromdates_in_one_df("Salary", "20171128", "20171213")
  proj <- put_all_fromdates_in_one_df("Projections", "20171128", "20171213")
  blank <- put_all_fromdates_in_one_df("Blank", "20171128", "20171213")
  dplyr::left_join(blank, proj, by=c('FD.Nickname' = "DFN.Name", "Date")) %>% View
}


#' Join data from nba, salary, projections, and blank into one big table
#'
#' @param nba Table of players sheet
#' @param datelow Start date for date range
#' @param datehigh End date for date range
#'
#' @return Big table
#' @export
#'
#' @examples
#' #
join_data <- function(nba, datelow, datehigh) {
  # Make sure dates are in correct format
  if (!is.data.frame(nba)) {stop("nba not good #58209")}
  if (is.numeric(date)) {date <- as.character(date)}
  if (!is.character(datelow)  || nchar(datelow)!=8  || substr(datelow,1,3)!="201" ) {stop("date should be YYYYMMDD int or char")}
  if (!is.character(datehigh) || nchar(datehigh)!=8 || substr(datehigh,1,3)!="201") {stop("date should be YYYYMMDD int or char")}

  # Gather data for date ranges
  salary <- put_all_fromdates_in_one_df("Salary", datelow, datehigh) #read.csv(paste0("data//Salary//", date, ".csv"))
  projections <- put_all_fromdates_in_one_df("Projections", datelow, datehigh) #read.csv(paste0("data//Projections//", date, ".csv"))
  blank <- put_all_fromdates_in_one_df("Blank", datelow, datehigh) #read.csv(paste0("data//Blank//", date, ".csv"))

  # Add date to nba, only keep entries in date range
  # nba$GAME_YYYMMDD <- sapply(nba$GAME_DATE_EST, function(gd) {paste0(substr(gd,1,4), substr(gd,6,7), substr(gd,9,10))})
  # nba$Date <- as.Date(nba$GAME_YYYMMDD, "%Y%m%d")
  nba <- nba[nba$Date >=as.Date(datelow, format='%Y%m%d') & nba$Date <= as.Date(datehigh, format='%Y%m%d'),]
  nba$PLAYER_NAME.NoDot <- gsub("[.]","",nba$PLAYER_NAME)
  # nba$stdname <- convert.nickname.to.standard.name(nba$PLAYER_NAME)

  # Keep track of which ones they were in
  salary$in.salary <- TRUE
  projections$in.projections <- TRUE
  blank$in.blank <- TRUE
  nba$in.nba <- TRUE

  # Now try to join them
  # blank_proj <- dplyr::full_join(blank, projections, by=c('FD.Nickname' = "DFN.Name", "Date"))
  # which(all_salary$FD.Nickname == "A.J. Hammons")
  # blank_proj <- dplyr::full_join(blank, projections, by=c('FD.Nickname' = "FD.Nickname", "Date"))
  blank_proj <- dplyr::full_join(blank, projections, by=c('stdname', "Date"))

  print("These show up in blank but not proj, consider checking them")
  # print(blank_proj[is.na(blank_proj$DFN.Projection),] %>% .$stdname %>% unique %>% sort)
  print(blank_proj[is.na(blank_proj$DFN.Projection),][,c("stdname", "Date")])
  # print("These show up in proj but not blank")
  # print(blank_proj[is.na(blank_proj$Salary),] %>% .$stdname %>% unique %>% sort)
  print(paste(nrow(blank_proj[is.na(blank_proj$Salary),]), "show up in proj but not in blank, can ignore"))
  blank_proj_sal <- dplyr::full_join(blank_proj, salary, by=c('stdname', "Date"))

  # Fix duplicates
  # salary and blank both have FD.Id, Position, make sure all match, then remove one column and rename other
  if (any(blank_proj_sal$FD.Id.x != blank_proj_sal$FD.Id.y, na.rm = T)) {browser(); warning("Not all FD.id's match #8237")}
  blank_proj_sal$FD.Id.y <- NULL
  names(blank_proj_sal)[names(blank_proj_sal) == 'FD.Id.x'] <- 'FD.Id'
  if (any(blank_proj_sal$Position.x != blank_proj_sal$Position.y, na.rm = T)) {
    # browser();
    warning("Not all Positions match #8237")
    print("Positions that don't match are as follows, going to ignore and assume not an issue, use Position.x")
    print(blank_proj_sal[sapply(blank_proj_sal$Position.x != blank_proj_sal$Position.y, isTRUE),][,c('stdname', 'Date', 'Position.x', 'Position.y')])
  }
  blank_proj_sal$Position.y <- NULL
  names(blank_proj_sal)[names(blank_proj_sal) == 'Position.x'] <- 'Position'
  if (any(blank_proj_sal$Salary.x != blank_proj_sal$Salary.y, na.rm = T)) {
    warning("Not all Salarys match #8237")
    print("Salaries that don't match are as follows, going to ignore and assume Salary.x is correct")
    print(blank_proj_sal[sapply(blank_proj_sal$Salary.x != blank_proj_sal$Salary.y, isTRUE),][,c('stdname', 'Date', 'Salary.x', 'Salary.y')])
  }
  blank_proj_sal$Salary.y <- NULL
  names(blank_proj_sal)[names(blank_proj_sal) == 'Salary.x'] <- 'Salary'
  if (any(blank_proj_sal$Team.x != blank_proj_sal$Team.y, na.rm = T)) {browser(); warning("Not all Teams match #8237")}
  blank_proj_sal$Team.y <- NULL
  names(blank_proj_sal)[names(blank_proj_sal) == 'Team.x'] <- 'Team'
  if (any(blank_proj_sal$Opponent.x != blank_proj_sal$Opponent.y, na.rm = T)) {browser(); warning("Not all Opponents match #8237")}
  blank_proj_sal$Opponents.y <- NULL
  names(blank_proj_sal)[names(blank_proj_sal) == 'Opponent.x'] <- 'Opponent'

  # Join these with nba
  nba_blank_proj_sal <- dplyr::full_join(nba, blank_proj_sal, by=c('stdname', "Date"))
  # Track which has which values
  #   First set NA for in.<name> to FALSE
  nba_blank_proj_sal$in.blank[is.na(nba_blank_proj_sal$in.blank)] <- FALSE
  nba_blank_proj_sal$in.projections[is.na(nba_blank_proj_sal$in.projections)] <- FALSE
  nba_blank_proj_sal$in.salary[is.na(nba_blank_proj_sal$in.salary)] <- FALSE
  nba_blank_proj_sal$in.nba[is.na(nba_blank_proj_sal$in.nba)] <- FALSE
  #   Set in.spbn to be four characters showing which each row came from, dash indicates missing
  nba_blank_proj_sal$in.spbn <- sapply(1:nrow(nba_blank_proj_sal), function(i) {paste0(if (isTRUE(nba_blank_proj_sal$in.salary[i])) "S" else "-", if (isTRUE(nba_blank_proj_sal$in.projections[i])) "P" else "-", if (isTRUE(nba_blank_proj_sal$in.blank[i])) "B" else "-", if (isTRUE(nba_blank_proj_sal$in.nba[i])) "N" else "-")})
  # Print to see where data came from
  print(table(nba_blank_proj_sal$in.spbn))
  # To see where rows are
  # print(c(nrow(nba), nrow(blank_proj_sal), nrow(nba) + nrow(blank_proj_sal), nrow(nba_blank_proj_sal), nrow(nba) + nrow(blank_proj_sal) - nrow(nba_blank_proj_sal)))
  # print("These show up in bpj but not nba")
  # print(nba_blank_proj_sal[is.na(nba_blank_proj_sal$in.nba),] %>% .$stdname %>% unique %>% sort)
  # print("These show up in nba but not bpj, should be 23")
  # print(nba_blank_proj_sal[is.na(nba_blank_proj_sal$stdname),] %>% .$stdname %>% unique %>% sort)

  print("These players show up in nba but not blank_proj_sal")
  # print(dplyr::anti_join(nba, blank_proj_sal, by=c('stdname', "Date"))$stdname)
  print(nba_blank_proj_sal[nba_blank_proj_sal$in.spbn=="---N",][,c("stdname", "Date")])

  # Fix things that are NA after join
  nba_blank_proj_sal$`In`

  # Plot shows distribution of data for players in groups
  #   Should see that players not in nba don't score points/play in game
  boxplot(FDPoints ~ in.spbn, data=nba_blank_proj_sal)
  # print("Here is table of which players show up in which tables")
  # nba_blank_proj_sal$in.spbn %>% table

  # Return big table
  return(nba_blank_proj_sal)
}
if (F) {
  year <- 2017
  year_file_name <- paste0("data/Player/", year, ".csv")
  ydf <- read.csv(year_file_name)
  source('~/GitHub/NBAFantasy/R/nba_functions.R')
  source('~/GitHub/NBAFantasy/R/convert_nickname_to_stdname.R')
  source('~/GitHub/NBAFantasy/R/convert_teamname_to_stdteamname.R')
  nba <- convert.raw.nba(year_file_name)
  # join_data(nba, "20171128", "20171213")
  df1 <- join_data(nba, "20171128", "20171213")
}
