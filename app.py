import warnings
warnings.filterwarnings("ignore")
#---------R2Py Resources --------------------------------------------------------------------------------------------#
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri # Define the R script and loads the instance in Python
from rpy2.robjects.conversion import localconverter
r = ro.r
r['source']('R_Codes/all_R_functions.R')  # Loading the function we have defined in R.
run_NetMeta_r = ro.globalenv['run_NetMeta']    # Get run_NetMeta from R
league_table_r = ro.globalenv['league_table']  # Get league_table from R
#--------------------------------------------------------------------------------------------------------------------#
import os, io, base64, pickle, shutil, time, copy
import pandas as pd, numpy as np
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq
import dash_table
#from dash_extensions import Download
import dash_cytoscape as cyto
from assets.cytoscape_styleesheeet import get_stylesheet
from assets.tab_styles import subtab_style, subtab_selected_style
from assets.dropdowns_values import *

from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.colors as clrs
#--------------------------------------------------------------------------------------------------------------------#

def write_node_topickle(store_node):
    with open('db/.temp/selected_nodes.pickle', 'wb') as f:
        pickle.dump(store_node, f, protocol=pickle.HIGHEST_PROTOCOL)
def read_node_frompickle():
    return pickle.load(open('db/.temp/selected_nodes.pickle', 'rb'))
def write_edge_topickle(store_edge):
    with open('db/.temp/selected_edges.pickle', 'wb') as f:
        pickle.dump(store_edge, f, protocol=pickle.HIGHEST_PROTOCOL)
def read_edge_frompickle():
    return pickle.load(open('db/.temp/selected_edges.pickle', 'rb'))

UPLOAD_DIRECTORY = "db/.temp/UPLOAD_DIRECTORY"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

shutil.rmtree('db/.temp', ignore_errors=True)
os.makedirs('db/.temp', exist_ok=True)

EMPTY_SELECTION_NODES = {'active': {'ids': dict()}}
EMPTY_SELECTION_EDGES = {'id': None}
write_node_topickle(EMPTY_SELECTION_NODES)
write_edge_topickle(EMPTY_SELECTION_EDGES)

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

app = dash.Dash(__name__, meta_tags=[{"name": "viewport",
                                      "content": "width=device-width, initial-scale=1"}],
                suppress_callback_exceptions=True)
server = app.server

styles = {
    'output': {'overflow-y': 'scroll',
               'overflow-wrap': 'break-word',
               'height': 'calc(100% - 25px)',
               'border': 'thin lightgrey solid'},
    'tab': {'height': 'calc(98vh - 115px)'}
}
# Load extra layouts
cyto.load_extra_layouts()


def get_network(df):
    edges = df.groupby(['treat1', 'treat2']).TE.count().reset_index()
    all_nodes = np.unique(edges[['treat1', 'treat2']].values.flatten())
    df_n1 = df.groupby(['treat1']).n1.sum().reset_index()
    df_n1 = df_n1.rename(columns={'treat1': 'treat', 'n1':'n'})
    df_n2 = df.groupby(['treat2']).n2.sum().reset_index()
    df_n2 = df_n2.rename(columns={'treat2': 'treat', 'n2':'n'})
    all_nodes_sized = pd.concat([df_n1,df_n2]).groupby(['treat']).sum().reset_index()
    cy_edges = [{'data': {'source': source, 'target': target, 'weight': weight * 2, 'weight_lab': weight}}
                for source, target, weight in edges.values]
    cy_nodes = [{"data": {"id": target, "label": target, 'classes':'genesis', 'size': np.sqrt(size)*2}}
                    for target, size in all_nodes_sized.values]
    for el in cy_nodes:
        el['data'].update({'pie1':4, 'pie2':1, 'pie3': 6})
    return cy_edges + cy_nodes


# Save default dataframe for demo use
GLOBAL_DATA = {'net_data': pd.read_csv('db/Senn2013.csv'),
               'cinema_net_data': pd.read_csv('db/Cinema_report.csv'),
               'forest_data': pd.read_csv('db/forest_data/forest_data.csv'),
               'forest_data_outcome2': pd.read_csv('db/forest_data/forest_data_outcome2.csv'),
               'league_table_data': pd.read_csv('db/league_table_data/league_table.csv', index_col=0)}
GLOBAL_DATA['default_elements'] = GLOBAL_DATA['user_elements'] = get_network(df=GLOBAL_DATA['net_data'])

GLOBAL_DATA['dwnld_bttn_calls'] = 0
GLOBAL_DATA['WAIT'] = False

options_var = []
for col in GLOBAL_DATA['net_data'].columns:
    options_var.append({'label':'{}'.format(col, col), 'value':col})

options_trt = []
edges = GLOBAL_DATA['net_data'].groupby(['treat1', 'treat2']).TE.count().reset_index()
all_nodes = np.unique(edges[['treat1', 'treat2']].values.flatten())
for trt in all_nodes:
    options_trt.append({'label':'{}'.format(trt, trt), 'value':trt})

##############################################################################
##########################------- APP LAYOUT -------##########################
##############################################################################

