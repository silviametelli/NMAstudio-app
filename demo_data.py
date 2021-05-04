import numpy as np, pandas as pd
from assets.effect_sizes import OR_effect_measure, MD_effect_measure


def get_demo_data():
    # Save default dataframes for demo use
    GLOBAL_DATA = {'net_data':             pd.read_csv('db/psoriasis_wide.csv'),
                   'cinema_net_data':      pd.read_csv('db/Cinema/PASI90_cinema.csv'),
                   'forest_data':          pd.read_csv('db/forest_data/forest_data.csv'),
                   'forest_data_pairwise': pd.read_csv('db/forest_data/forest_data_pairwise.csv'),
                   'forest_data_outcome2': pd.read_csv('db/forest_data/forest_data_outcome2.csv'),
                   'league_table_data':    pd.read_csv('db/league_table_data/league_table.csv', index_col=0)}

    ##add columns TE,seTE from raw data
    #GLOBAL_DATA['net_data']['TE'] =  OR_effect_measure(GLOBAL_DATA['net_data'],'r1','r2','n1', 'n2')[0].astype('float64')
    #GLOBAL_DATA['net_data']['seTE'] = OR_effect_measure(GLOBAL_DATA['net_data'],'r1','r2','n1','n2')[1].astype('float64')
    GLOBAL_DATA['net_data']  = GLOBAL_DATA['net_data'].loc[:, ~GLOBAL_DATA['net_data'].columns.str.contains('^Unnamed')]
    if 'rob' not in GLOBAL_DATA['net_data'].select_dtypes(include=['int16', 'int32', 'int64',
                                                                   'float16', 'float32', 'float64']).columns:
            if any(GLOBAL_DATA['net_data']['rob'].str.contains('l|m|h', na=False)):
               GLOBAL_DATA['net_data']['rob'].replace({'l':1,'m':2,'h':3}, inplace=True)
            elif any(GLOBAL_DATA['net_data']['rob'].str.contains('L|M|H', na=False)):
              GLOBAL_DATA['net_data']['rob'].replace({'L': 1, 'M': 2, 'H': 3}, inplace=True)
    else:
        pass

    replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
    leaguetable = GLOBAL_DATA['league_table_data'].copy(deep=True)
    GLOBAL_DATA['league_table_data'] = pd.DataFrame([[replace_and_strip(col) for col in list(row)]
                                                     for idx, row in leaguetable.iterrows()], columns=leaguetable.columns, index=leaguetable.index)

    #for year slider
    if 'year' not in GLOBAL_DATA['net_data'].columns:
        GLOBAL_DATA['net_data']['year'] = GLOBAL_DATA['net_data'][f'{GLOBAL_DATA["net_data"].filter(regex="YEAR|year|Year|year publication|Year Publication|Year publication|year Publication").columns[0]}']
        #GLOBAL_DATA['net_data']['year'] = GLOBAL_DATA['net_data']['year'].astype(str)

    GLOBAL_DATA['y_min'] = GLOBAL_DATA['net_data'].year.min()
    GLOBAL_DATA['y_max'] = GLOBAL_DATA['net_data'].year.max()
    GLOBAL_DATA['dwnld_bttn_calls'] = 0
    GLOBAL_DATA['WAIT'] = False

    return GLOBAL_DATA

### end demo data function