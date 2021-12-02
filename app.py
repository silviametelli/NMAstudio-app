# Title     :  Dash NMA app
# Objective :  visualization tabs based on network interactivity
# Created by:  Silvia Metelli
# Created on: 10/11/2020
# --------------------------------------------------------------------------------------------------------------------#
import os, io, base64, shutil

import numpy as np

from tools.PATHS import __SESSIONS_FOLDER, TEMP_PATH

TEMP_DIR = "./__temp_logs_and_globals"
for dir in [TEMP_DIR, __SESSIONS_FOLDER, TEMP_PATH]:
    if not os.path.exists(dir): os.makedirs(dir)

import warnings
from collections import Counter
warnings.filterwarnings("ignore")
# --------------------------------------------------------------------------------------------------------------------#
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from flask_caching import Cache
from assets.COLORS import CINEMA_g, CINEMA_y, CINEMA_lb, CINEMA_r
import plotly.express as px, plotly.graph_objects as go
from tools.layouts import *
from tools.utils import *

from tools.functions_ranking_plots import __ranking_plot, __ranking_heatmap, __ranking_scatter
from tools.functions_funnel_plot import __Tap_funnelplot
from tools.functions_nmaforest_plot import __TapNodeData_fig, __TapNodeData_fig_bidim
from tools.functions_pairwise_plots import __update_forest_pairwise
from tools.functions_boxplots import __update_boxplot

# --------------------------------------------------------------------------------------------------------------------#

shutil.rmtree(TEMP_PATH, ignore_errors=True)
os.makedirs(TEMP_PATH, exist_ok=True)

EMPTY_SELECTION_NODES = {'active': {'ids': dict()}}
EMPTY_SELECTION_EDGES = {'id': None}
write_node_topickle(EMPTY_SELECTION_NODES)
write_edge_topickle(EMPTY_SELECTION_EDGES)

# Load extra layouts
cyto.load_extra_layouts()

GLOBAL_DATA = dict()

options_effect_size_cont = [{'label':'MD',  'value':'MD'},
                             {'label':'SMD',     'value':'SMD'}]
options_effect_size_bin = [{'label':'OR',  'value':'OR'},
                             {'label':'RR',     'value':'RR'}]

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                #external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
# app.config.suppress_callback_exceptions = True


# from assets.storage import STORAGE

server = app.server
app.layout = html.Div([dcc.Location(id='url', refresh=False),
                       html.Div(id='page-content')])


# ------------------------------ app interactivity ----------------------------------#

#####################################################################################
################################ MULTIPAGE CALLBACKS ################################
#####################################################################################

HOMEPAGE = Homepage()

# Update the index
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':  return HOMEPAGE
    elif pathname == '/doc': return doc_layout
    elif pathname == '/news': return news_layout
    else:  return HOMEPAGE

# Update which link is active in the navbar
@app.callback(Output('homepage-link', 'active'),
              [Input('url', 'pathname')])
def set_homepage_active(pathname):
    return pathname == '/home'

@app.callback(Output('docpage-link', 'active'), [Input('url', 'pathname')])
def set_docpage_active(pathname):
    return pathname == '/doc'

@app.callback(Output('newspage-link', 'active'), [Input('url', 'pathname')])
def set_docpage_active(pathname):
    return pathname == '/news'

#####################################################################################
#####################################################################################
################## -------- ALL PLOTS/TABLES CALLBACKS --------- ####################
#####################################################################################
#####################################################################################


### ---------------- PROJECT SETUP --------------- ###
@app.callback(Output("second-selection", "children"),
              [Input("dropdown-format", "value"),
               Input("dropdown-outcome1", "value"),
               Input("dropdown-outcome2", "value")])
def update_options(search_value_format, search_value_outcome1, search_value_outcome2):

    if search_value_format is None: return None
    if search_value_outcome1 is None: return None

    name_outcomes = ['1st outcome*', '2nd outcome'] if search_value_outcome2 is not None else ['1st outcome']
    search_values = [search_value_outcome1, search_value_outcome2] if search_value_outcome2 is not None else [search_value_outcome1]
    selectors_ef = html.Div([html.Div(
        [dbc.Row([html.P("Select effect size", style={'color': 'white', 'vertical-align': 'middle'})])] +
         [dbc.Row([dbc.Col(dbc.Row(
                  [html.P(f"{name}", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                   'margin-left': '0px', 'font-size': '12px'}),
                  dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-{name_outcomes}'},
                               options=options_effect_size_cont if val=='continuous' else options_effect_size_bin,
                               searchable=True, placeholder="...",
                               clearable=False, style={'width': '60px', "height":'20px',
                                                       'vertical-align': 'middle',
                                                       "font-size": "1em",
                                                       "font-family": "sans-serif",
                                                       'margin-bottom': '10px',
                                                       'display': 'inline-block',
                                                       'color': CLR_BCKGRND_old, 'font-size': '10px',
                                                       'background-color': CLR_BCKGRND_old} )]
          ),  style={'margin-left': '55px', 'margin-right': '5px'}) for name, val in zip(name_outcomes, search_values)]
        )],
     )])
    return selectors_ef


@app.callback([Output("dropdowns-DIV", "style"),
               Output("uploaded_datafile", "children")],
              Input('datatable-upload', 'filename'))
def is_data_file_uploaded(filename):
    show_DIV_style = {'display': 'inline-block', 'margin-bottom': '0px'}
    donot_show_DIV_style = {'display': 'none', 'margin-bottom': '0px'}
    if filename:
        return show_DIV_style, filename or ''
    else:
        return donot_show_DIV_style, ''


### --- update graph layout with dropdown: graph layout --- ###
@app.callback([Output('cytoscape', 'layout'),
               Output('modal-cytoscape', 'layout')],
              [Input('graph-layout-dropdown', 'children')],
              prevent_initial_call=False)
def update_cytoscape_layout(layout):
    ctx = dash.callback_context
    return {'name': layout.lower() if layout else 'circle',
            'animate': True}, {'name': layout.lower() if layout else 'circle',
                               'fit': True,
                               'animate': True}


