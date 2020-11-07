library(netmeta)
library(dplyr)
setwd("/Users/silvia/Desktop/Dash-Net2")

dat = read.csv("db/Senn2013.csv", header = T)
colnames(dat) = c("X","TE","seTE","t1","t2","studlab")
ref="Placebo" ## else pass a dataset with a 'reference' column
N.t=unique(c(dat$t1, dat$t2))


# subnet_temp = dat %>%
#               filter(dat$t1==x | dat$t2==x)

for(x in N.t){
    NMAresults = netmeta(
                              dat$TE,dat$seTE,
                              dat$t1,dat$t2,
                              dat$studlab,
                              comb.random=TRUE,
                              backtransf = TRUE,
                              reference.group = x
                              )
    cl1 = NMAresults$treat1.pos # class positions
    cl2 = NMAresults$treat2.pos
    y.m = NMAresults$TE
    nt  = NMAresults$n # number of treatments 
    
    treatment_list = NMAresults$trts[NMAresults$trts!=x] 
    b =  NMAresults$TE.random[, x]
    b_names = names(b)[sapply(b, is.numeric)]
    b = b[which(b_names!=x)]
    se = NMAresults$seTE.random[, x] 
    se = se[which(b_names!=x)]
    bweights = 1/NMAresults$seTE.random[, x]/1.5 # weights propto precision
    bweights = bweights[which(b_names!=x)]
    ci_lo = b-1.96*se
    ci_up = b+1.96*se
    df = data.frame(treatment_list, round(b,3), round(ci_lo,3), round(ci_up,2), round(bweights,3))
    colnames(df) = c("Treatment", "MD", "CI_lower", "CI_upper", "WEIGHT")
    write.csv(df, paste0("db/forest_data/", x,".csv"), row.names=F)
    
}

