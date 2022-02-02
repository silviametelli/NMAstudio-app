import numpy as np, pandas as pd
import dash, dash_html_components as html
import dash_table
from tools.utils import set_slider_marks
from assets.COLORS import *

def __update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
                  league_table_data, cinema_net_data1, cinema_net_data2, data_and_league_table_DATA,
                  reset_btn, net_data_STORAGE_TIMESTAMP, league_table_data_STORAGE_TIMESTAMP):

    # ctx = dash.callback_context
    # print(net_data_STORAGE_TIMESTAMP, league_table_data_STORAGE_TIMESTAMP,
    #       net_data_STORAGE_TIMESTAMP - league_table_data_STORAGE_TIMESTAMP)
    # if ((abs(net_data_STORAGE_TIMESTAMP - league_table_data_STORAGE_TIMESTAMP)>150_000) and
    #     (net_data_STORAGE_TIMESTAMP < league_table_data_STORAGE_TIMESTAMP)):
    #     print('preventing update')
    #     raise PreventUpdate
    # if ctx.triggered:
    #     print(ctx.triggered[0]['prop_id'].split('.')[0])

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

    leaguetable = pd.read_json(league_table_data, orient='split')
    confidence_map = {k: n for n, k in enumerate(['low', 'medium', 'high'])}
    treatments = np.unique(net_data[['treat1', 'treat2']].dropna().values.flatten())
    robs = (net_data.groupby(['treat1', 'treat2']).rob.mean().reset_index()
            .pivot_table(index='treat2', columns='treat1', values='rob')
            .reindex(index=treatments, columns=treatments, fill_value=np.nan))
    if toggle_cinema:
        cinema_net_data1 = pd.read_json(cinema_net_data1, orient='split')
        cinema_net_data2 = pd.read_json(cinema_net_data2, orient='split')
        confidence_map = {k: n for n, k in enumerate(['very low', 'low', 'moderate', 'high'])}
        comparisons = cinema_net_data1.Comparison.str.split(':', expand=True)
        confidence1 = cinema_net_data1['Confidence rating'].str.lower().map(confidence_map)
        confidence2 = cinema_net_data2['Confidence rating'].str.lower().map(confidence_map) #if content2 is not None else confidence1
        comprs_conf_ut = comparisons.copy()  # Upper triangle
        comparisons.columns = [1, 0]  # To get lower triangle
        comprs_conf_lt = comparisons[[0, 1]]  # Lower triangle
        comprs_conf_lt['Confidence'] = confidence1
        comprs_conf_ut['Confidence'] = confidence2
        comprs_conf = pd.concat([comprs_conf_ut, comprs_conf_lt])
        comprs_conf = comprs_conf.pivot_table(index=0, columns=1, values='Confidence')
        robs = comprs_conf+1
    # Filter according to cytoscape selection
    if store_node:
        slctd_trmnts = [nd['id'] for nd in store_node]
        if len(slctd_trmnts) > 0:

            tril_order = pd.DataFrame(np.tril(np.ones(leaguetable.shape)),
                                      columns=leaguetable.columns,
                                      index=leaguetable.columns)
            tril_order = tril_order.loc[slctd_trmnts, slctd_trmnts]
            filter = np.tril(tril_order==0)
            filter += filter.T #  inverting of rows and columns common in meta-analysis visualization

            leaguetable = leaguetable.loc[slctd_trmnts, slctd_trmnts]
            leaguetable_values = leaguetable.values
            leaguetable_values[filter] = leaguetable_values.T[filter]
            leaguetable = pd.DataFrame(leaguetable_values,
                                       columns=leaguetable.columns,
                                       index=leaguetable.columns)

            robs = robs.loc[slctd_trmnts, slctd_trmnts]
            robs_values = robs.values
            robs_values[filter] = robs_values.T[filter]
            robs = pd.DataFrame(robs_values,
                                columns=robs.columns,
                                index=robs.columns)

            treatments = slctd_trmnts

    #####   Add style colouring and legend
    N_BINS = 3 if not toggle_cinema else 4
    bounds = np.arange(N_BINS + 1) / N_BINS

    leaguetable_colr = robs.copy(deep=True)
    np.fill_diagonal(leaguetable_colr.values, np.nan)
    leaguetable_colr = leaguetable_colr.astype(np.float64)

    # cmap = [clrs.to_hex(plt.get_cmap('RdYlGn_r', N_BINS)(n)) for n in range(N_BINS)]
    cmap = [CINEMA_g, CINEMA_y,CINEMA_r] if not toggle_cinema else [CINEMA_r, CINEMA_y, CINEMA_lb, CINEMA_g]
    legend_height = '4px'
    legend = [html.Div(style={'display': 'inline-block', 'width': '100px'},
                       children=[html.Div(),
                                 html.Small('Risk of bias: ' if not toggle_cinema else 'CINeMA rating: ',
                                            style={'color': 'white'})])]
    legend += [html.Div(style={'display': 'inline-block', 'width': '60px'},
                        children=[html.Div(style={'backgroundColor': cmap[n],
                                                  # 'borderLeft': f'1px {BORDER_LEFT_CLR} solid',
                                                  'height': legend_height}), html.Small(
                            ('Very Low' if toggle_cinema else 'Low') if n == 0 else 'High' if n == N_BINS - 1 else None,
                            style={'paddingLeft': '2px', 'color': 'white'})])
               for n in range(N_BINS)]

    #df_max, df_min = leaguetable_colr.max().max(), leaguetable_colr.min().min()
    df_max, df_min = max(confidence_map.values()), min(confidence_map.values())
    ranges = (df_max - df_min) * bounds + df_min
    ranges[-1] *= 1.001
    ranges = ranges + 1
    league_table_styles = []
    for treat_c in treatments:
        for treat_r in treatments:
            rob = robs.loc[treat_r, treat_c]
            indxs = np.where(rob < ranges)[0] if rob == rob else [0]
            clr_indx = indxs[0] - 1 if len(indxs) else 0
            diag, empty = treat_r == treat_c, rob != rob
            league_table_styles.append({'if': {'filter_query': f'{{Treatment}} = {{{treat_r}}}',
                                               'column_id': treat_c},
                                        'backgroundColor': cmap[clr_indx] if not empty else CLR_BCKGRND2,
                                        'color': CX1 if not empty else CX2 if diag else 'white'})
    league_table_styles.append({'if': {'column_id': 'Treatment'},
                                'backgroundColor': CX1})

    # Prepare for output
    tips = robs
    leaguetable = leaguetable.reset_index().rename(columns={'index': 'Treatment'})

    leaguetable_cols = [{"name": c, "id": c} for c in leaguetable.columns]
    leaguetable = leaguetable.to_dict('records')

    tooltip_values = [{col['id']: {'value': f"**Average ROB:** {tip[col['id']]}",
                                   'type': 'markdown'} if col['id'] != 'Treatment' else None
                           for col in leaguetable_cols} for rn, (_, tip) in enumerate(tips.iterrows())]
    if toggle_cinema:
        tooltip_values = [{col['id']: {'value': f"**Average ROB:** {tip[col['id']]}\n\n**Reason for Downgrading:**",
                                       'type': 'markdown'} if col['id'] != 'Treatment' else None
                       for col in leaguetable_cols} for rn, (_, tip) in enumerate(tips.iterrows())]


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