app.layout = html.Div(
    [html.Div(            # Header
             [html.Div([html.H4("VisualNMA", className="app__header__title"),
                        html.P("An interactive tool for data visualisation of network meta-analysis.",
                               className="app__header__title--grey")], className="app__header__desc"),

             html.Div([html.Img(src=app.get_asset_url("logo_universite_paris.jpg"),
                                className="app__menu__img")],
                      className="app__header__logo")],
             className="app__header"),
    html.Div([html.Div(   # NMA Graph
                 [html.Div([dbc.Row([html.Div(Dropdown_graphlayout, style={'display': 'inline-block', 'font-size': '11px'}),
                                     html.Div(Dropdown_nodesize,    style={'display': 'inline-block', 'font-size': '11px'}),
                                     html.Div(Dropdown_nodecolor,   style={'display': 'inline-block', 'font-size': '11px'}),
                                     html.A(html.Img(src="/assets/NETD.png", style={'width':'50px','filter':'invert()'}),
                                                     id="btn-get-png", style={'display': 'inline-block'})
                                     ]),
                 ], style={'margin-left':'-30px'}),
                         cyto.Cytoscape(id='cytoscape',   #responsive=True,
                                 elements=GLOBAL_DATA['user_elements'],
                                 style={'height': '75vh', 'width': '125%','margin-top': '0px','margin-left': '-100px'},
                                 stylesheet=get_stylesheet())],
                  className="one-half column"),
                 html.Div(className='graph__title', children=[]),
                 html.Div(
                      [html.Div(  # Information
                           [html.Div([dbc.Row([
                                              html.H6("Information", className="box__title"),
                                             # html.H6("Download button here?")
                                              ]),
                                      ]),
                            html.Div([html.P(id='cytoscape-mouseTapEdgeData-output', className="info_box"),
                                      html.Br()],
                                      className="content_information"),
                            html.Div([],className="auto__container")],
                          className="info__container"),
                          # tabs
                          html.Div([
                              dcc.Tabs([
                                        # Project set up
                                  dcc.Tab(label='Set up',children=[html.Div(children=[
                                          html.Br(),
                                          dbc.Row([dbc.Col([
                                              dcc.Upload(html.A('Upload main data file*',
                                                                     style={'margin-left': '5px'}),
                                                              id='datatable-upload', multiple=False,
                                                              style={'display': 'inline-block'})
                                          ],style={'display': 'inline-block'}),
                                    dbc.Col([html.Ul(id="file-list", style={'margin-left': '15px'})],
                                            style={'display': 'inline-block'})
                                          ]),
                                          html.Br(),
                                          dbc.Row([
                                              dbc.Col([html.P("Format*:", className="graph__title2",
                                                       style={'display': 'inline-block', 'margin-left': '5px',
                                                              'paddingLeft': '0px','font-size': '11px','vertical-alignment':'middle'}),
                                                       html.Div(dcc.RadioItems(id='dropdown-format',
                                                                               options=options_format,
                                                                               style={'width': '80px', 'margin-left': '-20px',
                                                                       'color': '#1b242b', 'font-size': '10px',
                                                                       'background-color': '#40515e'}),
                                                                style={'display': 'inline-block', 'margin-bottom': '-15px'})],
                                                      width="auto", style={'display': 'inline-block'}),

                                              dbc.Col([html.P(["1",html.Sup("st"), " outcome*:"], className="graph__title2",
                                                            style={'display': 'inline-block', 'paddingLeft': '10px','font-size': '11px'}),
                                                   html.Div(dcc.RadioItems(id='dropdown-outcome1', options=options_outcomes,
                                                                          style={'width': '80px', 'margin-left': '-20px',
                                                                                 'color': '#1b242b', 'font-size': '10px',
                                                                                 'background-color': '#40515e'}),
                                                             style={'display': 'inline-block', 'margin-bottom': '-15px'})],width="auto", style={'display': 'inline-block'}),

                                              dbc.Col([html.P(["2",html.Sup("nd"), " outcome:"], className="graph__title2",
                                                      style={'display': 'inline-block', 'paddingLeft': '10px','font-size': '11px'}),
                                              html.Div(dcc.RadioItems(id='dropdown-outcome2', options=options_outcomes,
                                                                    style={'width': '80px', 'margin-left': '-20px',
                                                                           'color': '#1b242b', 'font-size': '10px',
                                                                           'background-color': '#40515e'}),
                                                       style={'display': 'inline-block', 'margin-bottom': '-15px'})],width="auto", style={'display': 'inline-block'})
                                          ]),
                                   html.Div(id='second-selection')
                                  ])]),

                                  dcc.Tab(label='Forest plots', value='mainTabForest',
                                          children=[
                                              dcc.Tabs(id='subtabs1', value='subtab1', vertical=False, persistence=True,
                                                       children=[
                                                                 dcc.Tab(label='NMA', id='tab1', value='Tab1',
                                                                         style=subtab_style, selected_style=subtab_selected_style,
                                                                         children=[html.Div([html.P(id='tapNodeData-info', className="box__title"),
                                                                                                 html.Br()]),
                                                                                       html.Div([
                                                                                            dbc.Row([

                                                                                                    html.Div([html.P("Beneficial", id='forestswitchlabel1',
                                                                                                                    style={'display': 'inline-block',
                                                                                                                           'margin': 'auto','font-size':'10px',
                                                                                                                           'padding-left':'20px'}),
                                                                                                             daq.ToggleSwitch(
                                                                                                                id='dropdown-direction',
                                                                                                                 # on=True,
                                                                                                                 color='',
                                                                                                                 size=35,
                                                                                                                 label={'label':"Outcome", 'style':dict(color='white')},
                                                                                                                 labelPosition="top",
                                                                                                                 style={'display': 'inline-block',
                                                                                                                        'margin': 'auto',
                                                                                                                        'padding-left':'20px', 'padding-right':'20px'}),
                                                                                                             html.P('Harmful', id='forestswitchlabel2',
                                                                                                                    style={'display': 'inline-block',
                                                                                                                           'margin': 'auto','font-size':'10px',
                                                                                                                           'padding-right':'20px'})
                                                                                                             ], style={'margin-left':'auto'})

                                                                                            ]),
                                                                                           dcc.Loading(
                                                                                               dcc.Graph(
                                                                                            id='tapNodeData-fig',
                                                                                            config={
                                                                                                    'modeBarButtonsToRemove': [
                                                                                                    'toggleSpikelines',
                                                                                                    "pan2d",
                                                                                                    "select2d",
                                                                                                    "lasso2d",
                                                                                                    "autoScale2d",
                                                                                                    "hoverCompareCartesian"],
                                                                                                    'toImageButtonOptions': {
                                                                                                    'format': 'png',
                                                                                                    # one of png, svg,
                                                                                                    'filename': 'custom_image',
                                                                                                    'scale': 10
                                                                                                    # Multiply title/legend/axis/canvas sizes by this factor
                                                                                                    },
                                                                                            'displaylogo': False})) ])

                                                       ]),
                                                                dcc.Tab(label='Pairwise', id='tab2', value='Tab2', style=subtab_style,selected_style=subtab_selected_style,
                                                                        children=[html.Div([html.P(
                                                                            id='tapEdgeData-info',
                                                                            className="box__title"),
                                                                                            html.Br()]),
                                                                        dcc.Loading(
                                                                            html.Div([
                                                                            dcc.Graph(
                                                                                id='tapNodeData-fig-pairwise',
                                                                                config={
                                                                                    'modeBarButtonsToRemove': [
                                                                                        'toggleSpikelines',
                                                                                        "pan2d",
                                                                                        "select2d",
                                                                                        "lasso2d",
                                                                                        "autoScale2d",
                                                                                        "hoverCompareCartesian"],
                                                                                        'toImageButtonOptions': {
                                                                                        'format': 'png',
                                                                                        # one of png, svg,
                                                                                        'filename': 'custom_image',
                                                                                        'scale': 10
                                                                                        # Multiply title/legend/axis/canvas sizes by this factor
                                                                                    },
                                                                                    'displaylogo': False})])

                                                                                  ),
                                                                ]),

                                                                dcc.Tab(label='Two-dimensional', id='tab3', value='Tab3', style=subtab_style,selected_style=subtab_selected_style,
                                                                        children=[html.Div([html.P(id='tapNodeData-info-bidim', className="box__title"),
                                                                                                 html.Br()]),
                                                                                 # html.Br(),
                                                                            # html.Div([dbc.Row([html.H6(
                                                                            #     "Choose reference trt:",
                                                                            #     className="graph__title2",
                                                                            #     style={'display': 'inline-block'}),
                                                                            #                    html.Div(
                                                                            #                        dcc.Dropdown(
                                                                            #                            id='dropdown-reference-trt',
                                                                            #                            options=options_trt,
                                                                            #                            clearable=False,
                                                                            #                            className="tapEdgeData-fig-class",
                                                                            #                            style={
                                                                            #                                'width': '100px','font size':'11px',
                                                                            #                                'vertical-align': 'middle',
                                                                            #                                'color': '#1b242b',
                                                                            #                                'display': 'inline-block',
                                                                            #                                'background-color': '#40515e',
                                                                            #                                'padding-bottom': '5px'}),
                                                                            #                        style={
                                                                            #                            'display': 'inline-block',
                                                                            #                            'margin-bottom': '-15px'})
                                                                            #                    ])],
                                                                        dcc.Loading(
                                                                                html.Div([
                                                                                    dcc.Graph(
                                                                                        id='tapNodeData-fig-bidim',
                                                                                        config={'editable': True,
                                                                                            'modeBarButtonsToRemove': [
                                                                                            'toggleSpikelines',
                                                                                            "pan2d",
                                                                                            "select2d",
                                                                                            "lasso2d",
                                                                                            "autoScale2d",
                                                                                            "hoverCompareCartesian"],
                                                                                            'toImageButtonOptions': {
                                                                                            'format': 'png',
                                                                                            # one of png, svg,
                                                                                            'filename': 'custom_image',
                                                                                            'scale': 10
                                                                                            # Multiply title/legend/axis/canvas sizes by this factor
                                                                                        },
                                                                                        'displaylogo': False})])
                                                                        )],
                                                                        )
                              ])]),
                                  dcc.Tab(label='Funnel plots', children=[html.P("Work in Progress..")
                                                                          ]),

                                  dcc.Tab(label='League Table',
                                      children=[html.Div([dbc.Row([dbc.Col([
                                              dcc.Upload(html.A('Upload CINeMA file',
                                                                     style={'margin-left': '5px'}),
                                                              id='datatable-secondfile-upload', multiple=False,
                                                              style={'display': 'inline-block'})
                                          ],style={'display': 'inline-block'}),
                                    dbc.Col([html.Ul(id="file2-list", style={'margin-left': '15px'})],
                                            style={'display': 'inline-block'}
                                            )]),
                                                          html.Br(),
                                                          html.Div(id='league_table_legend',
                                                                   style={'float': 'right',
                                                                          'padding': '5px 5px 5px 5px'}),
                                                          html.Div(id='league_table')
                                      ])]),

                                  dcc.Tab(label='Transitivity',
                                          children=[
                                              html.Div([dbc.Row([html.P("Choose effect modifier:", className="graph__title2",
                                                                  style={'display': 'inline-block', 'vertical-align': 'middle', 'font-size':'12px','margin-bottom':'-10px'}),
                                                              dcc.Dropdown(id='dropdown-effectmod', options=options_var,
                                                                           clearable=True, className="tapEdgeData-fig-class",
                                                                           style={'width': '100px','height': '30px', 'vertical-align': 'top',
                                                                                  'color': '#1b242b','display': 'inline-block','margin-bottom': '-5px',
                                                                                  'background-color': '#40515e','padding-bottom':'0px'})
                                                   ]) ]),

                                        dcc.Graph(id='tapEdgeData-fig',
                                                  config={'editable': True,
                                                          'modeBarButtonsToRemove':['toggleSpikelines', "pan2d",
                                                                                    "select2d", "lasso2d", "autoScale2d",
                                                                                    "hoverCompareCartesian"],
                                                           'toImageButtonOptions': {'format': 'png', # one of png, svg,
                                                                                    'filename': 'custom_image',
                                                                                    'scale': 10  # Multiply title/legend/axis/canvas sizes by this factor
                                                                                    },
                                                           'displaylogo':False})]),

                                  dcc.Tab(label='Data',
                                          children=[html.Div([
                                                     dash_table.DataTable(
                                                                     id='datatable-upload-container',
                                                                     editable=False,
                                                                     style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                                                                 'color': 'white',
                                                                                 'border': '1px solid #5d6d95',
                                                                                 'textOverflow': 'ellipsis',
                                                                                 'font-family': 'sans-serif',
                                                                                 'foontSize': 10
                                                                                 },
                                                                     style_data_conditional=[
                                                                         {'if': {'row_index': 'odd'},
                                                                          'backgroundColor': 'rgba(0,0,0,0.2)'},
                                                                         {'if': {'state': 'active'},
                                                                          'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                                                          'border': '1px solid rgb(0, 116, 217)'}],
                                                                     style_header={'backgroundColor': 'rgb(26, 36, 43)',
                                                                                   'fontWeight': 'bold',
                                                                                   'border': '1px solid #5d6d95'},
                                                                     style_table={'overflowX': 'scroll',
                                                                                  'overflowY': 'auto',
                                                                                  'height': '99%',
                                                                                  'max-height': '400px',
                                                                                  'width':'99%',
                                                                                  'max-width':'calc(40vw)',
                                                                                  'padding': '5px 5px 5px 5px'},
                                                                     css=[
                                                                          {'selector': 'tr:hover',
                                                                           'rule': 'background-color: rgba(0, 0, 0, 0);'},
                                                                          {'selector': 'td:hover',
                                                                           'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])
                                              ]
                                                )])
                                  ], colors={"border": "#1b242b", "primary": "#1b242b", "background": "#1b242b"},
                                     style=dict(color='#40515e')),
                                    ],
                                      className="graph__container second"),
                      ], className="one-half column")
    ],
              className="app__content"),
        html.P('Copyright © 2020. All rights reserved.', className='__footer'),
        html.Div(id='__storage_netdata', style={'display': 'none'}),
        html.Div(id='__storage_netdata_cinema', style={'display': 'none'}),
        # dcc.Interval(id='interval-component',
        #              interval=1*1000, # in milliseconds
        #              n_intervals=0)

    ],
    className="app__container")


##################################################################################
##################################################################################
################################ CALLBACKS #######################################
##################################################################################
##################################################################################

### ---------------- PROJECT SETUP --------------- ###
@app.callback(Output("second-selection", "children"),
              #Output("my-dynamic-dropdown2", "options"),
              [Input("dropdown-format", "value"),
               Input("dropdown-outcome1", "value"),
               Input("dropdown-outcome2", "value")])
def update_options(search_value_format, search_value_outcome1, search_value_outcome2):

    if search_value_format is None: return None
    col_vars = [[]]*3
    if search_value_format == 'long':
        col_vars[0] = ['study id', 'treat', 'rob']
        if search_value_outcome1 == 'continuous':
            col_vars[1] = ['y', 'sd','n']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['r', 'n']
        else:
            return None
    elif search_value_format == 'contrast':
        col_vars[0] = ['treat 1', 'treat 2', 'rob']
        if search_value_outcome1 == 'continuous':
            col_vars[0] += ['n1', 'n2']
            col_vars[1] = ['y1', 'sd1', 'y2', 'sd2']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['r1', 'n1', 'r2', 'n2']
        else:
            return None

    selectors_row = html.Div(
        [dbc.Row([html.P("Select your variables")])]+[
         dbc.Row([dbc.Col(dbc.Row(
                 [html.P(f"{name}:", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                   'margin-left': '0px', 'font-size': '10px'}),
                 dcc.Dropdown(id=f'dropdown-{nrow}-{ncol}', options=options_var, searchable=True, placeholder="...", #className="box",
                              clearable=False, style={'width': '60px', 'height': '20px', 'vertical-align': 'middle',
                                                      'margin-left': '-8px',
                                                      'padding-left':'0px',
                                                      'display': 'inline-block',
                                                      'color': '#1b242b', 'font-size': '10px',
                                                      'background-color': '#40515e'})]), style={'margin-bottom': '0px'})
                            for nrow, name in enumerate(col_var)],
                style={'display': 'inline-block'})
        for ncol, col_var in enumerate(col_vars)]
    )
    return selectors_row


### --- update graph layout with dropdown: graph layout --- ###
@app.callback(Output('cytoscape', 'layout'),
             [Input('graph-layout-dropdown', 'children')])
def update_cytoscape_layout(layout):
        return {'name': layout.lower() if layout else 'circle',
                'animate': True}

### ----- save network plot as png ------ ###
@app.callback(Output("cytoscape", "generateImage"),
              Input("btn-get-png", "n_clicks"),
              prevent_initial_call=True)
def get_image(button):
    GLOBAL_DATA['WAIT'] = True
    while GLOBAL_DATA['WAIT']:
        time.sleep(0.05)
    action = 'store'
    ctx = dash.callback_context
    if ctx.triggered:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if input_id != "tabs": action = "download"
    #print('End of get_image download function')
    return {'type': 'png','action': action,
            'options':{#'bg':'#40515e',
                       'scale':5}}


### ----- update graph layout on node click ------ ###
@app.callback(Output('cytoscape', 'stylesheet'),
              [Input('cytoscape', 'tapNode'),
               Input('cytoscape','selectedNodeData'),
               Input('cytoscape','elements'),
               Input('cytoscape','selectedEdgeData'),
               Input('dd_nclr', 'children'),
               Input('dd_nds', 'children'),
               Input("btn-get-png", "n_clicks"),
               ])
def generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        pie, dd_nds,
                        dwld_button):
    #print('generating stylesheet')
    node_size = dd_nds or 'Default'
    node_size = node_size=='Tot randomized'
    pie = pie=='Risk of Bias'
    FOLLOWER_COLOR, FOLLOWING_COLOR = '#07ABA0', '#07ABA0'
    stylesheet = get_stylesheet(pie=pie, node_size=node_size)
    edgedata = [el['data'] for el in elements if 'target' in el['data'].keys()]
    all_nodes_id = [el['data']['id'] for el in elements if 'target' not in el['data'].keys()]

    if slct_nodesdata:
        selected_nodes_id = [d['id'] for d in slct_nodesdata]
        all_slct_src_trgt = list({e['source'] for e in edgedata if e['source'] in selected_nodes_id
                                  or e['target'] in selected_nodes_id}
                                 | {e['target'] for e in edgedata if e['source'] in selected_nodes_id
                                    or e['target'] in selected_nodes_id})

        stylesheet = get_stylesheet(pie=pie, node_size=node_size,
                                            nodes_opacity=0.2, edges_opacity=0.1)+[
                      {"selector": 'node[id = "{}"]'.format(id),
                       "style": {"border-color": "#751225", "border-width": 5, "border-opacity": 1,
                                 "opacity": 1}}
                      for id in selected_nodes_id ] + [
            {"selector": 'edge[id= "{}"]'.format(edge['id']),
            "style": {'opacity': 1, # "line-color": 'pink',
            'z-index': 5000}} for edge in edgedata if edge['source'] in selected_nodes_id
                                                      or edge['target'] in selected_nodes_id] +[
            {"selector": 'node[id = "{}"]'.format(id),
             "style": {"opacity": 1}}
        for id in all_nodes_id if id not in slct_nodesdata and id in all_slct_src_trgt]
    if slct_edgedata and False:  # Not doing anything at the moment
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

    if dwld_button and dwld_button > GLOBAL_DATA['dwnld_bttn_calls']:
        GLOBAL_DATA['dwnld_bttn_calls'] += 1
        stylesheet[0]['style']['color'] = 'black'
        time.sleep(0.05)

    GLOBAL_DATA['WAIT'] = False
    return stylesheet


### ----- update node info on NMA forest plot  ------ ###
@app.callback(Output('tapNodeData-info', 'children'),
              [Input('cytoscape', 'tapNodeData')])
def TapNodeData_info(data):
    if data:
        return 'Reference treatment selected: ', data['label']
    else:
        return 'Click on a node to display the associated plot'

### ----- update node info on bidim forest plot  ------ ###
@app.callback(Output('tapNodeData-info-bidim', 'children'),
              [Input('cytoscape', 'tapNodeData')],
              prevent_initial_call=True)
def TapNodeData_info(data):
    if data:
        return 'Reference treatment selected: ', data['label']
    else:
        return 'Click on a node to choose reference treatment'


### ----- display forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig', 'figure'),
              [Input('cytoscape', 'tapNodeData'),
               Input("dropdown-direction", "value")])
def TapNodeData_fig(data, outcome_direction):
    if data:
        treatment = data['label']
        df = GLOBAL_DATA['forest_data'][GLOBAL_DATA['forest_data'].Reference==treatment].copy()
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] /2
        effect_size = df.columns[1]
        #weight_es = round(df['WEIGHT'],3)
        df = df.sort_values(by=effect_size)
    else:
        effect_size = ''
        df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf'])

    xlog = effect_size in ('RR', 'OR')

    fig = px.scatter(df, x=effect_size, y="Treatment",
                     error_x_minus='CI_lower' if xlog else None,
                     error_x='CI_width_hf' if data else 'CI_width' if xlog else None,
                     log_x=xlog,
                     size=df.WEIGHT/float(1.2) if data else None)

    fig.update_layout(paper_bgcolor = 'rgba(0,0,0,0)',
                      plot_bgcolor = 'rgba(0,0,0,0)')
    # fig.update_layout(paper_bgcolor='#40515e',
    #                   plot_bgcolor='#40515e')
    if xlog:
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                      line=dict(color="black", width=1), layer='below')
    fig.update_traces(marker=dict(symbol='square',
                                  opacity=0.7 if data else 0,
                                  line=dict(color='black',width=0), color='dimgrey',
                                  ),
                      error_x=dict(thickness=1.3, color="black")
                      )
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5,
                     tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                     ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                     range=[0.1, 1] if xlog else None,
                     autorange=True, showline=True,linewidth=2, linecolor='black',
                     zeroline=True, zerolinecolor='black')

    if data:
        fig.update_layout(clickmode='event+select',
                      font_color="black",
                      margin=dict(l=5, r=10, t=12, b=80),
                      xaxis=dict(showgrid=False, tick0=0, title=''),
                      yaxis=dict(showgrid=False, title=''),
                      title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                      annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=False, text=effect_size),
                                   dict(x=df.CI_lower.min(), ax=0, y=-0.15, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=3,
                                        arrowcolor='green' if outcome_direction else 'black'),
                                   dict(x=df.CI_upper.max(), ax=0, y=-0.15, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=3,
                                        arrowcolor='black' if outcome_direction else 'green'),  #'#751225'
                                   dict(x=df.CI_lower.min()/2, y=-0.22, xref='x', yref='paper', text='Favours treatment',
                                        showarrow=False),
                                   dict(x=df.CI_upper.max()/2, y=-0.22, xref='x', yref='paper', text=f'Favours {treatment}',
                                        showarrow=False)]
                      )

    else:
        fig.update_layout(clickmode='event+select',
                      font_color="black",
                      margin=dict(l=5, r=10, t=12, b=80),
                      xaxis=dict(showgrid=False, tick0=0, title=''),
                      yaxis=dict(showgrid=False, title=''),
                      title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                      annotations=[]
                      )

    if not data:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig


### ----- display dibim forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig-bidim', 'figure'),
              [Input('cytoscape', 'tapNodeData')])
def TapNodeData_fig_bidim(data):
    if data:
        treatment = data['label']
        df = GLOBAL_DATA['forest_data'][GLOBAL_DATA['forest_data'].Reference==treatment].copy()
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] /2
        effect_size = df.columns[1]
        #weight_es = round(df['WEIGHT'],3)
        df = df.sort_values(by=effect_size)
        df_second = GLOBAL_DATA['forest_data_outcome2'][GLOBAL_DATA['forest_data_outcome2'].Reference==treatment].copy()
        df_second['CI_width'] = df_second.CI_upper - df_second.CI_lower
        df_second['CI_width_hf'] = df_second['CI_width'] /2
        effect_size_2 = df_second.columns[1]
    else:
        effect_size = effect_size_2 = ''
        df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf'])
        df_second = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf'])

    xlog = effect_size in ('RR', 'OR')

    fig = px.scatter(df, x=df[effect_size], y=df_second[effect_size_2], color=df.Treatment,
                     error_x_minus=df.CI_lower if xlog else None,
                     error_x=df.CI_width_hf if data else df.CI_width if xlog else None,
                     error_y_minus=df_second.CI_lower if xlog else None,
                     error_y=df_second.CI_width_hf if data else df_second.CI_width if xlog else None,
                     log_x=xlog)

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')  #paper_bgcolor='#40515e', #626C78
                      #plot_bgcolor='#40515e') #626C78

    if xlog:
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                      line=dict(color="black", width=1, dash='dashdot'), layer='below')

    fig.update_traces(marker=dict(symbol='circle',
                                  size=11,
                                  opacity=0.9 if data else 0,
                                  line=dict(color='black'),
                                  #color='Whitesmoke'
                                  ),
                      error_y=dict(thickness=1.3),
                      error_x=dict(thickness=1.3),
                      ),

    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5,
                     tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                     ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                     range=[0.1, 1] if xlog else None,
                     autorange=True, showline=True,linewidth=2, linecolor='black',
                     zeroline=True, zerolinecolor='gray', zerolinewidth=1),

    fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5,
                     tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                     ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                     range=[0.1, 1] if xlog else None,
                     autorange=True, showline=True,linewidth=2, linecolor='black',
                     zeroline=True, zerolinecolor='gray', zerolinewidth=1),

    fig.update_layout(clickmode='event+select',
                      font_color="black",
                      margin=dict(l=5, r=10, t=12, b=80),
                      xaxis=dict(showgrid=False, tick0=0, title=f'Click to enter x label ({effect_size})'),
                      yaxis=dict(showgrid=False, title=f'Click to enter y label ({effect_size})'),
                      title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                      )
    if not data:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zerolinecolor='gray', zerolinewidth=1)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80), coloraxis_showscale=False)
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig

