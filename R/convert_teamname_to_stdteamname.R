convert.teamname.to.stdteamname <- function(tms) {
  # These names need to be fixed
  tms[tms=="NO"] <- "NOR"
  tms[tms=="NOP"] <- "NOR"
  tms[tms=="NY"] <- "NYK"
  tms[tms=="GS"] <- "GSW"
  tms[tms=="SA"] <- "SAS"
  tms[tms=="PHX"] <- "PHO"
  # Could also make sure upper case?
  tms
}
