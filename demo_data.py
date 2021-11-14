import numpy as np, pandas as pd
from assets.effect_sizes import get_OR, get_RR, get_MD
from utils  import get_network

def get_demo_data():
    # Save default dataframes for demo use
    GLOBAL_DATA = {'net_data':             pd.read_csv('db/psoriasis_wide.csv'),
                   # 'cinema_net_data1':     pd.read_csv('db/Cinema/cinema_report_PASI90.csv'),
                   # 'cinema_net_data2':     pd.read_csv('db/Cinema/cinema_report_SAE.csv'),
                   # 'forest_data':          pd.read_csv('db/forest_data/forest_data.csv'),
                   # 'forest_data_pairwise': pd.read_csv('db/forest_data/forest_data_pairwise.csv'),
                   # 'forest_data_outcome2': pd.read_csv('db/forest_data/forest_data_outcome2.csv'),
                   # 'consistency_data':     pd.read_csv('db/consistency/consistency.csv'),
                   # 'netsplit_data':        pd.read_csv('db/consistency/consistency_netsplit.csv'),
                   # 'ranking_data':         pd.read_csv('db/ranking/rank.csv'),
                   # 'funnel_data':          pd.read_csv('db/funnel/funnel_data.csv'),
                   # 'league_table_data':    pd.read_csv('db/league_table_data/league_table.csv', index_col=0)
                   }

    # if GLOBAL_DATA['net_data']['rob'].dtype == np.object:
    #     GLOBAL_DATA['net_data']['rob'] = (GLOBAL_DATA['net_data']['rob'].str.lower()
    #                                       .replace({'low': 'l', 'medium': 'm', 'high': 'h'})
    #                                       .replace({'l': 1, 'm': 2, 'h': 3}))

    # replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
    # leaguetable = GLOBAL_DATA['league_table_data'].copy(deep=True)
    # GLOBAL_DATA['league_table_data'] = pd.DataFrame([[replace_and_strip(col) for col in list(row)]
    #                                                 for idx, row in leaguetable.iterrows()], columns=leaguetable.columns, index=leaguetable.index)

    #for year slider
    # if 'year' not in GLOBAL_DATA['net_data'].columns:
    #     GLOBAL_DATA['net_data']['year'] = GLOBAL_DATA['net_data'][f'{GLOBAL_DATA["net_data"].filter(regex="YEAR|year|Year|year publication|Year Publication|Year publication|year Publication").columns[0]}']
        #GLOBAL_DATA['net_data']['year'] = GLOBAL_DATA['net_data']['year'].astype(str)

    # GLOBAL_DATA['y_min'] = GLOBAL_DATA['net_data'].year.min()
    # GLOBAL_DATA['y_max'] = GLOBAL_DATA['net_data'].year.max()
    # GLOBAL_DATA['dwnld_bttn_calls'] = 0
    # GLOBAL_DATA['WAIT'] = False
    if "treat1_class" and "treat2_class" in GLOBAL_DATA['net_data'].columns:
        GLOBAL_DATA['n_class'] = get_network(GLOBAL_DATA['net_data'])[-1]["data"]['n_class']

    return GLOBAL_DATA

### end demo data function
