# from assets.modal_values import *
import dash_core_components as dcc
import pandas as pd
from tools.utils import get_network
from tools.PATHS import SESSION_TYPE
from collections import OrderedDict


NET_DATA = pd.read_csv('db/psoriasis_wide_complete.csv', encoding='iso-8859-1')
NET_DATA2 = NET_DATA.drop(["TE", "seTE", "n1", "n2"], axis=1)
NET_DATA2 = NET_DATA2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
DEFAULT_ELEMENTS = USER_ELEMENTS = get_network(df=NET_DATA)
DEFAULT_ELEMENTS2 = USER_ELEMENTS2 = get_network(df=NET_DATA2)
FOREST_DATA = pd.read_csv('db/forest_data/forest_data.csv')
FOREST_DATA_OUT2 = pd.read_csv('db/forest_data/forest_data_outcome2.csv')
FOREST_DATA_PRWS = pd.read_csv('db/forest_data/forest_data_pairwise.csv')
FOREST_DATA_PRWS_OUT2 = pd.read_csv('db/forest_data/forest_data_pairwise_out2.csv')
LEAGUE_TABLE_DATA = pd.read_csv('db/league_table_data/league_table.csv', index_col=0)
replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
LEAGUE_TABLE_DATA = LEAGUE_TABLE_DATA.fillna('')
LEAGUE_TABLE_DATA = pd.DataFrame([[replace_and_strip(col) for col in list(row)] for idx, row in LEAGUE_TABLE_DATA.iterrows()],
                           columns=LEAGUE_TABLE_DATA.columns,
                           index=LEAGUE_TABLE_DATA.index)
CINEMA_NET_DATA1 =  pd.read_csv('db/Cinema/cinema_report_PASI90.csv')
CINEMA_NET_DATA2 =  pd.read_csv('db/Cinema/cinema_report_SAE.csv')
CONSISTENCY_DATA = pd.read_csv('db/consistency/consistency.csv')
NETSPLIT_DATA =  pd.read_csv('db/consistency/consistency_netsplit.csv')
NETSPLIT_DATA_OUT2 =  pd.read_csv('db/consistency/consistency_netsplit_out2.csv')
NETSPLIT_DATA_ALL =  pd.read_csv('db/consistency/netsplit_all.csv')
NETSPLIT_DATA_ALL_OUT2 =  pd.read_csv('db/consistency/netsplit_all_out2.csv')
RANKING_DATA = pd.read_csv('db/ranking/rank.csv')
FUNNEL_DATA = pd.read_csv('db/funnel/funnel_data.csv')
FUNNEL_DATA_OUT2 = pd.read_csv('db/funnel/funnel_data_out2.csv')

DEFAULT_DATA = OrderedDict(net_data_STORAGE=NET_DATA,
                           net_data_out2_STORAGE=NET_DATA2,
                           consistency_data_STORAGE=CONSISTENCY_DATA,
                           user_elements_STORAGE=USER_ELEMENTS,
                           user_elements_out2_STORAGE=USER_ELEMENTS2,
                           forest_data_STORAGE=FOREST_DATA,
                           forest_data_out2_STORAGE=FOREST_DATA_OUT2,
                           forest_data_prws_STORAGE=FOREST_DATA_PRWS,
                           forest_data_prws_out2_STORAGE=FOREST_DATA_PRWS_OUT2,
                           ranking_data_STORAGE=RANKING_DATA,
                           funnel_data_STORAGE=FUNNEL_DATA,
                           funnel_data_out2_STORAGE=FUNNEL_DATA_OUT2,
                           league_table_data_STORAGE=LEAGUE_TABLE_DATA,
                           net_split_data_STORAGE=NETSPLIT_DATA,
                           net_split_data_out2_STORAGE=NETSPLIT_DATA_OUT2,
                           net_split_ALL_data_STORAGE=NETSPLIT_DATA_ALL,
                           net_split_ALL_data_out2_STORAGE=NETSPLIT_DATA_ALL_OUT2,
                           cinema_net_data1_STORAGE=CINEMA_NET_DATA1,
                           cinema_net_data2_STORAGE=CINEMA_NET_DATA2,
                           )

OPTIONS_VAR = [{'label': '{}'.format(col), 'value': col} for col in NET_DATA.select_dtypes(['number']).columns]
N_CLASSES = USER_ELEMENTS[-1]["data"]['n_class'] if "n_class" in USER_ELEMENTS[-1]["data"] else 1

STORAGE = [dcc.Store(id=label, data=(data.to_json(orient='split')
                                     if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE', 'filename_data_STORAGE']
                                     else data),
                     storage_type=SESSION_TYPE)
           for label, data in DEFAULT_DATA.items()] + [
            dcc.Store(id='TEMP_'+new_id, storage_type=SESSION_TYPE) for new_id in DEFAULT_DATA.keys()
] + [
dcc.Store(id='data_and_league_table_DATA', data=dict(), storage_type=SESSION_TYPE),
dcc.Store(id='net_download_activation', data=False, storage_type=SESSION_TYPE),
dcc.Store(id='datatable-filename-upload', data=None, storage_type=SESSION_TYPE),
dcc.Store(id='uploaded_datafile_to_disable_cinema', data=False, storage_type=SESSION_TYPE),

]

