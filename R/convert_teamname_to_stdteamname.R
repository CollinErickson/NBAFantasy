#' Convert NBA team name to my standard format
#'
#' Some times have variant abbreviations that need to be fixed.
#'
#' @param tms Vector of char team names to be standardized
#'
#' @return vector of char with standardized team names
#' @export
#'
#' @examples
#' convert.teamname.to.stdteamname(c("BOS", "CLE", "NO", "GS"))
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
