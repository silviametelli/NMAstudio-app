import dash
import os
import pandas as pd
import numpy as np
from assets.storage import DEFAULT_DATA
from tools.utils import adjust_data, parse_contents
from collections import OrderedDict
from tools.utils import get_network, get_network_new
import secrets
from dash import html



def __data_modal(
        # open_modal_data,
        trans_to_results, 
        upload, submit, filename2,
               search_value_format, search_value_outcome1, search_value_outcome2,modal_transitivity_is_open,
            #    modal_data_is_open, 
               modal_data_checks_is_open,
               contents, filename, dataselectors, TEMP_net_data_STORAGE,
               ):
    ctx = dash.callback_context
    if not ctx.triggered: button_id = 'No clicks yet'
    else:                 button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    #filename_storage = filename if filename is not None else ''
    #filename_exists = True if filename is not None or filename_storage =='' else False
    filename_exists = True if filename is not None else False
    treat_list=[{'label': '{}'.format('treat_name'), 'value': 'treat_name'}]

    # if open_modal_data:
    if upload and button_id=='upload_modal_data2':
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
        
        if search_value_format == 'iv':
            combined_values = np.concatenate((data_user['treat1'], data_user['treat2']))
            unique_values = np.unique(combined_values)
            treat_list = [{'label': '{}'.format(treat_name), 'value': treat_name}
                for treat_name in sorted(unique_values)]
        elif search_value_format == 'contrast':
            combined_values = np.concatenate((data_user['treat1'], data_user['treat2']))
            unique_values = np.unique(combined_values)
            treat_list = [{'label': '{}'.format(treat_name), 'value': treat_name}
                for treat_name in sorted(unique_values)]
        else:
            treat_list = [{'label': '{}'.format(treat_name), 'value': treat_name}
                for treat_name in sorted(data_user['treat'].unique())]
            


        try:
            data = adjust_data(data_user, search_value_format, search_value_outcome2)

            TEMP_net_data_STORAGE = data.to_json(orient='split')
        #except:
                #TEMP_net_data_STORAGE = {}
                #raise ValueError('Data conversion failed')

        except Exception as Rconsole_error_data:
            TEMP_net_data_STORAGE = {}
            error = Rconsole_error_data
        
            return modal_transitivity_is_open, modal_data_checks_is_open, TEMP_net_data_STORAGE, filename_exists, str(error), True, treat_list

        return modal_transitivity_is_open, not modal_data_checks_is_open, TEMP_net_data_STORAGE, filename_exists, '', False, treat_list

    if submit and button_id == 'submit_modal_data':
        return  not modal_transitivity_is_open, not modal_data_checks_is_open, TEMP_net_data_STORAGE, filename_exists, '', False, treat_list 

    if trans_to_results:
        return not modal_transitivity_is_open, modal_data_checks_is_open, TEMP_net_data_STORAGE, filename_exists, '', False, treat_list
    
    return modal_transitivity_is_open, modal_data_checks_is_open, TEMP_net_data_STORAGE, filename_exists, '', False, treat_list
    # else:
    #     return modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE, filename_exists, '', False, treat_list


