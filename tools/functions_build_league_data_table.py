import numpy as np, pandas as pd
import dash, dash_html_components as html
import dash_table
from tools.utils import set_slider_marks
from assets.COLORS import *

def __update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
                   league_table_data, cinema_net_data1, cinema_net_data2, data_and_league_table_DATA,
                   forest_data, forest_data_out2, reset_btn, ranking_data, net_storage, net_data_STORAGE_TIMESTAMP,
                   data_filename, league_table_data_STORAGE_TIMESTAMP, filename_cinema1, filename_cinema2, filename_cinema2_disabled):


    YEARS_DEFAULT = np.array([1963, 1990, 1997, 2001, 2003, 2004, 2005, 2006, 2007, 2008, 2010,
                              2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020])

    reset_btn_triggered = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'reset_project.n_clicks' in triggered: reset_btn_triggered = True

    net_data = pd.read_json(net_data, orient='split').round(3)

    years = net_data.year if not reset_btn_triggered else YEARS_DEFAULT
    slider_min, slider_max = years.min(), years.max()
    slider_marks = set_slider_marks(slider_min, slider_max, years)
    _out_slider = [slider_min, slider_max, slider_marks]


    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'rob_vs_cinema.value' in triggered:
        toggle_cinema_modal = toggle_cinema
    elif 'rob_vs_cinema_modal.value' in triggered:
        toggle_cinema = toggle_cinema_modal

    if 'slider-year.value' in triggered:
        _data = pd.read_json(data_and_league_table_DATA['FULL_DATA'], orient='split').round(3)
        data_output = _data[_data.year <= slider_value].to_dict('records')
        _OUTPUT0 = data_and_league_table_DATA['OUTPUT']
        _output = [data_output]+[_OUTPUT0[1]]+[data_output] + _OUTPUT0[3:]

        return _output + _out_slider + [data_and_league_table_DATA]

    ranking_data = pd.read_json(ranking_data, orient='split')
    leaguetable = pd.read_json(league_table_data, orient='split')
    confidence_map = {k: n for n, k in enumerate(['low', 'medium', 'high'])}
    treatments = np.unique(net_data[['treat1', 'treat2']].dropna().values.flatten())
    robs = (net_data.groupby(['treat1', 'treat2']).rob.mean().reset_index()
            .pivot_table(index='treat2', columns='treat1', values='rob')
            .reindex(index=treatments, columns=treatments, fill_value=np.nan))
    robs = robs.fillna(robs.T) if not toggle_cinema else robs
    robs_slct = robs #robs + robs.T - np.diag(np.diag(robs))  if not toggle_cinema else robs ## full rob table

    comprs_downgrade  = pd.DataFrame()
    comprs_conf_lt = comprs_conf_ut = None

    if toggle_cinema:

        cinema_net_data1 = pd.read_json(cinema_net_data1, orient='split')
        cinema_net_data2 = pd.read_json(cinema_net_data2, orient='split')
        confidence_map = {k: n for n, k in enumerate(['very low', 'low', 'moderate', 'high'])}
        comparisons1 = cinema_net_data1.Comparison.str.split(':', expand=True)
        confidence1 = cinema_net_data1['Confidence rating'].str.lower().map(confidence_map)
        if filename_cinema2 is not None or (filename_cinema2 is None and "Default_data" in cinema_net_data2.columns):
            confidence2 = cinema_net_data2['Confidence rating'].str.lower().map(confidence_map)
        else:
            confidence2 = pd.Series(np.array([np.nan]*len(confidence1)), copy=False)
        comparisons2 = cinema_net_data2.Comparison.str.split(':', expand=True) if filename_cinema2 is not None or (filename_cinema2 is None and "Default_data" not in cinema_net_data2.columns) else comparisons1
        comprs_conf_ut = comparisons2.copy()  # Upper triangle
        comparisons1.columns = [1, 0]  # To get lower triangle
        comprs_conf_lt = comparisons1  # Lower triangle
        comprs_downgrade_lt = comprs_conf_lt
        comprs_downgrade_ut = comprs_conf_ut
        if "Reason(s) for downgrading" in cinema_net_data1.columns:
            downgrading1 = cinema_net_data1["Reason(s) for downgrading"]
            comprs_downgrade_lt['Downgrading'] = downgrading1
            if (filename_cinema2 is not None and "Reason(s) for downgrading" in cinema_net_data2.columns):
                downgrading2 = cinema_net_data2["Reason(s) for downgrading"]
            else:
                downgrading2 = pd.Series(np.array([np.nan]*len(downgrading1)), copy=False)
            comprs_downgrade_ut['Downgrading'] = downgrading2
            comprs_downgrade = pd.concat([comprs_downgrade_ut, comprs_downgrade_lt])
            comprs_downgrade = comprs_downgrade.pivot(index=0, columns=1, values='Downgrading')
        comprs_conf_lt['Confidence'] = confidence1
        comprs_conf_ut['Confidence'] = confidence2
        comprs_conf = pd.concat([comprs_conf_ut, comprs_conf_lt])
        comprs_conf = comprs_conf.pivot_table(index=0, columns=1, values='Confidence')

        if filename_cinema2 is None and "pscore2" not in ranking_data.columns:
            ut = np.triu(np.ones(comprs_conf.shape), 1).astype(bool)
            comprs_conf = comprs_conf.where(ut == False, np.nan)

        robs = comprs_conf
    # Filter according to cytoscape selection

    if store_node:
        slctd_trmnts = [nd['id'] for nd in store_node]
        if len(slctd_trmnts) > 0:
            forest_data = pd.read_json(forest_data, orient='split')
            net_data = pd.read_json(net_storage, orient='split')
            forest_data_out2 = pd.read_json(forest_data_out2, orient='split') if 'pscore2' in ranking_data.columns else None
            dataselectors = []
            dataselectors += [forest_data.columns[1], net_data["outcome1_direction"].iloc[1]]
            if 'pscore2' in ranking_data.columns:
                dataselectors += [forest_data_out2.columns[1], net_data["outcome2_direction"].iloc[1]]

            leaguetable = leaguetable.loc[slctd_trmnts, slctd_trmnts]
            robs_slct = robs.loc[slctd_trmnts, slctd_trmnts]
            leaguetable_bool = pd.DataFrame(np.triu(np.ones(leaguetable.shape)).astype(bool),
                                            columns=slctd_trmnts,
                                            index=slctd_trmnts) #define upper and lower triangle

            ### pick correct comparison from FOREST_DATA and FOREST_DATA_OUT2
            for treat_c in slctd_trmnts:
                for treat_r in slctd_trmnts:
                    if treat_c != treat_r:
                        if not leaguetable_bool.loc[treat_r][treat_c]:
                            effcsze = round(forest_data[dataselectors[0]][(forest_data.Treatment == treat_c) & (forest_data.Reference == treat_r)].values[0], 2)
                            ci_lower = round(forest_data['CI_lower'][(forest_data.Treatment == treat_c) & (forest_data.Reference == treat_r)].values[0], 2)
                            ci_upper = round(forest_data['CI_upper'][(forest_data.Treatment == treat_c) & (forest_data.Reference == treat_r)].values[0], 2)
                            leaguetable.loc[treat_r][treat_c] = f'{effcsze}\n{ci_lower, ci_upper}'
                        else:
                            pass
                            #direct = round(float(leaguetable.loc[treat_r][treat_c].strip().split("\n")[0]), 2) if leaguetable[treat_r][treat_c] != "." else None
                            #leaguetable.loc[treat_r][treat_c] = np.exp( -np.log(direct)) if leaguetable[treat_r][treat_c] != "." else  "." # TODO: might want to save direct evidence from R and update it upoon filtering, so far it is removed iif nodes are filtered
                            # leaguetable = pd.DataFrame(np.tril(leaguetable), columns=slctd_trmnts, index=slctd_trmnts)
                        if 'pscore2' in ranking_data.columns:
                            effcsze2 = round(forest_data_out2[dataselectors[2]][(forest_data_out2.Treatment == treat_r) & (forest_data_out2.Reference == treat_c)].values[0], 2)
                            ci_lower2 = round(forest_data_out2['CI_lower'][(forest_data_out2.Treatment == treat_r) & (forest_data_out2.Reference == treat_c)].values[0], 2)
                            ci_upper2 = round(forest_data_out2['CI_upper'][(forest_data_out2.Treatment == treat_r) & (forest_data_out2.Reference == treat_c)].values[0], 2)

                            if leaguetable_bool.loc[treat_r][treat_c]:
                                leaguetable.loc[treat_r][treat_c] = f'{effcsze2}\n{ci_lower2, ci_upper2}'
                                if toggle_cinema: robs_slct.loc[treat_r][treat_c] = comprs_conf_ut['Confidence'][(comprs_conf_ut[0] == treat_c) & (comprs_conf_ut[1] == treat_r) |
                                                                                    (comprs_conf_ut[0] == treat_r) & (comprs_conf_ut[1] == treat_c)].values[0]
                                else:
                                    robs_slct.loc[treat_r][treat_c] = robs_slct[treat_r][treat_c] if not np.isnan(robs_slct[treat_r][treat_c]) else robs_slct[treat_c][treat_r]

                            else:
                                if toggle_cinema: robs_slct.loc[treat_r][treat_c] = comprs_conf_lt['Confidence'][(comprs_conf_lt[0] == treat_c) & (comprs_conf_lt[1] == treat_r) |
                                                                                    (comprs_conf_lt[0] == treat_r) & (comprs_conf_lt[1] == treat_c)].values[0]
                                else:
                                    robs_slct.loc[treat_r][treat_c] = robs_slct[treat_r][treat_c] if not np.isnan(robs_slct[treat_r][treat_c]) else robs_slct[treat_c][treat_r]
                        else:
                            if toggle_cinema:
                                robs_slct.loc[treat_r][treat_c] = comprs_conf_lt['Confidence'][
                                    (comprs_conf_lt[0] == treat_c) & (comprs_conf_lt[1] == treat_r) |
                                    (comprs_conf_lt[0] == treat_r) & (comprs_conf_lt[1] == treat_c)].values[0]
                            else:
                                robs_slct.loc[treat_r][treat_c] = robs_slct[treat_r][treat_c] if not np.isnan(
                                    robs_slct[treat_r][treat_c]) else robs_slct[treat_c][treat_r]

            if 'pscore2' not in ranking_data.columns:
                if not toggle_cinema:
                    robs_slct = robs_slct[leaguetable_bool.T]
                    leaguetable = leaguetable[leaguetable_bool.T]
                else:
                    robs_slct = robs_slct[leaguetable_bool.T]
                    #leaguetable = leaguetable[leaguetable_bool.T]


            leaguetable.replace(0, np.nan) #inplace

            tril_order = pd.DataFrame(np.tril(np.ones(leaguetable.shape)),
                                      columns=leaguetable.columns,
                                      index=leaguetable.columns)
            tril_order = tril_order.loc[slctd_trmnts, slctd_trmnts]
            filter = np.tril(tril_order == 0)
            filter += filter.T  # inverting of rows and columns common in meta-analysis visualissation

            robs = robs.loc[slctd_trmnts, slctd_trmnts]
            robs_values = robs.values
            #robs_values[filter] = robs_values.T[filter]
            robs = pd.DataFrame(robs_values,
                                columns=robs.columns,
                                index=robs.columns)

            robs = robs.T if 'pscore2' not in ranking_data.columns else robs

            treatments = slctd_trmnts

    #####   Add style colouring and legend
    N_BINS = 3 if not toggle_cinema else 4
    bounds = np.arange(N_BINS + 1) / N_BINS
    leaguetable_colr = robs.copy(deep=True)
    np.fill_diagonal(leaguetable_colr.values, np.nan)
    leaguetable_colr = leaguetable_colr.astype(np.float64)

    cmap = [CINEMA_g, CINEMA_y, CINEMA_r] if not toggle_cinema else [CINEMA_r, CINEMA_y, CINEMA_lb, CINEMA_g]
    legend_height = '4px'
    legend = [html.Div(style={'display': 'inline-block', 'width': '100px'},
                       children=[html.Div(),
                                 html.Small('Risk of bias: ' if not toggle_cinema else 'CINeMA rating: ',
                                            style={'color': 'white'})])]
    legend += [html.Div(style={'display': 'inline-block', 'width': '60px'},
                        children=[html.Div(style={'backgroundColor': cmap[n],
                                                  'height': legend_height}), html.Small(
                            ('Very Low' if toggle_cinema else 'Low') if n == 0 else 'High' if n == N_BINS - 1 else None,
                            style={'paddingLeft': '2px', 'color': 'white'})])
               for n in range(N_BINS)]

    cmap = [CINEMA_g, CINEMA_y, CINEMA_r] if not toggle_cinema else [CINEMA_r, CINEMA_y, CINEMA_lb, CINEMA_g]

    df_max, df_min = max(confidence_map.values()), min(confidence_map.values())
    ranges = (df_max - df_min) * bounds + df_min
    ranges[-1] *= 1.001
    ranges = ranges + 1 if not toggle_cinema else ranges
    league_table_styles = []

    for treat_c in treatments:
        for treat_r in treatments:
            if treat_r!=treat_c:

                rob = robs.loc[treat_r, treat_c] if not store_node else robs_slct.loc[treat_r, treat_c]
                indxs = np.where(rob < ranges)[0] if rob == rob else [0]
                clr_indx = indxs[0] - 1 if len(indxs) else 0
                diag, empty = treat_r == treat_c, rob != rob
                league_table_styles.append({'if': {'filter_query': f'{{Treatment}} = {{{treat_r}}}',
                                                'column_id': treat_c},
                                                'backgroundColor': cmap[clr_indx] if not empty else CLR_BCKGRND2,
                                                'color': CX1 if not empty else CX2 if diag else 'white'})
    league_table_styles.append({'if': {'column_id': 'Treatment'}, 'backgroundColor': CX1})


    # Prepare for output
    tips = robs
    leaguetable = leaguetable.reset_index().rename(columns={'index': 'Treatment'})
    leaguetable_cols = [{"name": c, "id": c} for c in leaguetable.columns]
    leaguetable = leaguetable.to_dict('records')


    tooltip_values = [{col['id']: {'value': f"**Average ROB:** {tip[col['id']]}",
                                   'type': 'markdown'} if col['id'] != 'Treatment' else None
                           for col in leaguetable_cols} for rn, (_, tip) in enumerate(tips.iterrows())]
    if toggle_cinema:
        tooltip_values = [{col['id']: {'value': f"**Reason for Downgrading:**{tip[col['id']]}" if not comprs_downgrade.empty else f"**Reason for Downgrading:**",
                                       'type': 'markdown'} if col['id'] != 'Treatment' else None
                       for col in leaguetable_cols} for rn, (_, tip) in enumerate(comprs_downgrade.iterrows())]


    if store_edge or store_node:
        slctd_nods = {n['id'] for n in store_node} if store_node else set()
        slctd_edgs = [e['source'] + e['target'] for e in store_edge] if store_edge else []
        net_data = net_data[net_data.treat1.isin(slctd_nods) | net_data.treat2.isin(slctd_nods)
                    | (net_data.treat1 + net_data.treat2).isin(slctd_edgs) | (net_data.treat2 + net_data.treat1).isin(slctd_edgs)]

    data_cols = [{"name": c, "id": c} for c in net_data.columns]
    data_output = net_data[net_data.year <= slider_value].to_dict('records')
    league_table = build_league_table(leaguetable, leaguetable_cols, league_table_styles, tooltip_values)
    league_table_modal = build_league_table(leaguetable, leaguetable_cols, league_table_styles, tooltip_values, modal=True)
    _output = [data_output, data_cols] * 2 + [league_table, league_table_modal] + [legend] * 2 + [toggle_cinema, toggle_cinema_modal]

    data_and_league_table_DATA['FULL_DATA'] = net_data.to_json( orient='split')
    data_and_league_table_DATA['OUTPUT'] = _output
    return _output + _out_slider + [data_and_league_table_DATA]




