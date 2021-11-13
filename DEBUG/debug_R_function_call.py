import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri  # Define the R script and loads the instance in Python
from rpy2.robjects.conversion import localconverter
from  collections  import OrderedDict
r = ro.r
r['source']('R_Codes/all_R_functions.R')  # Loading the function we have defined in R.
run_NetMeta_r = ro.globalenv['run_NetMeta']  # Get run_NetMeta from R
league_table_r = ro.globalenv['league_rank']  # Get league_table from R
pairwise_forest_r = ro.globalenv['pairwise_forest']  # Get pairwise_forest from R

GLOBAL_DATA = {'net_data': pd.read_csv('db/psoriasis_wide_small.csv')}
data = GLOBAL_DATA['net_data']

def apply_r_func(func, df):
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(df.reset_index(drop=True))
    func_r_res = func(dat=df_r)
    r_result = pandas2ri.rpy2py(func_r_res)
    if isinstance(r_result, ro.vectors.ListVector):
        leaguetable, pscores, consist, netsplit = (pd.DataFrame(rf)for rf in r_result)
        return leaguetable, pscores, consist, netsplit
    else:
        df_result = r_result.reset_index(drop=True)  # Convert back to a pandas.DataFrame.
        return df_result


GLOBAL_DATA['forest_data'] = apply_r_func(func=run_NetMeta_r, df=data)
#GLOBAL_DATA['forest_data_pairwise'] = apply_r_func(func=pairwise_forest_r, df=data)
leaguetable, pscores, consist, netsplit = apply_r_func(func=league_table_r, df=data)