def __data_trans(
        #  trans_to_results,
              upload,  filename2,
              submit,
               search_value_format, overall_variables, number_outcomes,outcome_type,
               effectselectors, directionselectors, variableselectors, 
               modal_data_checks_is_open,
               contents, filename, 
               TEMP_net_data_STORAGE,
               TEMP_raw_data_STORAGE
               ):

    

    ctx = dash.callback_context
    if not ctx.triggered: button_id = 'No clicks yet'
    
    else:                 button_id = ctx.triggered[0]['prop_id'].split('.')[0]


    #filename_storage = filename if filename is not None else ''
    #filename_exists = True if filename is not None or filename_storage =='' else False
    filename_exists = True if filename is not None else False
    treat_list=[{'label': '{}'.format('treat_name'), 'value': 'treat_name'}]

    # if open_modal_data:
    # if ctx.triggered_id == "upload_modal_data2":
    if upload and button_id=='upload_modal_data2':
        #filename_exists = True if filename is not None else False
        filename_exists = True if filename is not None else False

        try:
            data_user = parse_contents(contents, filename)
            TEMP_raw_data_STORAGE = [data_user.to_json(orient='split')]

        except:
            raise ValueError('Data upload failed: likely UnicodeDecodeError or MultipleTypeError, check variable characters and type')
              
        var_dict = dict()
        var_outcomes = dict()
        number_outcomes = int(number_outcomes)
        effect_data = [[] for _ in range(number_outcomes)]
        direct_data = [[] for _ in range(number_outcomes)]


        if search_value_format == 'iv':
            
            studlab, treat1, treat2, rob, year = overall_variables[0:]
            var_dict1 = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year'}
            iv_data = [[] for _ in range(number_outcomes)]  # Initialize as a list of lists
            
            for i in range(number_outcomes):
                iv_data[i] = variableselectors[4 * i:4 + 4 * i]
                effect_data[i] = effectselectors[i]
                direct_data[i] = directionselectors[i]
            

            TE_dict = {iv_data[i][0]:f'TE{i+1}' for i in range(number_outcomes)}
            seTE_dict = {iv_data[i][1] : f'seTE{i+1}' for i in range(number_outcomes)}
            n1_dict = {iv_data[i][2]:f'n1{i+1}' for i in range(number_outcomes)}
            n2_dict = {iv_data[i][3]:f'n2{i+1}' for i in range(number_outcomes)}
            effect_size = {f'effect_size{i+1}' : effect_data[i] for i in range(number_outcomes)}
            direct = {f'outcome{i+1}_direction' :  direct_data[i] for i in range(number_outcomes)}
            


            var_dict = var_dict1.copy()  # Make a copy of the first dictionary
            var_dict.update({**TE_dict, **seTE_dict, **n1_dict, **n2_dict})  # Merge 
            var_outcomes.update({**effect_size, **direct})
            

        elif search_value_format == 'contrast':
            studlab, treat1, treat2, rob, year = overall_variables[0:]
            var_dict1 = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year'}
            len_n = [6 if type_i=='continuous' else 4 for type_i in outcome_type]
            len_ci = [sum(len_n[:i_n+1]) for i_n in range(len(len_n))]
            iv_data =[variableselectors[i:j] for i, j in zip([0] + len_ci[:-1], len_ci)]
            name_n = [
                    [
                    f'y1{j+1}', f'sd1{j+1}', f'y2{j+1}', f'sd2{j+1}', f'n1{j+1}', f'n2{j+1}'
                    ] if type_i == 'continuous' else [f'r1{j+1}', f'n1{j+1}', f'r2{j+1}', f'n2{j+1}']
                    for j, type_i in enumerate(outcome_type)
                ]
            
            for i in range(number_outcomes):
                effect_data[i] = effectselectors[i]
                direct_data[i] = directionselectors[i]
            
            var_dict = var_dict1.copy()
            effect_size = {f'effect_size{i+1}':  effect_data[i] for i in range(number_outcomes)}
            direct = {f'outcome{i+1}_direction':  direct_data[i] for i in range(number_outcomes)}
            
            result_dict = {}
            add_dirct = {}
            for sublist_a, sublist_b in zip(iv_data, name_n):  
                for key, value in zip(sublist_a, sublist_b):
                    add_dirct = {key: value}
                    result_dict.update({**add_dirct})

            var_dict.update({**result_dict})
            var_outcomes.update({**effect_size, **direct})

        else:

            studlab, treat, rob, year = overall_variables[0:]
            var_dict1 = {studlab: 'studlab', treat: 'treat',rob: 'rob', year: 'year'}
            len_n = [3 if type_i=='continuous' else 2 for type_i in outcome_type]
            len_ci = [sum(len_n[:i_n+1]) for i_n in range(len(len_n))]
            long_data =[variableselectors[i:j] for i, j in zip([0] + len_ci[:-1], len_ci)]
            name_n = [
                    [
                    f'y{j+1}', f'sd{j+1}',f'n{j+1}'
                    ] if type_i == 'continuous' else [f'r{j+1}', f'n{j+1}']
                    for j, type_i in enumerate(outcome_type)
                ]
            
            for i in range(number_outcomes):
                effect_data[i] = effectselectors[i]
                direct_data[i] = directionselectors[i]
            
            var_dict = var_dict1.copy()
            effect_size = {f'effect_size{i+1}':  effect_data[i] for i in range(number_outcomes)}
            direct = {f'outcome{i+1}_direction':  direct_data[i] for i in range(number_outcomes)}
            
            result_dict = {}
            add_dirct = {}
            for sublist_a, sublist_b in zip(long_data, name_n):  
                for key, value in zip(sublist_a, sublist_b):
                    add_dirct = {key: value}
                    result_dict.update({**add_dirct})

            var_dict.update({**result_dict})
            var_outcomes.update({**effect_size, **direct})


        data_user.rename(columns=var_dict, inplace=True)
        var_outs = pd.Series(var_outcomes, index=var_outcomes.keys())
        
        
        # data_user.to_csv('USR_DATASETS/test.csv', encoding='utf-8')

        for i_out in range(number_outcomes):
            data_user[f'effect_size{i_out+1}'] = var_outs[f'effect_size{i_out+1}']
            data_user[f'outcome{i_out+1}_direction'] = var_outs[f'outcome{i_out+1}_direction']
        
        if search_value_format == 'iv':
            combined_values = np.concatenate((data_user['treat1'], data_user['treat2']))
            unique_values = np.unique(combined_values)
            treat_list = [{'label': str(treat_name), 'value': str(treat_name)}
              for treat_name in sorted(unique_values)]
            
        
        elif search_value_format == 'contrast':
            combined_values = np.concatenate((data_user['treat1'], data_user['treat2']))
            unique_values = np.unique(combined_values)
            treat_list = [{'label': str(treat_name), 'value': str(treat_name)}
              for treat_name in sorted(unique_values)]
        else:
            treat_list = [{'label': str(treat_name), 'value': str(treat_name)}
              for treat_name in sorted(data_user['treat'].unique(), key=str)]
            
        
        
        try:
            data = adjust_data(data_user, search_value_format, number_outcomes)

            TEMP_net_data_STORAGE = [data.to_json(orient='split')]
            # data.to_csv('db/test_dat2.csv', encoding='utf-8')
     
        #except:
                #TEMP_net_data_STORAGE = {}
                #raise ValueError('Data conversion failed')

        except Exception as Rconsole_error_data:
            TEMP_net_data_STORAGE = []
            error = Rconsole_error_data
        
            return  modal_data_checks_is_open,TEMP_raw_data_STORAGE, TEMP_net_data_STORAGE, filename_exists, str(error), True, treat_list



        return  not modal_data_checks_is_open,TEMP_raw_data_STORAGE, TEMP_net_data_STORAGE, filename_exists, '', False, treat_list

    # if  ctx.triggered_id == "submit_modal_data":
    if submit and button_id == 'submit_modal_data':

        return   not modal_data_checks_is_open,TEMP_raw_data_STORAGE, TEMP_net_data_STORAGE, filename_exists, '', False, treat_list 
    
    # if  ctx.triggered_id == "trans_to_results":
    # if trans_to_results and button_id == 'trans_to_results':
        
    #     return  modal_data_checks_is_open, TEMP_net_data_STORAGE, filename_exists, '', False, treat_list

    return  modal_data_checks_is_open ,TEMP_raw_data_STORAGE, TEMP_net_data_STORAGE, filename_exists, '', False, treat_list
    # else:
    #     return modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE, filename_exists, '', False, treat_list












