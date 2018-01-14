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
  nms <- gsub("[II]","",nms)
  nms <- gsub("[III]","",nms)
  nms <- gsub(" jr","",nms)

  nms
}
