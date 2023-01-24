import os, shutil, pickle, base64, io
from pandas.api.types import is_numeric_dtype
from tools.PATHS import __TEMP_LOGS_AND_GLOBALS, __SESSIONS_FOLDER, YESTERDAY
from assets.effect_sizes import *
# ---------R2Py Resources --------------------------------------------------------------------------------------------#
import rpy2
from rpy2.robjects import pandas2ri  # Define the R script and loads the instance in Python
#pandas2ri.activate()
import rpy2.robjects as ro
import rpy2.rinterface_lib as rlib
from rpy2.robjects.conversion import localconverter
#import plotly.express as px

r = ro.r
r['source']('R_Codes/all_R_functions.R')  # Loading the function we have defined in R.
run_NetMeta_r = ro.globalenv['run_NetMeta']  # Get run_NetMeta from R
league_table_r = ro.globalenv['league_rank']  # Get league_table from R
pairwise_forest_r = ro.globalenv['pairwise_forest']  # Get pairwise_forest from R
funnel_plot_r = ro.globalenv['funnel_funct']  # Get pairwise_forest from R
run_pairwise_data_long_r = ro.globalenv['get_pairwise_data_long']  # Get pairwise data from long format from R
run_pairwise_data_contrast_r = ro.globalenv['get_pairwise_data_contrast']  # Get pairwise data from contrast format from R


## read R console for printing errors
def  my_consoleread(promp: str) -> str:
    custom_prompt = f'R is asking this: {promp}'
    return input(custom_prompt)

def print_console_error():
    rlib.callbacks.consoleread = my_consoleread

def apply_r_func(func, df):
    df['rob'] = df['rob'].astype("string")
    df['rob'] = (df['rob'].str.lower()
                      .str.strip()
                      .replace({'low': 'l', 'medium': 'm', 'high': 'h'})
                      .replace({'l': 1, 'm': 2, 'h': 3}))
    with localconverter(ro.default_converter + pandas2ri.converter):
        #print(df.reset_index(drop=True))
        df_r = ro.conversion.py2rpy(df.reset_index(drop=True))
    func_r_res = func(dat=df_r)
    r_result = pandas2ri.rpy2py(func_r_res)

    if isinstance(r_result, ro.vectors.ListVector):
        with localconverter(ro.default_converter + pandas2ri.converter):
            leaguetable, pscores, consist, netsplit, netsplit_all  = (ro.conversion.rpy2py(rf) for rf in r_result)
        return leaguetable, pscores, consist, netsplit, netsplit_all
    else:
        df_result = r_result.reset_index(drop=True)  # Convert back to a pandas.DataFrame.
        return df_result


def apply_r_func_two_outcomes(func, df):
    df['rob'] = df['rob'].astype("string")
    df['rob'] = (df['rob'].str.lower()
                 .str.strip()
                 .replace({'low': 'l', 'medium': 'm', 'high': 'h'})
                 .replace({'l': 1, 'm': 2, 'h': 3}))
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(df.reset_index(drop=True))
    func_r_res = func(dat=df_r, outcome2=True)
    r_result = pandas2ri.rpy2py(func_r_res)

    if isinstance(r_result, ro.vectors.ListVector):
        with localconverter(ro.default_converter + pandas2ri.converter):
            leaguetable, pscores, consist, netsplit, netsplit2, netsplit_all, netsplit_all2 = (ro.conversion.rpy2py(rf) for rf in r_result)
        return leaguetable, pscores, consist, netsplit, netsplit2, netsplit_all, netsplit_all2
    else:
        df_result = r_result.reset_index(drop=True)  # Convert back to a pandas.DataFrame.
        return df_result

# ----------------------------------------------------------------------------------
## -------------------------------------------------------------------------------- ##

def generate_ssl_perm_and_key(cert_name, key_name):
    os.system(f"""openssl req -newkey rsa:4096 \
                                 -x509 \
                                 -sha256 \
                                 -days 3650 \
                                 -nodes \
                                 -out {cert_name} \
                                 -keyout {key_name} \
                                 -subj '/C=FR/ST=Paris/L=Paris/O=Security/OU=CRESS/CN=www.nmastudioapp.com'""")
    return cert_name, key_name

# def write_session_pickle(dct, path):
#     with open(path, 'wb') as f:
#         pickle.dump(dct, f, protocol=pickle.HIGHEST_PROTOCOL)
# def read_session_pickle(path):
#     return pickle.load(open(path, 'rb'))


## --------------------------------MISC-------------------------------------------- ##
def set_slider_marks(y_min, y_max, years):
    return {int(x): {'label': str(x),
                     'style': {'color': 'white', 'font-size':'10px',
                               'opacity':1 if x in (y_min,y_max) else 0}}
            for x in np.unique(years).astype('int')
            }


## ----------------------------  NETWORK FUNCTION --------------------------------- ##
CMAP = ['bisque', 'gold', 'light blue', 'tomato', 'orange', 'olivedrab', 'darkslategray', 'orchid', 'brown', 'navy', 'palegreen']
#CMAP = px.colors.qualitative.Light24