### ----- update graph layout on node click ------ ###
@app.callback([Output('cytoscape', 'stylesheet'),
               Output('modal-cytoscape', 'stylesheet'),
               Output("consts_STORAGE", "data")],
              [Input('cytoscape', 'tapNode'),
               Input('cytoscape', 'selectedNodeData'),
               Input('cytoscape', 'elements'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('dd_nclr', 'children'),
               Input('dd_eclr', 'children'),
               Input('node_color_input', 'value'),
               Input('edge_color_input', 'value'),
               Input('dd_nds', 'children'),
               Input('dd_egs', 'children'),
               Input("btn-get-png", "n_clicks"),
               Input("btn-get-png-modal", "n_clicks"),],
               State("consts_STORAGE", "data"),
              )
def generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, dd_nds, dd_egs,
                        dwld_button, dwld_button_modal, constants):

    nodes_color = (custom_nd_clr or DFLT_ND_CLR) if dd_nclr != 'Default' else DFLT_ND_CLR
    edges_color = (custom_edg_clr or None) if dd_eclr != 'Default' else None

    node_size = dd_nds or 'Default'
    node_size = node_size == 'Tot randomized'
    edge_size = dd_egs or 'Number of studies'
    edge_size = edge_size == 'No size'
    pie = dd_nclr == 'Risk of Bias'
    cls = dd_nclr == 'By class'
    edg_lbl = dd_eclr == 'Add label'
    FOLLOWER_COLOR, FOLLOWING_COLOR = DFLT_ND_CLR, DFLT_ND_CLR
    stylesheet = get_stylesheet(pie=pie, classes=cls, edg_lbl=edg_lbl, edg_col=edges_color, nd_col=nodes_color, node_size=node_size, edge_size=edge_size)
    edgedata = [el['data'] for el in elements if 'target' in el['data'].keys()]
    all_nodes_id = [el['data']['id'] for el in elements if 'target' not in el['data'].keys()]

    if slct_nodesdata:
        selected_nodes_id = [d['id'] for d in slct_nodesdata]
        all_slct_src_trgt = list({e['source'] for e in edgedata if e['source'] in selected_nodes_id
                                  or e['target'] in selected_nodes_id}
                                 | {e['target'] for e in edgedata if e['source'] in selected_nodes_id
                                    or e['target'] in selected_nodes_id})

        stylesheet = get_stylesheet(pie=pie,  classes=cls, edg_lbl=edg_lbl, edg_col=edges_color, nd_col=nodes_color, node_size=node_size,
                                    nodes_opacity=0.2, edges_opacity=0.1) + [
                         {"selector": 'node[id = "{}"]'.format(id),
                          "style": {"border-color": "#751225", "border-width": 5, "border-opacity": 1,
                                    "opacity": 1}}
                         for id in selected_nodes_id] + [
                         {"selector": 'edge[id= "{}"]'.format(edge['id']),
                          "style": {'opacity': 1,  # "line-color": 'pink',
                                    'z-index': 5000}} for edge in edgedata if edge['source'] in selected_nodes_id
                                                                              or edge['target'] in selected_nodes_id] + [
                         {"selector": 'node[id = "{}"]'.format(id),
                          "style": {"opacity": 1}}
                         for id in all_nodes_id if id not in slct_nodesdata and id in all_slct_src_trgt]
    if slct_edgedata and False:  #TODO: Not doing much at the moment
        for edge in edgedata:
            if edge['source'] in selected_nodes_id:
                stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(edge['target']),
                    "style": {'background-color': FOLLOWING_COLOR, 'opacity': 0.9}})
                stylesheet.append({"selector": 'edge[id= "{}"]'.format(edge['id']),
                                   "style": {'opacity': 0.9,
                                             # "line-color": FOLLOWING_COLOR,
                                             # "mid-target-arrow-color": FOLLOWING_COLOR,
                                             # "mid-target-arrow-shape": "vee",
                                             'z-index': 5000}})
            if edge['target'] in selected_nodes_id:
                stylesheet.append({"selector": 'node[id = "{}"]'.format(edge['source']),
                                   "style": {'background-color': FOLLOWER_COLOR,
                                             'opacity': 0.9,
                                             'z-index': 9999}})
                stylesheet.append({"selector": 'edge[id= "{}"]'.format(edge['id']),
                                   "style": {'opacity': 1,
                                             "line-color": FOLLOWER_COLOR,
                                             "mid-target-arrow-color": FOLLOWER_COLOR,
                                             "mid-target-arrow-shape": "vee",
                                             'z-index': 5000}})

    if dwld_button and dwld_button > constants['dwnld_bttn_calls']:
        constants['dwnld_bttn_calls'] += 1
        stylesheet[0]['style']['color'] = 'black'
        time.sleep(0.05)

    if dwld_button_modal and dwld_button_modal > constants['dwnld_bttn_calls']:
        constants['dwnld_bttn_calls'] += 1
        stylesheet[0]['style']['color'] = 'black'
        time.sleep(0.05)

    sess_pickle = read_session_pickle(constants['session_pickle_path'])
    sess_pickle['wait'] = False
    write_session_pickle(dct=sess_pickle, path=constants['session_pickle_path'])
    stylesheet_modal  = stylesheet
    return stylesheet, stylesheet_modal, constants



### ----- save network plot as png ------ ###
@app.callback(Output("cytoscape", "generateImage"),
              [Input("btn-get-png", "n_clicks"),
               Input("btn-get-png-modal", "n_clicks"),
               Input('exp-options', 'children'),],
              State('consts_STORAGE','data'),
              prevent_initial_call=True)
def get_image(button, button_modal, export, constants):
    sess_pickle = read_session_pickle(constants['session_pickle_path'])
    sess_pickle['wait'] = True
    write_session_pickle(dct=sess_pickle, path=constants['session_pickle_path'])
    while read_session_pickle(constants['session_pickle_path'])['wait']:
        time.sleep(0.05)
    action = 'store'
    ctx = dash.callback_context
    if ctx.triggered:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if input_id != "tabs": action = "download"
    export_selection = export or 'as jpeg'
    return {'type': 'jpeg' if export_selection=='as jpeg' else ('png' if export_selection=='as png' else 'svg'), 'action': action,
            'options': {  # 'bg':'#40515e',
                'scale': 3}}
    # return {'type': 'jpeg' , 'action': action,
    #         'options': {  # 'bg':'#40515e',
    #             'scale': 3}}

### ----- update node info on NMA forest plot  ------ ###
@app.callback(Output('tapNodeData-info', 'children'),
              [Input('cytoscape', 'selectedNodeData')])
def TapNodeData_info(data):
    if data:
        return 'Reference treatment: ', data[0]['label']
    else:
        return 'Click on a node to choose reference'


### ----- update node info on bidim forest plot  ------ ###
@app.callback(Output('tapNodeData-info-bidim', 'children'),
              [Input('cytoscape', 'selectedNodeData')],
              # prevent_initial_call=True
              )
def TapNodeData_info(data):
    if data:
        return 'Reference treatment selected: ', data[0]['label']
    else:
        return 'Click on a node to choose reference'


### ----- update edge information on pairwise plot ------ ###
@app.callback(Output('tapEdgeData-info', 'children'),
              Input('cytoscape', 'selectedEdgeData'))
def TapEdgeData_info(data):
    if data:
        return 'Selected comparison: ', f"{data[0]['source'].upper()} vs {data[0]['target'].upper()}"
    else:
        return 'Click on an edge to display the associated  plot'


