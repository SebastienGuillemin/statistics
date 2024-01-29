library(PCAmixdata)
library("FactoMineR")
library(tidyverse)
library(dplyr)
library(missMDA)
library(mice)
library(VIM)


# Multivariate analysis with mix data : https://chavent.github.io/PCAmixdata/

# Importer fichier csv.
cana<-cannabis

# Convertir colonne id en nom de lignes
cana<-data.frame(cana,row.names=1)
str(cana)

cana.df1<-cana[,1:10]
cana.df2<-cana[,1:12]



# Avec les données
split <- splitmix(cana.df1)
X1 <- split$X.quanti 
X2 <- split$X.quali

res.pcamix <- PCAmix(X.quanti=X1, X.quali=X2,rename.level=TRUE,
                     graph=FALSE)
res.pcamix$eig

par(mfrow=c(2,2))
plot(res.pcamix,choice="ind",label=FALSE, main="Observations")
plot(res.pcamix,choice="levels",xlim=c(-1.5,2.5), main="Levels")
plot(res.pcamix,choice="cor",main="Numerical variables")
plot(res.pcamix,choice="sqload",coloring.var=T, leg=FALSE,
     posleg="topright", main="All variables")

par(mfrow=c(1,1))
plot(res.pcamix,choice="ind",label=TRUE, cex=0.8, main="Observations")

splitb <- splitmix(cana.df1[,1:9])
X1b <- splitb$X.quanti 
X2b <- splitb$X.quali
X.quanti.sup <-cana.df1[,1]
X.quali.sup <-cana.df1[,9,drop=FALSE]
pca<-PCAmix(X.quanti=X1b, X.quali=X2b,ndim=4,graph=FALSE)
pca2 <- supvar(pca,X.quanti.sup,X.quali.sup)
plot(pca2,choice="levels")
plot(pca2,choice="cor")
plot(pca2,choice="sqload")
plot(pca2,choice="ind",label=TRUE, cex=0.8, main="Observations")

par(mfrow=c(2,2))
plot(pca2,choice="ind",label=FALSE, main="Observations")
plot(pca2,choice="levels",xlim=c(-1.5,2.5), main="Levels")
plot(pca2,choice="cor",main="Numerical variables")
plot(pca2,choice="sqload",coloring.var=T, leg=FALSE,
     posleg="topright", main="All variables")

##
# AFDM avec FactoMineR

# subset the rows of dataframe with multiple conditions
df = cana[,1:10]
str(df)
df1<-df[,-9]

# res.famd <- FAMD(df1, graph = FALSE)


# https://delladata.fr/imputation-donnees-manquantes-missmda/

cana.df1$etiquette<-as.factor(cana.df1$etiquette)
cana.df1$presentation<-as.factor(cana.df1$presentation)
str(cana.df1)
ncomp <- estim_ncpFAMD(cana.df1)
res.impute <- imputeFAMD(cana.df1, ncp=ncomp$ncp)
res.comp <- MIFAMD(cana.df1, ncp = ncomp$ncp, nboot = 100)
head(res.comp$res.MI[[1]])
plot(res.comp)
# long avec nboot = 1000

## The output can be used as an input of the FAMD function of the FactoMineR package 
##to perform the FAMD on the incomplete data ozone 
res.famd <- FAMD(cana.df1,
                 tab.disj=res.impute$tab.disj,graph=FALSE)

# res.famd <- FAMD(cana.df1[,c(1:8)],sup.var=c(9),
#                 tab.disj=res.impute$tab.disj,graph=FALSE)

#res.famd <- FAMD(cana.df1[,c(1:9)],sup.var=c(1))
print(res.famd)

library("factoextra")
eig.val <- get_eigenvalue(res.famd)
head(eig.val)
fviz_screeplot(res.famd)
var <- get_famd_var(res.famd)

