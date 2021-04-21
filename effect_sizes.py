import numpy as np

## OR
def OR_effect_measure(df):

    df.r1 = pd.to_numeric(df.r1, errors='coerce')
    df.r2 = pd.to_numeric(df.r2, errors='coerce')
    df.n1 = pd.to_numeric(df.n1, errors='coerce')
    df.n2 = pd.to_numeric(df.n2, errors='coerce')
    ## Define continuity correction
    incr1 = np.where(((df.r1 == 0) | (df.r1 == df.n1)), 0.5, 0)
    incr2 = np.where(((df.r2 == 0) | (df.r2 == df.n2)), 0.5, 0)
    ## Multiply by incl to exclude double-zero studies TODO: check
    incl = np.where(((df.r1 == 0) & (df.r2 == 0) | ((df.r1 == df.n1) & (df.r2 == df.n2))), np.nan, 1)
    n11 = df.r1 * incl; n21 = df.r2 * incl
    n1 = df.n1 * incl;  n2 = df.n2 * incl
    n12 = n1 - n11; n22 = n2 - n21
    TE = np.log(((n11 + incr1) * (n22 + incr2)) / ((n12 + incr1) * (n21 + incr2)))
    seTE = np.sqrt((1 / (n11 + incr1) + 1 / (n12 + incr1) + 1 / (n21 + incr2) + 1 / (n22 + incr2)))

    return round(TE,3), round(seTE,3)

## RR
def RR_effect_measure(df): #TODO: to be checked if correct formula
    df.r1 = pd.to_numeric(df.r1, errors='coerce')
    df.r2 = pd.to_numeric(df.r2, errors='coerce')
    df.n1 = pd.to_numeric(df.n1, errors='coerce')
    df.n2 = pd.to_numeric(df.n2, errors='coerce')
    incr1 = np.where(((df.r1 == 0) | (df.r1 == df.n1)), 0.5, 0)
    incr2 = np.where(((df.r2 == 0) | (df.r2 == df.n2)), 0.5, 0)
    ## Multiply by incl to exclude double-zero studies
    incl = np.where(((df.r1 == 0) & (df.r2 == 0) | ((df.r1 == df.n1) & (df.r2 == df.n2))), np.nan, 1)
    n11 = df.r1 * incl; n21 = df.r2 * incl
    n1_ = df.n1 * incl; n2_ = df.n2 * incl
    TE = np.log(((n11 + incr1) / (n1_. + incr1)) / ((n21 + incr2) / (n2_ + incr2)))
    seTE = np.sqrt((1 / (n11 + incr1) - 1 / (n1_ + incr1) + 1 / (n21 + incr2) - 1 / (n2_. + incr2)))

    return round(TE, 3), round(seTE, 3)

## MD
def MD_effect_measure(df):

    df.y1 = pd.to_numeric(df.y1, errors='coerce')
    df.sd1 = pd.to_numeric(df.sd1, errors='coerce')
    df.y2 = pd.to_numeric(df.y1, errors='coerce')
    df.sd2 = pd.to_numeric(df.sd1, errors='coerce')
    df.n1 = pd.to_numeric(df.n1, errors='coerce')
    df.n2 = pd.to_numeric(df.n2, errors='coerce')

    #N =  df.n1 + df.n2
    #sigma2_pooled = ((df.n1 - 1) * pow(df.sd1,2) + (df.n2 - 1) * pow(df.sd2,2)) / (N - 2)
    #seTE =  sqrt(sigma2_pooled.pooled * (1 / df.n1 + 1 / df.n2)))

    TE =  df.y1 - df.y2
    seTE =  sqrt(pow(df.sd1,2) / df.n1 + pow(df.sd2,2) / df.n2)
    seTE[np.isnan(TE)] = np.nan

    return round(TE,3), round(seTE,3)