### ----- update node info on funnel plot  ------ ###
@app.callback(Output('tapNodeData-info-funnel', 'children'),
              [Input('cytoscape', 'tapNodeData')],
              # prevent_initial_call=True
              )
def TapNodeData_info(data):
    if data:
        return 'Reference treatment selected: ', data['label']
    else:
        return 'Click on a node to choose reference treatment'



### - display information box - ###
@app.callback(Output('cytoscape-mouseTapEdgeData-output', 'children'),
              [Input('cytoscape', 'selectedEdgeData')])
def TapEdgeData(edge):
    if edge:
        #     store_edge = read_edge_frompickle()
        #     if edge['id']==store_edge['id']: # You clicked it before: unselect it TODO: not working
        #         write_edge_topickle(EMPTY_SELECTION_EDGES)
        #     else:                            # New click: reset layout on nodes and select layout on edge
        #         write_edge_topickle(edge)
        n_studies = edge[0]['weight_lab']
        studies_str = f"{n_studies}" + (' studies' if n_studies > 1 else ' study')
        return f"{edge[0]['source'].upper()} vs {edge[0]['target'].upper()}: {studies_str}"
    else:
        return "Click on an edge to get information."


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:  # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:  # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded))



#### ---------------------- consistency table and netsplit table ------------------------ ####
@app.callback([Output('netsplit_table-container', 'data'),
              Output('netsplit_table-container', 'columns'),
               Output('consistency-table', 'data'),
               Output('consistency-table', 'columns')],
              [Input('cytoscape', 'selectedEdgeData'),
               Input("toggle_consistency_direction", "value"),
               Input('net_split_data_STORAGE', 'data'),
               Input('net_split_data_out2_STORAGE', 'data'),
               Input('consistency_data_STORAGE', 'data'),]
              )
def netsplit(edges, outcome, net_split_data, net_split_data_out2, consistency_data):

    df = (pd.read_json(net_split_data, orient='split') if not outcome
          else  pd.read_json(net_split_data_out2, orient='split') if net_split_data_out2 else None)
    consistency_data = pd.read_json(consistency_data, orient='split')
    if df is not None:
        comparisons = df.comparison.str.split(':', expand=True)
        df['Comparison'] = comparisons[0] + ' vs ' + comparisons[1]
        df = df.loc[:, ~df.columns.str.contains("comparison")]
        df = df.sort_values(by='Comparison').reset_index()
        df = df[['Comparison', "direct", "indirect", "p-value"]].round(decimals=4)

    slctd_comps = []
    for edge in edges or []:
        src, trgt = edge['source'], edge['target']
        slctd_comps += [f'{src} vs {trgt}']
    if edges and df is not None:
        df = df[df.Comparison.isin(slctd_comps)]

    data_cols = [{"name": c, "id": c} for c in df.columns]
    data_output = df.to_dict('records') if df is not None else dict()
    _out_net_split_table = [data_output, data_cols]

    data_consistency = consistency_data.round(decimals=4).to_dict('records')
    consistency_tbl_cols = [{"name": i, "id": i} for i in consistency_data.columns]
    _out_consistency_table = [data_consistency, consistency_tbl_cols]

    return _out_net_split_table + _out_consistency_table

### ----- upload CINeMA data file 1 ------ ###
@app.callback([Output("cinema_net_data1_STORAGE", "data"),
               Output("file2-list", "children")],
              [Input('datatable-secondfile-upload', 'contents'),
               Input('cinema_net_data1_STORAGE', 'data')],
              [State('datatable-secondfile-upload', 'filename')])
def get_new_data_cinema1(contents, cinema_net_data1, filename):
    if contents is None:
        cinema_net_data1 = pd.read_json(cinema_net_data1, orient='split')
    else:
        cinema_net_data1 = parse_contents(contents, filename)
    if filename is not None:
        return cinema_net_data1.to_json(orient='split'), 'loaded'
    else:
        return cinema_net_data1.to_json(orient='split'), ''

### ----- upload CINeMA data file 2 ------ ###
@app.callback([Output("cinema_net_data2_STORAGE", "data"),
               Output("file2-list-2", "children"),],
              [Input('datatable-secondfile-upload-2', 'contents'),
               Input('cinema_net_data2_STORAGE', 'data'),],
              [State('datatable-secondfile-upload-2', 'filename')])
def get_new_data_cinema2(contents, cinema_net_data2, filename):

    if contents is None:
        cinema_net_data2 = pd.read_json(cinema_net_data2, orient='split')
    else:
        cinema_net_data2 = parse_contents(contents, filename)

    if filename is not None:
        return cinema_net_data2.to_json(orient='split'), 'loaded'
    else:
        return cinema_net_data2.to_json(orient='split'), ''


### ----- Update layout with slider ------ ###
@app.callback([Output('cytoscape', 'elements'),
               Output('modal-cytoscape', 'elements')
               ],
              [Input('net_data_STORAGE', 'data'),
               Input('slider-year', 'value')])
def update_layour_year_slider(net_data, slider_year):
    net_data = pd.read_json(net_data, orient='split')
    net_data = net_data[net_data.year <= slider_year]
    elements = get_network(df=net_data)
    return elements, elements