### ----- display information on edge click ------ ###
@app.callback(Output('tapEdgeData-info', 'children'),
              Input('cytoscape', 'tapEdgeData'))
def TapEdgeData_info(data):
    if data:
        return 'Selected comparison: ', f"{data['source'].upper()} vs {data['target'].upper()}"
    else:
        return 'Click on an edge to display the associated  plot'

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
        studies_str = f"{n_studies}" + (' studies' if n_studies>1 else ' study')
        return f"{edge[0]['source'].upper()} vs {edge[0]['target'].upper()}: {studies_str}"
    else:

        return "Click on an edge to get information."

def parse_contents(contents, filename):
    #print(contents)
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:    # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:  # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded))

### ----- upload main data file ------ ###
@app.callback([Output('__storage_netdata', 'children'),
               Output('cytoscape', 'elements'),
               Output("file-list", "children")],
              [Input('datatable-upload', 'contents'),
               # Input('dropdown-0-0', 'children')
               ],
              [State('datatable-upload', 'filename')])
def get_new_data(contents, filename):
    def apply_r_func(func, df):
        with localconverter(ro.default_converter + pandas2ri.converter):
            df_r = ro.conversion.py2rpy(df.reset_index(drop=True))
        func_r_res = func(dat=df_r)  # Invoke R function and get the result
        df_result = pandas2ri.rpy2py(func_r_res).reset_index(drop=True)  # Convert back to a pandas.DataFrame.
        return df_result
    if contents is None:
        data = GLOBAL_DATA['net_data']
    else:
        data = parse_contents(contents, filename)
        GLOBAL_DATA['net_data'] = data = data.loc[:, ~data.columns.str.contains('^Unnamed')]  # Remove unnamed columns
        GLOBAL_DATA['user_elements'] = get_network(df=GLOBAL_DATA['net_data'])
        GLOBAL_DATA['forest_data'] = apply_r_func(func=run_NetMeta_r, df=data)
        leaguetable  = apply_r_func(func=league_table_r, df=data)
        leaguetable.columns = leaguetable.index = leaguetable.values.diagonal()
        leaguetable = leaguetable.reset_index().rename(columns={'index':'Treatments'})
        GLOBAL_DATA['league_table_data'] = leaguetable
    elements = GLOBAL_DATA['user_elements']
    if filename is not None:
        return data.to_json(orient='split'), elements, f'{filename}'
    else:
        return data.to_json(orient='split'), elements, 'No file uploaded'
    # def save_file(name, content):
    #     data = content.encode("utf8").split(b";base64,")[1]
    #     with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
    #         fp.write(base64.decodebytes(data))
    #
    # if filename is not None and contents is not None:
    #     for name, data in zip(filename, contents):
    #         save_file(name, data)
    # files = uploaded_files()
    # if len(files) == 0:
    #     return [html.Li("No files yet!")]
    # else:
    #     file_string = [html.Li(file_download_link(filename)) for filename in files]