########## submit + load project using token
# def __modal_SUBMIT_button(submit,  reset_btn,
#                         token_data, token_btn,
#                         token_data_load, token_load_btn,
#                         filename,
#                         TEMP_net_data_STORAGE,
#                         TEMP_net_data_out2_STORAGE,
#                         TEMP_consistency_data_STORAGE,
#                         TEMP_user_elements_STORAGE,
#                         TEMP_user_elements_out2_STORAGE,
#                         TEMP_forest_data_STORAGE,
#                         TEMP_forest_data_out2_STORAGE,
#                         TEMP_forest_data_prws_STORAGE,
#                         TEMP_forest_data_prws_out2_STORAGE,
#                         TEMP_ranking_data_STORAGE,
#                         TEMP_funnel_data_STORAGE,
#                         TEMP_funnel_data_out2_STORAGE,
#                         TEMP_league_table_data_STORAGE,
#                         TEMP_net_split_data_STORAGE,
#                         TEMP_net_split_data_out2_STORAGE,
#                         TEMP_net_split_ALL_data_STORAGE,
#                         TEMP_net_split_ALL_data_out2_STORAGE,
#                         ):
#     """ reads in temporary data for all analyses and outputs them in non-temp storages """
#     submit_modal_data_trigger = False
#     triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
#     if 'submit_modal_data.n_clicks' in triggered: submit_modal_data_trigger = True
#     token_btn_triggered = False
#     if 'button-token.n_clicks' in triggered: token_btn_triggered = True
#     load_btn_triggered = False
#     if 'load-project.n_clicks' in triggered: load_btn_triggered = True
#     OUT_DATA = [TEMP_net_data_STORAGE, TEMP_net_data_out2_STORAGE, TEMP_consistency_data_STORAGE,
#                 TEMP_user_elements_STORAGE, TEMP_user_elements_out2_STORAGE, TEMP_forest_data_STORAGE,
#                 TEMP_forest_data_out2_STORAGE, TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2_STORAGE,
#                 TEMP_ranking_data_STORAGE, TEMP_funnel_data_STORAGE, TEMP_funnel_data_out2_STORAGE,
#                 TEMP_league_table_data_STORAGE, TEMP_net_split_data_STORAGE, TEMP_net_split_data_out2_STORAGE,
#                 TEMP_net_split_ALL_data_STORAGE, TEMP_net_split_ALL_data_out2_STORAGE]
#     OUT_DATA_NAMES = ["TEMP_net_data_STORAGE", "TEMP_net_data_out2_STORAGE", "TEMP_consistency_data_STORAGE",
#                 "TEMP_user_elements_STORAGE", "TEMP_user_elements_out2_STORAGE", "TEMP_forest_data_STORAGE",
#                 "TEMP_forest_data_out2_STORAGE", "TEMP_forest_data_prws_STORAGE", "TEMP_forest_data_prws_out2_STORAGE",
#                 "TEMP_ranking_data_STORAGE", "TEMP_funnel_data_STORAGE", "TEMP_funnel_data_out2_STORAGE",
#                 "TEMP_league_table_data_STORAGE", "TEMP_net_split_data_STORAGE", "TEMP_net_split_data_out2_STORAGE",
#                 "TEMP_net_split_ALL_data_STORAGE", "TEMP_net_split_ALL_data_out2_STORAGE"]
#     if submit_modal_data_trigger:  # Is triggered by submit_modal_data.n_clicks
#             return OUT_DATA + ['']
#     else:  # Must be triggered by reset_project.n_clicks
#         if token_btn_triggered and filename and len(token_data['token']) >= 6:
#             usr_token = token_data['token']
#             directory = f"{usr_token}"
#             parent_dir = "USR_DATASETS/"
#             path = os.path.join(parent_dir, directory)
#             os.mkdir(path)
#             for i in range(len(OUT_DATA)):
#                 df_i = OUT_DATA[i]
#                 dfname_i = OUT_DATA_NAMES[i]

