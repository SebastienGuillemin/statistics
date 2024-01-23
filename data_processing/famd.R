library(missMDA)
library(naniar)
library(visdat)
library(descriptr)
library(FactoMineR)

options(ggrepel.max.overlaps = Inf)

drug_type <- commandArgs(trailingOnly = TRUE)
data_path <- "~/Documents/these/code/clustering/data"
pdf_path <- paste(data_path, "missing_data.pdf", sep="/")
csv_path <- paste(data_path, paste(drug_type, ".csv", sep=""), sep="/")

csv <- read.csv(csv_path)
csv[csv == ""] <- NA

boolean_cols <- c("abime", "etiquette", "logo", "visqueux")
factor_cols <- c("type_drogue", "forme", "presentation", "couleur")

# Drop id column
csv = csv[-1]
#csv = csv[c(1:2000),]
csv[boolean_cols] <- lapply(csv[boolean_cols] , as.logical)
csv[factor_cols] <- lapply(csv[factor_cols] , factor)

ds_screener(csv)

pdf(pdf_path)
print(gg_miss_var(csv))
print(vis_miss(csv))

csv <- imputeFAMD(csv)

ds_screener(csv)

res <- FAMD(csv)
print(res)
