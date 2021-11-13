import pickle, numpy as np, pandas as pd
from PATHS import TEMP_PATH
from  collections  import OrderedDict

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
## -------------------------------------------------------------------------------- ##


## ----------------------------  NETWORK FUNCTION --------------------------------- ##
def get_network(df):
    global num_classes
    cmaps = OrderedDict()
    cmaps['Sequential'] = ['purple', 'green', 'blue', 'red', 'black', 'yellow', 'black', 'orange', 'pink']
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
    df[['treat1', 'treat2']] = sorted_edges
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
                          }, 'classes': f'{cmaps["Sequential"][cls]}'} for target, size, r1, r2, r3, cls in all_nodes_sized.values]
    else:
        print(all_nodes_robs, all_nodes_sized.values)

        cy_nodes = [{"data": {"id": target,
                          "label": target,
                          'classes':'genesis',
                          'size': np.sqrt(size)/max_trsfrmd_size,
                          'pie1': r1/(r1+r2+r3),
                          'pie2':r2/(r1+r2+r3),
                          'pie3': r3/(r1+r2+r3)}} for target, size, r1, r2, r3 in all_nodes_sized.values]
    return cy_edges + cy_nodes

## ----------------------  Reshape pd data from long to wide  --------------------------- ##

def data_reshape(long_df):
    wide_df = long_df.pivot(index='treat')
    return wide_df


