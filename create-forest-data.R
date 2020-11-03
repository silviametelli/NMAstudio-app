library(netmeta)
library(dplyr)
setwd("/Users/silvia/Desktop/Dash-Net2")

dat = read.csv("db/Senn2013.csv", header = T)
colnames(dat) = c("X","TE","seTE","t1","t2", "treat1", "treat2","studlab")
  
N.t=unique(c(dat$t1, dat$t2))
#forest plot data for each node-subnetwork
for(x in 1:N.t){
    subnet_temp = dat %>%
                  filter(dat$t1==x | dat$t2==x)
    NMAresults_temp = netmeta(
                              subnet_temp$TE, subnet_temp$seTE,
                              subnet_temp$t1,subnet_temp$t2,
                              subnet_temp$studlab,
                              comb.random=TRUE,
                              backtransf = TRUE,
                              reference.group = "Placebo"
                              )
}