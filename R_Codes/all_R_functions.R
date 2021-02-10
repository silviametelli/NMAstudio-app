options(warn=-1)
suppressMessages(library(netmeta))
suppressMessages(library(dplyr))
suppressMessages(library(meta))
suppressMessages(library(metafor))
suppressMessages(library(tidyverse))

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
              ### Values
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

## pairwise forest plots for all different comparisons in df
## sorted_dat: dat sorted by treatemnt comparison
pairwise_forest <- function(dat){

  DFs_pairwise <- list()
  dat %>% arrange(dat, treat1, treat2)
  dat$ID <- dat %>% group_indices(treat1, treat2)

  for (id in dat$ID){
    dat_temp <- dat[which(dat$ID==id), ]
    model_temp = metagen(TE=TE,seTE=sqrt(seTE), studlab = studlab, data=dat_temp,
                         comb.random = T, sm="MD")

    studlab <- dat_temp$studlab
    t1 <- dat_temp$treat1
    t2 <- dat_temp$treat2
    TE <- model_temp$TE
    TE_diamond <- model_temp$TE.random
    se <- model_temp$seTE.random
    ci_lo <- TE_diamond-1.96*se ## if MD
    ci_up <- TE_diamond+1.96*se
    ci_lo_individual <- TE-1.96*dat_temp$seTE ## if MD
    ci_up_individual <- TE+1.96*dat_temp$seTE
    TEweights <- model_temp$w.random

    df <- data.frame(TE, TE_diamond, id, studlab, t1, t2, ci_lo_individual, ci_up_individual, ci_lo, ci_up, TEweights)
    colnames(df) <- c( "MD", "TE_diamond", "id", "studlab", "treat1", "treat2", "CI_lower", "CI_upper","CI_lower_diamond", "CI_upper_diamond", "WEIGHT")
    DFs_pairwise[[id]] <- df
  }
  DFs_pairwise <- do.call('rbind', DFs_pairwise)
  return(DFs_pairwise)
}