import pickle
from tools.PATHS import TEMP_PATH
from assets.effect_sizes import *
# ---------R2Py Resources --------------------------------------------------------------------------------------------#
from rpy2.robjects import pandas2ri  # Define the R script and loads the instance in Python
import rpy2.robjects as ro
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
        with localconverter(ro.default_converter + pandas2ri.converter):
            leaguetable, pscores, consist, netsplit = (ro.conversion.rpy2py(rf) for rf in r_result)
        return leaguetable, pscores, consist, netsplit
    else:
        df_result = r_result.reset_index(drop=True)  # Convert back to a pandas.DataFrame.
        return df_result

def apply_r_func_twooutcomes(func, df):
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(df.reset_index(drop=True))
    func_r_res = func(dat=df_r, outcome2=True)
    r_result = pandas2ri.rpy2py(func_r_res)
    if isinstance(r_result, ro.vectors.ListVector):
        with localconverter(ro.default_converter + pandas2ri.converter):
            leaguetable, pscores, consist, netsplit, netsplit2 = (ro.conversion.rpy2py(rf) for rf in r_result)
        return leaguetable, pscores, consist, netsplit, netsplit2
    else:
        df_result = r_result.reset_index(drop=True)  # Convert back to a pandas.DataFrame.
        return df_result
# ----------------------------------------------------------------------------------
## -------------------------------------------------------------------------------- ##
def write_node_topickle(store_node):
    with open(f'{TEMP_PATH}/selected_nodes.pickle', 'wb') as f:
        pickle.dump(store_node, f, protocol=pickle.HIGHEST_PROTOCOL)

def read_node_frompickle():
    return pickle.load(open(f'{TEMP_PATH}/selected_nodes.pickle', 'rb'))

def write_edge_topickle(store_edge):
    with open(f'{TEMP_PATH}/selected_edges.pickle', 'wb') as f:
        pickle.dump(store_edge, f, protocol=pickle.HIGHEST_PROTOCOL)

def read_edge_frompickle():
    return pickle.load(open(f'{TEMP_PATH}/selected_edges.pickle', 'rb'))

def write_session_pickle(dct, path):
    with open(path, 'wb') as f:
        pickle.dump(dct, f, protocol=pickle.HIGHEST_PROTOCOL)

def read_session_pickle(path):
    return pickle.load(open(path, 'rb'))
## --------------------------------MISC-------------------------------------------- ##
def set_slider_marks(y_min, y_max, years):
    return {int(x): {'label': str(x),
                     'style': {'color': 'white', 'font-size':'10px',
                               'opacity':1 if x in (y_min,y_max) else 0}}
            for x in np.unique(years).astype('int')
            }

