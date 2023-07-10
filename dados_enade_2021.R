lista<-list.files("microdados_Enade_2021_LGPD/2.DADOS/")
d<-read.csv2(paste0("microdados_Enade_2021_LGPD/2.DADOS/",lista[43]))


for (i in 1:42) {
  x <- read.csv2(paste0("microdados_Enade_2021_LGPD/2.DADOS/",lista[i]))
  d <- cbind(d,x)
}
names(d)
duplicated_names <- duplicated(colnames(d))
d<-d[!duplicated_names]

library(tidyverse)

write_csv(d, "DADOS_ENADE_2021.csv")
