#---------R2Py Resources --------------------------------------------------------------------------------------------#
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri # Define the R script and loads the instance in Python
from rpy2.robjects.conversion import localconverter
r = ro.r
r['source']('R_Codes/all_R_functions.R')  # Loading the function we have defined in R.
run_NetMeta_r = ro.globalenv['run_NetMeta']    # Get run_NetMeta from R
league_table_r = ro.globalenv['league_table']  # Get league_table from R
#--------------------------------------------------------------------------------------------------------------------#
import os, io, base64, pickle, shutil, time
import pandas as pd, numpy as np
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_table
import dash_cytoscape as cyto
from assets.cytoscape_styleesheeet import default_stylesheet, download_stylesheet
from dash.dependencies import Input, Output, State
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as clrs
#--------------------------------------------------------------------------------------------------------------------#

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

app = dash.Dash(__name__, meta_tags=[{"name": "viewport",
                                      "content": "width=device-width, initial-scale=1"}])
server = app.server

styles = {
    'output': {
        'overflow-y': 'scroll',
        'overflow-wrap': 'break-word',
        'height': 'calc(100% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'}
}
# Load extra layouts
cyto.load_extra_layouts()
network_layouts = [{'label': 'circle',        'value': 'circle'},
                   {'label': 'breadthfirst',  'value': 'breadthfirst'},
                   {'label': 'grid',          'value': 'grid'},
                   {'label': 'spread',        'value': 'spread'},
                   {'label': 'cola',          'value': 'cola'},
                   {'label': 'random',        'value': 'random'}
                   ]

def get_network(df):
    edges = df.groupby(['treat1', 'treat2']).TE.count().reset_index()
    all_nodes = np.unique(edges[['treat1', 'treat2']].values.flatten())
    cy_edges = [{'data': {'source': source, 'target': target, 'weight': weight * 2, 'weight_lab': weight}}
                for source, target, weight in edges.values]
    cy_nodes = [{"data": {"id": target, "label": target, 'classes':'genesis'}}
                for target in all_nodes]
    return cy_edges + cy_nodes

# Save default dataframe for use
GLOBAL_DATA = {'net_data':pd.read_csv('db/Senn2013.csv'),
               'forest_data':pd.read_csv('db/forest_data/forest_data.csv'),
               'league_table_data':pd.read_csv('db/league_table_data/league_table.csv', index_col=0)}
GLOBAL_DATA['default_elements'] = GLOBAL_DATA['user_elements'] = get_network(df=GLOBAL_DATA['net_data'])
GLOBAL_DATA['dwnld_bttn_calls'] = 0
GLOBAL_DATA['WAIT'] = False
EMPTY_SELECTION = {'active': {'ids': dict()}}