#########################################################
### ----- display Data Table and League Table ------ ###
#########################################################
@app.callback([Output('datatable-upload-container', 'data'),
               Output('datatable-upload-container', 'columns'),
               Output('datatable-upload-container-expanded', 'data'),
               Output('datatable-upload-container-expanded', 'columns'),
               Output('league_table', 'children'),
               Output('modal_league_table_data', 'children'),
               Output('league_table_legend', 'children'),
               Output('modal_league_table_legend', 'children'),
               Output('rob_vs_cinema', 'value'),
               Output('rob_vs_cinema_modal', 'value'),
               Output('slider-year', 'min'),
               Output('slider-year', 'max'),
               Output('slider-year', 'marks')],
              [Input('cytoscape', 'selectedNodeData'),
               Input('net_data_STORAGE', 'data'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('rob_vs_cinema', 'value'),
               Input('rob_vs_cinema_modal', 'value'),
               Input('slider-year', 'value'),
               #Input('datatable-secondfile-upload-2', 'contents')
               Input('league_table_data_STORAGE', 'data'),
               Input('cinema_net_data1_STORAGE', 'data'),
               Input('cinema_net_data2_STORAGE', 'data'),
                ],
              [State('net_data_STORAGE', 'modified_timestamp'),
               State('league_table_data_STORAGE', 'modified_timestamp')],
              prevent_initial_call=True)
def update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
                  league_table_data, cinema_net_data1, cinema_net_data2,
                  net_data_STORAGE_TIMESTAMP, league_table_data_STORAGE_TIMESTAMP):

    # ctx = dash.callback_context
    # print(net_data_STORAGE_TIMESTAMP, league_table_data_STORAGE_TIMESTAMP,
    #       net_data_STORAGE_TIMESTAMP - league_table_data_STORAGE_TIMESTAMP)
    # if ((abs(net_data_STORAGE_TIMESTAMP - league_table_data_STORAGE_TIMESTAMP)>150_000) and
    #     (net_data_STORAGE_TIMESTAMP < league_table_data_STORAGE_TIMESTAMP)):
    #     print('preventing update')
    #     raise PreventUpdate
    # if ctx.triggered:
    #     print(ctx.triggered[0]['prop_id'].split('.')[0])

    net_data = pd.read_json(net_data, orient='split').round(3)
    years = net_data.year
    slider_min, slider_max = years.min(), years.max()
    slider_marks = set_slider_marks(slider_min, slider_max, years)
    _out_slider = [slider_min, slider_max, slider_marks]

    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'rob_vs_cinema.value' in triggered:
        toggle_cinema_modal = toggle_cinema
    elif 'rob_vs_cinema_modal.value' in triggered:
        toggle_cinema = toggle_cinema_modal

    if 'slider-year.value' in triggered:
        _data = GLOBAL_DATA["data_and_league_table_callback_FULL_DATA"]
        data_output = _data[_data.year <= slider_value].to_dict('records')
        _OUTPUT0 = GLOBAL_DATA["data_and_league_table_callback_OUTPUT"]
        _output = [data_output]+[_OUTPUT0[1]]+[data_output] + _OUTPUT0[3:]

        return _output + _out_slider

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
        robs = comprs_conf
    # Filter according to cytoscape selection
    if store_node:
        slctd_trmnts = [nd['id'] for nd in store_node]
        if len(slctd_trmnts) > 0:
            leaguetable = leaguetable.loc[slctd_trmnts, slctd_trmnts]
            robs = robs.loc[slctd_trmnts, slctd_trmnts]
            treatments = slctd_trmnts

    #####   Add style colouring and legend
    N_BINS = 3 if not toggle_cinema else 4
    bounds = np.arange(N_BINS + 1) / N_BINS

    leaguetable_colr = robs.copy(deep=True)
    np.fill_diagonal(leaguetable_colr.values, np.nan)
    leaguetable_colr = leaguetable_colr.astype(np.float64)

    # cmap = [clrs.to_hex(plt.get_cmap('RdYlGn_r', N_BINS)(n)) for n in range(N_BINS)]
    cmap = [CINEMA_g, CINEMA_y, CINEMA_r] if not toggle_cinema else [CINEMA_r, CINEMA_y, CINEMA_lb, CINEMA_g]
    legend_height = '4px'
    legend = [html.Div(style={'display': 'inline-block', 'width': '100px'},
                       children=[html.Div(),
                                 html.Small('Risk of bias: ' if not toggle_cinema else 'CINeMA rating: ',
                                            style={'color': 'white'})])]
    legend += [html.Div(style={'display': 'inline-block', 'width': '60px'},
                        children=[html.Div(style={'backgroundColor': cmap[n],
                                                  'borderLeft': '1px rgb(50, 50, 50) solid',
                                                  'height': legend_height}), html.Small(
                            ('Very Low' if toggle_cinema else 'Low') if n == 0 else 'High' if n == N_BINS - 1 else None,
                            style={'paddingLeft': '2px', 'color': 'white'})])
               for n in range(N_BINS)]

    #df_max, df_min = leaguetable_colr.max().max(), leaguetable_colr.min().min()
    df_max, df_min = max(confidence_map.values()), min(confidence_map.values())
    ranges = (df_max - df_min) * bounds + df_min
    ranges[-1] *= 1.001
    league_table_styles = []
    for treat_c in treatments:
        for treat_r in treatments:
            rob = robs.loc[treat_r, treat_c]
            indxs = np.where(rob < ranges)[0] if rob == rob else [0]
            clr_indx = indxs[0] - 1 if len(indxs) else 0
            diag, empty = treat_r == treat_c, rob != rob
            league_table_styles.append({'if': {'filter_query': f'{{Treatment}} = {{{treat_r}}}',
                                  'column_id': treat_c},
                           'backgroundColor': cmap[clr_indx] if not empty else '#40515e',
                           'color': 'rgb(26, 36, 43)' if not empty else '#d6d6d6' if diag else 'white'})
    league_table_styles.append({'if': {'column_id': 'Treatment'},
                   'backgroundColor': 'rgb(26, 36, 43)'})

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
    GLOBAL_DATA["data_and_league_table_callback_FULL_DATA"] = net_data
    _output = [data_output, data_cols] * 2 + [league_table, league_table_modal] + [legend] * 2 + [toggle_cinema, toggle_cinema_modal]
    GLOBAL_DATA["data_and_league_table_callback_OUTPUT"] =   _output
    return _output + _out_slider

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


#######################################################################################
########################## ALL plots calling tools.function ###########################
#######################################################################################


### - figures on edge click: transitivity boxplots  - ###
@app.callback(Output('tapEdgeData-fig', 'figure'),
              [Input('dropdown-effectmod', 'value'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('net_data_STORAGE','data')])
def update_boxplot(value, edges, net_data):
    return __update_boxplot(value, edges, net_data)



### - figures on edge click: pairwise forest plots  - ###
@app.callback(Output('tapEdgeData-fig-pairwise', 'figure'),
              [Input('cytoscape', 'selectedEdgeData'),
               Input("toggle_forest_pair_outcome", "value"),
               Input('forest_data_prws_STORAGE', 'data'),
               Input('forest_data_prws_out2_STORAGE', 'data')])

def  update_forest_pairwise(edge, outcome, forest_data_prws, forest_data_prws_out_2):
    return __update_forest_pairwise(edge, outcome, forest_data_prws, forest_data_prws_out_2)



### ----- display forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input("toggle_forest_direction", "value"),
               Input("toggle_forest_outcome", "value"),
               Input("forest_data_STORAGE", "data"),
               Input("forest_data_out2_STORAGE", "data")
               ])
def TapNodeData_fig(data, outcome_direction, outcome, forest_data, forest_data_out2):
    return __TapNodeData_fig(data, outcome_direction, outcome, forest_data, forest_data_out2)



### ----- display dibim forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig-bidim', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input('forest_data_STORAGE', 'data'),
               Input('forest_data_out2_STORAGE', 'data')],
               State('ranking_data_STORAGE', 'data')
              )
def TapNodeData_fig_bidim(data, forest_data, forest_data_out2, ranking_data):
    return __TapNodeData_fig_bidim(data, forest_data, forest_data_out2, ranking_data)



