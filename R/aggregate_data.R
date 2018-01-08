# This function gathers all Salary, Projections, or ? data into one big df.
# Each is stored in a separate .csv file, so this loops over them.
#' @param folder Name of folder. One of Salary, Projection, ?
#' @param datelow Begin date in format "YYYYMMDD".
#' @param datehigh End date in format "YYYYMMDD".
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
  } else if (folder=="Projections") {browser()
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
  } else if (folder=="Blank") {
    all_salary$Team <- toupper(all_salary$Team)
    all_salary$Opponent <- toupper(all_salary$Opponent)
    names(all_salary)[1] <- "FD.Id"
    names(all_salary)[c(3,5,4)] <- c("FD.First.Name", "FD.Last.Name", "FD.Nickname")
    all_salary$FD.Nickname.NoDot <- gsub("[.]","",all_salary$FD.Nickname)
  } else {stop("#328722")}
  all_salary
}
if (F) {
  sal <- put_all_fromdates_in_one_df("Salary", "20171128", "20171213")
  proj <- put_all_fromdates_in_one_df("Projections", "20171128", "20171213")
  blank <- put_all_fromdates_in_one_df("Blank", "20171128", "20171213")
  dplyr::left_join(blank, proj, by=c('FD.Nickname' = "DFN.Name", "Date")) %>% View
}

join_data <- function(nba, datelow, datehigh) {browser()
  if (!is.data.frame(nba)) {stop("nba not good #58209")}
  if (is.numeric(date)) {date <- as.character(date)}
  if (!is.character(datelow)  || nchar(datelow)!=8  || substr(datelow,1,3)!="201" ) {stop("date should be YYYYMMDD int or char")}
  if (!is.character(datehigh) || nchar(datehigh)!=8 || substr(datehigh,1,3)!="201") {stop("date should be YYYYMMDD int or char")}
  salary <- put_all_fromdates_in_one_df("Salary", datelow, datehigh) #read.csv(paste0("data//Salary//", date, ".csv"))
  projections <- put_all_fromdates_in_one_df("Projections", datelow, datehigh) #read.csv(paste0("data//Projections//", date, ".csv"))
  blank <- put_all_fromdates_in_one_df("Blank", datelow, datehigh) #read.csv(paste0("data//Blank//", date, ".csv"))
  nba$GAME_YYYMMDD <- sapply(nba$GAME_DATE_EST, function(gd) {paste0(substr(gd,1,4), substr(gd,6,7), substr(gd,9,10))})
  # nbadate <- nba[, nba$]
  nba$Date <- as.Date(nba$GAME_YYYMMDD, "%Y%m%d")

  # Now try to join them
  # blank_proj <- dplyr::full_join(blank, projections, by=c('FD.Nickname' = "DFN.Name", "Date"))
  # which(all_salary$FD.Nickname == "A.J. Hammons")
  # blank_proj <- dplyr::full_join(blank, projections, by=c('FD.Nickname' = "FD.Nickname", "Date"))
  blank_proj <- dplyr::full_join(blank, projections, by=c('FD.Nickname.NoDot' = "FD.Nickname.NoDot", "Date"))
  print("These show up in blank but not proj")
  print(blank_proj[is.na(blank_proj$DFN.Projection),] %>% .$FD.Nickname.NoDot %>% unique %>% sort)
  print("These show up in proj but not blank")
  print(blank_proj[is.na(blank_proj$Salary),] %>% .$FD.Nickname.NoDot %>% unique %>% sort)
  blank_proj_sal <- dplyr::full_join(blank_proj, salary, by=c('FD.Nickname.NoDot' = "FD.Nickname.NoDot", "Date"))

  nba_blank_proj_sal <- dplyr::full_join(nba, blank_proj_sal, by=c('PLAYER_NAME' = "FD.Nickname.NoDot", "Date"))

  return()
}
if (F) {
  join_data(nba, "20171128", "20171213")
}
