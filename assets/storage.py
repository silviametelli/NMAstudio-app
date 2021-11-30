# from assets.modal_values import *
import dash_core_components as dcc
import pandas as pd
from tools.utils import get_network, write_session_pickle
import uuid
from tools.PATHS import __SESSIONS_FOLDER, TODAY
from collections import OrderedDict

SESSION_ID = uuid.uuid4().__str__()
SESSION_PICKLE_PATH = f'{__SESSIONS_FOLDER}/{SESSION_ID}.pickle'
SESSION_PICKLE = {'wait':False}

SESSION_TYPE = 'session'

write_session_pickle(dct=SESSION_PICKLE, path=SESSION_PICKLE_PATH)
# read_session_pickle(SESSION_PICKLE_PATH)

NET_DATA = pd.read_csv('db/psoriasis_wide.csv')
CONSISTENCY_DATA = pd.read_csv('db/consistency/consistency.csv')
DEFAULT_ELEMENTS = USER_ELEMENTS = get_network(df=NET_DATA)
FOREST_DATA = pd.read_csv('db/forest_data/forest_data.csv')
FOREST_DATA_OUT2 = pd.read_csv('db/forest_data/forest_data_outcome2.csv')
FOREST_DATA_PRWS = pd.read_csv('db/forest_data/forest_data_pairwise.csv')
FOREST_DATA_PRWS_OUT2 = pd.read_csv('db/forest_data/forest_data_pairwise_out2.csv')
LEAGUE_TABLE_DATA = pd.read_csv('db/league_table_data/league_table.csv', index_col=0)
CINEMA_NET_DATA1 =  pd.read_csv('db/Cinema/cinema_report_PASI90.csv')
CINEMA_NET_DATA2 =  pd.read_csv('db/Cinema/cinema_report_SAE.csv')
NETSPLIT_DATA =  pd.read_csv('db/consistency/consistency_netsplit.csv')
NETSPLIT_DATA_OUT2 =  pd.read_csv('db/consistency/consistency_netsplit_out2.csv')
RANKING_DATA = pd.read_csv('db/ranking/rank.csv')
FUNNEL_DATA = pd.read_csv('db/funnel/funnel_data.csv')
FUNNEL_DATA_OUT2 = pd.read_csv('db/funnel/funnel_data_out2.csv')

DEFAULT_DATA = OrderedDict(net_data_STORAGE=NET_DATA,
                           consistency_data_STORAGE=CONSISTENCY_DATA,
                           user_elements_STORAGE=USER_ELEMENTS,
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
                           cinema_net_data1_STORAGE=CINEMA_NET_DATA1,
                           cinema_net_data2_STORAGE=CINEMA_NET_DATA2,
                           )
OPTIONS_VAR = [{'label': '{}'.format(col), 'value': col}
               for col in NET_DATA.select_dtypes(['number']).columns]
N_CLASSES = USER_ELEMENTS[-1]["data"]['n_class'] if "n_class" in USER_ELEMENTS[-1]["data"] else 1

STORAGE = [dcc.Store(id=label, data=data.to_json(orient='split') if label!='user_elements_STORAGE' else data,
                     storage_type=SESSION_TYPE)
           for label, data in DEFAULT_DATA.items()
           ] + [
    dcc.Store(id='consts_STORAGE', data={'dwnld_bttn_calls':0,
                                         'today':TODAY,
                                         'session_ID':SESSION_ID,
                                         'session_pickle_path':SESSION_PICKLE_PATH},
              storage_type=SESSION_TYPE)
] + [
    dcc.Store(id='TEMP_'+new_id, storage_type=SESSION_TYPE) for new_id in DEFAULT_DATA.keys()
]