############ - Funnel plot  - ###############
@app.callback(Output('funnel-fig', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input("toggle_funnel_direction", "value"),
               Input("funnel_data_STORAGE", "data"),
               Input("funnel_data_out2_STORAGE", "data")],
               #State({'type': 'dataselectors', 'index': ALL}, 'value')
               )
def Tap_funnelplot(node, outcome2, funnel_data, funnel_data_out2):
    return __Tap_funnelplot(node, outcome2, funnel_data, funnel_data_out2)



############ - ranking plots  - ###############
@app.callback([Output('tab-rank1', 'figure'),
               Output('tab-rank2', 'figure')],
              [Input('toggle_rank_direction', 'value'),
               Input('toggle_rank2_direction', 'value'),
               Input('toggle_rank2_direction_outcome1', 'value'),
               Input('toggle_rank2_direction_outcome2', 'value'),
               Input('net_data_STORAGE', 'data'),
               Input('ranking_data_STORAGE', 'data')])
def ranking_plot(outcome_direction_1, outcome_direction_2,
                 outcome_direction_11, outcome_direction_22,
                 net_data, ranking_data):
    return __ranking_plot(outcome_direction_1, outcome_direction_2,
                          outcome_direction_11, outcome_direction_22,
                          net_data, ranking_data)


#############################################################################
############################# TOGGLE SECTION ################################
#############################################################################

### -------------- toggle switch forest beneficial/harm ---------------- ###
@app.callback([Output("forestswitchlabel1", "style"),
               Output("forestswitchlabel2", "style")],
              [Input("toggle_forest_direction", "value")])
def color_forest_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', }
    return style1, style2

### -------------- toggle switch forest outcome1/outcome2 ---------------- ###
@app.callback([Output("forestswitchlabel_outcome1", "style"),
               Output("forestswitchlabel_outcome2", "style")],
              [Input("toggle_forest_outcome", "value")])
def color_funnel_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

### -------------- toggle switch forest pairwise outcome1/outcome2 ---------------- ###
@app.callback([Output("forest_pair_switchlabel_outcome1", "style"),
               Output("forest_pair_switchlabel_outcome2", "style")],
              [Input("toggle_forest_pair_outcome", "value")])
def color_funnel_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

### -------------- toggle switch rank  ---------------- ###
### heatmap
@app.callback([Output("rankswitchlabel1", "style"),
               Output("rankswitchlabel2", "style")],
              [Input("toggle_rank_direction", "value")])
def color_rank1_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

@app.callback([Output("rank2switchlabel1", "style"),
               Output("rank2switchlabel2", "style")],
              [Input("toggle_rank2_direction", "value")])
def color_rank2_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

#### scatter plot
@app.callback([Output("rank2switchlabel11", "style"),
               Output("rank2switchlabel22", "style")],
              [Input("toggle_rank2_direction_outcome1", "value")])
def color_rank1_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

@app.callback([Output("rankswitchlabel11", "style"),
               Output("rankswitchlabel22", "style")],
              [Input("toggle_rank2_direction_outcome2", "value")])
def color_rank2_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

### -------------- toggle switch league table ---------------- ###
@app.callback([Output("cinemaswitchlabel1", "style"),
               Output("cinemaswitchlabel2", "style")],
              [Input("rob_vs_cinema", "value")])
def color_leaguetable_toggle(toggle_value):
    style1 = {'color': '#808484' if toggle_value else '#b6e1f8', 'font-size': '12px',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '10px'}
    style2 = {'color': '#b6e1f8' if toggle_value else '#808484', 'font-size': '12px',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '0px', }
    return style1, style2

### -------------- toggle switch funnel plot ---------------- ###
@app.callback([Output("funnelswitchlabel1", "style"),
               Output("funnelswitchlabel2", "style")],
              [Input("toggle_funnel_direction", "value")])
def color_funnel_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

### -------------- toggle switch consistency ---------------- ###
@app.callback([Output("consistencyswitchlabel1", "style"),
               Output("consistencyswitchlabel2", "style")],
              [Input("toggle_consistency_direction", "value")])
def color_funnel_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

##############################################################################
######################### DISABLE  TOGGLE SWITCHES ###########################
##############################################################################

## disable outcome 2 toggle if no outcome 2 is given in data
@app.callback([Output('toggle_funnel_direction', 'disabled'),
              Output('toggle_forest_outcome', 'disabled'),
              Output('toggle_forest_pair_outcome', 'disabled'),
              Output('toggle_rank2_direction', 'disabled'),
              Output('toggle_rank2_direction_outcome1', 'disabled'),
              Output('toggle_rank2_direction_outcome2', 'disabled'),
              Output('toggle_consistency_direction', 'disabled'),
               ],
              Input('ranking_data_STORAGE','data')
              )
