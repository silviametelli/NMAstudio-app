import dash
import os
import pandas as pd
from assets.storage import DEFAULT_DATA
from tools.utils import adjust_data, parse_contents
from collections import OrderedDict
from tools.utils import get_network


def __data_modal(open_modal_data, upload, submit, filename2,
               search_value_format, search_value_outcome1, search_value_outcome2,
               modal_data_is_open, modal_data_checks_is_open,
               contents, filename, dataselectors, TEMP_net_data_STORAGE,
               ):
    ctx = dash.callback_context
    if not ctx.triggered: button_id = 'No clicks yet'
    else:                 button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    #filename_storage = filename if filename is not None else ''
    #filename_exists = True if filename is not None or filename_storage =='' else False
    filename_exists = True if filename is not None else False

    if open_modal_data:
        if upload and button_id=='upload_modal_data':
            #filename_exists = True if filename is not None else False
            filename_exists = True if filename is not None else False

            try:
                data_user = parse_contents(contents, filename)

            except:
                raise ValueError('Data upload failed: likely UnicodeDecodeError or MultipleTypeError, check variable characters and type')
            var_dict = dict()
            var_outcomes = dict()
            if search_value_format == 'iv':
                if search_value_outcome2 is None:
                    out1_type, out1_direction = dataselectors[0:2]
                    studlab, treat1, treat2, rob, year, TE, seTE, n1, n2 = dataselectors[2: ] # first dataselector is the effect size
                    var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2',  rob: 'rob', year: 'year',
                                TE: 'TE', seTE: 'seTE', n1: 'n1', n2:'n2'}
                    var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction}
                else:
                    out1_type, out1_direction, out2_type, out2_direction,  = dataselectors[2:4]
                    studlab, treat1, treat2, rob, year, TE, seTE, n1, n2, TE2, seTE2, n21, n22 = dataselectors[4: ]
                    var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2',  rob: 'rob', year: 'year',
                                TE: 'TE', seTE: 'seTE', n1: 'n1', n2:'n2',
                                TE2: 'TE2', seTE2: 'seTE2', n21: 'n2.1', n22:  'n2.2'}
                    var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                    'effect_size2': out2_type, 'outcome2_direction': out2_direction}

            elif search_value_format == 'contrast':
                if search_value_outcome1 == 'continuous':
                    if search_value_outcome2 is None:
                        out1_type, out1_direction = dataselectors[0:2]
                        studlab, treat1, treat2, rob, year, y1, sd1, y2, sd2, n1, n2 = dataselectors[2: ]  # first dataselector is the effect size
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    y1: 'y1', sd1: 'sd1',
                                    y2: 'y2', sd2: 'sd2', n1: 'n1', n2: 'n2'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction}

                    elif search_value_outcome2 == 'continuous':
                        out1_type, out1_direction, out2_type, out2_direction, = dataselectors[0:4]
                        studlab, treat1, treat2, rob, year, y1, sd1, y2, sd2, n1, n2, y21, sd12, y22, sd22, n21, n22 = dataselectors[4: ]
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    y1: 'y1', sd1: 'sd1', y2: 'y2', sd2: 'sd2', n1: 'n1', n2: 'n2', y21: 'y2.1', sd12: 'sd1.2', y22: 'y2.2', sd22: 'sd2.2',
                                    n21: 'n2.1', n22: 'n2.2'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                        'effect_size2': out2_type, 'outcome2_direction': out2_direction}
                    else:
                        out1_type, out1_direction, out2_type, out2_direction, = dataselectors[0:4]
                        studlab, treat1, treat2, rob, year, y1, sd1, y2, sd2, n1, n2, z1, z2, n21, n22 = dataselectors[4: ]
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    y1: 'y1', sd1: 'sd1', y2: 'y2', sd2: 'sd2', n1: 'n1', n2: 'n2', z1: 'z1', z2: 'z2',
                                    n21: 'n2.1', n22: 'n2.2'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                        'effect_size2': out2_type, 'outcome2_direction': out2_direction}

                if search_value_outcome1 == 'binary':
                    if search_value_outcome2 is None:
                        out1_type, out1_direction = dataselectors[0:2]
                        studlab, treat1, treat2, rob, year, r1, n1, r2, n2 = dataselectors[2: ]  # first dataselector is the effect size
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    r1: 'r1', r2: 'r2', n1: 'n1', n2: 'n2'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction}

                    elif search_value_outcome2 == 'continuous':
                        out1_type, out2_type, out1_direction, out2_direction, = dataselectors[0:4]
                        studlab, treat1, treat2, rob, year, r1, r2, n1, n2, y21, sd12, y22, sd22, n21, n22 = dataselectors[4: ]  # first dataselector is the effect size
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    r1: 'r1', r2: 'r2', n1: 'n1', n2: 'n2',  y21: 'y2.1', sd12: 'sd1.2', y22: 'y2.2', sd22: 'sd2.2', n21: 'n2.1', n22: 'n2.2'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                        'effect_size2': out2_type, 'outcome2_direction': out2_direction}
                    else:
                        out1_type, out2_type, out1_direction, out2_direction, = dataselectors[0:4]
                        studlab, treat1, treat2, rob, year, r1, r2, n1, n2, z1, z2, n21, n22 = dataselectors[4: ]  # first dataselector is the effect size
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    r1: 'r1', r2: 'r2', n1: 'n1', n2: 'n2',
                                    z1: 'z1', z2: 'z2', n21: 'n2.1', n22: 'n2.2',
                                    }
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                        'effect_size2': out2_type, 'outcome2_direction': out2_direction}
            else:  #long format
                if search_value_outcome1 == 'continuous':
                    if search_value_outcome2 is None:
                        out1_type, out1_direction = dataselectors[0:2]
                        studlab, treat, rob, year, y, sd, n = dataselectors[2: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    y: 'y', sd: 'sd', n: 'n'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction}

                    elif search_value_outcome2 == 'continuous':
                        out1_type, out2_type, out1_direction, out2_direction, = dataselectors[0:4]
                        studlab, treat, rob, year, y, sd, n, y2, sd2, n2 = dataselectors[4: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    y: 'y', sd: 'sd', n: 'n', y2: 'y2', sd2: 'sd2', n2: 'n2'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                        'effect_size2': out2_type, 'outcome2_direction': out2_direction}
                    else:
                        out1_type, out2_type, out1_direction, out2_direction, = dataselectors[0:4]
                        studlab, treat, rob, year, y, sd, n, z1, nz = dataselectors[4: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    y: 'y', sd: 'sd', n: 'n', z1: 'z1', nz: 'nz'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                        'effect_size2': out2_type, 'outcome2_direction': out2_direction}
                if search_value_outcome1 == 'binary':
                    if search_value_outcome2 is None:
                        out1_type, out1_direction = dataselectors[0:2]
                        studlab, treat, rob, year, r, n = dataselectors[2: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    r: 'r', n: 'n'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction}

                    elif search_value_outcome2 == 'continuous':
                        out1_type, out2_type, out1_direction, out2_direction, = dataselectors[0:4]
                        studlab, treat, rob, year, r, n, y2, sd2, n2 = dataselectors[4: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    r: 'r', n: 'n', y2: 'y2', sd2: 'sd2', n2:'n2'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                        'effect_size2': out2_type, 'outcome2_direction': out2_direction}
                    else:
                        out1_type, out2_type, out1_direction, out2_direction, = dataselectors[0:4]
                        studlab, treat, rob, year, r, n, z1, nz = dataselectors[4: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    r: 'r', n: 'n', z1:'z1', nz: 'nz'}
                        var_outcomes = {'effect_size1': out1_type, 'outcome1_direction': out1_direction,
                                        'effect_size2': out2_type, 'outcome2_direction': out2_direction}

            data_user.rename(columns=var_dict, inplace=True)
            var_outs = pd.Series(var_outcomes, index=var_outcomes.keys())

            if len(var_outcomes.keys()) == 2:
                data_user['effect_size1'] = var_outs['effect_size1']
                data_user['outcome1_direction'] = var_outs['outcome1_direction']
            if len(var_outcomes.keys()) == 4:
                data_user['effect_size1'] = var_outs['effect_size1']
                data_user['outcome1_direction'] = var_outs['outcome1_direction']
                data_user['effect_size2'] = var_outs['effect_size2']
                data_user['outcome2_direction'] = var_outs['outcome2_direction']

            try:
                data = adjust_data(data_user, search_value_format, search_value_outcome2)

                TEMP_net_data_STORAGE = data.to_json(orient='split')
            #except:
                 #TEMP_net_data_STORAGE = {}
                 #raise ValueError('Data conversion failed')

            except Exception as Rconsole_error_data:
                TEMP_net_data_STORAGE = {}
                error = Rconsole_error_data
                return modal_data_is_open, modal_data_checks_is_open, TEMP_net_data_STORAGE, filename_exists, str(error), True

            return not modal_data_is_open, not modal_data_checks_is_open, TEMP_net_data_STORAGE, filename_exists, '', False

        if submit and button_id == 'submit_modal_data':

            return modal_data_is_open, not modal_data_checks_is_open and (not modal_data_is_open), TEMP_net_data_STORAGE, filename_exists, '', False

        return not modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE, filename_exists, '', False
    else:
        return modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE, filename_exists, '', False