def get_network(df):
    num_classes = None
    df = df.dropna(subset=['TE', 'seTE'])
    if "treat1_class" and "treat2_class" in df.columns:
        df_treat = df.treat1.dropna().append(df.treat2.dropna()).reset_index(drop=True)
        df_class = df.treat1_class.dropna().append(df.treat2_class.dropna()).reset_index(drop=True)
        long_df_class = pd.concat([df_treat,df_class], axis=1).reset_index(drop=True)
        long_df_class = long_df_class.rename({long_df_class.columns[0]: 'treat', long_df_class.columns[1]: 'class'}, axis='columns')
        if not is_numeric_dtype(long_df_class.columns[1]):
            long_df_class["class_codes"] = long_df_class['class'].astype("category").cat.codes
            long_df_class = long_df_class.rename({long_df_class.columns[0]: 'treat', long_df_class.columns[1]: 'class_names',
                                                  long_df_class.columns[2]: 'class'},
                                                  axis='columns')
        all_nodes_class = long_df_class.drop_duplicates().sort_values(by='treat').reset_index(drop=True)
        num_classes = all_nodes_class['class'].max() + 1 #because all_nodes_class was shifted by minus 1
    sorted_edges = np.sort(df[['treat1', 'treat2']], axis=1)  ## removes directionality
    df.loc[:,['treat1', 'treat2']] = sorted_edges
    edges = df.groupby(['treat1', 'treat2']).TE.count().reset_index()
    df_n1g = df.rename(columns={'treat1': 'treat', 'n1': 'n'}).groupby(['treat'])
    df_n2g = df.rename(columns={'treat2': 'treat', 'n2': 'n'}).groupby(['treat'])
    df_n1, df_n2 = df_n1g.n.sum(), df_n2g.n.sum()
    all_nodes_sized = df_n1.add(df_n2, fill_value=0)
    df_n1, df_n2 = df_n1g.rob.value_counts(), df_n2g.rob.value_counts()
    all_nodes_robs = df_n1.add(df_n2, fill_value=0).rename(('count')).unstack('rob', fill_value=0)
    all_nodes_sized = pd.concat([all_nodes_sized, all_nodes_robs], axis=1).reset_index()

    if "treat1_class" and "treat2_class" in df.columns: all_nodes_sized = pd.concat([all_nodes_sized, all_nodes_class['class']], axis=1).reset_index(drop=True)

    if isinstance(all_nodes_sized.columns[2], str):
        for c in {'1', '2', '3'}.difference(all_nodes_sized): all_nodes_sized[c] = 0
    elif all_nodes_sized.columns[2] in {1, 2, 3}:
        for c in {1, 2, 3}.difference(all_nodes_sized): all_nodes_sized[c] = 0
    elif all_nodes_sized.columns[2] in {1.0, 2.0, 3.0}:
        for c in {1.0, 2.0, 3.0}.difference(all_nodes_sized): all_nodes_sized[c] = 0

    all_nodes_sized.drop(columns=[col for col in all_nodes_sized if col not in ['treat', 'n', 'class', 1.0, 2.0, 3.0, 1, 2, 3, '1','2','3']], inplace=True)

    cy_edges = [{'data': {'source': source, 'target': target,
                          'weight':  weight * 1 if (len(edges)<100 and len(edges)>13) else weight * 0.75 if len(edges)<13  else weight * 0.7,
                          'weight_lab': weight}}
                for source, target, weight in edges.values]
    max_trsfrmd_size_nodes = np.sqrt(all_nodes_sized.iloc[:,1].max()) / 70

    if "treat1_class" and "treat2_class" in df.columns:
        cy_nodes = [{"data": {"id": target,
                              "label": target,
                              "n_class": num_classes,
                              'size': np.sqrt(size) / max_trsfrmd_size_nodes,
                              'pie1': r1 / (r1 + r2 + r3) if not r1 + r2 + r3 == 0 else None,
                              'pie2': r2 / (r1 + r2 + r3) if not r1 + r2 + r3 == 0 else None,
                              'pie3': r3 / (r1 + r2 + r3) if not r1 + r2 + r3 == 0 else None,
                              }, 'classes': f'{CMAP[cls]}'} for target, size, r1, r2, r3, cls in all_nodes_sized.values]
    else:
        cy_nodes = [{"data": {"id": target,
                              "label": target,
                              'classes': 'genesis',
                              'size': np.sqrt(size) / max_trsfrmd_size_nodes,
                              'pie1': r1 / (r1 + r2 + r3) if not r1 + r2 + r3 == 0 else None,
                              'pie2': r2 / (r1 + r2 + r3) if not r1 + r2 + r3 == 0 else None,
                              'pie3': r3 / (r1 + r2 + r3) if not r1 + r2 + r3 == 0 else None}} for
                    target, size, r1, r2, r3 in all_nodes_sized.values]

    return cy_edges + cy_nodes


