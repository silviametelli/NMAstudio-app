options(warn=-1)
suppressMessages(library(netmeta))
suppressMessages(library(dplyr))

## forest plots with reference treatments
run_NetMeta <- function(dat){
       treatments <- c(dat$treat1, dat$treat2)
       treatments <- treatments[!duplicated(treatments)]
       ALL_DFs <- list()
       for (treatment in treatments){
              nma_temp <- netmeta(dat$TE, dat$seTE, dat$treat1, dat$treat2, dat$studlab,
                                         sm = "MD",
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

## league tables for two outcomes
league_table <- function(dat){
        nma_primary <- netmeta(TE=dat$TE, seTE=dat$seTE,
                               treat1=dat$treat1, treat2=dat$treat2,
                               studlab=dat$studlab,
                               sm = "MD",
                               comb.random = TRUE,
                               backtransf = TRUE,
                               reference.group = dat$treat2[1])
        nma_secondary <- netmeta(TE=dat$TE2, seTE=dat$seTE2,
                                 treat1=dat$treat1, treat2=dat$treat2,
                                 studlab=dat$studlab,
                                 sm = "MD",
                                 comb.random = TRUE,
                                 backtransf = TRUE,
                                 reference.group = dat$treat2[1])
        # - network estimates of first outcome in lower triangle
        # - network estimates of second outcome in upper triangle
        netleague_table <- netleague(nma_primary, nma_secondary, digits = 2,
                                     backtransf = TRUE, ci = FALSE)

        return(netleague_table$random)
}

