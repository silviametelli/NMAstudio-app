import numpy as np
import pandas as pd


## OR
def OR_effect_measure(df, dfr1, dfr2,dfn1,dfn2):
    r1 = pd.to_numeric(df[dfr1], errors='coerce')
    r2 = pd.to_numeric(df[dfr2], errors='coerce')
    n1 = pd.to_numeric(df[dfn1], errors='coerce')
    n2 = pd.to_numeric(df[dfn2], errors='coerce')
    ## Define continuity correction
    incr1 = np.where(((r1 == 0) | (r1 == n1)), 0.5, 0)
    incr2 = np.where(((r2 == 0) | (r2 == n2)), 0.5, 0)
    ## Multiply by incl to exclude double-zero studies TODO: check
    incl = np.where(((r1 == 0) & (r2 == 0) | ((r1 == n1) & (r2 == n2))), np.nan, 1)
    n11 = r1 * incl; n21 = r2 * incl
    n1 = n1 * incl;  n2 = n2 * incl
    n12 = n1 - n11; n22 = n2 - n21
    TE = np.log(((n11 + incr1) * (n22 + incr2)) / ((n12 + incr1) * (n21 + incr2)))
    seTE = np.sqrt((1 / (n11 + incr1) + 1 / (n12 + incr1) + 1 / (n21 + incr2) + 1 / (n22 + incr2)))

    return round(TE,3), round(seTE,3)

## RR #TODO: change as OR
def RR_effect_measure(df): #TODO: check formula
    dfr1 = pd.to_numeric(df.r1, errors='coerce')
    dfr2 = pd.to_numeric(df.r2, errors='coerce')
    dfn1 = pd.to_numeric(df.n1, errors='coerce')
    dfn2 = pd.to_numeric(df.n2, errors='coerce')
    incr1 = np.where(((dfr1 == 0) | (dfr1 == dfn1)), 0.5, 0)
    incr2 = np.where(((dfr2 == 0) | (dfr2 == dfn2)), 0.5, 0)
    ## Multiply by incl to exclude double-zero studies
    incl = np.where(((dfr1 == 0) & (dfr2 == 0) | ((dfr1 == dfn1) & (dfr2 == dfn2))), np.nan, 1)
    n11 = dfr1 * incl; n21 = dfr2 * incl
    n1_ = dfn1 * incl; n2_ = dfn2 * incl
    TE = np.log(((n11 + incr1) / (n1_ + incr1)) / ((n21 + incr2) / (n2_ + incr2)))
    seTE = np.sqrt((1 / (n11 + incr1) - 1 / (n1_ + incr1) + 1 / (n21 + incr2) - 1 / (n2_ + incr2)))

    return round(TE, 3), round(seTE, 3)

## MD #TODO: change as OR
def MD_effect_measure(df):
    dfy1 = pd.to_numeric(df.y1, errors='coerce')
    dfsd1 = pd.to_numeric(df.sd1, errors='coerce')
    dfy2 = pd.to_numeric(df.y1, errors='coerce')
    dfsd2 = pd.to_numeric(df.sd1, errors='coerce')
    dfn1 = pd.to_numeric(df.n1, errors='coerce')
    dfn2 = pd.to_numeric(df.n2, errors='coerce')
    #N =  df.n1 + df.n2
    #sigma2_pooled = ((df.n1 - 1) * pow(df.sd1,2) + (df.n2 - 1) * pow(df.sd2,2)) / (N - 2)
    #seTE =  sqrt(sigma2_pooled.pooled * (1 / df.n1 + 1 / df.n2)))
    TE =  dfy1 - dfy2
    seTE =  np.sqrt(pow(dfsd1,2) / dfn1 + pow(dfsd2,2) / dfn2)
    seTE[np.isnan(TE)] = np.nan

    return round(TE,3), round(seTE,3)
