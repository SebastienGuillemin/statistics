library(FactoMineR)
library(dplyr)
library(missMDA)
library(mice)
library(VIM)
library(descriptr)
library(factoextra)

pdf(file = "./results.pdf")

## AFDM avec FactoMineR
# Import fichier csv.
cana<-cannabis

# Convertion colonne 'id' (première colonne) en nom de lignes
cana<-data.frame(cana, row.names=1)

# Copie du dataframe cana pour garder les données de départ.
df <- cana
# Transformation de certaines colonnes en factor.
df$abime<-as.factor(df$abime)
df$etiquette<-as.factor(df$etiquette)
df$presentation<-as.factor(df$presentation)
df$visqueux<-as.factor(df$visqueux)
ds_screener(df)

# Imputation des données manquantes
# Estimation du nombre de composantes pour AFDM
ncomp <- estim_ncpFAMD(df, ncp.max=2, maxiter=100)

# Imputation des données manquantes
imputed <- imputeFAMD(df, ncp=ncomp$ncp)
ds_screener(df)

# Calcule FAMD sur les données imputées 
res_famd <- FAMD(df, tab.disj=imputed$tab.disj, graph=FALSE)

# Récupération des valeurs propres
eig.val <- get_eigenvalue(res_famd)
head(eig.val)
fviz_screeplot(res_famd)
# vars <- get_famd_var(res_famd)

## Affichage des résultats FAMD
par(mfrow=c(1,1))
# Cercle de corrélation des variables quantitatives
fviz_famd_var(res_famd, "quanti.var",  col.var = "contrib", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE)

# Affichage des variables qualitatives
fviz_famd_var(res_famd, "quali.var",  col.var = "contrib", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE)


# Graphique des individus de la FAMD
# fviz_famd_ind(res_famd, repel=TRUE)

# Couleur par valeurs cos2: qualité sur le plan des facteurs
fviz_famd_var(res_famd, "quanti.var", col.var = "cos2", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE)
dev.off()
