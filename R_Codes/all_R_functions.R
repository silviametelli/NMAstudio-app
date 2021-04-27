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

## forest plots with reference treatments
run_NetMeta <- function(dat){
       treatments <- unique(c(dat$treat1, dat$treat2)) # TODO:  MOVE IT TO PYTHON
       ALL_DFs <- list()
       for (treatment in treatments){
              if(dat$type_outcome1[1]=="continuous"){sm <- "MD"}
              else{sm <- "OR"}
              nma_temp <- netmeta(dat$TE, dat$seTE, dat$treat1, dat$treat2, dat$studlab,
                                         sm = sm,
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
              if(dat$type_outcome1[1]=="continuous"){sm1 <- "MD"}
              else{sm1 <- "OR"}
        treatments <- sort(unique(c(dat$treat1, dat$treat2)))
        nma_primary <- netmeta(TE=dat$TE, seTE=dat$seTE,
                               treat1=dat$treat1, treat2=dat$treat2,
                               studlab=dat$studlab,
                               sm = sm1,
                               comb.random = TRUE,
                               backtransf = TRUE,
                               reference.group = dat$treat2[1])
        if("TE2" %in% colnames(dat)){
          if(dat$type_outcome1[1]=="continuous"){sm2 <- "MD"}
          else{sm2 <- "OR"}
          nma_secondary <- netmeta(TE=dat$TE2, seTE=dat$seTE2,
                                 treat1=dat$treat1, treat2=dat$treat2,
                                 studlab=dat$studlab,
                                 sm = sm2,
                                 comb.random = TRUE,
                                 backtransf = TRUE,
                                 reference.group = dat$treat2[1])
        # - network estimates of first outcome in lower triangle
        # - network estimates of second outcome in upper triangle
        netleague_table <- netleague(nma_primary, nma_secondary, digits = 2, bracket="(",
                                     backtransf = TRUE, ci = TRUE, separator=',')
        }else{
          netleague_table <- netleague(nma_primary, digits = 2, bracket="(",
                                     backtransf = TRUE, ci = TRUE, separator=',')
        }
        lt <- netleague_table$random
        colnames(lt)<- treatments
        rownames(lt)<- treatments
        return(lt)
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