# from assets.modal_values import *
import dash_core_components as dcc
import pandas as pd
from tools.utils import get_network, get_network_new
from tools.PATHS import SESSION_TYPE
from collections import OrderedDict


NET_DATA = pd.read_csv('db/psoriasis_wide_complete.csv', encoding='iso-8859-1')
NET_DATA2 = NET_DATA.drop(["TE1", "seTE1", "n11", "n21"], axis=1)
# NET_DATA2 = NET_DATA2.rename(columns={"TE2": "TE2", "seTE2": "seTE2", "n12": "n1", "n22": "n2"})
DEFAULT_ELEMENTS = USER_ELEMENTS = get_network_new(df=NET_DATA, i=0)
DEFAULT_ELEMENTS2 = USER_ELEMENTS2 = get_network_new(df=NET_DATA2, i=1)
FOREST_DATA = pd.read_csv('db/forest_data/forest_data.csv')
FOREST_DATA_OUT2 = pd.read_csv('db/forest_data/forest_data_outcome2.csv')
FOREST_DATA_PRWS = pd.read_csv('db/forest_data/forest_data_pairwise.csv')
FOREST_DATA_PRWS_OUT2 = pd.read_csv('db/forest_data/forest_data_pairwise_out2.csv')
LEAGUE_TABLE_DATA1 = pd.read_csv('db/league_table_data/league_1.csv', index_col=0)
LEAGUE_TABLE_DATA2 = pd.read_csv('db/league_table_data/league_2.csv', index_col=0)

replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
LEAGUE_TABLE_DATA1 = LEAGUE_TABLE_DATA1.fillna('')
LEAGUE_TABLE_DATA1 = pd.DataFrame([[replace_and_strip(col) for col in list(row)] for idx, row in LEAGUE_TABLE_DATA1.iterrows()],
                           columns=LEAGUE_TABLE_DATA1.columns,
                           index=LEAGUE_TABLE_DATA1.index)
LEAGUE_TABLE_DATA2 = LEAGUE_TABLE_DATA2.fillna('')
LEAGUE_TABLE_DATA2 = pd.DataFrame([[replace_and_strip(col) for col in list(row)] for idx, row in LEAGUE_TABLE_DATA2.iterrows()],
                           columns=LEAGUE_TABLE_DATA2.columns,
                           index=LEAGUE_TABLE_DATA2.index)
CINEMA_NET_DATA1 =  pd.read_csv('db/Cinema/cinema_report_PASI90.csv')
CINEMA_NET_DATA2 =  pd.read_csv('db/Cinema/cinema_report_SAE.csv')
CONSISTENCY_DATA = pd.read_csv('db/consistency/consistency.csv')
NETSPLIT_DATA =  pd.read_csv('db/consistency/consistency_netsplit.csv')
NETSPLIT_DATA_OUT2 =  pd.read_csv('db/consistency/consistency_netsplit_out2.csv')
NETSPLIT_DATA_ALL =  pd.read_csv('db/consistency/netsplit_all.csv')
NETSPLIT_DATA_ALL_OUT2 =  pd.read_csv('db/consistency/netsplit_all_out2.csv')
RANKING_DATA = pd.read_csv('db/ranking/rank.csv')
RANKING_DATA2 = pd.read_csv('db/ranking/rank2.csv')
FUNNEL_DATA = pd.read_csv('db/funnel/funnel_data.csv')
FUNNEL_DATA_OUT2 = pd.read_csv('db/funnel/funnel_data_out2.csv')