#                 if (df_i is not None) and (type(df_i) != list) and (type(df_i) != dict):
#                     df_i = pd.read_json(df_i, orient='split')
#                     df_i.to_csv(f'{path}/{dfname_i}.csv', encoding='utf-8')

#                 else:
#                     df_i = pd.DataFrame(dict())
#                     df_i.to_csv(f'{path}/{dfname_i}.csv', encoding='utf-8')

#             return OUT_DATA + ['']

#         else:
#             if not load_btn_triggered:
#                 return [data.to_json(orient='split')
#                     if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE']
#                     else data
#                     for label, data in DEFAULT_DATA.items()][:-2] + ['']

#             else:
#                 usr_token_load_ = token_data_load
#                 parent_dir_load = "USR_DATASETS/"
#                 directory_load = f"{usr_token_load_}"
#                 path = os.path.join(parent_dir_load, directory_load)

#                 for foldername in os.listdir(parent_dir_load):
#                     d = foldername
#                     if not d.startswith('.'):
#                         if usr_token_load_ in d:

#                             NET_DATA_USR = pd.read_csv(f'{path}/TEMP_net_data_STORAGE.csv')
#                             NET_DATA2_USR= pd.read_csv(f'{path}/TEMP_net_data_out2_STORAGE.csv')
#                             DEFAULT_ELEMENTS_USR = USER_ELEMENTS_USR = get_network(df=NET_DATA_USR)
#                             DEFAULT_ELEMENTS2_USR = USER_ELEMENTS2_USR = get_network(df=NET_DATA2_USR) if not NET_DATA2_USR.empty else []
#                             FOREST_DATA_USR = pd.read_csv(f'{path}/TEMP_forest_data_STORAGE.csv')
#                             FOREST_DATA_OUT2_USR = pd.read_csv(f'{path}/TEMP_forest_data_out2_STORAGE.csv')
#                             FOREST_DATA_PRWS_USR = pd.read_csv(f'{path}/TEMP_forest_data_prws_STORAGE.csv')
#                             FOREST_DATA_PRWS_OUT2_USR = pd.read_csv(f'{path}/TEMP_forest_data_out2_STORAGE.csv')
#                             LEAGUE_TABLE_DATA_USR = pd.read_csv(f'{path}/TEMP_league_table_data_STORAGE.csv', index_col=0)
#                             replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
#                             LEAGUE_TABLE_DATA_USR = LEAGUE_TABLE_DATA_USR.fillna('')
#                             LEAGUE_TABLE_DATA_USR = pd.DataFrame(
#                                 [[replace_and_strip(col) for col in list(row)] for idx, row in LEAGUE_TABLE_DATA_USR.iterrows()],
#                                 columns=LEAGUE_TABLE_DATA_USR.columns,
#                                 index=LEAGUE_TABLE_DATA_USR.index)
#                             CINEMA_NET_DATA1_USR = None
#                             CINEMA_NET_DATA2_USR = None
#                             CONSISTENCY_DATA_USR = pd.read_csv(f'{path}/TEMP_consistency_data_STORAGE.csv')
#                             NETSPLIT_DATA_USR = pd.read_csv(f'{path}/TEMP_net_split_data_STORAGE.csv')
#                             NETSPLIT_DATA_OUT2_USR = pd.read_csv(f'{path}/TEMP_net_split_data_out2_STORAGE.csv')
#                             NETSPLIT_DATA_ALL_USR = pd.read_csv(f'{path}/TEMP_net_split_ALL_data_STORAGE.csv')
#                             NETSPLIT_DATA_ALL_OUT2_USR = pd.read_csv(f'{path}/TEMP_net_split_ALL_data_out2_STORAGE.csv')
#                             RANKING_DATA_USR = pd.read_csv(f'{path}/TEMP_ranking_data_STORAGE.csv')
#                             FUNNEL_DATA_USR = pd.read_csv(f'{path}/TEMP_funnel_data_STORAGE.csv')
#                             FUNNEL_DATA_OUT2_USR = pd.read_csv(f'{path}/TEMP_funnel_data_out2_STORAGE.csv')

