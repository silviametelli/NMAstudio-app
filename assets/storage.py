from assets.modal_values import *
import pandas as pd
from utils import get_network, write_session_pickle
import uuid, datetime, os, pickle

TODAY = str(datetime.datetime.today().date())
__SESSIONS_FOLDER = f'__temp_logs_and_globals/{TODAY}'
SESSION_ID = uuid.uuid4().__str__()
SESSION_PICKLE_PATH = f'{__SESSIONS_FOLDER}/{SESSION_ID}.pickle'
SESSION_PICKLE = {'wait':False}

if not os.path.exists(__SESSIONS_FOLDER):
    os.mkdir(__SESSIONS_FOLDER)
write_session_pickle(dct=SESSION_PICKLE, path=SESSION_PICKLE_PATH)
# read_session_pickle(SESSION_PICKLE_PATH)

NET_DATA = pd.read_csv('db/psoriasis_wide.csv', index_col=0)
CONSISTENCY_DATA = pd.read_csv('db/consistency/consistency.csv')
# DEFAULT_ELEMENTS = USER_ELEMENTS = get_network(df=NET_DATA)
FOREST_DATA = pd.read_csv('db/forest_data/forest_data.csv')
FOREST_DATA_OUT2 = pd.read_csv('db/forest_data/forest_data_outcome2.csv')
FOREST_DATA_PRWS = pd.read_csv('db/forest_data/forest_data_pairwise.csv')

RANKING_DATA = pd.read_csv('db/ranking/rank.csv')
FUNNEL_DATA = pd.read_csv('db/funnel/funnel_data.csv')


STORAGE = [
dcc.Store(id='net_data_STORAGE', data=NET_DATA.to_json( orient='split')),
# dcc.Store(id='consistency_data_STORAGE', data=CONSISTENCY_DATA.to_json( orient='split')),
# dcc.Store(id='default_elements_STORAGE', data=DEFAULT_ELEMENTS),
# dcc.Store(id='user_elements_STORAGE', data=USER_ELEMENTS),
dcc.Store(id='forest_data_STORAGE', data=FOREST_DATA.to_json( orient='split')),
dcc.Store(id='forest_data_out2_STORAGE', data=FOREST_DATA_OUT2.to_json( orient='split')),
dcc.Store(id='forest_data_prws_STORAGE', data=FOREST_DATA_PRWS.to_json( orient='split')),
dcc.Store(id='ranking_data_STORAGE', data=RANKING_DATA.to_json( orient='split')),
dcc.Store(id='funnel_data_STORAGE', data=FUNNEL_DATA.to_json( orient='split')),
dcc.Store(id='temporarily_uploaded_data'),
dcc.Store(id='submitted_data'),
dcc.Store(id='NMA_data_STORAGE'),
dcc.Store(id='LEAGUETABLE_data_STORAGE'),
dcc.Store(id='consts_STORAGE', data={'dwnld_bttn_calls':0,
                                     'today':TODAY,
                                     'session_ID':SESSION_ID,
                                     'session_pickle_path':SESSION_PICKLE_PATH}),
]