DEFAULT_DATA = OrderedDict(net_data_STORAGE=[NET_DATA],
                        #    net_data_out2_STORAGE=NET_DATA2,
                           consistency_data_STORAGE= [CONSISTENCY_DATA],
                           # user_elements_STORAGE=[USER_ELEMENTS, USER_ELEMENTS2],
                        #    user_elements_out2_STORAGE=USER_ELEMENTS2,
                           forest_data_STORAGE=[FOREST_DATA,FOREST_DATA_OUT2],
                        #    forest_data_out2_STORAGE=FOREST_DATA_OUT2,
                           forest_data_prws_STORAGE=[FOREST_DATA_PRWS,FOREST_DATA_PRWS_OUT2],
                        #    forest_data_prws_out2_STORAGE=FOREST_DATA_PRWS_OUT2,
                           ranking_data_STORAGE=[RANKING_DATA,RANKING_DATA2],
                           funnel_data_STORAGE=[FUNNEL_DATA,FUNNEL_DATA_OUT2],
                        #    funnel_data_out2_STORAGE=FUNNEL_DATA_OUT2,
                        #    league_table_data_STORAGE=[LEAGUE_TABLE_DATA2],
                           league_table_data_STORAGE=[LEAGUE_TABLE_DATA1,LEAGUE_TABLE_DATA2],
                           net_split_data_STORAGE=[NETSPLIT_DATA,NETSPLIT_DATA_OUT2],
                        #    net_split_data_out2_STORAGE = NETSPLIT_DATA_OUT2,
                           net_split_ALL_data_STORAGE=[NETSPLIT_DATA_ALL,NETSPLIT_DATA_ALL_OUT2],
                        #    net_split_ALL_data_out2_STORAGE=NETSPLIT_DATA_ALL_OUT2,
                           cinema_net_data_STORAGE=[CINEMA_NET_DATA1, CINEMA_NET_DATA2]
                        #    cinema_net_data2_STORAGE=CINEMA_NET_DATA2,
                           )


OPTIONS_VAR = [{'label': '{}'.format(col), 'value': col} for col in NET_DATA.select_dtypes(['number']).columns]
N_CLASSES = USER_ELEMENTS[-1]["data"]['n_class'] if "n_class" in USER_ELEMENTS[-1]["data"] else 1

# STORAGE = [dcc.Store(id=label, data=(data.to_json(orient='split')
#                                      if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE', 'filename_data_STORAGE']
#                                      else data),
#                      storage_type=SESSION_TYPE) 
#            for label, data in DEFAULT_DATA.items()] + [
#             dcc.Store(id='TEMP_'+new_id, storage_type=SESSION_TYPE) for new_id in DEFAULT_DATA.keys()
# ] + [
# dcc.Store(id='data_and_league_table_DATA', data=dict(), storage_type=SESSION_TYPE),
# dcc.Store(id='net_download_activation', data=False, storage_type=SESSION_TYPE),
# dcc.Store(id='datatable-filename-upload', data=None, storage_type=SESSION_TYPE),
# dcc.Store(id='uploaded_datafile_to_disable_cinema', data=False, storage_type=SESSION_TYPE),
# dcc.Store(id='username-token-upload', data=None, storage_type=SESSION_TYPE),

# ]


STORAGE = [
    dcc.Store(
        id=f'{label}',
        data=[(data.to_json(orient='split')
              if label not in ['user_elements_STORAGE', 'filename_data_STORAGE']
              else data) for data in data_each],
        storage_type=SESSION_TYPE
    )
    for label, data_each in DEFAULT_DATA.items()
]+ [
    dcc.Store(id='TEMP_'+new_id, storage_type=SESSION_TYPE) for new_id in DEFAULT_DATA.keys()
]+[
dcc.Store(id='data_and_league_table_DATA', data=dict(), storage_type=SESSION_TYPE),
dcc.Store(id='net_download_activation', data=False, storage_type=SESSION_TYPE),
dcc.Store(id='datatable-filename-upload', data=None, storage_type=SESSION_TYPE),
dcc.Store(id='uploaded_datafile_to_disable_cinema', data=False, storage_type=SESSION_TYPE),
dcc.Store(id='username-token-upload', data=None, storage_type=SESSION_TYPE),

]