# Graphique des variables
fviz_famd_var(res.famd, repel = TRUE)
quanti.var <- get_famd_var(res.famd, "quanti.var")
fviz_famd_var(res.famd, "quanti.var", col.var = "contrib", 
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
              repel = TRUE)

# Couleur par valeurs cos2: qualité sur le plan des facteurs
fviz_famd_var(res.famd, "quanti.var", col.var = "cos2",
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), 
              repel = TRUE)

fviz_famd_var(res.famd, "quanti.var", col.var = "cos2", axes=c(2,3),
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), 
              repel = TRUE)

quali.var <- get_famd_var(res.famd, "quali.var")
fviz_famd_var(res.famd, "quali.var", col.var = "contrib", 
              gradient.cols = "jco")

fviz_famd_var(res.famd, "quali.var", col.var = "cos2", 
              gradient.cols = "jco",col.var.sup = "black")

fviz_famd_var(res.famd, "quali.var", col.var = "cos2", axes = c(1, 3),
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"))

fviz_famd_var(res.famd, "quali.var", col.var = "cos2", 
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),sup.var="black")


ind <- get_famd_ind(res.famd)

fviz_famd_ind(res.famd, col.ind = "cos2", 
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
              labels = FALSE)

fviz_mfa_ind(res.famd, 
             habillage = "presentation", # color by groups 
             palette = "jco",
             addEllipses = TRUE, ellipse.type = "confidence", 
             labels = FALSE
)

fviz_mfa_ind(res.famd, 
             habillage = "presentation", # color by groups 
             palette = "jco",
             addEllipses = TRUE, ellipse.type = "confidence", 
             repel = TRUE # Avoid text overlapping
)

# Avec package mice
# https://datascienceplus.com/imputing-missing-data-with-r-mice-package/

par(mfrow=c(1,1))
md.pattern(cana.df1)

aggr_plot <- aggr(cana.df1, col=c('navyblue','red'), numbers=TRUE, 
                  sortVars=TRUE, labels=names(data), 
                  cex.axis=.5, gap=1, 
                  ylab=c("Histogram of missing data","Pattern"))
marginplot(cana.df1[c(1,2)])

tempData <- mice(cana.df1,m=14,maxit=50,meth='pmm',seed=500)
# methods(mice) pour obtenir la liste des méthodes d'imputation disponibles
summary(tempData)
completedData <- complete(tempData,1)
densityplot(tempData)

res.famd <- FAMD(completedData,graph=FALSE)
eig.val <- get_eigenvalue(res.famd)
head(eig.val)
fviz_screeplot(res.famd)
var <- get_famd_var(res.famd)

# Graphique des variables
fviz_famd_var(res.famd, repel = TRUE)
quanti.var <- get_famd_var(res.famd, "quanti.var")
fviz_famd_var(res.famd, "quanti.var", col.var = "contrib", 
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
              repel = TRUE)

# Couleur par valeurs cos2: qualité sur le plan des facteurs
fviz_famd_var(res.famd, "quanti.var", col.var = "cos2",
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"), 
              repel = TRUE)

quali.var <- get_famd_var(res.famd, "quali.var")
fviz_famd_var(res.famd, "quali.var", col.var = "contrib", 
              gradient.cols = "jco")

fviz_famd_var(res.famd, "quali.var", col.var = "cos2", 
              gradient.cols = "jco",col.var.sup = "black")

fviz_famd_var(res.famd, "quali.var", col.var = "cos2", axes = c(1, 3),
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"))

fviz_famd_var(res.famd, "quali.var", col.var = "cos2", 
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),sup.var="black")


ind <- get_famd_ind(res.famd)

fviz_famd_ind(res.famd, col.ind = "cos2", 
              gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
              labels = FALSE)

fviz_mfa_ind(res.famd, 
             habillage = "presentation", # color by groups 
             palette = "jco",
             addEllipses = TRUE, ellipse.type = "confidence", 
             labels = FALSE
)
