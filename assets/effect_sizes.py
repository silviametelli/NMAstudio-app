import numpy as np, pandas as pd
from scipy.special import loggamma
#### OR
def get_OR(df, effect=1):
    cols = ('r1', 'r2', 'n1', 'n2')
    if effect==2: cols = ('z1', 'n1.z', 'z2', 'n2.z')
    for c in cols:
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

#### RR
def get_RR(df, effect=1): #TODO: check formula
    cols = ('r1', 'r2', 'n1', 'n2')
    if effect==2: cols = ('z1', 'n1.z', 'z2', 'n2.z')
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    incr1 = np.where(((df.r1 == 0) | (df.r1 == df.n1)), 0.5, 0)
    incr2 = np.where(((df.r2 == 0) | (df.r2 == df.n2)), 0.5, 0)
    ## Multiply by incl to exclude double-zero studies
    incl = np.where(((df.r1 == 0) & (df.r2 == 0) | ((df.r1 == df.n1) & (df.r2 == df.n2))), np.nan, 1)
    n11, n21, n1_, n2_ = df[['r1', 'r2', 'n1', 'n2']] * incl
    TE = np.log(((n11 + incr1) / (n1_ + incr1)) / ((n21 + incr2) / (n2_ + incr2)))
    seTE = np.sqrt(1 / (n11 + incr1) - 1 / (n1_ + incr1) + 1 / (n21 + incr2) - 1 / (n2_ + incr2))

    return round(TE, 3), round(seTE, 3)

#### MD
def get_MD(df, effect=1):
    cols = ('y1', 'sd1', 'y2', 'sd2', 'n1', 'n2')
    if effect==2: cols = ('y2.1', 'sd1.2', 'y2.2', 'sd2.2', 'n2.1', 'n2.2')
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    TE =  df.y1 - df.y2
    seTE =  np.sqrt( df.sd1**2 / df.n1 + df.sd2**2 / df.n2)
    seTE[np.isnan(TE)] = np.nan
    return round(TE,3), round(seTE,3)

##correction factor for Cohen's d
def cmicalc(mi) :
    if mi <= 1:
        return np.nan
    else: return np.exp(loggamma(mi/2) - np.log(np.sqrt(mi/2)) - loggamma((mi-1)/2))

#### SMD #TODO: seTE adjusted for multiarm? use Hedges's
def get_SMD(df, effect=1):
    cols = ('y1', 'sd1', 'y2', 'sd2', 'n1', 'n2')
    if effect==2:
        cols = ('y2.1', 'sd1.2', 'y2.2', 'sd2.2', 'n2.1', 'n2.2')
        df.rename(columns={'y2.1':'y1', 'sd1.2':'sd1', 'y2.2':'y2', 'sd2.2':'sd2', 'n2.1':'n1', 'n2.2':'n2'})
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    N =  df.n1 + df.n2
    mi = N-2
    sigma2_pooled = ((df.n1 - 1) * pow(df.sd1,2) + (df.n2 - 1) * pow(df.sd2,2)) / mi
    TE =  (df.y1 - df.y2)/np.sqrt(sigma2_pooled)
    cmi = cmicalc(N-2)
    yi = TE*cmi
    ###### large sample approximation to the sampling variance used as default
    #seTE = np.sqrt( 1/df.n1 + 1/df.n2 + (1-(mi)/mi*cmi**2)*yi**2 ) # UB: unbiased estimate of the sampling sd
    seTE = np.sqrt(1/df.n1 + 1/df.n2 + yi**2/(2*N))
    seTE[np.isnan(TE)] = np.nan

    return round(TE,3), round(seTE,3)
