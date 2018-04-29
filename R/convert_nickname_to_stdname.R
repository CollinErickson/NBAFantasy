#' Convert names
#'
#' Converts from FanDuel nickname to my standardized name format.
#' Uses data//FD_DFN_name_conversion.csv for conversion from
#' Daily Fantasy Nerd names to FD names.
#' Our standardized version is all lower case,
#' punctuation and jr removed.
#'
#' @param nms vector of names
#'
#' @return vector of names in standard format
#' @export
convert.nickname.to.standard.name <- function(nms) {#browser()

  # Convert  Daily Fantasy Nerd names to FD names
  namedf <- read.csv("data//FD_DFN_name_conversion.csv", stringsAsFactors = F)
  DFN_to_FD <- namedf$FD.Nickname
  names(DFN_to_FD) <- namedf$DFN.Name
  nms <- sapply(nms, function(i) {if (i %in% namedf$DFN.Name) {DFN_to_FD[i]} else {i}})
  names(nms) <- NULL

  # Remove characters
  nms <- gsub("[.]","",nms)
  nms <- gsub("[']","",nms)
  nms <- gsub("[-]","",nms)
  # Lower case
  nms <- tolower(nms)
  # Remove II, III, and jr
  nms <- gsub(" ii","",nms)
  nms <- gsub(" iii","",nms)
  nms <- gsub(" jr","",nms)

  # Special names that mess it up
  nms[nms=="guillermo hernangomez"] <- "willy hernangomez"
  nms[nms=="vince hunter"] <- "vincent hunter"
  nms[nms=="moe harkless"] <- "maurice harkless"

  nms
}
