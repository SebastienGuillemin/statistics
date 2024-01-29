library("FactoMineR")
library(dplyr)
library(missMDA)
library(mice)
library(VIM)
library(descriptr)
library("factoextra")

## AFDM avec FactoMineR
# Import fichier csv.
cana<-cannabis

# Convertion colonne 'id' (première colonne) en nom de lignes
cana<-data.frame(cana,row.names=1)

# Copie du dataframe cana pour garder les données de départ.
df <- cana
# Transformation de certaines colonnes en factor.
df$abime<-as.factor(df$abime)
df$etiquette<-as.factor(df$etiquette)
df$presentation<-as.factor(df$presentation)
df$visqueux<-as.factor(df$visqueux)
ds_screener(df)

# Imputation des données manquantes
# https://delladata.fr/imputation-donnees-manquantes-missmda/
ncomp <- estim_ncpFAMD(df, ncp.max=2)
res.impute <- imputeFAMD(df, ncp=ncomp$ncp)
res.comp <- MIFAMD(df, ncp = ncomp$ncp, nboot = 100)
head(res.comp$res.MI[[1]])

# FAMD appliquée aux données imputées 
res.famd <- FAMD(df, tab.disj=res.impute$tab.disj,graph=TRUE)
print(res.famd)

# Récupération des valeurs propres
eig.val <- get_eigenvalue(res.famd)
head(eig.val)
fviz_screeplot(res.famd)
var <- get_famd_var(res.famd)

# Graphique des variables
fviz_famd_ind(res.famd, repel = TRUE)
# quanti.var <- get_famd_var(res.famd, "quanti.var")
# fviz_famd_var(res.famd, "quanti.var", col.var = "contrib", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE)

# Couleur par valeurs cos2: qualité sur le plan des facteurs
# fviz_famd_var(res.famd, "quanti.var", col.var = "cos2", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE)

# fviz_famd_var(res.famd, "quanti.var", col.var = "cos2", axes=c(2,3), gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE)

# quali.var <- get_famd_var(res.famd, "quali.var")
# fviz_famd_var(res.famd, "quali.var", col.var = "contrib", gradient.cols = "jco")

# fviz_famd_var(res.famd, "quali.var", col.var = "cos2", gradient.cols = "jco",col.var.sup = "black")

# fviz_famd_var(res.famd, "quali.var", col.var = "cos2", axes = c(1, 3), gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"))

# fviz_famd_var(res.famd, "quali.var", col.var = "cos2", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),sup.var="black")


# ind <- get_famd_ind(res.famd)

# fviz_famd_ind(res.famd, col.ind = "cos2", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), labels = FALSE)

# fviz_mfa_ind(res.famd, 
#              habillage = "presentation", # color by groups 
#              palette = "jco",
#              addEllipses = TRUE, ellipse.type = "confidence", 
#              labels = FALSE
# )

# fviz_mfa_ind(res.famd, 
#             habillage = "presentation", # color by groups 
#             palette = "jco",
#             addEllipses = TRUE, ellipse.type = "confidence", 
#             repel = TRUE # Avoid text overlapping
# )

# Avec package mice
# https://datascienceplus.com/imputing-missing-data-with-r-mice-package/

# par(mfrow=c(1,1))
# md.pattern(cana.df1)

# aggr_plot <- aggr(cana.df1, col=c('navyblue','red'), numbers=TRUE, 
#                   sortVars=TRUE, labels=names(data), 
#                   cex.axis=.5, gap=1, 
#                   ylab=c("Histogram of missing data","Pattern"))
# marginplot(cana.df1[c(1,2)])

# tempData <- mice(cana.df1,m=14,maxit=50,meth='pmm',seed=500)
# methods(mice) pour obtenir la liste des méthodes d'imputation disponibles
# summary(tempData)
# completedData <- complete(tempData,1)
# densityplot(tempData)

# res.famd <- FAMD(completedData,graph=FALSE)
# eig.val <- get_eigenvalue(res.famd)
# head(eig.val)
# fviz_screeplot(res.famd)
# var <- get_famd_var(res.famd)

# Graphique des variables
# fviz_famd_var(res.famd, repel = TRUE)
# quanti.var <- get_famd_var(res.famd, "quanti.var")
# fviz_famd_var(res.famd, "quanti.var", col.var = "contrib", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE)

# Couleur par valeurs cos2: qualité sur le plan des facteurs
# fviz_famd_var(res.famd, "quanti.var", col.var = "cos2", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), repel = TRUE)

# quali.var <- get_famd_var(res.famd, "quali.var")
# fviz_famd_var(res.famd, "quali.var", col.var = "contrib", gradient.cols = "jco")

# fviz_famd_var(res.famd, "quali.var", col.var = "cos2", gradient.cols = "jco",col.var.sup = "black")

# fviz_famd_var(res.famd, "quali.var", col.var = "cos2", axes = c(1, 3), gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"))

# fviz_famd_var(res.famd, "quali.var", col.var = "cos2", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),sup.var="black")


# ind <- get_famd_ind(res.famd)

# fviz_famd_ind(res.famd, col.ind = "cos2", gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), labels = FALSE)

# fviz_mfa_ind(res.famd, 
#              habillage = "presentation", # color by groups 
#              palette = "jco",
#              addEllipses = TRUE, ellipse.type = "confidence", 
#              labels = FALSE
# )