### ----- upload CINeMA data file ------ ###
@app.callback([Output('__storage_netdata_cinema', 'children'), Output("file2-list", "children")],
              [Input('datatable-secondfile-upload', 'contents')],
              [State('datatable-secondfile-upload', 'filename')])
def get_new_data_cinema(contents, filename):
    if contents is None:
        data = GLOBAL_DATA['cinema_net_data']
    else:
        data = parse_contents(contents, filename)
        GLOBAL_DATA['cinema_net_data'] = data = data.loc[:, ~data.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    if filename is not None:
        return data.to_json(orient='split'), f'{filename}'
    else:
        return data.to_json(orient='split'), 'No file uploaded'


### ----- display Data Table and League Table ------ ###
@app.callback([Output('datatable-upload-container', 'data'),
               Output('datatable-upload-container', 'columns'),
               Output('league_table', 'children'),
               Output('league_table_legend', 'children')],
              [Input('cytoscape','selectedNodeData'),
               Input('__storage_netdata', 'children'),
               Input('cytoscape', 'selectedEdgeData')])
def update_output(store_node, data, store_edge):
    data = pd.read_json(data, orient='split').round(3)
    leaguetable = GLOBAL_DATA['league_table_data'].copy(deep=True)
    treatments = np.unique(data[['treat1', 'treat2']].values.flatten())
    robs = (data.groupby(['treat1', 'treat2']).rob.mean().reset_index()
                .pivot_table(index='treat1', columns='treat2', values='rob')
                .reindex(index=treatments, columns=treatments, fill_value=np.nan))
    # Filter according to cytoscape selection
    if store_node:
        slctd_trmnts = [nd['id'] for nd in store_node]
        if len(slctd_trmnts)>0:
            leaguetable = leaguetable.loc[slctd_trmnts, slctd_trmnts]
            robs        = robs.loc[slctd_trmnts, slctd_trmnts]
            treatments = slctd_trmnts

    #####   Add style colouring and legend
    N_BINS = 5
    bounds = np.arange(N_BINS + 1)/N_BINS

    leaguetable_colr = robs.copy(deep=True)
    np.fill_diagonal(leaguetable_colr.values, np.nan)
    leaguetable_colr = leaguetable_colr.astype(np.float64)


    cmap = [clrs.to_hex(plt.get_cmap('RdYlGn_r', N_BINS)(n)) for n in range(N_BINS)]
    legend = [html.Div(style={'display': 'inline-block', 'width': '100px'},
                       children=[html.Div(),
                                 html.Small('Risk of bias: ',
                                            style={'color':'white'})])]
    legend += [html.Div(style={'display': 'inline-block', 'width': '60px'},
                               children=[html.Div(style={'backgroundColor': cmap[n],
                                                         'borderLeft': '1px rgb(50, 50, 50) solid',
                                                         'height': '10px'}),
                                         html.Small('Low' if n==0 else 'High' if n==len(bounds)-2 else None,
                                                    style={'paddingLeft': '2px', 'color':'white'})])
              for n in range(len(bounds)-1)]

    df_max, df_min = leaguetable_colr.max().max(), leaguetable_colr.min().min()
    ranges = (df_max - df_min) * bounds + df_min
    ranges[-1] *= 1.001
    styles = []
    for treat_c in treatments:
        for treat_r in treatments:
            rob = robs.loc[treat_r, treat_c]
            indxs = np.where(rob < ranges)[0] if rob==rob else [0]
            clr_indx =  indxs[0] - 1 if len(indxs) else 0
            diag, empty = treat_r==treat_c, rob!=rob
            styles.append({'if': {'filter_query':f'{{Treatment}} = {{{treat_r}}}',
                                  'column_id': treat_c},
                           'backgroundColor': cmap[clr_indx] if not empty else '#40515e',
                           'color': 'rgb(26, 36, 43)' if not empty else 'gray' if diag else 'white'})
    styles.append({'if': {'column_id': 'Treatment'},
                   'backgroundColor': 'rgb(26, 36, 43)'})

    # Prepare for output
    leaguetable = leaguetable.reset_index().rename(columns={'index':'Treatment'})
    leaguetable_cols = [{"name": c, "id": c} for c in leaguetable.columns]
    leaguetable = leaguetable.to_dict('records')

    if store_edge or store_node:
        slctd_elms = {e['source'] for e in store_edge} | {e['target'] for e in store_edge} if store_edge else set()
        slctd_elms |= {n['id'] for n in store_node} if store_node else set()
        data = data[data.treat1.isin(slctd_elms) | data.treat2.isin(slctd_elms)]

    data_cols = [{"name": c, "id": c} for c in data.columns]
    data_output = data.to_dict('records')

    return data_output, data_cols, build_league_table(leaguetable, leaguetable_cols, styles), legend

def build_league_table(data, columns, style_data_conditional):
    return dash_table.DataTable(style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                     'color': 'white',
                                     'border': '1px solid #5d6d95',
                                     'font-family': 'sans-serif',
                                     'textOverflow': 'ellipsis'
                                     },
                                data=data,
                                columns=columns,
                                export_format="csv",
                                style_data_conditional=style_data_conditional,
                                # fixed_rows={'headers': True, 'data': 0},    # DOES NOT WORK / LEADS TO BUG
                                # fixed_columns={'headers': True, 'data': 1}, # DOES NOT WORK / LEADS TO BUG
                                style_header={'backgroundColor': 'rgb(26, 36, 43)',
                                              'border': '1px solid #5d6d95'},
                                style_header_conditional=[{'if': {'column_id': 'Treatment',
                                                                  'header_index': 0},
                                                           'fontWeight': 'bold'}],
                                style_table={'overflow': 'auto',
                                             'width': '100%',
                                             'max-width': 'calc(40vw)',
                                             # 'padding': '5px 5px 5px 5px'
                                             },
                                css=[{"selector": "table",
                                      "rule": "width: 100%; "},
                                     {'selector': 'tr:hover',
                                      'rule': 'background-color: rgba(0, 0, 0, 0);'},
                                     {'selector': 'td:hover',
                                      'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])


### - figures on edge click: transitivity boxplots  - ###
@app.callback(Output('tapEdgeData-fig', 'figure'),
             [Input('dropdown-effectmod', 'value'),
              Input('cytoscape', 'selectedEdgeData')])
def update_boxplot(value, edges):
    active, non_active = '#1f77b4', '#797B7D'  #'#0757AD', '#797B7D'
    if value:
            df = GLOBAL_DATA['net_data'][['treat1', 'treat2', value]].copy()
            df['Comparison'] = df['treat1'] + ' vs ' + df['treat2']
            df = df.sort_values(by='Comparison').reset_index()
            margin = (df[value].max() - df[value].min()) * .4  # 40%
            range1 = df[value].min() - margin
            range2 = df[value].max() + margin
            df['color'] = non_active
            df['selected'] = 'nonactive'

            slctd_comps = []
            for edge in edges or []:
                src, trgt = edge['source'], edge['target']
                slctd_comps += [f'{src} vs {trgt}']
            # if df.Comparison.iloc[0] in slctd_comps:    ## for px express only
            #     active, non_active = non_active, active
            for ind, row in df.iterrows():
                df.loc[ind, 'color'] = active if row.Comparison in slctd_comps else non_active
                df.loc[ind, 'selected'] = 'active' if row.Comparison in slctd_comps else 'nonactive'

            unique_comparisons = df.Comparison.sort_values().unique()
            fig = go.Figure(data=[go.Box(y=df[df.Comparison == comp][value],
                                         name=comp,
                                         width=.6,
                                         marker_color=active if comp in slctd_comps else non_active
                                         )
                                  for comp in unique_comparisons]
                            # +[go.Scatter(xaxis='x2')]
                            )
    else:
            df = pd.DataFrame([[0] * 3], columns=['Comparison', 'value', 'selected'])
            value = df['value']
            range1 = range2 = 0
            fig = go.Figure(data=[go.Box(y=df['value'])])
            fig.update_layout(margin=dict(l=100, r=100, t=12, b=80), xaxis=dict(showgrid=False, tick0=0, title=''),
                              yaxis=dict(showgrid=False, tick0=0, title=''))

    #
    # fig.update_layout(
    # xaxis=dict(
    #     range=[0, len(unique_comparisons)],
    #     tickfont=dict(color=active),
    #     tickmode='array',
    #     tickvals=[n+1 for n,_ in enumerate(unique_comparisons)],
    #     ticktext=[comp if comp in slctd_comps else ''
    #               for n, comp in enumerate(unique_comparisons)],
    # ),
    # xaxis2=dict(
    #     range=[0, len(unique_comparisons)],
    #     tickfont=dict(color=non_active),
    #     tickmode='array',
    #     tickvals=[n+1 for n,_ in enumerate(unique_comparisons)],
    #     ticktext=[comp if comp not in slctd_comps else ''
    #               for n, comp in enumerate(unique_comparisons)],
    #     overlaying="x",
    #     side="bottom",
    # ),
    # )

    fig.update_layout(clickmode='event+select',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      font_color="black",
                      yaxis_range=[range1, range2],
                      showlegend=False,
                      font=dict(
                          #family="sans serif",
                          size=11,
                          #color="RebeccaPurple" if edges else 'black'
                      ),
                      xaxis=dict(showgrid=False, tick0=0),
                      yaxis=dict(showgrid=False)
                      )

    fig.update_traces(boxpoints='outliers', quartilemethod="inclusive",hoverinfo= "x+y",
                      selector=dict(mode='markers'), showlegend=False,opacity=1,
                      marker=dict(opacity=1, line=dict(color='black', outlierwidth=2))
                      )

    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5,
                     showline=True, zerolinecolor='black',tickangle=30, linecolor='black')

    fig.update_yaxes(showgrid=False, ticklen=5, tickwidth=2, tickcolor='black', showline=True, linecolor='black')


    if not any(value):
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(tickvals=[], ticktext=[],zerolinecolor='gray', zerolinewidth=1, tickangle=0)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80), xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, tick0=0, title=''))
        fig.update_traces(quartilemethod="exclusive", hoverinfo='skip', hovertemplate=None)

    return fig


