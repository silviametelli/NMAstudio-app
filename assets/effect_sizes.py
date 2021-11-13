import numpy as np, pandas as pd

#### OR
def get_OR(df):
    for c in ['r1', 'r2', 'n1', 'n2']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    r1, r2, n1, n2 = df.r1, df.r2, df.n1, df.n2
    ## Define continuity correction
    incr1 = np.where(((r1 == 0) | (r1 == n1)), 0.5, 0)
    incr2 = np.where(((r2 == 0) | (r2 == n2)), 0.5, 0)
    ## Multiply by incl to exclude double-zero studies TODO: check
    incl = np.where(((r1 == 0) & (r2 == 0) | ((r1 == n1) & (r2 == n2))), np.nan, 1)
    n11, n21 = r1 * incl,  r2 * incl
    n1 *= incl
    n2 *= incl
    n12, n22 = n1 - n11, n2 - n21
    TE = np.log(((n11 + incr1) * (n22 + incr2)) / ((n12 + incr1) * (n21 + incr2)))
    seTE = np.sqrt(1 / (n11 + incr1) + 1 / (n12 + incr1) + 1 / (n21 + incr2) + 1 / (n22 + incr2))

    return round(TE,3), round(seTE,3)

#### RR #TODO: change
def get_RR(df): #TODO: check formula
    for c in ['r1', 'r2', 'n1', 'n2']:
        # df[c] = df[c].astype(np.float64)
        df[c] = pd.to_numeric(df[c], errors='coerce')
    incr1 = np.where(((df.r1 == 0) | (df.r1 == df.n1)), 0.5, 0)
    incr2 = np.where(((df.r2 == 0) | (df.r2 == df.n2)), 0.5, 0)
    ## Multiply by incl to exclude double-zero studies
    incl = np.where(((df.r1 == 0) & (df.r2 == 0) | ((df.r1 == df.n1) & (df.r2 == df.n2))), np.nan, 1)
    n11 = df.r1 * incl
    n21 = df.r2 * incl
    n1_ = df.n1 * incl
    n2_ = df.n2 * incl
    TE = np.log(((n11 + incr1) / (n1_ + incr1)) / ((n21 + incr2) / (n2_ + incr2)))
    seTE = np.sqrt(1 / (n11 + incr1) - 1 / (n1_ + incr1) + 1 / (n21 + incr2) - 1 / (n2_ + incr2))

    return round(TE, 3), round(seTE, 3)

#### MD #TODO: change
def get_MD(df):
    for c in ['y1', 'sd1', 'y2', 'sd2', 'n1', 'n2']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    #N =  df.n1 + df.n2
    #sigma2_pooled = ((df.n1 - 1) * pow(df.sd1,2) + (df.n2 - 1) * pow(df.sd2,2)) / (N - 2)
    #seTE =  sqrt(sigma2_pooled.pooled * (1 / df.n1 + 1 / df.n2)))
    TE =  df.y1 - df.y2
    seTE =  np.sqrt( df.sd1**2 / df.n1 + df.sd2**2 / df.n2)
    seTE[np.isnan(TE)] = np.nan

    return round(TE,3), round(seTE,3)


#### SMD #TODO: change
def get_SMD(df):
    for c in ['y1', 'sd1', 'y2', 'sd2', 'n1', 'n2']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    #N =  df.n1 + df.n2
    #sigma2_pooled = ((df.n1 - 1) * pow(df.sd1,2) + (df.n2 - 1) * pow(df.sd2,2)) / (N - 2)
    #seTE =  sqrt(sigma2_pooled.pooled * (1 / df.n1 + 1 / df.n2)))
    TE =  df.y1 - df.y2
    seTE =  np.sqrt( df.sd1**2 / df.n1 + df.sd2**2 / df.n2)
    seTE[np.isnan(TE)] = np.nan

    return round(TE,3), round(seTE,3)