## ----------------------------  NETWORK FUNCTION --------------------------------- ##
def get_network(df):
    df = df.dropna(subset=['TE', 'seTE'])
    if "treat1_class" and "treat2_class" in df.columns:
        df_treat = df.treat1.dropna().append(df.treat2.dropna()).reset_index(drop=True)
        df_class = df.treat1_class.dropna().append(df.treat2_class.dropna()).reset_index(drop=True)
        long_df_class = pd.concat([df_treat,df_class], axis=1).reset_index(drop=True)
        long_df_class = long_df_class.rename({long_df_class.columns[0]: 'treat', long_df_class.columns[1]: 'class'}, axis='columns')
        long_df_class['class'].replace(dict(zip(long_df_class['class'], [int(x-1) for x in long_df_class['class']])), inplace=True)
        all_nodes_class = long_df_class.drop_duplicates().sort_values(by='treat').reset_index(drop=True)
        num_classes = all_nodes_class['class'].max()+1 #because all_nodes_class was shifted by minus 1
    sorted_edges = np.sort(df[['treat1', 'treat2']], axis=1)  ## removes directionality
    df.loc[:,['treat1', 'treat2']] = sorted_edges
    edges = df.groupby(['treat1', 'treat2']).TE.count().reset_index()
    df_n1g = df.rename(columns={'treat1': 'treat', 'n1':'n'}).groupby(['treat'])
    df_n2g = df.rename(columns={'treat2': 'treat', 'n2':'n'}).groupby(['treat'])
    df_n1, df_n2 = df_n1g.n.sum(), df_n2g.n.sum()
    all_nodes_sized = df_n1.add(df_n2, fill_value=0)
    df_n1, df_n2 = df_n1g.rob.value_counts(), df_n2g.rob.value_counts()
    all_nodes_robs = df_n1.add(df_n2, fill_value=0).rename(('count')).unstack('rob', fill_value=0)
    all_nodes_sized = pd.concat([all_nodes_sized, all_nodes_robs], axis=1).reset_index()
    if "treat1_class" and "treat2_class" in df.columns: all_nodes_sized = pd.concat([all_nodes_sized, all_nodes_class['class']], axis=1).reset_index(drop=True)
    for c in {1,2,3}.difference(all_nodes_sized): all_nodes_sized[c] = 0
    cy_edges = [{'data': {'source': source,  'target': target,
                          'weight': weight * 1, 'weight_lab': weight}}
                for source, target, weight in edges.values]
    max_trsfrmd_size = np.sqrt(all_nodes_sized.iloc[:,1].max()) / 70
    if "treat1_class" and "treat2_class" in df.columns:
        cy_nodes = [{"data": {"id": target,
                          "label": target,
                          "n_class": num_classes,
                          'size': np.sqrt(size)/max_trsfrmd_size,
                          'pie1': r1/(r1+r2+r3), 'pie2':r2/(r1+r2+r3), 'pie3': r3/(r1+r2+r3),
                          }, 'classes': f'{CMAP[cls]}'} for target, size, r1, r2, r3, cls in all_nodes_sized.values]
    else:
        cy_nodes = [{"data": {"id": target,
                          "label": target,
                          'classes':'genesis',
                          'size': np.sqrt(size)/max_trsfrmd_size,
                          'pie1': r1/(r1+r2+r3),
                          'pie2':r2/(r1+r2+r3),
                          'pie3': r3/(r1+r2+r3)}} for target, size, r1, r2, r3 in all_nodes_sized.values]
    return cy_edges + cy_nodes

## ----------------------  Reshape pd data from long to wide  --------------------------- ##

def adjust_data(data, dataselectors, value_format, value_outcome1, value_outcome2):

    effect_sizes = {'continuous': {'MD': get_MD, 'SMD': get_SMD},
                    'binary': {'OR': get_OR, 'RR': get_RR}}

    data['effect_size1'] = dataselectors[0]
    get_effect_size1 = effect_sizes[value_outcome1][dataselectors[0]]

    if value_format=='long':
        data = apply_r_func(func=run_pairwise_data_r, df=data)

    if value_format=='contrast':
        data['TE'], data['seTE'] = get_effect_size1(data, effect=1)
        if value_outcome2:
            data['effect_size2'] = dataselectors[1]
            get_effect_size2 = effect_sizes[value_outcome2][dataselectors[1]]
            data['TE2'], data['seTE2'] = get_effect_size2(data, effect=2)
    if data['rob'].dtype == np.object:
        data['rob'] = (data['rob'].str.lower()
                      .replace({'low': 'l', 'medium': 'm', 'high': 'h'})
                      .replace({'l': 1, 'm': 2, 'h': 3}))

    if value_format == 'iv':
        data['effect_size1'] = dataselectors[0]
        if value_outcome2: data['effect_size2'] = dataselectors[1]
        data = data

    return data

## ----------------------  FUNCTIONS for Running data analysis  --------------------------- ##

def data_checks(df):
    return {'check1': True, 'check2': False, 'check3': False, 'check4': True} #TODO: add specific checks


def run_network_meta_analysis(df):
    data_forest = apply_r_func(func=run_NetMeta_r, df=df)
    return data_forest



def run_pairwise_MA(df):
    forest_MA = apply_r_func(func=pairwise_forest_r, df=df)
    return forest_MA


def generate_league_table(df, outcome2=False):

    if outcome2: leaguetable, pscores, consist, netsplit, netsplit2 = apply_r_func_twooutcomes(func=league_table_r, df=df)
    else:        leaguetable, pscores, consist, netsplit = apply_r_func(func=league_table_r, df=df)

    replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
    leaguetable = pd.DataFrame([[replace_and_strip(col) for col in list(row)] for idx, row in leaguetable.iterrows()],
                               columns=leaguetable.columns,
                               index=leaguetable.index)
    leaguetable.columns = leaguetable.index = leaguetable.values.diagonal()
    if outcome2:
        return leaguetable, pscores, consist, netsplit, netsplit2
    else:
        return leaguetable, pscores, consist, netsplit



def generate_funnel_data(df):
    funnel = apply_r_func(func=funnel_plot_r, df=df)
    return funnel



