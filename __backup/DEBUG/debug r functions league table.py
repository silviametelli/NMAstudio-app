# from assets.modal_values import *
from tools.utils import write_session_pickle, adjust_data
import uuid, pandas as pd
from tools.PATHS import __SESSIONS_FOLDER
SESSION_ID = uuid.uuid4().__str__()
SESSION_PICKLE_PATH = f'{__SESSIONS_FOLDER}/{SESSION_ID}.pickle'
SESSION_PICKLE = {'wait':False}
write_session_pickle(dct=SESSION_PICKLE, path=SESSION_PICKLE_PATH)
from assets.effect_sizes import *
# ---------R2Py Resources --------------------------------------------------------------------------------------------#
from rpy2.robjects import pandas2ri
pandas2ri.activate()
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri  # Define the R script and loads the instance in Python
from rpy2.robjects.conversion import localconverter
r = ro.r
r['source']('R_Codes/all_R_functions.R')  # Loading the function we have defined in R.
run_NetMeta_r = ro.globalenv['run_NetMeta']  # Get run_NetMeta from R
league_table_r = ro.globalenv['league_rank']  # Get league_table from R
pairwise_forest_r = ro.globalenv['pairwise_forest']  # Get pairwise_forest from R
funnel_plot_r = ro.globalenv['funnel_funct']  # Get pairwise_forest from R
run_pairwise_data_r = ro.globalenv['get_pairwise_data']  # Get pairwise data from long format from R
CMAP = ['purple', 'green', 'blue', 'red', 'black', 'yellow', 'orange', 'pink', 'brown', 'grey']

def apply_r_func(func, df):
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(df.reset_index(drop=True))
    func_r_res = func(dat=df_r)
    r_result = pandas2ri.rpy2py(func_r_res)
    if isinstance(r_result, ro.vectors.ListVector):
        leaguetable, pscores, consist, netsplit = (ro.conversion.rpy2py(rf) for rf in r_result)
        return leaguetable, pscores, consist, netsplit
    else:
        df_result = r_result.reset_index(drop=True)  # Convert back to a pandas.DataFrame.
        return df_result


df = NET_DATA = pd.read_csv('db/chilados_wide.csv')

data = adjust_data(data=df, dataselectors=['MD', ''],
            value_format='contrast', value_outcome1='continuous',
            value_outcome2=None)


leaguetable, pscores, consist, netsplit = apply_r_func(func=league_table_r, df=data)
