import rpy2.robjects as ro
from rpy2.robjects import pandas2ri # Define the R script and loads the instance in Python
from rpy2.robjects.conversion import localconverter
r = ro.r
r['source']('create-forest-data.R')  # Loading the function we have defined in R.
run_NetMeta_r = ro.globalenv['run_NetMeta']  # Reading and processing data

import os, io, base64, pickle
import pandas as pd, numpy as np
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_table
import dash_cytoscape as cyto
from assets.cytoscape_styleesheeet import default_stylesheet
from dash.dependencies import Input, Output, State
import plotly.express as px


#---------R2Py Resources --------------------------------------------------------------------------------------------#

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
GLOBAL_DATA = {'default_net':pd.read_csv('db/Senn2013.csv'),
               'forest_data':pd.read_csv('db/forest_data/forest_data.csv')}
GLOBAL_DATA['default_elements'] = get_network(df=GLOBAL_DATA['default_net'])


app.layout = html.Div(
    [html.Div(  # header
             [html.Div([html.H4("Network Meta-Analysis Tool", className="app__header__title"),
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
                                              style={'display': 'inline-block', 'margin-bottom':'-10px'})]
                                    ), html.Br()]),
                  # html.Div([html.Div(style={'width': '10%', 'display': 'inline'}, children=[
                  #     'Node Color:', dcc.Input(id='input-bg-color', type='text') ])
                  #  ]),
                  cyto.Cytoscape(id='cytoscape',
                                 elements=GLOBAL_DATA['default_elements'],
                                 style={'height': '60vh', 'width': '100%'},
                                 stylesheet=default_stylesheet)],
                  className="one-half column"),
                 html.Div(className='graph__title', children=[html.Button("Download graph", id="btn-get-png")]),
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
                                                                      'displaylogo':False}))]
                                      ),
                              dcc.Tab(label='Data',
                                      children=[dcc.Upload(html.Button('Upload your file!',
                                                                       style=dict(color='white')),
                                                                       id='datatable-upload'),
                                                dash_table.DataTable(id='datatable-upload-container',
                                                                     style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                                                                 'color': 'white',
                                                                                 'border': '1px solid #5d6d95'},
                                                                     style_data_conditional=[
                                                                         {'if': {'row_index': 'odd'},
                                                                          'backgroundColor': 'rgba(0,0,0,0.2)'},
                                                                         {'if': {'state': 'active'},
                                                                          'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                                                          'border': '1px solid rgb(0, 116, 217)'}],
                                                                     style_header={'backgroundColor': 'rgb(26, 36, 43)',
                                                                                   'fontWeight': 'bold',
                                                                                   'border': '1px solid #5d6d95'},
                                                                     style_table={'height': '400px',
                                                                                  'overflowX': 'auto',
                                                                                  'overflowY': 'auto',
                                                                                  'border': '1px solid #5d6d95'},
                                                                     css=[{"selector": "table",
                                                                           "rule": "width: 100%;"},
                                                                          {'selector': 'tr:hover',
                                                                           'rule': 'background-color: rgba(0, 0, 0, 0);'},
                                                                          {'selector': 'td:hover',
                                                                           'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}
                                                                          ]
                                                                     )])
                          ],colors={"border": "#1b242b", "primary": "#1b242b", "background": "#1b242b"},
                            style=dict(color='#40515e', fontWeight= 'bold')),
                          ],
                                   className="graph__container second"),
                      ],
                      className="one-half column")
    ],
              className="app__content"),
        html.P('Copyright © 2020. All rights reserved.', className='__footer')
    ],
    className="app__container")

###############################################################################
###############################################################################
# ############################## CALLBACKS ####################################
###############################################################################
###############################################################################

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
    action = 'store'
    ctx = dash.callback_context
    if ctx.triggered:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if input_id != "tabs":
            action = "download"
    return {'type': 'png','action': action}

### ----- update graph layout on node click ------ ###
@app.callback(Output('cytoscape', 'stylesheet'),
              Input('cytoscape', 'tapNode'))