#                             USER_DATA = OrderedDict(net_data_STORAGE=NET_DATA_USR,
#                                                     net_data_out2_STORAGE=NET_DATA2_USR,
#                                                     consistency_data_STORAGE=CONSISTENCY_DATA_USR,
#                                                     user_elements_STORAGE=USER_ELEMENTS_USR,
#                                                     user_elements_out2_STORAGE=USER_ELEMENTS2_USR,
#                                                     forest_data_STORAGE=FOREST_DATA_USR,
#                                                     forest_data_out2_STORAGE=FOREST_DATA_OUT2_USR,
#                                                     forest_data_prws_STORAGE=FOREST_DATA_PRWS_USR,
#                                                     forest_data_prws_out2_STORAGE=FOREST_DATA_PRWS_OUT2_USR,
#                                                     ranking_data_STORAGE=RANKING_DATA_USR,
#                                                     funnel_data_STORAGE=FUNNEL_DATA_USR,
#                                                     funnel_data_out2_STORAGE=FUNNEL_DATA_OUT2_USR,
#                                                     league_table_data_STORAGE=LEAGUE_TABLE_DATA_USR,
#                                                     net_split_data_STORAGE=NETSPLIT_DATA_USR,
#                                                     net_split_data_out2_STORAGE=NETSPLIT_DATA_OUT2_USR,
#                                                     net_split_ALL_data_STORAGE=NETSPLIT_DATA_ALL_USR,
#                                                     net_split_ALL_data_out2_STORAGE=NETSPLIT_DATA_ALL_OUT2_USR,
#                                                     #cinema_net_data1_STORAGE=CINEMA_NET_DATA1_USR,
#                                                     #cinema_net_data2_STORAGE=CINEMA_NET_DATA2_USR,
#                                                     )

