from tools.utils import *
from dash import html



def __modal_submit_checks_DATACHECKS(modal_data_checks_is_open, num_outcomes,TEMP_net_data_STORAGE):
    if modal_data_checks_is_open:
        try:
            data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')
            passed_checks = data_checks(data, num_outcomes)
        except:
            passed_checks = data_checks(data, num_outcomes)
        if all(passed_checks.values()):
                return html.P(u"\u2713" + " All data checks passed.", style={"color":"green"}), '__Para_Done__'
        else:
            return (html.P(["WARNINGS:"]+sum([[html.Br(), f'{k}']
                                                     for k,v in passed_checks.items()
                                                                    if not v], []), style={"color": "orange"}), '__Para_Done__')
    else:
        return None, ''



def __modal_submit_checks_NMA(modal_data_checks_is_open, TEMP_net_data_STORAGE,
                            TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE):
    if modal_data_checks_is_open:
        net_data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')
        try:
            TEMP_user_elements_STORAGE = get_network(df=net_data)
            TEMP_user_elements_out2_STORAGE = []
            NMA_data = run_network_meta_analysis(net_data)
            TEMP_forest_data_STORAGE = NMA_data.to_json( orient='split')

            if "TE2" in net_data.columns:
                net_data_out2 = net_data.drop(["TE", "seTE",  "n1",  "n2", "effect_size1"], axis=1)
                net_data_out2 = net_data_out2.rename(columns={"TE2": "TE", "seTE2": "seTE", "effect_size2": 'effect_size1',
                                                              "n2.1": "n1", "n2.2": "n2"})

                TEMP_user_elements_out2_STORAGE = get_network(df=net_data_out2)
                NMA_data2 = run_network_meta_analysis(net_data_out2)
                TEMP_forest_data_out2_STORAGE = NMA_data2.to_json(orient='split')

            return (False, '', html.P(u"\u2713" + " Network meta-analysis run successfully.", style={"color":"green"}),
                    '__Para_Done__', TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE, TEMP_user_elements_STORAGE, TEMP_user_elements_out2_STORAGE)


        except Exception as Rconsole_error_nma:
            return (True, str(Rconsole_error_nma), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                        '__Para_Done__', TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE, TEMP_user_elements_STORAGE, TEMP_user_elements_out2_STORAGE)

    else:
        return False, '', None, '', TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE, None, None




def __modal_submit_checks_NMA_new(modal_data_checks_is_open, num_outcome,TEMP_net_data_STORAGE,
                            TEMP_forest_data_STORAGE):
    if modal_data_checks_is_open:
        net_data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')
        num_outcome = int(num_outcome)
        try:
            TEMP_user_elements_STORAGE = [[] for _ in range(num_outcome)]
            NMA_data = [[] for _ in range(num_outcome)]

            for i in range(num_outcome):
                TEMP_user_elements_STORAGE[i] = get_network_new(df=net_data, i=i)
                
                NMA_data[i] = run_network_meta_analysis(net_data, i)

            
            TEMP_forest_data_STORAGE = [df.to_json(orient='split') for df in NMA_data]
            # TEMP_user_elements_STORAGE = [df.to_json(orient='split') for df in TEMP_user_elements_STORAGE]

            return (False, '', html.P(u"\u2713" + " Network meta-analysis run successfully.", style={"color":"green"}),
                    '__Para_Done__', TEMP_forest_data_STORAGE)

        except Exception as Rconsole_error_nma:
            return (True, str(Rconsole_error_nma), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                        '__Para_Done__', TEMP_forest_data_STORAGE)

    else:
        
        return False, '', None, '', TEMP_forest_data_STORAGE




def __modal_submit_checks_PAIRWISE(nma_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2):
    if modal_data_checks_is_open:

        data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')
        try:
            PAIRWISE_data = run_pairwise_MA(data)
            TEMP_forest_data_prws_STORAGE = PAIRWISE_data.to_json( orient='split')
            TEMP_forest_data_prws_out2 = []

            if "TE2" in data.columns:
                pair_data_out2 = data.drop(["TE", "seTE",  "n1",  "n2"], axis=1)
                pair_data_out2 = pair_data_out2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
                PAIRWISE_data2 = run_pairwise_MA(pair_data_out2)
                TEMP_forest_data_prws_out2 = PAIRWISE_data2.to_json(orient='split')

            return (False, '', html.P(u"\u2713" + " Pairwise meta-analysis run successfully.", style={"color":"green"}),
                               '__Para_Done__', TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2)
        except Exception as Rconsole_error_pw:
                return (True, str(Rconsole_error_pw), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                              '__Para_Done__', TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2)

    else:
        return False, '', None, '', TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2


def __modal_submit_checks_PAIRWISE_new(nma_data_ts,num_outcome, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE):
    if modal_data_checks_is_open:

        data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')
        num_outcome = int(num_outcome)

        try:
            PAIRWISE_data = [[] for _ in range(num_outcome)]

            for i in range(num_outcome): 
                PAIRWISE_data[i] = run_pairwise_MA(data, i)

            
            TEMP_forest_data_prws_STORAGE = [df.to_json(orient='split') for df in PAIRWISE_data]


            return (False, '', html.P(u"\u2713" + " Pairwise meta-analysis run successfully.", style={"color":"green"}),
                               '__Para_Done__', TEMP_forest_data_prws_STORAGE)
            

        except Exception as Rconsole_error_pw:
                return (True, str(Rconsole_error_pw), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                              '__Para_Done__', TEMP_forest_data_prws_STORAGE)

    else:
        return False, '', None, '', TEMP_forest_data_prws_STORAGE




