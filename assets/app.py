# Title     :  Dash NMA app
# Objective :  visualization tabs based on network interactivity
# Created by:  Silvia Metelli
# Created on: 10/11/2020

#--------------------------------------------------------------------------------------------------------------------#
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
pairwise_forest_r = ro.globalenv['pairwise_forest'] # Get pairwise_forest from R
#--------------------------------------------------------------------------------------------------------------------#
import os, io, base64, pickle, shutil, time, copy
import pandas as pd, numpy as np
import dash, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq, dash_table
#from dash_extensions import Download
import dash_cytoscape as cyto
from assets.cytoscape_styleesheeet import get_stylesheet
from assets.tab_styles import subtab_style, subtab_selected_style
from assets.dropdowns_values import *
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.colors as clrs
from assets.COLORS import *
from navbar import Navbar


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
                #external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

app.config.suppress_callback_exceptions = True

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

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
    df_n1g = df.rename(columns={'treat1': 'treat', 'n1':'n'}).groupby(['treat'])
    df_n2g = df.rename(columns={'treat2': 'treat', 'n2':'n'}).groupby(['treat'])
    df_n1, df_n2 = df_n1g.n.sum(), df_n2g.n.sum()
    all_nodes_sized = df_n1.add(df_n2, fill_value=0)
    df_n1, df_n2 = df_n1g.rob.value_counts(), df_n2g.rob.value_counts()
    all_nodes_robs = df_n1.add(df_n2, fill_value=0).rename(('count')).unstack('rob', fill_value=0)
    all_nodes_sized = pd.concat([all_nodes_sized, all_nodes_robs], axis=1).reset_index()
    for c in {1,2,3}.difference(all_nodes_sized): all_nodes_sized[c] = 0
    cy_edges = [{'data': {'source': source,  'target': target,
                          'weight': weight * 2, 'weight_lab': weight}}
                for source, target, weight in edges.values]
    cy_nodes = [{"data": {"id": target, "label": target,
                          'classes':'genesis',
                          'size': np.sqrt(size)*2,
                          'pie1':r1/(r1+r2+r3), 'pie2':r2/(r1+r2+r3), 'pie3': r3/(r1+r2+r3)}}
                for target, size, r1, r2, r3 in all_nodes_sized.values]
    return cy_edges + cy_nodes


# Save default dataframe for demo use
GLOBAL_DATA = {'net_data': pd.read_csv('db/Senn2013.csv'),
               'cinema_net_data': pd.read_csv('db/Cinema_report.csv'),
               'forest_data': pd.read_csv('db/forest_data/forest_data.csv'),
               'forest_data_pairwise': pd.read_csv('db/forest_data/forest_data_pairwise.csv'),
               'forest_data_outcome2': pd.read_csv('db/forest_data/forest_data_outcome2.csv'),
               'league_table_data': pd.read_csv('db/league_table_data/league_table.csv', index_col=0)}
GLOBAL_DATA['default_elements'] = GLOBAL_DATA['user_elements'] = get_network(df=GLOBAL_DATA['net_data'])


replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
leaguetable = GLOBAL_DATA['league_table_data'].copy(deep=True)
GLOBAL_DATA['league_table_data'] = pd.DataFrame([[replace_and_strip(col) for col in list(row)]
                                                 for idx, row in leaguetable.iterrows()], columns=leaguetable.columns, index=leaguetable.index)

#for year slider
GLOBAL_DATA['y_min'] = GLOBAL_DATA['net_data'].year.min()
GLOBAL_DATA['y_max'] = GLOBAL_DATA['net_data'].year.max()

GLOBAL_DATA['dwnld_bttn_calls'] = 0
GLOBAL_DATA['WAIT'] = False

OPTIONS_VAR = [{'label':'{}'.format(col, col), 'value':col} for col in GLOBAL_DATA['net_data'].columns]


options_trt = []
edges = GLOBAL_DATA['net_data'].groupby(['treat1', 'treat2']).TE.count().reset_index()
all_nodes = np.unique(edges[['treat1', 'treat2']].values.flatten())
for trt in all_nodes:
    options_trt.append({'label':'{}'.format(trt, trt), 'value':trt})


def Homepage():
    layout_home = html.Div([nav,home_layout])
    return layout_home

nav = Navbar()