def disable_out2_toggle(ranking_data):
    df_ranking = pd.read_json(ranking_data, orient='split')
    df_ranking = df_ranking.loc[:, ~df_ranking.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    if "pscore2" not in df_ranking.columns:
        return True, True, True, True, True, True, True
    else: return False, False, False, False, False, False, False


@app.callback(Output('rob_vs_cinema', 'disabled'),
              Input('datatable-secondfile-upload', 'filename')
              )
def disable_cinema_toggle(filename):
    if filename is None: return True
    else: return False

###############################################################################
################### EXPORT TO  CSV ON CLICK BUTTON ############################
###############################################################################

@app.callback(Output("download_datatable", "data"),
              [Input('data-export', "n_clicks"),
               State('datatable-upload-container', 'data')],
               prevent_initial_call=True)
def generate_csv(n_nlicks, data):
    df = pd.DataFrame(data)
    return dash.dcc.send_data_frame(df.to_csv, filename="data_wide.csv")

@app.callback(Output("download_leaguetable", "data"),
              [Input('league-export', "n_clicks"),
               State("league_table", "children")],
               prevent_initial_call=True)
def generate_csv(n_nlicks, leaguedata):
    df = pd.DataFrame(leaguedata['props']['data'])
    # df.sort_values(by='Treatment').set_index('Treatment', inplace=True)
    df = df.set_index('Treatment')[df.Treatment]

    # def to_xlsx(bytes_io):
    #     writer = pd.ExcelWriter(bytes_io, engine='xlsxwriter')  # Create a Pandas Excel writer using XlsxWriter as the engine.
    #     df.to_excel(writer, sheet_name='Sheet1')  # Convert the dataframe to an XlsxWriter Excel object.
    #     workbook, worksheet = writer.book, writer.sheets['Sheet1']  # Get the xlsxwriter workbook and worksheet objects.
    #     # Add a format. Light red fill with dark red text.
    #     # CINEMA_r, CINEMA_y, CINEMA_lb, CINEMA_g
    #     format1 = workbook.add_format({'bg_color': CINEMA_r,
    #                                    'font_color': '#9C0006'})
    #     # Set the conditional format range.
    #     start_row, start_col = 1, 3
    #     end_row, end_cold = len(df), start_col
    #     # Apply a conditional format to the cell range.
    #     worksheet.conditional_format(start_row, start_col, end_row, end_cold,
    #                                  {'type': 'cell',
    #                                   'criteria': '>',
    #                                   'value': 20,
    #                                   'format': format1})
    #     for idx, col in enumerate(df):  # loop through all columns
    #         series = df[col]
    #         max_len = max((
    #             series.astype(str).map(len).max(),  # len of largest item
    #             len(str(series.name))  # len of column name/header
    #         )) + 1  # adding a little extra space
    #         worksheet.set_column(idx, idx, max_len)  # set column width
    #     writer.save()  # Close the Pandas Excel writer and output the Excel file.
    #
    # return dash.dcc.send_bytes(to_xlsx, filename="league_table.xlsx")
   # return dash.dcc.send_data_frame(writer.save(), filename="league_table.xlsx")

    return dash.dcc.send_data_frame(df.to_csv, filename="league_table.csv")

###############################################################################
################### Bootstrap Dropdowns callbacks #############################
###############################################################################

@app.callback([Output('dd_nds', 'children')],
              [Input('dd_nds_default', 'n_clicks_timestamp'), Input('dd_nds_default', 'children'),
               Input('dd_nds_tot_rnd', 'n_clicks_timestamp'), Input('dd_nds_tot_rnd', 'children')],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, tot_rnd_t, tot_rnd_v):
    values = [default_v, tot_rnd_v]
    dd_nds = [default_t or 0, tot_rnd_t or 0]
    which = dd_nds.index(max(dd_nds))
    return [values[which]]

@app.callback([Output('exp-options', 'children')],
              [Input('jpeg-option', 'n_clicks_timestamp'), Input('jpeg-option', 'children'),
               Input('png-option', 'n_clicks_timestamp'), Input('png-option', 'children'),
               Input('svg-option', 'n_clicks_timestamp'), Input('svg-option', 'children'),],
              prevent_initial_call=True)
def which_dd_export(default_t, default_v, png_t, png_v, svg_t, svg_v): #TODO: for some reason, default is svg
    values = [default_v, png_v, svg_v]
    dd_nds = [default_t or 0, png_t or 0, svg_t or 0]
    which = dd_nds.index(max(dd_nds))
    return [values[which]]

@app.callback([Output('dd_egs', 'children')],
              [Input('dd_egs_default', 'n_clicks_timestamp'), Input('dd_egs_default', 'children'),
               Input('dd_egs_tot_rnd', 'n_clicks_timestamp'), Input('dd_egs_tot_rnd', 'children')],
              prevent_initial_call=True)
def which_dd_egs(default_t, default_v, nstud_t, nstud_v):
    values = [default_v, nstud_v]
    dd_egs = [default_t or 0, nstud_t or 0]
    which = dd_egs.index(max(dd_egs))
    return [values[which]]


@app.callback([Output('dd_nclr', 'children'), Output('close_modal_dd_nclr_input', 'n_clicks'),
               Output("open_modal_dd_nclr_input", "n_clicks")],
              [Input('dd_nclr_default', 'n_clicks_timestamp'), Input('dd_nclr_default', 'children'),
               Input('dd_nclr_rob', 'n_clicks_timestamp'), Input('dd_nclr_rob', 'children'),
               Input('dd_nclr_class', 'n_clicks_timestamp'), Input('dd_nclr_class', 'children'),
               Input('close_modal_dd_nclr_input', 'n_clicks'),
               ],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, rob_t, rob_v, class_t, class_v, closing_modal):
    values = [default_v, rob_v, class_v]
    dd_nclr = [default_t or 0, rob_t or 0, class_t or 0]
    which = dd_nclr.index(max(dd_nclr))
    return values[which] if not closing_modal else None, None, None



@app.callback([Output('dd_eclr', 'children'), Output('close_modal_dd_eclr_input', 'n_clicks'),
               Output("open_modal_dd_eclr_input", "n_clicks")],
              [Input('dd_edge_default', 'n_clicks_timestamp'), Input('dd_edge_default', 'children'),
               Input('dd_edge_label', 'n_clicks_timestamp'), Input('dd_edge_label', 'children'),
               Input('close_modal_dd_eclr_input', 'n_clicks'),
               ],
              prevent_initial_call=True)
def which_dd_edges(default_t, default_v, eclr_t, eclr_v, closing_modal):
    values = [default_v, eclr_v]
    dd_eclr = [default_t or 0, eclr_t or 0]
    which = dd_eclr.index(max(dd_eclr))
    return values[which] if not closing_modal else None, None, None

flatten = lambda t: [item for sublist in t for item in sublist]



@app.callback([Output('graph-layout-dropdown', 'children')],
              flatten([[Input(f'dd_ngl_{item.lower()}', 'n_clicks_timestamp'),
                        Input(f'dd_ngl_{item.lower()}', 'children')]
                       for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                                    'Cose-Bilkent', 'Dagre', 'Klay']
                       ]),
              prevent_initial_call=True)
def which_dd_nds(circle_t, circle_v, breadthfirst_t, breadthfirst_v,
                 grid_t, grid_v, spread_t, spread_v, cose_t, cose_v,
                 cola_t, cola_v, cose_bilkent_t, cose_bilkent_v,
                 dagre_t, dagre_v, klay_t, klay_v):
    values = [circle_v, breadthfirst_v, grid_v, spread_v, cose_v, cola_v, cose_bilkent_v,
              dagre_v, klay_v]
    times = [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, cola_t, cose_bilkent_t,
             dagre_t, klay_t]
    dd_ngl = [t or 0 for t in times]
    which = dd_ngl.index(max(dd_ngl))
    return [values[which]]


#################################################################
############### Bootstrap MODALS callbacks ######################
#################################################################

# ----- node color modal -----#
@app.callback(Output("modal", "is_open"),
              [Input("open_modal_dd_nclr_input", "n_clicks"),
               Input("close_modal_dd_nclr_input", "n_clicks")],
              )
def toggle_modal(open_t, close):
    if open_t: return True
    if close: return False
    return False

# ----- edge color modal -----#
@app.callback(Output("modal_edge", "is_open"),
              [Input("open_modal_dd_eclr_input", "n_clicks"),
               Input("close_modal_dd_eclr_input", "n_clicks")],
              )
def toggle_modal_edge(open_t, close):
    if open_t: return True
    if close: return False
    return False


# ----- data selector modal -------#

