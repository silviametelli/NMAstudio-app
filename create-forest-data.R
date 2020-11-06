library(netmeta)
library(dplyr)
setwd("/Users/silvia/Desktop/Dash-Net2")

dat = read.csv("db/Senn2013.csv", header = T)
colnames(dat) = c("X","TE","seTE","t1","t2","studlab")
ref="Placebo" ## else pass a dataset with a 'reference' column
N.t=unique(c(dat$t1, dat$t2))

for(x in N.t){
   # subnet_temp = dat %>%
   #               filter(dat$t1==x | dat$t2==x)
    NMAresults_temp = netmeta(
                              dat$TE,dat$seTE,
                              dat$t1,dat$t2,
                              dat$studlab,
                              comb.random=TRUE,
                              backtransf = TRUE,
                              reference.group = x
                              )
    cl1 = NMAresults_temp$treat1.pos # class positions
    cl2 = NMAresults_temp$treat2.pos
    y.m = NMAresults_temp$TE
    nt  = NMAresults_temp$n # number of treatments 
    
    ### design matrix
    treatment_list = NMAresults_temp$trts[NMAresults_temp$trts!=x] 
    b =  NMAresults_temp$TE.random[, x]
    b_names = names(b)[sapply(b, is.numeric)]
    b = b[which(b_names!=x)]
    se = NMAresults_temp$seTE.random[, x] 
    se = se[which(b_names!=x)]
    bweights = 1/NMAresults_temp$seTE.random[, x] #precision
    bweights = bweights[which(b_names!=x)]
    ci_lo = b-1.96*se
    ci_up = b+1.96*se
    id=seq(0,(length(treatment_list)-1))
    df = data.frame(id,treatment_list, b, ci_lo, ci_up, bweights)
    colnames(df) = c("index", "Treatment", "MD", "CI_lower", "CI_upper", "WEIGHTS")
    #write.table(df, file=sprintf(“db/forest_data/%s.csv”,x), sep=”,” , row.names=FALSE)
    write.csv(df, paste0("db/forest_data/", x,".csv"), row.names=F)
    
}