def build_league_table(data, columns, style_data_conditional, tooltip_values, modal=False):

    return dash_table.DataTable(style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                            'color': 'white',
                                            'border': '1px solid #5d6d95',
                                            'font-family': 'sans-serif',
                                            'fontSize': 11,
                                            'minWidth': '55px',
                                            'textAlign': 'center',
                                            'whiteSpace': 'pre-line',  # 'inherit', nowrap
                                            'textOverflow': 'string'},  # 'ellipsis'
                                fixed_rows={'headers': True, 'data': 0},
                                data=data,
                                columns=columns,
                                # export_format="csv", #xlsx
                                # state='active',
                                tooltip_data= tooltip_values,
                                tooltip_delay=200,
                                tooltip_duration=None,
                                style_data_conditional=style_data_conditional,
                                # fixed_rows={'headers': True, 'data': 0},    # DOES NOT WORK / LEADS TO BUG
                                # fixed_columns={'headers': True, 'data': 1}, # DOES NOT WORK / LEADS TO BUG
                                style_header={'backgroundColor': 'rgb(26, 36, 43)',
                                              'border': '1px solid #5d6d95'},
                                style_header_conditional=[{'if': {'column_id': 'Treatment',
                                                                  'header_index': 0},
                                                           'fontWeight': 'bold'}],
                                style_table={'overflow': 'auto', 'width': '100%',
                                             'max-height': 'calc(50vh)',
                                             'max-width': 'calc(52vw)'} if not modal else {
                                    'overflowX': 'scroll',
                                    'overflowY': 'scroll',
                                    'height': '99%',
                                    'minWidth': '100%',
                                    'max-height': 'calc(85vh)',
                                    'width': '99%',
                                    'margin-top': '10px',
                                    'padding': '5px 5px 5px 5px'
                                },
                                css=[{"selector": '.dash-cell div.dash-cell-value',  # "table",
                                      "rule": "width: 100%; "},
                                     {'selector': 'tr:hover',
                                      'rule': 'background-color: rgba(0, 0, 0, 0);'},
                                     {'selector': 'td:hover',
                                      'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])
