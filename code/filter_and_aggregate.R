list.of.packages <- c("data.table", "stringr")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only=T)

setwd("~/git/NABU-Conservation/")

# Load data
crs = fread("large_input/crs_au.csv")

# Subset to possibly relevant purpose codes
bio = subset(crs,
             purpose_code %in% c("41030", "41040"))
sum(bio$usd_disbursement_deflated, na.rm=T)
possible_bio = subset(crs,
             purpose_code %in% c("41010", "41020"))

# Keyword search possible
quotemeta <- function(string) {
  str_replace_all(string, "(\\W)", "\\\\\\1")
}

remove_punct = function(string){
  str_replace_all(string, "[[:punct:]]", " ")
}

collapse_whitespace = function(string){
  str_replace_all(string, "\\s+", " ")
}

keyword_df = fread("input/keywords.csv")
keywords = unique(quotemeta(trimws(collapse_whitespace(remove_punct(tolower(keyword_df$keyword))))))
keyword_regex = paste0(
  "\\b",
  paste(keywords, collapse="\\b|\\b"),
  "\\b"
)
possible_bio$text = paste(
  possible_bio$project_title,
  possible_bio$short_description,
  possible_bio$long_description
)
possible_bio$text = trimws(collapse_whitespace(remove_punct(tolower(possible_bio$text))))
possible_bio$match = grepl(keyword_regex, possible_bio$text, perl=T, ignore.case = T)
mean(possible_bio$match)
possible_bio_match = subset(possible_bio, match)
possible_bio_match[,c("text", "match")] = NULL

# Row bind
bio = rbind(bio, possible_bio_match)
sum(bio$usd_disbursement_deflated, na.rm=T)

# Write
fwrite(bio, "output/crs_au_biodiversity_conservation.csv")

