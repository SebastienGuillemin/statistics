suppressMessages(library(FactoMineR))
library(missMDA)
library(descriptr)
library(factoextra)
library(rjson)
library(readr)

maketitle <- function(drug_type, csv_path) {
  plot.new()
  title <- paste("AFMD for", drug_type, "dataset")
  des <- paste("The following pages present graphical results for FAMD\nperformed over ", drug_type, " dataset (", csv_path, ").", sep = "")
  
  text(.5 - .5 / nchar(title), .7, title, cex = 2.5)
  text(.5 - .5 / 54, .3, des, cex = 1.1)
}

## AFDM avec FactoMineR
perform_famd <- function(drug_type, csv_path, factors) {
  maketitle(drug_type = drug_type, csv_path = csv_path)
  
  print(paste("Chargement des donnnées pour", drug_type))
  # Import fichier csv.
  df <- read_csv(csv_path, show_col_types = FALSE)
  
  # Convertion colonne 'id' (première colonne) en nom de lignes
  df<-data.frame(df, row.names=1)
  
  # Transformation de certaines colonnes en factor.
  for (drug_factor in factors) {
    df[[drug_factor]]<-as.factor(df[[drug_factor]])
  }
  print(ds_screener(df))
  
  # Estimation du nombre de composantes pour AFDM
  # print("Estimation du nombre de composantes pour AFDM")
  # ncomp <- estim_ncpFAMD(df, ncp.max = 2)
  
  # Imputation des données manquantes
  print("Imputation des données manquantes.")
  imputed <- imputeFAMD(df)
  
  # Calcule FAMD sur les données imputées
  print("Calcule AFDM sur les données imputées.")
  res_famd <- FAMD(df, tab.disj=imputed$tab.disj, graph=FALSE)
  
  # Calcul de la variance associée à chaque valeur propre
  print("Calcul de la variance associée à chaque valeur propre.")
  print(fviz_screeplot(res_famd))
  
  # Affichage des résultats FAMD
  print("Affichage des résultats AFDM")
  # Cercles de corrélation des variables quantitatives
  print("    Cercle de corrélation des variables quantitatives (dim. 1 et 2).")
  print(fviz_famd_var(res_famd, "quanti.var",  col.var = "contrib", axes = c(1, 2), gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE))
  
  print("    Cercle de corrélation des variables quantitatives (dim. 1 et 3).")
  print(fviz_famd_var(res_famd, "quanti.var",  col.var = "contrib", axes = c(1, 3), gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE))
  
  # Affichage des variables qualitatives
  print("    Contributions des variables qualitatives.")
  print(fviz_famd_var(res_famd, "quali.var",  col.var = "contrib", axes = c(1, 2), gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE))
  
  
  # Graphique des individus de la FAMD
  #print("    Graphique des individus de la FAMD")
  #print(fviz_famd_ind(head(res_famd), axes = c(1, 2), repel=TRUE))
  
  # Couleur par valeurs cos2: qualité sur le plan des facteurs
  print("    Cercle de corrélation des variables quantitatives selon le cos2.")
  print(fviz_famd_var(res_famd, "quanti.var", col.var = "cos2", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE))
  
  print("AFMD terminée.\n\n")
}

pdf(file = "./results.pdf", paper = "a4")
json_file <- fromJSON(file = "parameters.json")
for (drug_type in json_file$drug_types) {
  csv_path <- paste(json_file$data_path, paste(drug_type, ".csv", sep = ""), sep = "")
  
  perform_famd(drug_type = drug_type, csv_path = csv_path, factors = json_file$factors[[drug_type]])
}

suppressMessages(dev.off())