### - figures on edge click: pairwise forest plots  - ###
@app.callback(Output('tapNodeData-fig-pairwise', 'figure'),
              Input('cytoscape', 'tapEdgeData'))
def update_forest_pairwise(data):
    if data:
        pass
    else:
        effect_size = ''
        df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf'])
        fig = px.scatter(df, x=effect_size)
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

        return fig

    ### ----- display bidim forest plot on node click ------ ###


### -------------- toggle switch ---------------- ###
@app.callback([Output("forestswitchlabel1", "style"),
               Output("forestswitchlabel2", "style")],
              [Input("dropdown-direction", "value")])
def color_forest_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left':'20px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right':'20px',}
    return style1, style2

###########################################################
############ Bootstrap Dropdowns ##########################
###########################################################
@app.callback([Output('dd_nds', 'children')],
              [Input('dd_nds_default', 'n_clicks_timestamp'),Input('dd_nds_default', 'children'),
               Input('dd_nds_tot_rnd', 'n_clicks_timestamp'),Input('dd_nds_tot_rnd', 'children'),
               Input('dd_nds_other', 'n_clicks_timestamp'),Input('dd_nds_other', 'children')],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, tot_rnd_t, tot_rnd_v, other_t, other_v):
    values = [default_v, tot_rnd_v, other_v]
    dd_nds = [default_t or 0, tot_rnd_t or 0, other_t or 0]
    which = dd_nds.index(max(dd_nds))
    return [values[which]]