home_layout = html.Div(className="app__container", children=[html.Div(
        id='main_page',
        children=[
        html.Div(  # NMA Graph
            [html.Div([dbc.Row([html.Div(Dropdown_graphlayout, style={'display': 'inline-block', 'font-size': '11px'}),
                                html.Div(modal, style={'display': 'inline-block', 'font-size': '11px'}),
                                html.Div(modal_data, style={'display': 'inline-block', 'font-size': '11px'}),
                                html.Div(modal_data_table, style={'display': 'inline-block', 'font-size': '11px'}),
                                html.Div(modal_league_table, style={'display': 'inline-block', 'font-size': '11px'}),
                                html.A(html.Img(src="/assets/icons/NETD.png",
                                                style={'width': '50px', 'filter': 'invert()'}),
                                       id="btn-get-png", style={'display': 'inline-block'}),
                                dbc.Tooltip("save graph", style={'color': 'white',
                                                                 'font-size': 9,
                                                                 'margin-left': '10px',
                                                                 'letter-spacing': '0.3rem'
                                                                 }, placement='right',
                                            target='btn-get-png')
                                ]),

                       ], style={'margin-left': '-20px'}),
             cyto.Cytoscape(id='cytoscape',  # responsive=True,
                            elements=GLOBAL_DATA['user_elements'],
                            style={'height': '75vh', 'width': '100%', 'margin-top': '15px',
                                    'margin-left': '-30px'},
                            stylesheet=get_stylesheet())],
            className="one-half column"
            ),
            html.Div(className='graph__title', children=[]),

        html.Div(className ="one-half column",
         children=[
            html.Div(
                id='forna-control-tabs',
                className='control-tabs',
                children=[
                    dcc.Tabs(id='forna-tabs', children=[
                        dcc.Tab(
                            label='Setup & Data',
                            children=html.Div(className='control-tab', children=[
                                html.H4(className='what-is', children='What is NMAstudio?'),
                                dcc.Markdown('''
                                NMAstudio is a ...
                                ''')
                            ])
                        ),

                        dcc.Tab(
                            label='Transitivity boxplots',
                            children=html.Div(className='control-tab')
                               ),

                        dcc.Tab(
                            label='Forest plots',
                            children=html.Div(className='control-tab')
                        ),
                        dcc.Tab(
                            label='League Table',
                            children=html.Div(className='control-tab')
                        ),
                        dcc.Tab(
                            label='Funnel plot',
                            children=html.Div(className='control-tab')
                        ),
                        dcc.Tab(
                            label='Ranking plot',
                            children=html.Div(className='control-tab')
                        ),


                    ])
                ]),
        ])
    ]),
    ] )


doc_layout = html.Div([nav, html.H1('Doc')])



#------------------------------ app interactivity ----------------------------------#

#####################################################################################
#####################################################################################
################################ MULTIPAGE CALLBACKS ################################
#####################################################################################
#####################################################################################
# Update the index
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':
        return Homepage()
    elif pathname == '/doc':
        return doc_layout
    else:
        return Homepage()

# Update which link is active in the navbar
@app.callback(Output('homepage-link', 'active'), [Input('url', 'pathname')])
def set_homepage_active(pathname):
    return pathname == '/home'

    
@app.callback(Output('docpage-link', 'active'), [Input('url', 'pathname')])
def set_docpage_active(pathname):
    return pathname == '/doc'


#####################################################################################
#####################################################################################
######################## -------- CALLBACKS --------- ###############################
#####################################################################################
#####################################################################################



# callback to toggle the collapse on small screens
@app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

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
    return {'type': 'png','action': action,
            'options':{#'bg':'#40515e',
                       'scale':5}}

#################################################################
############ Bootstrap Dropdowns callbacks ######################
#################################################################

@app.callback([Output('dd_nds', 'children')],
              [Input('dd_nds_default', 'n_clicks_timestamp'),Input('dd_nds_default', 'children'),
               Input('dd_nds_tot_rnd', 'n_clicks_timestamp'),Input('dd_nds_tot_rnd', 'children')],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, tot_rnd_t, tot_rnd_v):
    values = [default_v, tot_rnd_v]
    dd_nds = [default_t or 0, tot_rnd_t or 0]
    which = dd_nds.index(max(dd_nds))
    return [values[which]]

@app.callback([Output('dd_egs', 'children')],
              [Input('dd_egs_default', 'n_clicks_timestamp'),Input('dd_egs_default', 'children'),
               Input('dd_egs_tot_rnd', 'n_clicks_timestamp'),Input('dd_egs_tot_rnd', 'children')],
              prevent_initial_call=True)
def which_dd_egs(default_t, default_v, nstud_t, nstud_v):
    values = [default_v, nstud_v]
    dd_egs = [default_t or 0, nstud_t or 0]
    which = dd_egs.index(max(dd_egs))
    return [values[which]]

@app.callback([Output('dd_nclr', 'children'), Output('close_modal_dd_nclr_input', 'n_clicks'), Output("open_modal_dd_nclr_input", "n_clicks")],
              [Input('dd_nclr_default', 'n_clicks_timestamp'),Input('dd_nclr_default', 'children'),
               Input('dd_nclr_rob', 'n_clicks_timestamp'),Input('dd_nclr_rob', 'children'),
               Input('close_modal_dd_nclr_input', 'n_clicks'),
               ],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, rob_t, rob_v, closing_modal):
    values = [default_v, rob_v]
    dd_nclr = [default_t or 0, rob_t or 0]
    which = dd_nclr.index(max(dd_nclr))
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
    values = [circle_v,breadthfirst_v,grid_v,spread_v,cose_v,  cola_v, cose_bilkent_v,
              dagre_v, klay_v]
    times = [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, cola_t, cose_bilkent_t,
             dagre_t, klay_t]
    dd_ngl = [t or 0 for t in times]
    which = dd_ngl.index(max(dd_ngl))
    return [values[which]]




##################################################################
########################### MAIN #################################
##################################################################

if __name__ == '__main__':
    app.run_server(debug=True, port=8888)


