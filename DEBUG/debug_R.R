source("R_Codes/all_R_functions.R")

dat <- read.csv("db/psoriasis_wide_small.csv", header = T)


run_NetMeta(dat)

league_rank(dat)