app.layout = html.Div(
    [html.Div(  # header
             [html.Div([html.H4("VisualNMA", className="app__header__title"),
                        html.P("An interactive tool for data visualisation of network meta-analysis.",
                               className="app__header__title--grey")], className="app__header__desc"),
             html.Div([html.Img(src=app.get_asset_url("logo_universite_paris.jpg"),
                                className="app__menu__img")],
                      className="app__header__logo")],
             className="app__header"),
    html.Div([html.Div(   # NMA Graph
                 [html.Div([dbc.Row([html.H6("Graph layout", className="graph__title",style={'display': 'inline-block'}),
                                     html.Div(dcc.Dropdown(id='dropdown-layout', options=network_layouts, clearable=False,
                                                  value='circle', style={'width':'170px',
                                                                         'color': '#1b242b',
                                                                         'background-color': '#40515e'}),
                                              style={'display': 'inline-block', 'margin-bottom':'-10px'}),
                                     html.Div(html.Button("Download graph",id="btn-get-png",style={'color': 'white',
                                                                                                   'height': '36.5px',
                                                                                                   'verticalAlign':'middle'}),
                                              style={'display': 'inline-block','paddingLeft':'15px',
                                                     'verticalAlign':'top'})]
                                    ), html.Br()]),
                  # html.Div([html.Div(style={'width': '10%', 'display': 'inline'}, children=[
                  #     'Node Color:', dcc.Input(id='input-bg-color', type='text') ])
                  #  ]),
                  cyto.Cytoscape(id='cytoscape',
                                 elements=GLOBAL_DATA['user_elements'],
                                 style={'height': '60vh', 'width': '100%'},
                                 stylesheet=default_stylesheet)],
                  className="one-half column"),
                 html.Div(className='graph__title', children=[]),
                 html.Div(
                      [html.Div(  # Information
                           [html.Div([html.H6("Information", className="box__title")]),
                            html.Div([html.P(id='cytoscape-mouseoverEdgeData-output', className="info_box"),
                                      html.Br()],
                                      className="content_information"),
                            html.Div([],className="auto__container")],
                          className="info__container"),
                          # Forest Plot
                          html.Div([dcc.Tabs([
                              dcc.Tab(label='Forest plot',
                                      children=[html.Div([html.P(id='tapNodeData-info', className="box__title"),
                                                          html.Br()]),
                                                dcc.Loading(
                                                    dcc.Graph(id='tapNodeData-fig',
                                                              config={'modeBarButtonsToRemove':['toggleSpikelines', "pan2d",
                                                                                                "select2d", "lasso2d", "autoScale2d",
                                                                                                "hoverCompareCartesian"],
                                                                      'toImageButtonOptions': {'format': 'png', # one of png, svg,
                                                                                               'filename': 'custom_image',
                                                                                               'scale': 10  # Multiply title/legend/axis/canvas sizes by this factor
                                                                                              },
                                                                      'displaylogo':False}))]),
                              dcc.Tab(label='League Table',
                                      children=[html.Div([html.Br(),
                                                      html.Button("Download table",id="btn-get-league",style={'color': 'white',
                                                                                                   'height': '36.5px',
                                                                                                   'verticalAlign':'middle'}),
                                                          html.Div(id='legend_table_legend',
                                                                   style={'float': 'right',
                                                                          'padding': '5px 5px 5px 5px'}),
                                                          html.Div(id='legend_table')])]),
                              dcc.Tab(label='Transitivity',
                                      children=[html.P('Work in progress...')]),
                              dcc.Tab(label='Data',
                                      children=[html.Div(html.Button(dcc.Upload(html.P('Upload your file!'),
                                                                                id='datatable-upload'),
                                                                     style=dict(color='white')),
                                                         style=dict(padding='5px 5px 5px 5px')),
                                                dash_table.DataTable(id='datatable-upload-container',
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
                                                                                  'height': '100%',
                                                                                  'max-height': '400px',
                                                                                  'width':'100%',
                                                                                  'max-width':'calc(40vw)',
                                                                                  'padding': '5px 5px 5px 5px'},
                                                                     css=[
                                                                          {'selector': 'tr:hover',
                                                                           'rule': 'background-color: rgba(0, 0, 0, 0);'},
                                                                          {'selector': 'td:hover',
                                                                           'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}
                                                                          ])
                                                ])
                          ],colors={"border": "#1b242b", "primary": "#1b242b", "background": "#1b242b"},
                            style=dict(color='#40515e')),
                          ],
                                   className="graph__container second"),
                      ], className="one-half column")
    ],
              className="app__content"),
        html.P('Copyright © 2020. All rights reserved.', className='__footer'),
        html.Div(id='__storage', style={'display': 'none'}),
        html.Div(id='__storage2', style={'display': 'none'})
    ],
    className="app__container")

##################################################################################
##################################################################################
################################ CALLBACKS #######################################
##################################################################################
##################################################################################

### ----- update graph layout with dropdown ------ ###
@app.callback(Output('cytoscape', 'layout'),
             [Input('dropdown-layout', 'value')])
def update_cytoscape_layout(layout):
    return {'name': layout,
            'animate': True}

### ----- save network plot as png ------ ###
@app.callback(Output("cytoscape", "generateImage"),
              Input("btn-get-png", "n_clicks"))
def get_image(button):
    GLOBAL_DATA['WAIT'] = True
    while GLOBAL_DATA['WAIT']:
        time.sleep(0.1)
    action = 'store'
    ctx = dash.callback_context
    if ctx.triggered:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if input_id != "tabs":
            action = "download"
    return {'type': 'png','action': action,
            'options':{#'bg':'#40515e',
                       'scale':5}}

### ----- update graph layout on node click ------ ###
@app.callback([Output('cytoscape', 'stylesheet'),
               Output('__storage', 'loading_state')],
              [Input('cytoscape', 'tapNode'),
               Input("btn-get-png", "n_clicks")])
