convert.teamname.to.stdteamname <- function(tms) {
  # These names need to be fixed
  tms[tms=="NO"] <- "NOR"
  tms[tms=="NY"] <- "NYK"
  tms[tms=="GS"] <- "GSW"
  tms[tms=="SA"] <- "SAS"
  # Could also make sure upper case?
  tms
}
