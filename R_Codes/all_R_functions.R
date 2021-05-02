# Title     :  R function for VisualNMA
# Objective :  compute NMA output via netmeta
# Created by:  Silvia Metelli
# Created on: 16/11/2020
options(warn=-1)
suppressMessages(library(netmeta))
suppressMessages(library(dplyr))
suppressMessages(library(meta))
suppressMessages(library(metafor))
suppressMessages(library(tidyverse))

#--------------------------------------- NMA forest plots -------------------------------------------------#

run_NetMeta <- function(dat){
  treatments <- unique(c(dat$treat1, dat$treat2))
  ALL_DFs <- list()
  if(dat$type_outcome1[1]=="continuous"){sm <- "MD"}else{sm <- "RR"}
  dat <- dat %>% filter_at(vars(TE,seTE),all_vars(!is.na(.))) %>% filter(seTE!=0)
  iswhole <- function(x, tol = .Machine$double.eps^0.5) abs(x - round(x)) < tol
  # if incorrect number of arms, then delete entire study
  tabnarms <- table(dat$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if (sum(sel.narms) >= 1){dat <- dat %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  nma_temp <- netmeta(dat$TE, dat$seTE, dat$treat1, dat$treat2, dat$studlab,
                        sm = sm,
                        comb.random = TRUE,
                        backtransf = TRUE,
                        reference.group = treatments[1])
    ### Values
  for (treatment in treatments){
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
      tau2 <- nma_temp$tau^2
      df <- data.frame(treatment_list, exp(TE),  exp(ci_lo),  exp(ci_up), TEweights, tau2)
      colnames(df) <- c("Treatment", sm, "CI_lower", "CI_upper", "WEIGHT", "tau2")
      df['Reference'] <- treatment
      ALL_DFs[[treatment]] <- df
      rm(nma_temp, TE, TE_names, se, ci_lo, ci_up, TEweights, tau2)
  }
  ALL_DFs <- do.call('rbind', ALL_DFs)
  return(ALL_DFs)
}

#--------------------------------------- NMA league table & ranking -------------------------------------------------#
## league tables for either one or two outcomes
league_rank <- function(dat){
  dat1 <- dat[, c("studlab", "treat1", "treat2", "TE", "seTE")]
  dat1 <- dat1 %>% filter_at(vars(TE,seTE),all_vars(!is.na(.))) %>% filter(seTE!=0)
  iswhole <- function(x, tol = .Machine$double.eps^0.5) abs(x - round(x)) < tol
  tabnarms <- table(dat1$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if (sum(sel.narms) >= 1){dat1 <- dat1 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  if(dat$type_outcome1[1]=="continuous"){sm1 <- "MD"}else{sm1 <- "RR"}
  nma_primary <- netmeta(TE=dat1$TE, seTE=dat1$seTE,
                         treat1=dat1$treat1, treat2=dat1$treat2,
                         studlab=dat1$studlab,
                         sm = sm1,
                         comb.random = TRUE, backtransf = TRUE,
                         reference.group = dat1$treat2[1])
  if("TE2" %in% colnames(dat)){
    dat2 <- dat[, c("studlab", "treat1", "treat2", "TE2", "seTE2")]
    dat2 <- dat2 %>% filter_at(vars(TE2,seTE2),all_vars(!is.na(.))) %>% filter(seTE2!=0)
    tabnarms <- table(dat2$studlab)
    sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
    if (sum(sel.narms) >= 1){dat2 <- dat2 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
    if(dat$type_outcome2[1]=="continuous"){sm2 <- "MD"}else{sm2 <- "RR"}
    nma_secondary <- netmeta(TE=dat2$TE2, seTE=dat2$seTE2,
                             treat1=dat2$treat1, treat2=dat2$treat2,
                             studlab=dat2$studlab,
                             sm = sm2,
                             comb.random = TRUE, backtransf = TRUE,
                             reference.group = dat2$treat2[1])
    # - network estimates of first outcome in lower triangle, second outcome in upper triangle
    netleague_table <- netleague(nma_primary, nma_secondary, digits = 2, bracket="(",
                                 backtransf = TRUE, ci = TRUE, separator=',')
    #p-scores
    outcomes <- c("Outcome1", "Outcome2")
    rank1 <- netrank(nma_primary, small.values = "good")
    rank2 <- netrank(nma_secondary, small.values = "good")
    r1 <- data.frame(names(rank1$Pscore.random), as.numeric(rank1$Pscore.random))
    colnames(r1)  <-  c("treatment", "pscore")
    r2 <- data.frame(names(rank2$Pscore.random), as.numeric(rank2$Pscore.random))
    colnames(r2)  <-  c("treatment", "pscore")
    rank <- merge(r1, r2, by = "treatment", all.x = TRUE)
    colnames(rank)  <-  c("treatment", "pscore")
  }else{
    netleague_table <- netleague(nma_primary, digits = 2, bracket="(",
                                 backtransf = TRUE, ci = TRUE, separator=',')
    #p-scores
    outcomes <- c("Outcome1")
    rank1 <- netrank(nma_primary, small.values = "good")
    rank <- data.frame(names(rank1$Pscore.random), as.numeric(rank1$Pscore.random))
    colnames(rank)  <-  c("treatment", "pscore")
  }
  lt <- netleague_table$random
  colnames(lt)<- treatments
  rownames(lt)<- treatments
  return(list(leaguetable=lt, pscores=rank))
}


## comparison adjusted funnel plots
funnel_plot <- function(dat,ref_vec){
        nma <- netmeta(TE=dat$TE, seTE=dat$seTE,
                       treat1=dat$treat1, treat2=dat$treat2,
                       studlab=dat$studlab,
                       sm = "MD", ## or OR TODO: pass effect size to func
                       comb.random = TRUE,
                       backtransf = TRUE,
                       reference.group = ref_vec[1])
        ordered_strategies <- unique(c(dat$treat1, dat$treat2))
        ordered_strategies <- c(ordered_strategies, ref_vec)
        netfun <- funnel(nma, order=ordered_strategies)
        funneldata <- droplevels(subset(netfun,treat2==ref))
  return(funneldata)
}


#------------------------------------- pairwise forest plots -------------------------------------------#
## pairwise forest plots for all different comparisons in df
## sorted_dat: dat sorted by treatemnt comparison
pairwise_forest <- function(dat){
  if(dat$type_outcome1[1]=="continuous"){sm <- "MD"}
  else{sm <- "OR"}
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
    ci_up <- TE_diamond+1.96*se ## if MD
    ci_lo_individual <- TE-1.96*dat_temp$seTE ## if MD
    ci_up_individual <- TE+1.96*dat_temp$seTE ## if MD
    TEweights <- model_temp$w.random

    df <- data.frame(TE, TE_diamond, id, studlab, t1, t2, ci_lo_individual, ci_up_individual, ci_lo, ci_up, TEweights)
    colnames(df) <- c( "MD", "TE_diamond", "id", "studlab", "treat1", "treat2", "CI_lower", "CI_upper","CI_lower_diamond", "CI_upper_diamond", "WEIGHT")
    DFs_pairwise[[id]] <- df
  }
  DFs_pairwise <- do.call('rbind', DFs_pairwise)
  return(DFs_pairwise)
}