def __modal_SUBMIT_button(submit,  reset_btn,
                        token_data, token_btn,
                        token_data_load, token_load_btn,
                        filename,
                        TEMP_net_data_STORAGE,
                        TEMP_net_data_out2_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        TEMP_user_elements_STORAGE,
                        TEMP_user_elements_out2_STORAGE,
                        TEMP_forest_data_STORAGE,
                        TEMP_forest_data_out2_STORAGE,
                        TEMP_forest_data_prws_STORAGE,
                        TEMP_forest_data_prws_out2_STORAGE,
                        TEMP_ranking_data_STORAGE,
                        TEMP_funnel_data_STORAGE,
                        TEMP_funnel_data_out2_STORAGE,
                        TEMP_league_table_data_STORAGE,
                        TEMP_net_split_data_STORAGE,
                        TEMP_net_split_data_out2_STORAGE,
                        TEMP_net_split_ALL_data_STORAGE,
                        TEMP_net_split_ALL_data_out2_STORAGE,
                        ):
    """ reads in temporary data for all analyses and outputs them in non-temp storages """
    submit_modal_data_trigger = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'submit_modal_data.n_clicks' in triggered: submit_modal_data_trigger = True
    token_btn_triggered = False
    if 'button-token.n_clicks' in triggered: token_btn_triggered = True
    load_btn_triggered = False
    if 'load-project.n_clicks' in triggered: load_btn_triggered = True
    OUT_DATA = [TEMP_net_data_STORAGE, TEMP_net_data_out2_STORAGE, TEMP_consistency_data_STORAGE,
                TEMP_user_elements_STORAGE,
                TEMP_user_elements_out2_STORAGE, TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE,
                TEMP_forest_data_prws_STORAGE,
                TEMP_forest_data_prws_out2_STORAGE, TEMP_ranking_data_STORAGE, TEMP_funnel_data_STORAGE,
                TEMP_funnel_data_out2_STORAGE,
                TEMP_league_table_data_STORAGE, TEMP_net_split_data_STORAGE, TEMP_net_split_data_out2_STORAGE,
                TEMP_net_split_ALL_data_STORAGE,
                TEMP_net_split_ALL_data_out2_STORAGE]
    OUT_DATA_NAMES = ["TEMP_net_data_STORAGE", "TEMP_net_data_out2_STORAGE", "TEMP_consistency_data_STORAGE",
                "TEMP_user_elements_STORAGE",
                "TEMP_user_elements_out2_STORAGE", "TEMP_forest_data_STORAGE", "TEMP_forest_data_out2_STORAGE",
                "TEMP_forest_data_prws_STORAGE",
                "TEMP_forest_data_prws_out2_STORAGE", "TEMP_ranking_data_STORAGE", "TEMP_funnel_data_STORAGE",
                "TEMP_funnel_data_out2_STORAGE",
                "TEMP_league_table_data_STORAGE", "TEMP_net_split_data_STORAGE", "TEMP_net_split_data_out2_STORAGE",
                "TEMP_net_split_ALL_data_STORAGE",
                "TEMP_net_split_ALL_data_out2_STORAGE"]
    if submit_modal_data_trigger:  # Is triggered by submit_modal_data.n_clicks
            return OUT_DATA
    else:  # Must be triggered by reset_project.n_clicks
        if token_btn_triggered and filename and len(token_data['token']) >= 6:
            usr_token = token_data['token']
            directory = f"{usr_token}"
            parent_dir = "USR_DATASETS/"
            path = os.path.join(parent_dir, directory)
            os.mkdir(path)
            for i in range(len(OUT_DATA)):
                df_i = OUT_DATA[i]
                dfname_i = OUT_DATA_NAMES[i]

                if (df_i is not None) and (type(df_i) != list) and (type(df_i) != dict):

                    df_i = pd.read_json(df_i, orient='split')
                    df_i.to_csv(f'{path}/{dfname_i}.csv', encoding='utf-8')

                else:
                    df_i = pd.DataFrame(dict())
                    df_i.to_csv(f'{path}/{dfname_i}.csv', encoding='utf-8')

            return OUT_DATA

        else:
            if not load_btn_triggered:
                return [data.to_json(orient='split')
                    if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE']
                    else data
                    for label, data in DEFAULT_DATA.items()][:-2]

            else:

                usr_token_load = token_data_load
                directory_load = f"{usr_token_load}"
                parent_dir_load = "USR_DATASETS/"
                path = os.path.join(parent_dir_load, directory_load)


                NET_DATA_USR = pd.read_csv(f'{path}/TEMP_net_data_STORAGE.csv')
                NET_DATA2_USR= pd.read_csv(f'{path}/TEMP_net_data_out2_STORAGE.csv')

                DEFAULT_ELEMENTS_USR = USER_ELEMENTS_USR = get_network(df=NET_DATA_USR)
                DEFAULT_ELEMENTS2_USR = USER_ELEMENTS2_USR = get_network(df=NET_DATA2_USR) if not NET_DATA2_USR.empty else []

                FOREST_DATA_USR = pd.read_csv(f'{path}/TEMP_forest_data_STORAGE.csv')
                FOREST_DATA_OUT2_USR = pd.read_csv(f'{path}/TEMP_forest_data_out2_STORAGE.csv')
                FOREST_DATA_PRWS_USR = pd.read_csv(f'{path}/TEMP_forest_data_prws_STORAGE.csv')
                FOREST_DATA_PRWS_OUT2_USR = pd.read_csv(f'{path}/TEMP_forest_data_out2_STORAGE.csv')
                LEAGUE_TABLE_DATA_USR = pd.read_csv(f'{path}/TEMP_league_table_data_STORAGE.csv', index_col=0)
                replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
                LEAGUE_TABLE_DATA_USR = LEAGUE_TABLE_DATA_USR.fillna('')
                LEAGUE_TABLE_DATA_USR = pd.DataFrame(
                    [[replace_and_strip(col) for col in list(row)] for idx, row in LEAGUE_TABLE_DATA_USR.iterrows()],
                    columns=LEAGUE_TABLE_DATA_USR.columns,
                    index=LEAGUE_TABLE_DATA_USR.index)
                CINEMA_NET_DATA1_USR = None
                CINEMA_NET_DATA2_USR = None
                CONSISTENCY_DATA_USR = pd.read_csv(f'{path}/TEMP_consistency_data_STORAGE.csv')
                NETSPLIT_DATA_USR = pd.read_csv(f'{path}/TEMP_net_split_data_STORAGE.csv')
                NETSPLIT_DATA_OUT2_USR = pd.read_csv(f'{path}/TEMP_net_split_data_out2_STORAGE.csv')
                NETSPLIT_DATA_ALL_USR = pd.read_csv(f'{path}/TEMP_net_split_ALL_data_STORAGE.csv')
                NETSPLIT_DATA_ALL_OUT2_USR = pd.read_csv(f'{path}/TEMP_net_split_ALL_data_out2_STORAGE.csv')
                RANKING_DATA_USR = pd.read_csv(f'{path}/TEMP_ranking_data_STORAGE.csv')
                FUNNEL_DATA_USR = pd.read_csv(f'{path}/TEMP_funnel_data_STORAGE.csv')
                FUNNEL_DATA_OUT2_USR = pd.read_csv(f'{path}/TEMP_funnel_data_out2_STORAGE.csv')

                USER_DATA = OrderedDict(net_data_STORAGE=NET_DATA_USR,
                                        net_data_out2_STORAGE=NET_DATA2_USR,
                                        consistency_data_STORAGE=CONSISTENCY_DATA_USR,
                                        user_elements_STORAGE=USER_ELEMENTS_USR,
                                        user_elements_out2_STORAGE=USER_ELEMENTS2_USR,
                                        forest_data_STORAGE=FOREST_DATA_USR,
                                        forest_data_out2_STORAGE=FOREST_DATA_OUT2_USR,
                                        forest_data_prws_STORAGE=FOREST_DATA_PRWS_USR,
                                        forest_data_prws_out2_STORAGE=FOREST_DATA_PRWS_OUT2_USR,
                                        ranking_data_STORAGE=RANKING_DATA_USR,
                                        funnel_data_STORAGE=FUNNEL_DATA_USR,
                                        funnel_data_out2_STORAGE=FUNNEL_DATA_OUT2_USR,
                                        league_table_data_STORAGE=LEAGUE_TABLE_DATA_USR,
                                        net_split_data_STORAGE=NETSPLIT_DATA_USR,
                                        net_split_data_out2_STORAGE=NETSPLIT_DATA_OUT2_USR,
                                        net_split_ALL_data_STORAGE=NETSPLIT_DATA_ALL_USR,
                                        net_split_ALL_data_out2_STORAGE=NETSPLIT_DATA_ALL_OUT2_USR,
                                        #cinema_net_data1_STORAGE=CINEMA_NET_DATA1_USR,
                                        #cinema_net_data2_STORAGE=CINEMA_NET_DATA2_USR,
                                        )

                # Remove unnamed columns
                for label, data in USER_DATA.items():
                    if (data is not None) and (type(data) != list) and (type(data) != dict):
                        USER_DATA[label] = USER_DATA[label].loc[:, ~USER_DATA[label].columns.str.contains('^Unnamed')]

                return [data.to_json(orient='split')
                    if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE']
                    else data
                    for label, data in USER_DATA.items()]