def generate_stylesheet(node, dwld_button):
    def io_node_topickle(store_node):
        with open('db/.temp/selected_nodes.pickle', 'wb') as f:
            pickle.dump(store_node, f, protocol=pickle.HIGHEST_PROTOCOL)
    FOLLOWER_COLOR = '#07ABA0'
    FOLLOWING_COLOR = '#07ABA0'
    NODE_SHAPE = 'ellipse' # One of  'ellipse', 'triangle', 'rectangle', 'diamond', 'pentagon', 'hexagon', 'heptagon', 'octagon', 'star', 'polygon'
    DWNLD = False
    if dwld_button and dwld_button > GLOBAL_DATA['dwnld_bttn_calls']:
        GLOBAL_DATA['dwnld_bttn_calls'] += 1
        DWNLD = True
    GLOBAL_DATA['WAIT'] = DWNLD
    if node and not DWNLD:
        store_node = pickle.load(open('db/.temp/selected_nodes.pickle', 'rb'))
        if node['data']['id'] in store_node['active']['ids'].keys():
            del store_node['active']['ids'][node['data']['id']]
            io_node_topickle(store_node)
        else:
            store_node['active']['ids'][node['data']['id']] = node
            io_node_topickle(store_node)
        if not len(store_node['active']['ids']):
            GLOBAL_DATA['cytoscape_layout'] = download_stylesheet if DWNLD else default_stylesheet
            return GLOBAL_DATA['cytoscape_layout'], EMPTY_SELECTION
    elif DWNLD:
        if os.path.exists('db/.temp/selected_nodes.pickle'):
            store_node = pickle.load(open('db/.temp/selected_nodes.pickle', 'rb'))
        else:
            store_node = EMPTY_SELECTION
    else:
        shutil.rmtree('db/.temp', ignore_errors=True)
        os.makedirs('db/.temp', exist_ok=True)
        io_node_topickle(EMPTY_SELECTION)
        GLOBAL_DATA['cytoscape_layout'] = download_stylesheet if DWNLD else default_stylesheet
        return GLOBAL_DATA['cytoscape_layout'], EMPTY_SELECTION


    stylesheet = [{"selector": 'node',
                   'style': {'opacity': 0.2, 'color': "#1b242b" if DWNLD else "white",
                             'label': "data(label)",
                             'background-color': "#07ABA0", 'shape': NODE_SHAPE}},
                  {'selector': 'edge',
                   'style': {'opacity': 0.1, 'width': 'data(weight)',
                             "curve-style": "bezier"}}]+[
                  {"selector": 'node[id = "{}"]'.format(id),
                   "style": {'background-color': '#07ABA0',
                             "border-color": "#751225", "border-width": 5, "border-opacity": 1,
                             "opacity": 1,
                             "label": "data(label)",
                             "color": "#1b242b" if DWNLD else "white",
                             "text-opacity": 1,
                             'shape': 'ellipse',
                             # "font-size": 12,
                             'z-index': 9999}}
                  for id in store_node['active']['ids']]
    for nd in store_node['active']['ids'].values():
        for edge in nd['edgesData']:
            if edge['source'] in store_node['active']['ids']:
                stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(edge['target']),
                    "style": {'background-color': FOLLOWING_COLOR, 'opacity': 0.9}})
                stylesheet.append({"selector": 'edge[id= "{}"]'.format(edge['id']),
                                   "style": {'opacity': 0.9,
                                             # "line-color": FOLLOWING_COLOR,
                                             # "mid-target-arrow-color": FOLLOWING_COLOR,
                                             # "mid-target-arrow-shape": "vee",
                                             'z-index': 5000}})

            if edge['target'] in store_node['active']['ids']:
                stylesheet.append({"selector": 'node[id = "{}"]'.format(edge['source']),
                                   "style": {'background-color': FOLLOWER_COLOR,
                                             'opacity': 0.9,
                                             'z-index': 9999}})
                stylesheet.append({"selector": 'edge[id= "{}"]'.format(edge['id']),
                                   "style": {'opacity': 1,
                                             # "line-color": FOLLOWER_COLOR,
                                             # "mid-target-arrow-color": FOLLOWER_COLOR,
                                             # "mid-target-arrow-shape": "vee",
                                             'z-index': 5000}})

    GLOBAL_DATA['cytoscape_layout'] = stylesheet
    GLOBAL_DATA['WAIT'] = False
    return stylesheet, store_node

### ----- update node info on forest plot  ------ ###
@app.callback(Output('tapNodeData-info', 'children'),
              [Input('cytoscape', 'tapNodeData')])
def TapNodeData_info(data):
    if data:
        return 'Treatment selected: ', data['label']
    else:
        return 'Click on a node to display the associated forest plot'

### ----- display forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig', 'figure'),
              [Input('cytoscape', 'tapNodeData')])