#                             # Remove unnamed columns
#                             for label, data in USER_DATA.items():
#                                 if (data is not None) and (type(data) != list) and (type(data) != dict):
#                                     USER_DATA[label] = USER_DATA[label].loc[:, ~USER_DATA[label].columns.str.contains('^Unnamed')]

#                             return [data.to_json(orient='split')
#                                 if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE']
#                                 else data
#                                 for label, data in USER_DATA.items()] + ['']

#                         else:
#                             return [data.to_json(orient='split')
#                         if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE']
#                         else data
#                         for label, data in DEFAULT_DATA.items()][:-2] + [u"\u274C" + 'Token not found: please double-check']


def generate_password(length=8):
    while '_' in (password := secrets.token_urlsafe(length)):
        pass
    return password


def __modal_SUBMIT_button_new(submit,  reset_btn,
                        # token_data, 
                        token_btn,
                        token_data_load, token_load_btn,
                        filename,
                        input_token,
                        TEMP_raw_data_STORAGE,
                        TEMP_net_data_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        # TEMP_user_elements_STORAGE,
                        TEMP_forest_data_STORAGE,
                        TEMP_forest_data_prws_STORAGE,
                        TEMP_ranking_data_STORAGE,
                        TEMP_funnel_data_STORAGE,
                        TEMP_league_table_data_STORAGE,
                        TEMP_net_split_data_STORAGE,
                        TEMP_net_split_ALL_data_STORAGE,
                        num_out
                        ):
    """ reads in temporary data for all analyses and outputs them in non-temp storages """
    submit_modal_data_trigger = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'submit_modal_data.n_clicks' in triggered: submit_modal_data_trigger = True
    token_btn_triggered = False
    if 'button-token.n_clicks' in triggered: token_btn_triggered = True
    load_btn_triggered = False
    if 'load-project.n_clicks' in triggered: load_btn_triggered = True
    OUT_DATA = [TEMP_raw_data_STORAGE,
                TEMP_net_data_STORAGE, TEMP_consistency_data_STORAGE,
                # TEMP_user_elements_STORAGE, 
                TEMP_forest_data_STORAGE, TEMP_forest_data_prws_STORAGE,
                TEMP_ranking_data_STORAGE, TEMP_funnel_data_STORAGE, 
                TEMP_league_table_data_STORAGE, TEMP_net_split_data_STORAGE,
                TEMP_net_split_ALL_data_STORAGE]
    OUT_DATA_NAMES = ['TEMP_raw_data_STORAGE',"TEMP_net_data_STORAGE",  "TEMP_consistency_data_STORAGE",
                # "TEMP_user_elements_STORAGE", 
                "TEMP_forest_data_STORAGE", "TEMP_forest_data_prws_STORAGE", 
                "TEMP_ranking_data_STORAGE", "TEMP_funnel_data_STORAGE",
                "TEMP_league_table_data_STORAGE", "TEMP_net_split_data_STORAGE", 
                "TEMP_net_split_ALL_data_STORAGE"]
    # num_out = int(num_out) if num_out else 1
    if submit_modal_data_trigger:  # Is triggered by submit_modal_data.n_clicks

            return OUT_DATA + ['']+[None, None, False]
    else:  # Must be triggered by reset_project.n_clicks
        if token_btn_triggered and filename and input_token:
            if len(input_token) >= 6:
                password = generate_password()
                token = input_token + "-" + password + '_'+ str(num_out)
                token_data = {'token': token}
                if token_btn > 0 :
                    usr_token = token_data['token']
                    directory = f"{usr_token}"
                    # token_outnum = token_data['token'].split('.')
                    # out_num = int(token_outnum[1])

                    parent_dir = "USR_DATASETS/"
                    path = os.path.join(parent_dir, directory)
                    os.mkdir(path)
                    for i, df_list in enumerate(OUT_DATA):
       
                        for j, df in enumerate(df_list):
                            dfname_i = OUT_DATA_NAMES[i] + f'_{j}'
                            df_i = df

                            if (df_i is not None) and (type(df_i) != list) and (type(df_i) != dict):
                                df_i = pd.read_json(df_i, orient='split')
                                df_i.to_csv(f'{path}/{dfname_i}.csv', encoding='utf-8')
                            else:
                                df_i = pd.DataFrame(dict())
                                df_i.to_csv(f'{path}/{dfname_i}.csv', encoding='utf-8')
                
                    return OUT_DATA + ['']+[html.P(u"\u2713" + " Successfully generated user",style={"color": "#B1D27B", "font-size":"11px","font-weight": "530"})]+[f'{token}', True]
            else:
                return OUT_DATA + ['']+[html.P(u"\u274C" + " Username must be at least 6 characters", style={"color": "red"}), None, False]
        else:
            # if not load_btn_triggered:
            #     return [data[0].to_json(orient='split')
            #         if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE']
            #         else data
            #         for label, data in DEFAULT_DATA.items()][:-2] + ['']
            if not load_btn_triggered:
                result = [
                        [(data.to_json(orient='split') if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE'] else data) for data in data_each]
                        for label, data_each in DEFAULT_DATA.items()                    
                    ][:-1] + ['']
                return result+[None, None, False]

            else:
                usr_token_load_ = token_data_load
                parent_dir_load = "USR_DATASETS/"
                directory_load = f"{usr_token_load_}"
                path = os.path.join(parent_dir_load, directory_load)
                token_outnum = usr_token_load_.split('_')
                out_num = int(token_outnum[1])
                
                foldername = os.listdir(parent_dir_load)
                if usr_token_load_ in foldername:
                    RAW_DATA_USR = [pd.read_csv(f'{path}/TEMP_raw_data_STORAGE_0.csv')]
                    NET_DATA_USR = [pd.read_csv(f'{path}/TEMP_net_data_STORAGE_0.csv')]
                    # DEFAULT_ELEMENTS_USR = USER_ELEMENTS_USR = get_network_new(df=NET_DATA_USR[0], i=0)
                    FOREST_DATA_USR = [pd.read_csv(f'{path}/TEMP_forest_data_STORAGE_{i}.csv') for i in range(out_num)]
                    FOREST_DATA_PRWS_USR = [pd.read_csv(f'{path}/TEMP_forest_data_prws_STORAGE_{i}.csv') for i in range(out_num)]
                    LEAGUE_TABLE_DATA_USR = [pd.read_csv(f'{path}/TEMP_league_table_data_STORAGE_{i}.csv', index_col=0)for i in range(out_num)]
                    replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
                    for j in range(out_num):
                        LEAGUE_TABLE_DATA_USR[j] = LEAGUE_TABLE_DATA_USR[j].fillna('')
                        LEAGUE_TABLE_DATA_USR[j] = pd.DataFrame(
                            [[replace_and_strip(col) for col in list(row)] for idx, row in LEAGUE_TABLE_DATA_USR[j].iterrows()],
                            columns=LEAGUE_TABLE_DATA_USR[j].columns,
                            index=LEAGUE_TABLE_DATA_USR[j].index)
                    CINEMA_NET_DATA1_USR = None
                    CONSISTENCY_DATA_USR = [pd.read_csv(f'{path}/TEMP_consistency_data_STORAGE_{i}.csv')for i in range(out_num)]
                    NETSPLIT_DATA_USR = [pd.read_csv(f'{path}/TEMP_net_split_data_STORAGE_{i}.csv')for i in range(out_num)]
                    NETSPLIT_DATA_ALL_USR = [pd.read_csv(f'{path}/TEMP_net_split_ALL_data_STORAGE_{i}.csv')for i in range(out_num)]
                    RANKING_DATA_USR = [pd.read_csv(f'{path}/TEMP_ranking_data_STORAGE_{i}.csv')for i in range(out_num)]
                    FUNNEL_DATA_USR = [pd.read_csv(f'{path}/TEMP_funnel_data_STORAGE_{i}.csv')for i in range(out_num)]

                    USER_DATA = OrderedDict(raw_data_STORAGE=RAW_DATA_USR,
                                            net_data_STORAGE=NET_DATA_USR,
                                            consistency_data_STORAGE=CONSISTENCY_DATA_USR,
                                            # user_elements_STORAGE=USER_ELEMENTS_USR,
                                            forest_data_STORAGE=FOREST_DATA_USR,
                                            forest_data_prws_STORAGE=FOREST_DATA_PRWS_USR,
                                            ranking_data_STORAGE=RANKING_DATA_USR,
                                            funnel_data_STORAGE=FUNNEL_DATA_USR,
                                            league_table_data_STORAGE=LEAGUE_TABLE_DATA_USR,
                                            net_split_data_STORAGE=NETSPLIT_DATA_USR,
                                            net_split_ALL_data_STORAGE=NETSPLIT_DATA_ALL_USR,
                                            #cinema_net_data1_STORAGE=CINEMA_NET_DATA1_USR,
                                            #cinema_net_data2_STORAGE=CINEMA_NET_DATA2_USR,
                                            )

                    # Remove unnamed columns
                    # for label, each_data in USER_DATA.items():
                    #     for data in each_data:
                    #         if (data is not None) and (type(data) != list) and (type(data) != dict):
                    #             data[label] = data[label].loc[:, ~data[label].columns.str.contains('^Unnamed')]
                    for label, data_list in USER_DATA.items():
                        for i, data in enumerate(data_list):
                            if data is not None and not isinstance(data, (list, dict)):
                                USER_DATA[label][i] = data.loc[:, ~data.columns.str.contains('^Unnamed')]
                    final_return = [
                            [(data.to_json(orient='split') if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE'] else data) for data in data_each]
                            for label, data_each in USER_DATA.items()]+ ['']
                    
                    return final_return+[None, None, False]

                else:
                    final_return = [
                            [(data.to_json(orient='split') if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE'] else data) for data in data_each]
                            for label, data_each in DEFAULT_DATA.items()][:-1] + [u"\u274C" + 'Token not found: please double-check']
                    
                    return final_return+[None, None, False]