def generate_stylesheet(node):
    FOLLOWER_COLOR = '#07ABA0'
    FOLLOWING_COLOR = '#07ABA0'
    NODE_SHAPE = 'ellipse' # One of  'ellipse', 'triangle', 'rectangle', 'diamond', 'pentagon', 'hexagon', 'heptagon', 'octagon', 'star', 'polygon'

    def io_node_topickle(store_node):
        with open('db/.temp/selected_nodes.pickle', 'wb') as f:
            pickle.dump(store_node, f, protocol=pickle.HIGHEST_PROTOCOL)
    if not node:
        os.makedirs('db/.temp', exist_ok=True)
        io_node_topickle({'label': None})
        return default_stylesheet
    else:
        store_node = pickle.load(open('db/.temp/selected_nodes.pickle', 'rb'))
        if node['data']['label']==store_node['label']:
            io_node_topickle({'label': None})
            return default_stylesheet
        else:
            io_node_topickle({'label': node['data']['label']})


    stylesheet = [{"selector": 'node',
                   'style': {'opacity': 0.2,
                             'color': "#fff",
                             'label': "data(label)",
                             'background-color': "#07ABA0",
                             'shape': NODE_SHAPE}},
                  {'selector': 'edge',
                   'style': {'opacity': 0.1,
                             'width': 'data(weight)',
                             "curve-style": "bezier"}},
                  {"selector": 'node[id = "{}"]'.format(node['data']['id']),
                   "style": {'background-color': '#07ABA0',
                             "border-color": "#751225",
                             "border-width": 5,
                             "border-opacity": 1,
                             "opacity": 1,
                             "label": "data(label)",
                             "color": "white",
                             "text-opacity": 1,
                             'shape': 'ellipse',
                             # "font-size": 12,
                             'z-index': 9999}}
                  ]
    for edge in node['edgesData']:
        if edge['source'] == node['data']['id']:
            stylesheet.append({
                "selector": 'node[id = "{}"]'.format(edge['target']),
                "style": {'background-color': FOLLOWING_COLOR,
                          'opacity': 0.9}})
            stylesheet.append({"selector": 'edge[id= "{}"]'.format(edge['id']),
                               "style": {
                                         # "line-color": FOLLOWING_COLOR,
                                         # "mid-target-arrow-color": FOLLOWING_COLOR,
                                         # "mid-target-arrow-shape": "vee",
                                         'opacity': 0.9,
                                         'z-index': 5000}})

        if edge['target'] == node['data']['id']:
            stylesheet.append({"selector": 'node[id = "{}"]'.format(edge['source']),
                               "style": {'background-color': FOLLOWER_COLOR,
                                         'opacity': 0.9,
                                         'z-index': 9999}})
            stylesheet.append({"selector": 'edge[id= "{}"]'.format(edge['id']),
                               "style": {
                                         # "line-color": FOLLOWER_COLOR,
                                         # "mid-target-arrow-color": FOLLOWER_COLOR,
                                         # "mid-target-arrow-shape": "vee",
                                         'opacity': 1,
                                         'z-index': 5000}})

    return stylesheet

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
        df = GLOBAL_DATA['forest_data'][GLOBAL_DATA['forest_data'].Reference==treatment]
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

### ----- display Data Table ------ ###
@app.callback([Output('datatable-upload-container', 'data'),
               Output('datatable-upload-container', 'columns'),
               Output('cytoscape', 'elements')],
              [Input('datatable-upload', 'contents')],
              [State('datatable-upload', 'filename')])
def update_output(contents, filename):
    if contents is None:
        df = GLOBAL_DATA['default_net']
        elements = GLOBAL_DATA['default_elements']
    else:
        df = parse_contents(contents, filename)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
        GLOBAL_DATA['user_net'] = df
        GLOBAL_DATA['user_elements'] = get_network(df=GLOBAL_DATA['user_net'])
        elements = GLOBAL_DATA['user_elements']
        # Create Forest data
        def forest_df(df):
            with localconverter(ro.default_converter + pandas2ri.converter):
                df_r = ro.conversion.py2rpy(df.reset_index(drop=True))
            netmeta_r = run_NetMeta_r(dat=df_r) # Invoke R function and get the result
            df_result = pandas2ri.rpy2py(netmeta_r).reset_index(drop=True)  # Convert back to a pandas.DataFrame.
            return df_result
        GLOBAL_DATA['forest_data'] = forest_df(df)

    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], elements

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
    app.run_server(debug=True, host='127.0.0.1')