def __modal_submit_checks_LT(pw_data_ts, modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data, net_split_data2,
                           netsplit_all, netsplit_all2, dataselectors):
    """ produce new league table from R """
    if modal_data_checks_is_open:

        data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')

        try:
            LEAGUETABLE_OUTS =  generate_league_table(data, outcome2=False) if "TE2" not in data.columns or dataselectors[1] not in ['MD','SMD','OR','RR'] else generate_league_table(data, outcome2=True)

            if "TE2" not in data.columns or dataselectors[1] not in ['MD', 'SMD', 'OR', 'RR']:
                (LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, netsplit_all) = [f.to_json( orient='split') for f in LEAGUETABLE_OUTS]
                net_split_data2 = {}
                netsplit_all2 = {}
            else:

                (LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2, netsplit_all, netsplit_all2) = [f.to_json( orient='split') for f in LEAGUETABLE_OUTS]

            return (False, '', html.P(u"\u2713" + " Successfully generated league table, consistency tables, ranking data.", style={"color":"green"}),
                         '__Para_Done__', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2, netsplit_all, netsplit_all2)
        except Exception as Rconsole_error_league:
            return (True, str(Rconsole_error_league), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                    '__Para_Done__', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, netsplit_all) if "TE2" not in data.columns else \
                                    (False, html.P(u"\u274C" + "An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                    '__Para_Done__', Rconsole_error_league, LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2, netsplit_all, netsplit_all2)
    else:
        net_split_data2 = {}
        netsplit_all2 = {}
        return False, '', None, '', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2, netsplit_all, netsplit_all2





def __modal_submit_checks_LT_new(pw_data_ts, num_outcome, modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data,
                           netsplit_all):
    """ produce new league table from R """
    if modal_data_checks_is_open:

        data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')
        num_outcome = int(num_outcome)

        try:
            LEAGUETABLE_OUTS = [[] for _ in range(num_outcome)]
            LEAGUETABLE_data = [[] for _ in range(num_outcome)]
            ranking_data = [[] for _ in range(num_outcome)]
            consistency_data = [[] for _ in range(num_outcome)]
            net_split_data=[[] for _ in range(num_outcome)]
            netsplit_all=[[] for _ in range(num_outcome)]
            

            for i in range(num_outcome): 
                LEAGUETABLE_OUTS[i] = generate_league_table(data, i)
                LEAGUETABLE_data[i],ranking_data[i],consistency_data[i],net_split_data[i],netsplit_all[i] = [f.to_json( orient='split') for f in LEAGUETABLE_OUTS[i]]
            
            
            # merged_ranking_data = pd.read_json(ranking_data[0], orient='split')
            # for i, json_path in enumerate(ranking_data[1:], start=2):
            #     df = pd.read_json(json_path, orient='split')
            #     # Rename the pscore column to pscorei, where i is the loop index
            #     df = df.rename(columns={'pscore': f'pscore{i+1}'})
            #     merged_ranking_data = pd.merge(merged_ranking_data, df, on='treatment', how='outer')
            
            # merged_ranking_data = merged_ranking_data.rename(columns={'pscore': 'pscore1'})
            # merged_ranking_data = merged_ranking_data.to_json(orient='split')

            return (False, '', html.P(u"\u2713" + " Successfully generated league table, consistency tables, ranking data.", style={"color":"green"}),
                         '__Para_Done__', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, netsplit_all)
        except Exception as Rconsole_error_league:
            return (True, str(Rconsole_error_league), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                    '__Para_Done__', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, netsplit_all) if "TE2" not in data.columns else \
                                    (False, html.P(u"\u274C" + "An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                    '__Para_Done__', Rconsole_error_league, LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, netsplit_all)
    else:
        return False, '', None, '', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data,  netsplit_all





def __modal_submit_checks_FUNNEL(lt_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data, FUNNEL_data2):
    if modal_data_checks_is_open:
        
        try:
            data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')
            FUNNEL_data = generate_funnel_data(data)
            FUNNEL_data = FUNNEL_data.to_json(orient='split')

            if "TE2" in data.columns:
                data_out2 = data.drop(["TE", "seTE",  "n1",  "n2"], axis=1)
                data_out2 = data_out2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
                FUNNEL_data2 = generate_funnel_data(data_out2)
                FUNNEL_data2 = FUNNEL_data2.to_json(orient='split')

            return (False, '', html.P(u"\u2713" + " Successfully generated funnel plot data.", style={"color": "green"}),
            '__Para_Done__', FUNNEL_data, FUNNEL_data2)
        except Exception as Rconsole_error_funnel:
            return (True, str(Rconsole_error_funnel), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color": "red"}),
                    '__Para_Done__', FUNNEL_data, FUNNEL_data2)

    else:
        return False, '', None, '', FUNNEL_data, FUNNEL_data2




def __modal_submit_checks_FUNNEL_new(lt_data_ts, num_outcome,modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data):
    if modal_data_checks_is_open:
        num_outcome = int(num_outcome)
        try:
            FUNNEL_data = [[] for _ in range(num_outcome)]
            data = pd.read_json(TEMP_net_data_STORAGE[0], orient='split')
            
            for i in range(num_outcome): 
                FUNNEL_data[i] = generate_funnel_data(data, i)

            FUNNEL_data = [df.to_json(orient='split') for df in FUNNEL_data]
            

            return (False, '', html.P(u"\u2713" + " Successfully generated funnel plot data.", style={"color": "green"}),
            '__Para_Done__', FUNNEL_data)
        
        except Exception as Rconsole_error_funnel:
            return (True, str(Rconsole_error_funnel), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color": "red"}),
                    '__Para_Done__', FUNNEL_data)

    else:
        return False, '', None, '', FUNNEL_data