## ---------------------------  Parse DATA  -------------------------------- ##

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    missing_values = ["n/a", "na", "--", '.', 'missing', 'NA', 'NAN', 'None', '', ' ']
    if 'csv' in filename:  # Assume that the user uploaded a CSV file
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8', errors = 'ignore')), na_values = missing_values)
        except:
            try:
                df = pd.read_csv(io.StringIO(decoded.decode('unicode-escape',errors ='ignore')), na_values = missing_values)
            except:
                df = pd.read_csv(io.StringIO(decoded.decode('ISO-8859-1')))
        return df
    elif 'xls' in filename:  # TODO: add xls options: so far this is not working
        return pd.read_excel(io.BytesIO(decoded))


## ----------------------  Reshape pd data from long to wide  --------------------------- ##

def adjust_data(data, value_format, value_outcome2):
    data['rob'] = data['rob'].astype("string")
    data['rob'] = (data['rob'].str.lower()
                      .str.strip()
                      .replace({'low': 'l', 'medium': 'm', 'high': 'h'})
                      .replace({'l': 1, 'm': 2, 'h': 3}))

    if value_format=='long':
        try:
            for c in data.columns:
                if data[c].dtype == object:
                    data[c].fillna('__NONE__', inplace=True)
        except:
            pass
        if value_outcome2:
            data = apply_r_func_two_outcomes(func=run_pairwise_data_long_r, df=data)
        else:

            data = apply_r_func(func=run_pairwise_data_long_r, df=data)
        data[data=='__NONE__'] = np.nan
    if value_format=='contrast':
        for c in data.columns:
            if data[c].dtype == object:
                data[c].fillna('__NONE__', inplace=True)
        if value_outcome2:
            data = apply_r_func_two_outcomes(func=run_pairwise_data_contrast_r, df=data)
        else:
            data = apply_r_func(func=run_pairwise_data_contrast_r, df=data)
        data[data=='__NONE__'] = np.nan

    if value_format == 'iv':
        data = data
        if value_outcome2:
            data = data
    return data


## ----------------------  FUNCTIONS for Running data analysis in R  --------------------------- ##

def data_checks(df):
    return {'Conversion to wide format failed': True,
            'Some variables are a mix of numerical and string values': all(df.applymap(type).nunique() >1),
            'Missing values present': df.isnull().sum().sum() < 1,
            'Non-negative variances': (any(df.seTE>0) if ("seTE2" not in df.columns) else (any(df.seTE > 0) or any(df.seTE2 > 0)))
            }


## run netmeta for nma forest plots
def run_network_meta_analysis(df):
    data_forest = apply_r_func(func=run_NetMeta_r, df=df)
    return data_forest


## run metagen for pairwise forest plots
def run_pairwise_MA(df):
    forest_MA = apply_r_func(func=pairwise_forest_r, df=df)
    return forest_MA


## run netmeta for league table, consistency tables and ranking plots
def generate_league_table(df, outcome2=False):

    if outcome2: leaguetable, pscores, consist, netsplit, netsplit2, netsplit_all, netsplit_all2  = apply_r_func_two_outcomes(func=league_table_r, df=df)
    else:        leaguetable, pscores, consist, netsplit, netsplit_all = apply_r_func(func=league_table_r, df=df)

    replace_and_strip = lambda x: x.replace(' (', '\n(').strip()

    leaguetable = leaguetable.fillna('')

    leaguetable = pd.DataFrame([[replace_and_strip(col) for col in list(row)] for idx, row in leaguetable.iterrows()],
                               columns=leaguetable.columns,
                               index=leaguetable.index)

    leaguetable.columns = leaguetable.index = leaguetable.values.diagonal()

    if outcome2:
        return leaguetable, pscores, consist, netsplit, netsplit2, netsplit_all, netsplit_all2
    else:
        return leaguetable, pscores, consist, netsplit, netsplit_all


## run netmeta for funnel plots
def generate_funnel_data(df):
    funnel = apply_r_func(func=funnel_plot_r, df=df)
    return funnel


def create_sessions_folders():
    for dir in [__TEMP_LOGS_AND_GLOBALS, __SESSIONS_FOLDER, __TEMP_LOGS_AND_GLOBALS]:
        if not os.path.exists(dir):
            os.makedirs(dir)
        # os.makedirs(__TEMP_LOGS_AND_GLOBALS, exist_ok=True)


def clean_sessions_folders():
    """Deletes all folders in __temp_logs_and_globals (__TEMP_LOGS_AND_GLOBALS)
    created more than 2 days ago."""
    del_folders = [p for p in os.listdir(__TEMP_LOGS_AND_GLOBALS)
                   if p[0]!='.' and p<YESTERDAY]
    for dir in del_folders:
        shutil.rmtree(f'{__TEMP_LOGS_AND_GLOBALS}/{dir}', ignore_errors=True)