@app.callback([Output("modal_data", "is_open"),
               Output("modal_data_checks", "is_open"),
               Output("TEMP_net_data_STORAGE", "data"),
               ],
              [Input("upload_your_data", "n_clicks_timestamp"),
               Input("upload_modal_data", "n_clicks_timestamp"),
               Input("submit_modal_data", "n_clicks_timestamp"),
               ],
              [State("dropdown-format","value"),
               State("dropdown-outcome1","value"),
               State("dropdown-outcome2","value"),
               State("modal_data", "is_open"),
               State("modal_data_checks", "is_open"),
               State('datatable-upload', 'contents'),
               State('datatable-upload', 'filename'),
               State({'type': 'dataselectors', 'index': ALL}, 'value'),
               State("TEMP_net_data_STORAGE", "data")
               ]
              )
def data_modal(open_modal_data, upload, submit,
               value_format, value_outcome1, value_outcome2,
               modal_data_is_open, modal_data_checks_is_open,
               contents, filename, dataselectors, TEMP_net_data_STORAGE
               ):
    ctx = dash.callback_context
    if not ctx.triggered: button_id = 'No clicks yet'
    else:                 button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if open_modal_data:
        if upload and button_id=='upload_modal_data':
            data = parse_contents(contents, filename)
            data = adjust_data(data, dataselectors, value_format ,value_outcome1, value_outcome2)
            TEMP_net_data_STORAGE = data.to_json( orient='split')
            if submit and button_id == 'submit_modal_data':
                return not modal_data_is_open, not modal_data_checks_is_open and (not modal_data_is_open), TEMP_net_data_STORAGE
            return not modal_data_is_open, not modal_data_checks_is_open, TEMP_net_data_STORAGE

        return not modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE
    else:
        return modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE



@app.callback(Output("upload_modal_data", "disabled"),
              Input({'type': 'dataselectors', 'index': ALL}, 'value'),
              )
def modal_ENABLE_UPLOAD_button(dataselectors):
    return not all(dataselectors) if len(dataselectors) else True


from assets.storage import DEFAULT_DATA

OUTPUTS_STORAGE_IDS = list(DEFAULT_DATA.keys())[:-2]

@app.callback([Output(id, 'data') for id in OUTPUTS_STORAGE_IDS],
              [Input("submit_modal_data", "n_clicks")],
              [State('TEMP_'+id, 'data') for id in OUTPUTS_STORAGE_IDS],
              prevent_initial_call=True)
def modal_SUBMIT_button(submit,
                        TEMP_net_data_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        TEMP_user_elements_STORAGE,
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
                        ):
    """ reads in temporary data for all analyses and outputs them in non-temp storages """
    if submit:
        OUT_DATA = [TEMP_net_data_STORAGE, TEMP_consistency_data_STORAGE, TEMP_user_elements_STORAGE, TEMP_forest_data_STORAGE,
                    TEMP_forest_data_out2_STORAGE, TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2_STORAGE,
                    TEMP_ranking_data_STORAGE, TEMP_funnel_data_STORAGE, TEMP_funnel_data_out2_STORAGE,
                    TEMP_league_table_data_STORAGE, TEMP_net_split_data_STORAGE, TEMP_net_split_data_out2_STORAGE]
        return OUT_DATA
    else:
        return list(DEFAULT_DATA.values())[:-2]


@app.callback(Output("dropdown-effectmod", "options"),
              Input("net_data_STORAGE", "data"),
              )
def update_dropdown_effect_mod(new_data):
    new_data = pd.read_json(new_data, orient='split')
    OPTIONS_VAR = [{'label': '{}'.format(col), 'value': col}
                   for col in new_data.select_dtypes(['number']).columns]
    return OPTIONS_VAR


import time
@app.callback([Output("para-check-data", "children"),
               Output('para-check-data', 'data')],
              Input("modal_data_checks", "is_open"),
              State("TEMP_net_data_STORAGE", "data"),
              )
def modal_submit_checks_DATACHECKS(modal_data_checks_is_open, TEMP_net_data_STORAGE):
    if modal_data_checks_is_open:
        data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
        passed_checks = data_checks(data)
        if all(passed_checks.values()):
            return html.P(u"\u2713" + " All data checks passed.", style={"color":"green"}), '__Para_Done__'
        else:
            return (html.P([u"\u274C",
                            " WARNING - some data checks failed:"]+sum([[html.Br(), f'Failed on {k}']
                                                                        for k,v in passed_checks.items()
                                                                        if not v], []), style={"color": "red"}),
                    '__Para_Done__')
    else:
        return None, ''


@app.callback([Output("para-anls-data", "children"),
               Output('para-anls-data', 'data'),
               Output("TEMP_forest_data_STORAGE", "data"),
               Output("TEMP_user_elements_STORAGE", "data")],
              Input("modal_data_checks", "is_open"),
              Input("toggle_forest_outcome", "value"),
              State("TEMP_net_data_STORAGE", "data"),
              State("TEMP_forest_data_STORAGE", "data")
              )
def modal_submit_checks_NMA(modal_data_checks_is_open, outcome2, TEMP_net_data_STORAGE, TEMP_forest_data_STORAGE):
    if modal_data_checks_is_open:
        net_data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
        NMA_data = run_network_meta_analysis(net_data)
        TEMP_forest_data_STORAGE = NMA_data.to_json( orient='split')
        TEMP_user_elements_STORAGE = get_network(df=net_data)
        if outcome2:
            pass
        return (html.P(u"\u2713" + " Network meta-analysis run successfully.", style={"color":"green"}),
                '__Para_Done__', TEMP_forest_data_STORAGE, TEMP_user_elements_STORAGE)
    else:
        return None, '', TEMP_forest_data_STORAGE, None


@app.callback([Output("para-pairwise-data", "children"),
               Output('para-pairwise-data', 'data'),
               Output("TEMP_forest_data_prws_STORAGE", "data")],
              Input('TEMP_forest_data_STORAGE', 'modified_timestamp'),
              State("modal_data_checks", "is_open"),
              State("TEMP_net_data_STORAGE", "data"),
              State("TEMP_forest_data_prws_STORAGE", "data")
              )
def modal_submit_checks_PAIRWISE(nma_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE):
    if modal_data_checks_is_open:
        PAIRWISE_data = run_pairwise_MA(pd.read_json(TEMP_net_data_STORAGE, orient='split'))
        TEMP_forest_data_prws_STORAGE = PAIRWISE_data.to_json( orient='split')


        return (html.P(u"\u2713" + " Pairwise meta-analysis run successfully.", style={"color":"green"}),
                '__Para_Done__', TEMP_forest_data_prws_STORAGE)
    else:
        return None, '', TEMP_forest_data_prws_STORAGE

