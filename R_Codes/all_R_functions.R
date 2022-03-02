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

iswhole <- function(x, tol = .Machine$double.eps^0.5) abs(x - round(x)) < tol


#--------------------------------------- NMA forest plots -------------------------------------------------#
run_NetMeta <- function(dat){
  ALL_DFs <- list()
  sm <- dat$effect_size1[1]
  dat <- dat %>% filter_at(vars(TE,seTE),all_vars(!is.na(.))) %>% filter(seTE!=0)
  treatments <- unique(c(dat$treat1, dat$treat2))
  # if incorrect number of arms, then delete entire study
  tabnarms <- table(dat$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if (sum(sel.narms) >= 1){dat <- dat %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  nma_temp <- netmeta(dat$TE, dat$seTE, dat$treat1, dat$treat2, dat$studlab,
                        sm = sm,
                        random = TRUE,
                        backtransf = TRUE,
                        #prediction = TRUE,
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
      if(sm=="MD" | sm=="SMD"){df <- data.frame(treatment_list, TE,  ci_lo, ci_up, TEweights, tau2)
      }else{df <- data.frame(treatment_list, exp(TE),  exp(ci_lo),  exp(ci_up), TEweights, tau2)}
      colnames(df) <- c("Treatment", sm, "CI_lower", "CI_upper", "WEIGHT", "tau2")
      df['Reference'] <- treatment
      ALL_DFs[[treatment]] <- df
      #rm(nma_temp, TE, TE_names, se, ci_lo, ci_up, TEweights, tau2)
  }
  ALL_DFs <- do.call('rbind', ALL_DFs)
  return(ALL_DFs)
}

#--------------------------------------- NMA league table & ranking -------------------------------------------------#
## league tables for either one or two outcomes
league_rank <- function(dat, outcome2=FALSE){
  dat1 <- dat[, c("studlab", "treat1", "treat2", "TE", "seTE")]
  dat1 <- dat1 %>% filter_at(vars(TE,seTE),all_vars(!is.na(.))) %>% filter(seTE!=0)
  tabnarms <- table(dat1$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if (sum(sel.narms) >= 1){dat1 <- dat1 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  sm1 <- dat$effect_size1[1]
  nma_primary <- netmeta(TE=dat1$TE, seTE=dat1$seTE,
                         treat1=dat1$treat1, treat2=dat1$treat2,
                         studlab=dat1$studlab,
                         sm = sm1,
                         random = TRUE, backtransf = TRUE,
                         reference.group = dat1$treat2[1])
  sortedseq <- sort(nma_primary$trts)
  netleague_table <- netleague(nma_primary, digits = 2,
                               seq = sortedseq,
                               bracket="(",
                               backtransf = TRUE, ci = TRUE, separator=',')
  lt <- netleague_table$random
  colnames(lt)<- sortedseq
  rownames(lt)<- sortedseq
  #p-scores
  rank1 <- netrank(nma_primary, small.values = "bad")
  rank <- data.frame(names(rank1$Pscore.random), as.numeric(round(rank1$Pscore.random,2)))
  colnames(rank)  <-  c("treatment", "pscore")
  #consistency
  consistency <- data.frame(nma_primary$Q.inconsistency, nma_primary$df.Q.inconsistency, nma_primary$pval.Q.inconsistency)
  colnames(consistency)  <-  c("Q1", "df_Q1", "p_Q1")
  #consistency node-split
  ne <- netsplit(nma_primary)
  comparison <- ne$compare.random$comparison[!is.na(ne$compare.random$p)]
  direct <- exp(ne$direct.random$TE[!is.na(ne$compare.random$p)])
  indirect <- exp(ne$indirect.random$TE[!is.na(ne$compare.random$p)])
  p <- ne$compare.random$p[!is.na(ne$compare.random$p)]
  df_cons <- data.frame(comparison, direct, indirect, p)
  colnames(df_cons) <- c("comparison", "direct", "indirect", "p-value")
  comp_all <- ne$compare.random$comparison
  k_all <- ne$k
  direct_all <- exp(ne$direct.random$TE)
  nma_all <- exp(ne$random$TE)
  indirect_all <- exp(ne$indirect.random$TE)
  p_all <- ne$compare.random$p
  netsplit_all <- data.frame(comp_all, k_all, direct_all, nma_all, indirect_all, p_all)
  colnames(netsplit_all) <- c("comparison", "k", "direct", "nma", "indirect", "p-value")
  if (all(is.na(ne$compare.random$p))==TRUE){
      df_cons <- data.frame(comp_all, direct_all, indirect_all, p_all)
      colnames(df_cons) <- c("comparison", "direct", "indirect", "p-value")
    }
  if(outcome2==TRUE){
    dat2 <- dat[, c("studlab", "treat1", "treat2", "TE2", "seTE2")]
    dat2 <- dat2 %>% filter_at(vars(TE2,seTE2),all_vars(!is.na(.))) %>% filter(seTE2!=0)
    tabnarms <- table(dat2$studlab)
    sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
    if (sum(sel.narms) >= 1){dat2 <- dat2 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
    sm2 <- dat$effect_size2[1]
    nma_secondary <- netmeta(TE=dat2$TE2, seTE=dat2$seTE2,
                             treat1=dat2$treat1, treat2=dat2$treat2,
                             studlab=dat2$studlab, sm = sm2,
                             random = TRUE, backtransf = TRUE,
                             reference.group = dat2$treat2[1])

    # - network estimates of first outcome in lower triangle, second outcome in upper triangle
    #if(length(sort(nma_primary$trts))>length(sort(nma_secondary$trts))){sortedseq <- sort(nma_primary$trts)}else{sortedseq <- sort(nma_secondary$trts)}

    netleague_table1 <- netleague(nma_primary, digits = 2,
                             bracket="(",  direct = FALSE,
                             backtransf = TRUE, ci = TRUE, separator=',')
    netleague_table2 <- netleague(nma_secondary, digits = 2,
                             bracket="(", direct = FALSE,
                             backtransf = TRUE, ci = TRUE, separator=',')

    lt1 <- netleague_table1$random
    lt2 <- netleague_table2$random
    l1_treats <- sort(nma_primary$trts)
    l2_treats <- sort(nma_secondary$trts)
    lt1[upper.tri(lt1)] <- NA
    lt2[upper.tri(lt2)] <- NA
    df_1 <-  as_tibble(lt1)
    df_2 <-  as_tibble(t(lt2))

    if(length(lt1)>length(lt2)){
      which_trts <- which(!(l1_treats %in% l2_treats))
      df_2 <- df_2 %>% add_column(NA,  .before = colnames(df_2)[which_trts], .name_repair = "universal")
      colnames <- paste0("V", 1:dim(df_2)[1])
      colnames(df_2) <- colnames
      df_2 <- df_2 %>% add_row( .before = as.numeric(rownames(df_2)[which_trts] ))
      for(x in which_trts){
        df_2[x, colnames[which_trts]] <- l1_treats[x]}
      lt <- matrix(NA, nrow = length(df_1), ncol = length(df_1))
      lt[upper.tri(lt, diag=T)] <- df_2[upper.tri(df_2, diag=T)]
      lt[lower.tri(lt, diag=T)] <- df_1[lower.tri(df_1, diag=T)]
      lt <- data.frame(lt)
      sortedseq <- l1_treats
    }else if (length(lt1)==length(lt2)){
      lt1 <- netleague_table1$random
      lt2 <- netleague_table2$random
      l1_treats <- sort(nma_primary$trts)
      l2_treats <- sort(nma_secondary$trts)
      df_1 <-  as_tibble(lt1)
      df_2 <-  as_tibble(t(lt2))
      lt <- matrix(NA, nrow = length(df_1), ncol = length(df_1))
      lt[upper.tri(lt, diag=T)] <- df_2[upper.tri(df_2, diag=T)]
      lt[lower.tri(lt, diag=T)] <- df_1[lower.tri(df_1, diag=T)]
      lt <- data.frame(lt)
      sortedseq <- l1_treats
    }else{
     is.empty <- function(x, mode = NULL){
        if (is.null(mode)) mode <- class(x)
        identical(vector(mode, 1), c(x, vector(class(x), 1)))}
      if(!is.empty(which_trts,"integer")){
        which_trts <- which(!(l2_treats %in% l1_treats))
        df_1 <- df_1 %>% add_column(NA,  .before = colnames(df_1)[which_trts], .name_repair = "universal")
        colnames <- paste0("V", 1:dim(df_1)[1])
        colnames(df_1) <- colnames
        df_1 <- df_1 %>% add_row( .before = as.numeric(rownames(df_1)[which_trts] ))
        for(x in which_trts){
          df_1[x, colnames[which_trts]] <- l2_treats[x]}
      }
      lt <- matrix(NA, nrow = length(df_2), ncol = length(df_2))
      lt[upper.tri(lt, diag=T)] <- df_2[upper.tri(df_2, diag=T)]
      lt[lower.tri(lt, diag=T)] <- df_1[lower.tri(df_1, diag=T)]
      lt <- data.frame(lt)
      sortedseq <- l2_treats

    }
    colnames(lt) <- sortedseq
    rownames(lt) <- sortedseq
    #p-scores
    # outcomes <- c("Outcome1", "Outcome2")
    rank1 <- netrank(nma_primary, small.values = "bad")
    rank2 <- netrank(nma_secondary, small.values = "bad")
    r1 <- data.frame(names(rank1$Pscore.random), round(as.numeric(rank1$Pscore.random),2))
    colnames(r1)  <-  c("treatment", "pscore")
    r2 <- data.frame(names(rank2$Pscore.random), round(as.numeric(rank2$Pscore.random),2))
    colnames(r2)  <-  c("treatment", "pscore")
    rank <- merge(r1, r2, by = "treatment", all.x = TRUE)
    colnames(rank)  <-  c("treatment", "pscore1",  "pscore2")
    #consistency design by treat
    consistency <- data.frame(nma_primary$Q.inconsistency, nma_primary$df.Q.inconsistency, nma_primary$pval.Q.inconsistency,
                              nma_secondary$Q.inconsistency, nma_secondary$df.Q.inconsistency, nma_secondary$pval.Q.inconsistency)
    colnames(consistency)  <-  c("Q1", "df(Q1)", "p(Q1)", "Q2", "df(Q2)", "p(Q2)")
    #consistency node-split
    ne2 <- netsplit(nma_secondary)
    comparison2 <- ne2$compare.random$comparison[!is.na(ne2$compare.random$p)]
    direct2<- exp(ne2$direct.random$TE[!is.na(ne2$compare.random$p)])
    indirect2 <- exp(ne2$indirect.random$TE[!is.na(ne2$compare.random$p)])
    p2 <- ne2$compare.random$p[!is.na(ne2$compare.random$p)]
    df_cons2 <- data.frame(comparison2, direct2, indirect2, p2)
    colnames(df_cons2) <- c("comparison", "direct", "indirect", "p-value")
    comp_all2 <- ne2$compare.random$comparison
    k_all2 <- ne2$k
    direct_all2 <- exp(ne2$direct.random$TE)
    nma_all2 <- exp(ne2$random$TE)
    indirect_all2 <- exp(ne2$indirect.random$TE)
    p_all2 <- ne2$compare.random$p
    netsplit_all2 <- data.frame(comp_all2, k_all2, direct_all2, nma_all2, indirect_all2, p_all2)
    colnames(netsplit_all2) <- c("comparison", "k", "direct", "nma", "indirect", "p-value")
    if (all(is.na(ne2$compare.random$p))==TRUE){
      df_cons <- data.frame(comp_all2, direct_all2, indirect_all2, p_all2)
      colnames(df_cons) <- c("comparison", "direct", "indirect", "p-value")
    }
  }

  if(outcome2==TRUE){return(list(lt, rank, consistency, df_cons, df_cons2, netsplit_all, netsplit_all2))}else{
    return(list(lt, rank, consistency, df_cons, netsplit_all))
  }
}

## comparison adjusted funnel plots
funnel_funct <- function(dat){
  ALL_DFs <- list()
  sm <- dat$effect_size1[1]
  dat <- dat %>% filter_at(vars(TE,seTE),all_vars(!is.na(.))) %>% filter(seTE!=0)
  iswhole <- function(x, tol = .Machine$double.eps^0.5) abs(x - round(x)) < tol
  tabnarms <- table(dat$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if (sum(sel.narms) >= 1){dat <- dat %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  treatments <- unique(c(dat$treat1, dat$treat2))
  x <- netmeta(TE=dat$TE, seTE=dat$seTE,
                 treat1=dat$treat1, treat2=dat$treat2,
                 studlab=dat$studlab,
                 sm = sm,
                 random = TRUE,
                 backtransf = FALSE,
                 reference.group = treatments[1])
  for (treatment in treatments){
    ordered_strategies <- unique(c(dat$treat1, dat$treat2))
    ordered_strategies <- ordered_strategies[ordered_strategies!=treatment]
    ordered_strategies <- c(ordered_strategies, rev(treatment))
    TE <- x$TE
    seTE <- x$seTE
    treat1 <- x$treat1
    treat2 <- x$treat2
    trts.abbr <- x$trts
    trt1 <- as.character(factor(treat1, levels = x$trts, labels = trts.abbr))
    trt2 <- as.character(factor(treat2, levels = x$trts, labels = trts.abbr))
    studlab <- x$studlab
    sep.trts <- ":"
    comp <- paste(trt1, trt2, sep = sep.trts)
    comp21 <- paste(trt2, trt1, sep = sep.trts)
    comparison <- paste(treat1, treat2, sep = sep.trts)
    comparison21 <- paste(treat2, treat1, sep = sep.trts)
    treat1.pos <- as.numeric(factor(treat1, levels = ordered_strategies))
    treat2.pos <- as.numeric(factor(treat2, levels = ordered_strategies))
    wo <- treat1.pos > treat2.pos
    if (any(wo)) {
      TE[wo] <- -TE[wo]
      ttreat1 <- treat1
      treat1[wo] <- treat2[wo]
      treat2[wo] <- ttreat1[wo]
      ttreat1.pos <- treat1.pos
      treat1.pos[wo] <- treat2.pos[wo]
      treat2.pos[wo] <- ttreat1.pos[wo]
      comp[wo] <- comp21[wo]
      comparison[wo] <- comparison21[wo]
    }
    o <- order(treat1.pos, treat2.pos)
    TE <- TE[o]
    seTE <- seTE[o]
    treat1 <- treat1[o]
    treat2 <- treat2[o]
    studlab <- studlab[o]
    comp <- comp[o]
    comparison <- comparison[o]
    res <- data.frame(studlab, treat1, treat2, comparison, comp, TE, TE.direct = NA, TE.adj = NA, seTE)
    if (is.numeric(treat1)){treat1 <- as.character(treat1)}
    if (is.numeric(treat2)){treat2 <- as.character(treat2)}
    if (x$fixed == TRUE){
           for (i in seq_along(res$TE))
               res$TE.direct[i] <- x$TE.direct.fixed[treat1[i], treat2[i]]
    }else{
           for (i in seq_along(res$TE))
             res$TE.direct[i] <- x$TE.direct.random[treat1[i], treat2[i]]
    }
    res$TE.adj <- res$TE - res$TE.direct
    #netfun <- funnel(nma, order=ordered_strategies)
    funneldata <- droplevels(subset(res, treat2==treatment))
    df <- data.frame(funneldata$studlab, funneldata$treat1, funneldata$treat2, funneldata$TE,
                                  funneldata$TE.direct, funneldata$TE.adj, funneldata$seTE)
    colnames(df) <- c("studlab", "treat1", "treat2", sm, "TE_direct", "TE_adj", "seTE")
    rownames(df) <- NULL
    ALL_DFs[[treatment]] <- df

  }
  ALL_DFs <- do.call('rbind', ALL_DFs)
  return(ALL_DFs)
}


#------------------------------------- pairwise forest plots -------------------------------------------#
## pairwise forest plots for all different comparisons in df
## sorted_dat: dat sorted by treatemnt comparison

pairwise_forest <- function(dat){
  sm <- dat$effect_size1[1]
  DFs_pairwise <- list()
  dat <- dat %>% filter_at(vars(TE, seTE), all_vars(!is.na(.))) %>% filter(seTE!=0)
  dat <- dat %>% arrange(dat, treat1, treat2)
  dat$ID <- dat %>% group_indices(treat1, treat2)

  for (id in dat$ID){
    dat_temp <- dat[which(dat$ID==id), ]
    model_temp <- metagen(TE=TE,seTE=sqrt(seTE), studlab = studlab, data=dat_temp,
                         random = T, sm=sm, prediction=TRUE)

    studlab <- dat_temp$studlab
    t1 <- dat_temp$treat1
    t2 <- dat_temp$treat2
    TE <- model_temp$TE
    TE_diamond <- model_temp$TE.random
    se <- model_temp$seTE.random
    ci_lo <- model_temp$lower.random
    ci_up <- model_temp$upper.random
    ci_lo_individual <- model_temp$lower
    ci_up_individual <- model_temp$upper
    predict_lo <- model_temp$lower.predict
    predict_up <- model_temp$upper.predict
    TEweights <- model_temp$w.random
    tau2 <- model_temp$tau^2
    I2 <- model_temp$I2
    if(sm=="MD" | sm=="SMD"){df <- data.frame(TE, TE_diamond, id, studlab, t1, t2, ci_lo_individual,
                                              ci_up_individual, ci_lo, ci_up, predict_lo, predict_up,
                                              TEweights, tau2, I2)
    }else{df <- data.frame(exp(TE), exp(TE_diamond), id, studlab, t1, t2, exp(ci_lo_individual),
                           exp(ci_up_individual), exp(ci_lo), exp(ci_up), exp(predict_lo),
                           exp(predict_up), TEweights, tau2, I2)}
    colnames(df) <- c(sm , "TE_diamond", "id", "studlab", "treat1", "treat2", "CI_lower",
                           "CI_upper", "CI_lower_diamond", "CI_upper_diamond", "Predict_lo",
                           "Predict_up", "WEIGHT", "tau2", "I2")
    DFs_pairwise[[id]] <- df
  }
  DFs_pairwise <- do.call('rbind', DFs_pairwise)
  return(DFs_pairwise)
}


#----------------------------------- pairwise function to convert data -----------------------------------------#

get_pairwise_data_long <- function(dat, outcome2=FALSE){
    sm1 <- dat$effect_size1[1]
    if(sm1 %in% c('RR','OR')){
    pairwise_dat1 <- netmeta::pairwise(data=dat,
                                       event=r,
                                       n=n,
                                       studlab=studlab,
                                       treat=treat,
                                       incr=0.5,
                                       sm=sm1)
    }else{
      pairwise_dat1 <- netmeta::pairwise(data=dat,
                                         mean=y,
                                         sd=sd,
                                         n=n,
                                         studlab=studlab,
                                         treat=treat,
                                         incr=0.5,
                                         sm=sm1)}
    pairwise_dat <- pairwise_dat1

    names(pairwise_dat)[names(pairwise_dat) == 'rob1'] <- 'rob'
    names(pairwise_dat)[names(pairwise_dat) == 'year1'] <- 'year'

  if(outcome2==TRUE){
      sm2 <- dat$effect_size2[1]
      if(sm2 %in% c('RR','OR')){
        pairwise_dat1 <- netmeta::pairwise(data=dat,
                                     event=r2,
                                     n=n2,
                                     studlab=studlab,
                                     treat=treat,
                                     incr=0.5,
                                     sm=sm2)
      }else{
        pairwise_dat2 <- netmeta::pairwise(data=dat,
                                           mean=y2,
                                           sd=sd2,
                                           n=n2,
                                           studlab=studlab,
                                           treat=treat,
                                           incr=0.5,
                                           sm=sm2)
      }
      pairwise_dat <- full_join(pairwise_dat1, pairwise_dat2, by = c("studlab","treat1","treat2"))
     names(pairwise_dat)[names(pairwise_dat) == 'TE.x'] <- 'TE'
     names(pairwise_dat)[names(pairwise_dat) == 'seTE.x'] <- 'seTE'
     names(pairwise_dat)[names(pairwise_dat) == 'n1.x'] <- 'n1'
     names(pairwise_dat)[names(pairwise_dat) == 'n2.x'] <- 'n2'
     names(pairwise_dat)[names(pairwise_dat) == 'effect_size1.x'] <- 'effect_size1'
     names(pairwise_dat)[names(pairwise_dat) == 'TE.y'] <- 'TE2'
     names(pairwise_dat)[names(pairwise_dat) == 'seTE.y'] <- 'seTE2'
     names(pairwise_dat)[names(pairwise_dat) == 'n1.y'] <- 'n2.1'
     names(pairwise_dat)[names(pairwise_dat) == 'n2.y'] <- 'n2.2'
     names(pairwise_dat)[names(pairwise_dat) == 'effect_size2.x'] <- 'effect_size2'
     names(pairwise_dat)[names(pairwise_dat) == 'rob.x'] <- 'rob'
     names(pairwise_dat)[names(pairwise_dat) == 'year.x'] <- 'year'

  }
  return (pairwise_dat)
}



get_pairwise_data_contrast <- function(dat, outcome2=FALSE){
    sm1 <- dat$effect_size1[1]
    if(sm1 %in% c('RR','OR')){
    pairwise_dat1 <- netmeta::pairwise(data=dat,
                                       event=list(r1,r2),
                                       n=list(n1,n2),
                                       studlab=studlab,
                                       treat=list(treat1,treat2),
                                       incr=0.5,
                                       sm=sm1)
    }else{
      pairwise_dat1 <- netmeta::pairwise(data=dat,
                                         mean=list(y1,y2),
                                         sd=list(sd1,sd2),
                                         n=list(n1,n2),
                                         studlab=studlab,
                                         treat=list(treat1,treat2),
                                         incr=0.5,
                                         sm=sm1)}
    pairwise_dat <- pairwise_dat1

    names(pairwise_dat)[names(pairwise_dat) == 'rob1'] <- 'rob'
    names(pairwise_dat)[names(pairwise_dat) == 'year1'] <- 'year'

  if(outcome2==TRUE){
      sm2 <- dat$effect_size2[1]
      if(sm2 %in% c('RR','OR')){
        pairwise_dat2 <- netmeta::pairwise(data=dat,
                                           event=list(z1,z2),
                                           n=list(n2.1,n2.2),
                                           studlab=studlab,
                                           treat=list(treat1,treat2),
                                           incr=0.5,
                                           sm=sm2)
      }else{
        pairwise_dat2 <- netmeta::pairwise(data=dat,
                                           mean=list(y2.1,y2.2),
                                           sd=list(sd1.2,sd2.2),
                                           n=list(n2.1, n2.2),
                                           studlab=studlab,
                                           treat=list(treat1,treat2),
                                           incr=0.5,
                                           sm=sm2)
      }
      pairwise_dat <- full_join(pairwise_dat1, pairwise_dat2, by = c("studlab","treat1","treat2"))
     names(pairwise_dat)[names(pairwise_dat) == 'TE.x'] <- 'TE'
     names(pairwise_dat)[names(pairwise_dat) == 'seTE.x'] <- 'seTE'
     names(pairwise_dat)[names(pairwise_dat) == 'n1.x'] <- 'n1'
     names(pairwise_dat)[names(pairwise_dat) == 'n2.x'] <- 'n2'
     names(pairwise_dat)[names(pairwise_dat) == 'effect_size1.x'] <- 'effect_size1'
     names(pairwise_dat)[names(pairwise_dat) == 'TE.y'] <- 'TE2'
     names(pairwise_dat)[names(pairwise_dat) == 'seTE.y'] <- 'seTE2'
     names(pairwise_dat)[names(pairwise_dat) == 'n1.y'] <- 'n2.1'
     names(pairwise_dat)[names(pairwise_dat) == 'n2.y'] <- 'n2.2'
     names(pairwise_dat)[names(pairwise_dat) == 'effect_size2.x'] <- 'effect_size2'
     names(pairwise_dat)[names(pairwise_dat) == 'rob.x'] <- 'rob'
     names(pairwise_dat)[names(pairwise_dat) == 'year.x'] <- 'year'

  }
  return (pairwise_dat)
}