@app.callback([Output('dd_nclr', 'children')],
              [Input('dd_nclr_default', 'n_clicks_timestamp'),Input('dd_nclr_default', 'children'),
               Input('dd_nclr_rob', 'n_clicks_timestamp'),Input('dd_nclr_rob', 'children')],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, rob_t, rob_v):
    values = [default_v, rob_v]
    dd_nclr = [default_t or 0, rob_t or 0]
    which = dd_nclr.index(max(dd_nclr))
    return [values[which]]


flatten = lambda t: [item for sublist in t for item in sublist]
@app.callback([Output('graph-layout-dropdown', 'children')],
              flatten([[Input(f'dd_ngl_{item.lower()}', 'n_clicks_timestamp'),
                        Input(f'dd_ngl_{item.lower()}', 'children')]
                        for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Random', 'Cola',
                                     'Cose-Bilkent', 'Euler', 'Dagre', 'Klay']
                      ]),
              prevent_initial_call=True)
def which_dd_nds(circle_t, circle_v, breadthfirst_t, breadthfirst_v,
                 grid_t, grid_v, spread_t, spread_v, cose_t, cose_v, random_t, random_v,
                 cola_t, cola_v, cose_bilkent_t, cose_bilkent_v, euler_t, euler_v,
                 dagre_t, dagre_v, klay_t, klay_v):
    values = [circle_v,breadthfirst_v,grid_v,spread_v,cose_v,random_v,  cola_v, cose_bilkent_v,
             euler_v, dagre_v, klay_v]
    times = [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, random_t, cola_t, cose_bilkent_t,
             euler_t, dagre_t, klay_t]
    dd_ngl = [t or 0 for t in times]
    which = dd_ngl.index(max(dd_ngl))
    return [values[which]]



###########################################################
########################### MAIN ##########################
###########################################################

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1')
    #app.run_server(debug=False)