@app.callback([Output("para-LT-data", "children"),
               Output('para-LT-data', 'data'),
               Output('TEMP_league_table_data_STORAGE', 'data'),
               Output('TEMP_ranking_data_STORAGE', 'data'),
               Output('TEMP_consistency_data_STORAGE', 'data'),
               Output('TEMP_net_split_data_STORAGE', 'data'),
               Output('TEMP_net_split_data_out2_STORAGE', 'data')],
               Input('TEMP_forest_data_prws_STORAGE', 'modified_timestamp'),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State('TEMP_league_table_data_STORAGE', 'data'),
               State('TEMP_ranking_data_STORAGE', 'data'),
               State('TEMP_consistency_data_STORAGE', 'data'),
               State('TEMP_net_split_data_STORAGE', 'data'),
               State('TEMP_net_split_data_out2_STORAGE', 'data')
              )
def modal_submit_checks_LT(pw_data_ts, modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data, net_split_data2):
    """ produce new league table from R """
    if modal_data_checks_is_open:
        data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
        LEAGUETABLE_OUTS =  generate_league_table(data, outcome2=False) if "TE2" not in data.columns else generate_league_table(data, outcome2=True)
        if "TE2" not in data.columns:
            (LEAGUETABLE_data, ranking_data, consistency_data, net_split_data)= [f.to_json( orient='split') for f in LEAGUETABLE_OUTS]
        else:  (LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2)= [f.to_json( orient='split') for f in LEAGUETABLE_OUTS]

        return (html.P(u"\u2713" + " Successfully generated league table.", style={"color":"green"}),
                '__Para_Done__', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data) if "TE2" not in data.columns else  (html.P(u"\u2713" + " Successfully generated league table.", style={"color":"green"}),
                '__Para_Done__', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2)
    else:
        net_split_data2 = {}
        return None, '', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2


@app.callback([Output("para-FA-data", "children"),
               Output('para-FA-data', 'data'),
               Output('TEMP_funnel_data_STORAGE', 'data')],
              Input("TEMP_league_table_data_STORAGE", "modified_timestamp"),
              State("modal_data_checks", "is_open"),
              State("TEMP_net_data_STORAGE", "data"),
              State('TEMP_funnel_data_STORAGE', 'data')
              )
def modal_submit_checks_FUNNEL(lt_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data):
    if modal_data_checks_is_open:
        FUNNEL_data = generate_funnel_data(pd.read_json(TEMP_net_data_STORAGE, orient='split'))
        FUNNEL_data = FUNNEL_data.to_json(orient='split')
        return (html.P(u"\u2713" + " Successfully generated funnel plot data.", style={"color":"green"}),
                '__Para_Done__', FUNNEL_data)
    else:
        return None, '', FUNNEL_data

@app.callback(Output("submit_modal_data", "disabled"),
              [Input(id, 'data') for id in ['para-check-data','para-anls-data','para-pairwise-data',
                                            'para-LT-data', 'para-FA-data']])
def modal_submit_button(para_check_data_DATA, para_anls_data_DATA, para_prw_data_DATA, para_LT_data_DATA, para_FA_data_DATA):
    return not (para_check_data_DATA==para_anls_data_DATA==para_prw_data_DATA==para_LT_data_DATA==para_FA_data_DATA=='__Para_Done__')




# ----- data expand modal -----#
@app.callback(
    Output("modal_data_table", "is_open"),
    [Input("data-expand", "n_clicks"),
     Input("close-data-expanded", "n_clicks")],
    [State("modal_data_table", "is_open")],
)
def toggle_modal(open, close, is_open):
    if open or close:
        return not is_open
    return is_open


# ----- league expand modal -----#
@app.callback(
    Output("modal_league_table", "is_open"),
    [Input("league-expand", "n_clicks"),
     Input("close-league-expanded", "n_clicks")],
    [State("modal_league_table", "is_open")],
)
def toggle_modal(open, close, is_open):
    if open or close:
        return not is_open
    return is_open

# ----- network expand modal -----#
@app.callback(
    Output("modal_network", "is_open"),
    [Input("network-expand", "n_clicks"),
     Input("close-network-expanded", "n_clicks")],
    [State("modal_network", "is_open")],
)
def toggle_modal(open, close, is_open):
    if open or close:
        return not is_open
    return is_open

##################################################################
########################### ALERTS ###############################
##################################################################

@app.callback(Output('data-type-danger', 'displayed'),
              [Input('datatable-upload', 'filename'),
              Input("net_data_STORAGE", "data"),
              Input("modal_data", "is_open"),
              Input("dropdown-outcome1", "value"),
              Input("dropdown-outcome2", "value")],
              )
def display_confirm(filename, data, modal_data_open, value_outcome1, value_outcome2):
    data_ = pd.read_json(data, orient='split')
    if modal_data_open and filename is not None and value_outcome1 is not None:
        if value_outcome2 is None:
            return True if ('y1' in data_.columns and value_outcome1=="continuous") or ('r1' in data_.columns and value_outcome1=="binary") else False
        else:
            return True if ('y1' in data_.columns and value_outcome1=="continuous") or ('r1' in data_.columns and value_outcome1=="binary") or ('y2' in data_.columns and value_outcome2=="continuous") or ('r2' in data_.columns and value_outcome2=="binary") else False
    else: return False




###################################################################
###################################################################
########################### MAIN ##################################
###################################################################
###################################################################

## screenshot leaguetable div TODO: change to xlsx colored file
app.clientside_callback(
    '''
    function (n_clicks) {
        if (n_clicks > 0) {
            window.scrollTo(0, 0);
            htmlRef = document.getElementById('league_table');
            html2canvas(htmlRef,  {
                scrollX: -window.scrollX,
                scrollY: -window.scrollY,
                windowWidth: document.documentElement.offsetWidth,
                windowHeight: htmlRef.scrollHeight,
      }).then(function(canvas) {
                var img = new Image();
                var height = canvas.height;
                img.src = canvas.toDataURL("image/png");
                document.getElementById('img_div').appendChild(img);

                var doc = new PDFDocument({layout:'portrait', margin: 25});
                var stream = doc.pipe(blobStream());

                var img_container = document.getElementById('img_div');
                var imgElement = img_container.getElementsByTagName('img');
                var imgSrc = imgElement[imgElement.length - 1].src;
                doc.image(imgSrc, {width: 600});

                doc.end();

                var saveData = (function () {
                    var a = document.createElement("a");
                    document.body.appendChild(a);
                    a.style = "display: none";
                    return function (blob, fileName) {
                        var url = window.URL.createObjectURL(blob);
                        a.href = url;
                        a.download = fileName;
                        a.click();
                        window.URL.revokeObjectURL(url);
                    };
                }());

                stream.on('finish', function() {
                  var blob = stream.toBlob('application/pdf');
                  saveData(blob, 'LeagueTable.pdf');
                });
            });


        }
        return false;
    }
    ''',
    Output('button', 'disabled'),
    [
        Input('button', 'n_clicks'),
    ]
)

if __name__ == '__main__':
    app._favicon = ("assets/favicon.ico")
    app.title = 'NMAstudio'
    app.run_server(debug=True)
