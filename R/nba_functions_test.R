year <- 2015
year_file_name <- paste0("data/Player/", year, ".csv")
ydf <- read.csv(year_file_name)
# ydf <- readr::read_csv(year_file_name)
# choose.files()
str(ydf)
View(ydf)

source('~/GitHub/NBAFantasy/R/nba_functions.R')
# nba <- convert.raw.nba("data\\Player\\2015.csv")
nba <- convert.raw.nba(year_file_name)
setdiff(colnames(nba), colnames(ydf))

sal <- read.csv("data\\FDSalaryNow_2_8_16.csv",stringsAsFactors=F)
res <- read.csv("data\\FDResults_2_8_16.csv",stringsAsFactors=F)
create.id.conversion.table(nba,sal)
FD.nba.conversion <- read.csv("data\\FD_nba_conversion.csv")
fit.LM.2(nba,sal,res)
