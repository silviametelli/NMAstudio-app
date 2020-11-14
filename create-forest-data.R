options(warn=-1)
suppressMessages(library(netmeta))
suppressMessages(library(dplyr))


run_NetMeta <- function(dat){
       treatments <- c(dat$treat1, dat$treat2)
       treatments <- treatments[!duplicated(treatments)]
       ALL_DFs <- list()
       for (treatment in treatments){
              nma_temp <- netmeta(dat$TE, dat$seTE, dat$treat1, dat$treat2, dat$studlab,
                                         comb.random = TRUE,
                                         backtransf = TRUE,
                                         reference.group = treatment)
              ### Design Matrix
              treatment_list <- nma_temp$trts[nma_temp$trts!=treatment]
              TE <-  nma_temp$TE.random[, treatment]
              TE_names <- names(TE)[sapply(TE, is.numeric)]
              TE <- TE[which(TE_names!=treatment)]
              se <- nma_temp$seTE.random[, treatment]
              se <- se[which(TE_names!=treatment)]
              ci_lo <- TE-1.96*se
              ci_up <- TE+1.96*se
              TEweights <- 1/nma_temp$seTE.random[, treatment] # Precision
              TEweights <- TEweights[which(TE_names!=treatment)]

              df <- data.frame(treatment_list, TE, ci_lo, ci_up, TEweights)
              colnames(df) <- c("Treatment", "MD", "CI_lower", "CI_upper", "WEIGHT")
              df['Reference'] <- treatment
              ALL_DFs[[treatment]] <- df
       }
       ALL_DFs <- do.call('rbind', ALL_DFs)
       return(ALL_DFs)
}