def TapNodeData_fig(data):
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
                     size='WEIGHT' if data else None)

    fig.update_layout(paper_bgcolor='#40515e',
                      plot_bgcolor='#40515e')
    if xlog:
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                      line=dict(color="white", width=1), layer='below')
    fig.update_traces(marker=dict(symbol='square',
                                  opacity=0.9 if data else 0,
                                  line=dict(color='Whitesmoke'), color='Whitesmoke')
                      )
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='white', ticklen=5,
                     tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                     ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                     range=[0.1, 1] if xlog else None,
                     autorange=True, showline=True,
                     zeroline=True)

    fig.update_layout(clickmode='event+select',
                      font_color="white",
                      margin=dict(l=5, r=10, t=12, b=80),
                      xaxis=dict(showgrid=False, tick0=0, title=''),
                      yaxis=dict(showgrid=False, title=''),
                      title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                      annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=False, text=effect_size),
                                   dict(x=df.CI_lower.min(), ax=0, y=-0.15, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor='green'),
                                   dict(x=df.CI_upper.max(), ax=0, y=-0.15, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor='white'),  #'#751225'
                                   dict(x=df.CI_lower.min()/2, y=-0.22, xref='x', yref='paper', text='Favours treatment',
                                        showarrow=False),
                                   dict(x=df.CI_upper.max()/2, y=-0.22, xref='x', yref='paper', text=f'Favours {treatment}',
                                        showarrow=False)] if data else []
                      )
    if not data:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig


### ----- display information on edge click ------ ###
@app.callback(Output('cytoscape-mouseoverEdgeData-output', 'children'),
              [Input('cytoscape', 'tapEdgeData')])
def mouseoverEdgeData(data):
    if data:
        n_studies = data['weight_lab']
        studies_str = f"{n_studies}" + (' studies' if n_studies>1 else ' study')
        return f"{data['source'].upper()} vs {data['target'].upper()}: {studies_str}"
    else:
        return "Click on an edge to get information."


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:    # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:  # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded))

### ----- upload new data ------ ###
@app.callback([Output('__storage2', 'children'),
               Output('cytoscape', 'elements')],
              [Input('datatable-upload', 'contents')],
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
    return data.to_json(orient='split'), elements

### ----- display Data Table and League Table ------ ###
@app.callback([Output('datatable-upload-container', 'data'),
               Output('datatable-upload-container', 'columns'),
               Output('legend_table', 'children'),
               Output('legend_table_legend', 'children')],
              [Input('__storage', 'loading_state'),
               Input('__storage2', 'children')])
def update_output(store_node, data):
    data = pd.read_json(data, orient='split').round(3)
    leaguetable = GLOBAL_DATA['league_table_data'].copy(deep=True)
    treatments = np.unique(data[['treat1', 'treat2']].values.flatten())
    robs = (data.groupby(['treat1', 'treat2']).rob.mean().reset_index()
                .pivot_table(index='treat1', columns='treat2', values='rob')
                .reindex(index=treatments, columns=treatments, fill_value=np.nan))
    # Filter according to cytoscape selection
    if store_node['active']['ids']:
        slctd_trmnts = [nd['data']['label'] for nd in store_node['active']['ids'].values()]
        data = data[data.treat1.isin(slctd_trmnts) | data.treat2.isin(slctd_trmnts) ]
        if len(slctd_trmnts)>1:
            leaguetable = leaguetable.loc[slctd_trmnts, slctd_trmnts]
            robs        = robs.loc[slctd_trmnts, slctd_trmnts]
            treatments = slctd_trmnts

    #####   Add style colouring and legend
    N_BINS = 5
    bounds = np.arange(N_BINS + 1)/N_BINS

    # leaguetable_colr = leaguetable.copy(deep=True)
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
    data_cols = [{"name": c, "id": c} for c in data.columns]
    data = data.to_dict('records')
    leaguetable = leaguetable.reset_index().rename(columns={'index':'Treatment'})
    leaguetable_cols = [{"name": c, "id": c} for c in leaguetable.columns]
    leaguetable = leaguetable.to_dict('records')

    return data, data_cols, build_league_table(leaguetable, leaguetable_cols, styles), legend


def build_league_table(data, columns, style_data_conditional):
    return dash_table.DataTable(style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                     'color': 'white',
                                     'border': '1px solid #5d6d95',
                                     'font-family': 'sans-serif',
                                     'textOverflow': 'ellipsis'
                                     },
                                data=data,
                                columns=columns,
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
                                             'padding': '5px 5px 5px 5px'},
                                css=[{"selector": "table",
                                      "rule": "width: 100%; "},
                                     {'selector': 'tr:hover',
                                      'rule': 'background-color: rgba(0, 0, 0, 0);'},
                                     {'selector': 'td:hover',
                                      'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])


# @app.callback(Output('cytoscape-tapEdgeData-output', 'children'),
#               [Input('cytoscape', 'tapEdgeData')])
# def TapEdgeData(data):
#     if data:
#         return "Clicked on edge between " + data['source'].upper() + " and " + data['target'].upper()


# @app.callback(Output('cytoscape-mouseoverNodeData-output', 'children'),
#               [Input('cytoscape', 'mouseoverNodeData')])
# def mouseoverNodeData(data):
#     if data:
#         return "Hovered over node: " + data['label']

if __name__ == "__main__":
    #app.run_server(debug=True, host='127.0.0.1')
    app.run_server(debug=False)
