# Title     :  Dash NMA app
# Objective :  visualization tabs based on network interactivity
# Created by:  Silvia Metelli
# Created on: 10/11/2020

# --------------------------------------------------------------------------------------------------------------------#
import warnings

warnings.filterwarnings("ignore")
# ---------R2Py Resources --------------------------------------------------------------------------------------------#
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri  # Define the R script and loads the instance in Python
from rpy2.robjects.conversion import localconverter

r = ro.r
r['source']('R_Codes/all_R_functions.R')  # Loading the function we have defined in R.
run_NetMeta_r = ro.globalenv['run_NetMeta']  # Get run_NetMeta from R
league_table_r = ro.globalenv['league_rank']  # Get league_table from R
pairwise_forest_r = ro.globalenv['pairwise_forest']  # Get pairwise_forest from R
# --------------------------------------------------------------------------------------------------------------------#
import os, io, base64, shutil, time, pandas as pd, numpy as np
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px, plotly.graph_objects as go
from assets.effect_sizes import OR_effect_measure, MD_effect_measure
from demo_data import get_demo_data
from layouts import *
# --------------------------------------------------------------------------------------------------------------------#
from utils import write_node_topickle, read_node_frompickle, write_edge_topickle, read_edge_frompickle, get_network
from PATHS import TEMP_PATH

UPLOAD_DIRECTORY = f"{TEMP_PATH}/UPLOAD_DIRECTORY"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

shutil.rmtree(TEMP_PATH, ignore_errors=True)
os.makedirs(TEMP_PATH, exist_ok=True)

EMPTY_SELECTION_NODES = {'active': {'ids': dict()}}
EMPTY_SELECTION_EDGES = {'id': None}
write_node_topickle(EMPTY_SELECTION_NODES)
write_edge_topickle(EMPTY_SELECTION_EDGES)

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

app = dash.Dash(__name__, meta_tags=[{"name": "viewport",
                                      "content": "width=device-width, initial-scale=1"}],
                # external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

app.config.suppress_callback_exceptions = True

server = app.server

app.layout = html.Div([dcc.Location(id='url', refresh=False),
                       html.Div(id='page-content')])

# Load extra layouts
cyto.load_extra_layouts()

GLOBAL_DATA = get_demo_data()
GLOBAL_DATA['default_elements'] = GLOBAL_DATA['user_elements'] = get_network(df=GLOBAL_DATA['net_data'])

OPTIONS_VAR = [{'label': '{}'.format(col), 'value': col} for col in GLOBAL_DATA['net_data'].columns]


# edges = GLOBAL_DATA['net_data'].groupby(['treat1', 'treat2']).TE.count().reset_index()
# all_nodes = np.unique(edges[['treat1', 'treat2']].values.flatten())
# options_trt = [{'label':'{}'.format(trt, trt), 'value':trt}
#                for trt in all_nodes]


# ------------------------------ app interactivity ----------------------------------#

#####################################################################################
################################ MULTIPAGE CALLBACKS ################################
#####################################################################################

# Update the index
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':
        return Homepage(GLOBAL_DATA)
    elif pathname == '/doc':
        return doc_layout
    else:
        return Homepage(GLOBAL_DATA)


# Update which link is active in the navbar
@app.callback(Output('homepage-link', 'active'),
              [Input('url', 'pathname')])
def set_homepage_active(pathname):
    return pathname == '/home'


@app.callback(Output('docpage-link', 'active'), [Input('url', 'pathname')])
def set_docpage_active(pathname):
    return pathname == '/doc'


#####################################################################################
#####################################################################################
################## -------- ALL PLOTS/TABLES CALLBACKS --------- ####################
#####################################################################################
#####################################################################################


### ---------------- PROJECT SETUP --------------- ###
@app.callback(Output("second-selection", "children"),
              [Input('datatable-upload', 'contents'),
               Input("dropdown-format", "value"),
               Input("dropdown-outcome1", "value"),
               Input("dropdown-outcome2", "value")],
              [State('datatable-upload', 'filename')])
def update_options(contents, search_value_format, search_value_outcome1, search_value_outcome2, filename):
    if contents is None:
        data = GLOBAL_DATA['net_data']
    else:
        data = parse_contents(contents, filename)
    options_var = [{'label': '{}'.format(col, col), 'value': col} for col in data.columns]

    if search_value_format is None: return None
    col_vars = [[]] * 3
    if search_value_format == 'long':
        col_vars[0] = ['study id', 'treat', 'rob']
        if search_value_outcome1 == 'continuous':
            col_vars[1] = ['y', 'sd', 'n']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2', 'sd2', 'n2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n.z']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['r', 'n']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2', 'sd2', 'n2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n.z']

        else:
            return None
    elif search_value_format == 'contrast':
        col_vars[0] = ['studlab', 'treat 1', 'treat 2', 'rob']
        if search_value_outcome1 == 'continuous':
            col_vars[0] += ['n1', 'n2']
            col_vars[1] = ['y1', 'sd1', 'y2', 'sd2']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2.1', 'sd1.2', 'y2.2', 'sd2.2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n1.z', 'z2.z', 'n2.z']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['r1', 'n1', 'r2', 'n2']
            if search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n1.z', 'z2', 'n2.z']
            elif search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2.1', 'sd1.2', 'y2.2', 'sd2.2']

        else:
            return None
    vars_names = [[f'{search_value_format}.{c}' for c in col_vars[0]],
                  [f'{search_value_outcome1}.{c}' for c in col_vars[1]],
                  [f'{search_value_outcome2}.{c}' for c in col_vars[2]]]
    selectors_row = html.Div(
        [dbc.Row([html.P("Select your variables", style={'color': 'white'})])] + [
            dbc.Row([dbc.Col(dbc.Row(
                [html.P(f"{name}:", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                  'margin-left': '0px', 'font-size': '12px'}),
                 dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-{var_name}'},
                              options=options_var, searchable=True, placeholder="...", className="box",
                              clearable=False, style={'width': '80px',  # 'height': '30px',
                                                      'vertical-align': 'middle',
                                                      'margin-bottom': '10px',
                                                      # 'padding-bottom':'10px',
                                                      'display': 'inline-block',
                                                      'color': CLR_BCKGRND_old, 'font-size': '10px',
                                                      'background-color': CLR_BCKGRND_old})]),
                style={'margin-bottom': '0px'})
                for var_name, name in zip(var_names, col_var)],
                style={'display': 'inline-block'})
            for var_names, col_var in zip(vars_names, col_vars)]
    )
    return selectors_row


### --- update graph layout with dropdown: graph layout --- ###
@app.callback(Output('cytoscape', 'layout'),
              [Input('graph-layout-dropdown', 'children')],
              prevent_initial_call=False)
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
    return {'type': 'png', 'action': action,
            'options': {  # 'bg':'#40515e',
                'scale': 5}}


### ----- update graph layout on node click ------ ###
@app.callback(Output('cytoscape', 'stylesheet'),
              [Input('cytoscape', 'tapNode'),
               Input('cytoscape', 'selectedNodeData'),
               Input('cytoscape', 'elements'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('dd_nclr', 'children'), Input('node_color_input', 'value'),
               Input('dd_nds', 'children'),
               Input('dd_egs', 'children'),
               Input("btn-get-png", "n_clicks")]
              )
def generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, custom_nd_clr, dd_nds, dd_egs, dwld_button):
    nodes_color = (custom_nd_clr or DFLT_ND_CLR) if dd_nclr != 'Default' else DFLT_ND_CLR
    node_size = dd_nds or 'Default'
    node_size = node_size == 'Tot randomized'
    edge_size = dd_egs or 'Number of studies'
    edge_size = edge_size == 'No size'
    pie = dd_nclr == 'Risk of Bias'
    FOLLOWER_COLOR, FOLLOWING_COLOR = DFLT_ND_CLR, DFLT_ND_CLR
    stylesheet = get_stylesheet(pie=pie, nd_col=nodes_color, node_size=node_size, edge_size=edge_size)
    edgedata = [el['data'] for el in elements if 'target' in el['data'].keys()]
    all_nodes_id = [el['data']['id'] for el in elements if 'target' not in el['data'].keys()]

    if slct_nodesdata:
        selected_nodes_id = [d['id'] for d in slct_nodesdata]
        all_slct_src_trgt = list({e['source'] for e in edgedata if e['source'] in selected_nodes_id
                                  or e['target'] in selected_nodes_id}
                                 | {e['target'] for e in edgedata if e['source'] in selected_nodes_id
                                    or e['target'] in selected_nodes_id})

        stylesheet = get_stylesheet(pie=pie, nd_col=nodes_color, node_size=node_size,
                                    nodes_opacity=0.2, edges_opacity=0.1) + [
                         {"selector": 'node[id = "{}"]'.format(id),
                          "style": {"border-color": "#751225", "border-width": 5, "border-opacity": 1,
                                    "opacity": 1}}
                         for id in selected_nodes_id] + [
                         {"selector": 'edge[id= "{}"]'.format(edge['id']),
                          "style": {'opacity': 1,  # "line-color": 'pink',
                                    'z-index': 5000}} for edge in edgedata if edge['source'] in selected_nodes_id
                                                                              or edge[
                                                                                  'target'] in selected_nodes_id] + [
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


### ----- display forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input("toggle_forest_direction", "value")])
def TapNodeData_fig(data, outcome_direction):
    if data:
        treatment = data[0]['label']
        df = GLOBAL_DATA['forest_data'][GLOBAL_DATA['forest_data'].Reference == treatment].copy()
        effect_size = df.columns[1]
        df['Treatment'] += ' ' * 20
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['lower_error'] = df[effect_size] - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] / 2
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        df['CI'] = '(' + round(df["CI_lower"],2).astype(str) + ', ' + round(df["CI_upper"],2).astype(str) + ')'
        df[effect_size] = round(df[effect_size], 2)
        df = df.sort_values(by=effect_size, ascending=False)
    else:
        effect_size = ''
        df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf'])


    xlog = effect_size in ('RR', 'OR')
    up_rng = df.CI_upper.max()
    up_rng = round(up_rng, -round(np.log10(up_rng))) if xlog else None
    print(up_rng)
    fig = px.scatter(df, x=effect_size, y="Treatment",
                     error_x_minus='lower_error' if xlog else None,
                     error_x='CI_width_hf' if xlog else 'CI_width' if data else None,
                     log_x=xlog,
                     size_max=10,
                     range_x=[0.1, up_rng] if xlog else None,
                     size=df.WEIGHT if data else None)

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)')
    if xlog:
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                      line=dict(color="black", width=1), layer='below')

    fig.update_traces(marker=dict(symbol='circle',
                                  opacity=0.8 if data else 0,
                                  line=dict(color='#313539', width=0),
                                  color='#ef563b'),
                      error_x=dict(thickness=2.6, color="#313539")  # '#313539' dark grey
                      )
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black',
                     ticklen=5,
                     categoryorder='category descending' if outcome_direction=="Beneficial" else 'category ascending',
                     # dtick=1,
                     autorange=False,
                     showline=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinecolor='black')

    if data:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          #width=500,
                          margin=dict(l=5, r=10, t=12, b=80),
                          xaxis=dict(showgrid=False,
                                     #tick0=0, # TODO: JUST EXPLAIN IT!!!
                                     title=''),
                          yaxis=dict(showgrid=False, title=''),
                          #title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                          annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                             showarrow=False, text=effect_size),
                          #              dict(x=df.CI_lower.min(), ax=0, y=-0.15, ay=-0.1, xref='x', axref='x', yref='paper',
                          #                   showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2.5,
                          #                   arrowcolor='green' if outcome_direction else 'black'),
                          #              dict(x=df.CI_upper.max(), ax=0, y=-0.15, ay=-0.1, xref='x', axref='x', yref='paper',
                          #                   showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2.5,
                          #                   arrowcolor='black' if outcome_direction else 'green'),  #'#751225'
                          #              dict(x=1-abs(df.CI_lower.min()) if xlog else 0-abs(df.CI_upper.min()), y=-0.22, xref='x', yref='paper', text='Favours treatment',
                          #                   showarrow=False),
                          #              dict(x=1+abs(df.CI_upper.max()) if xlog else 0-abs(df.CI_upper.max()), y=-0.22, xref='x', yref='paper', text=f'Favours {treatment}',
                          #                   showarrow=False)
                                 ]
                          )

        fig.add_trace(go.Scatter(x=[], y=[],
                                 marker=dict(opacity=0),
                                 showlegend=False, mode='markers',
                                 yaxis="y2"))

        fig.update_layout(
            yaxis2=dict(tickvals = [*range(df.shape[0])],
                        ticktext=[' '*20 + '{:.2f}   {:<15}'.format(x,y)
                                  for x, y in zip(df[effect_size].values, df['CI'].values)],
                        showgrid=False,  zeroline=False,
                        titlefont=dict(color=DFLT_ND_CLR),
                        tickfont=dict(color=DFLT_ND_CLR),
                        type='category',
                        range=[-1.4, df.shape[0]],
                        anchor="x", overlaying="y",
                        side="right"),

        ),


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
        fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig


### ----- display dibim forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig-bidim', 'figure'),
              [Input('cytoscape', 'selectedNodeData')])
def TapNodeData_fig_bidim(data):
    if data:
        treatment = data[0]['label']
        df = GLOBAL_DATA['forest_data'][GLOBAL_DATA['forest_data'].Reference == treatment].copy()
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] / 2
        effect_size = df.columns[1]
        # weight_es = round(df['WEIGHT'],3)
        df = df.sort_values(by=effect_size)
        df_second = GLOBAL_DATA['forest_data_outcome2'][
            GLOBAL_DATA['forest_data_outcome2'].Reference == treatment].copy()
        df_second['CI_width'] = df_second.CI_upper - df_second.CI_lower
        df_second['CI_width_hf'] = df_second['CI_width'] / 2
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
                      plot_bgcolor='rgba(0,0,0,0)',
                      autosize=True,
                      legend=dict(itemsizing='trace', itemclick="toggle",
                                  itemdoubleclick="toggleothers",
                                  # orientation='v', xanchor='auto',
                                  traceorder='normal',
                                  orientation='h', y=1.25, xanchor='auto',
                                  font=dict(size=10)) if df['Treatment'].unique().size > 10 else dict(
                          itemsizing='trace', itemclick="toggle", itemdoubleclick="toggleothers", orientation='v',
                          font=dict(size=10))
                      )

    if xlog:
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                      line=dict(color="black", width=1, dash='dashdot'), layer='below')

    fig.update_traces(marker=dict(symbol='circle',
                                  size=9,
                                  opacity=1 if data else 0,
                                  line=dict(color='black'),
                                  # color='Whitesmoke'
                                  ),
                      error_y=dict(thickness=1.3),
                      error_x=dict(thickness=1.3), ),

    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5,
                     tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                     ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                     range=[0.1, 1] if xlog else None,
                     autorange=True, showline=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinecolor='gray', zerolinewidth=1),

    fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5,
                     tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                     ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                     range=[0.1, 1] if xlog else None,
                     autorange=True, showline=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinecolor='gray', zerolinewidth=1),

    fig.update_layout(clickmode='event+select',
                      font_color="black",
                      margin=dict(l=10, r=10, t=12, b=80),
                      xaxis=dict(showgrid=False, tick0=0, title=f'Click to enter x label ({effect_size})'),
                      yaxis=dict(showgrid=False, title=f'Click to enter y label ({effect_size})'),
                      title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                      )
    if not data:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], title='', visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          coloraxis_showscale=False)  ## remove visible=False to show initial axes
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig


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


### ----- upload main data file ------ ###
# @app.callback([Output('__storage_netdata', 'children'),
#                Output('cytoscape', 'elements'),
#                Output("file-list", "children")],
#               [Input('datatable-upload', 'contents'),
#                Input({'type': 'dataselectors', 'index': ALL}, 'value'),
#                Input("dropdown-format", "value"),
#                Input("dropdown-outcome1", "value"),
#                Input("dropdown-outcome2", "value"),
#                Input('slider-year', 'value')
#                ],
#               [State('datatable-upload', 'filename')]
#               )
# def get_new_data(contents, dataselectors, search_value_format, search_value_outcome1, search_value_outcome2, slider_year, filename):
#     def apply_r_func(func, df):
#         with localconverter(ro.default_converter + pandas2ri.converter):
#             df_r = ro.conversion.py2rpy(df.reset_index(drop=True))
#         func_r_res = func(dat=df_r)  # Invoke R function and get the result
#         df_result = pandas2ri.rpy2py(func_r_res).reset_index(drop=True)  # Convert back to a pandas.DataFrame.
#         return df_result
#     if contents is None or not all(dataselectors):
#         data = GLOBAL_DATA['net_data']
#         GLOBAL_DATA['user_elements'] = get_network(df=data)
#         elements = get_network(df=data[data.year <= slider_year])
#     else:
#         data = parse_contents(contents, filename)
#         var_dict = dict()
#         if search_value_format == 'long':
#             if search_value_outcome1 == 'continuous':
#                 studlab, treat, rob, TE, seTE, n = dataselectors
#                 var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', TE: 'TE', seTE: 'seTE', n: 'n'}
#             elif search_value_outcome1 == 'binary':
#                 studlab, treat, rob, r, n = dataselectors
#                 var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', r: 'r', n: 'n'}
#         elif search_value_format == 'contrast':
#             if search_value_outcome1 == 'continuous':
#                 studlab, treat1, treat2, n1, n2, rob, TE1, seTE1, TE2, seTE2 = dataselectors
#                 var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', n1: 'n1', n2: 'n2',
#                             rob: 'rob', TE1: 'TE1', seTE1: 'seTE1', TE2: 'TE2', seTE2: 'seTE2'}
#             elif search_value_outcome1 == 'binary':
#                 studlab, treat1, treat2, n1, n2, rob, r1, r2 = dataselectors
#                 var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', n1: 'n1', n2: 'n2',
#                             rob: 'rob', r1: 'r1', r2: 'r2'}
#         data.rename(columns=var_dict, inplace=True)
#
#         if 'rob' not in GLOBAL_DATA['net_data'].select_dtypes(
#                 include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64']).columns:
#             if any(GLOBAL_DATA['net_data']['rob'].str.contains('l|m|h')):
#                 GLOBAL_DATA['net_data']['rob'].replace({'l': 1, 'm': 2, 'h': 3}, inplace=True)
#             elif any(GLOBAL_DATA['net_data']['rob'].str.contains('L|M|H')):
#                 GLOBAL_DATA['net_data']['rob'].replace({'L': 1, 'M': 2, 'H': 3}, inplace=True)
#         else:
#             pass
#         #GLOBAL_DATA['net_data']['TE'] = OR_effect_measure(GLOBAL_DATA['net_data'])[0]
#         #GLOBAL_DATA['net_data']['seTE'] = OR_effect_measure(GLOBAL_DATA['net_data'])[1]
#         OPTIONS_VAR = [{'label': '{}'.format(col, col), 'value': col} for col in data.columns]
#         GLOBAL_DATA['net_data'] = data = data.loc[:, ~data.columns.str.contains('^Unnamed')]  # Remove unnamed columns
#         data['type_outcome1'] = search_value_outcome1
#         #data['search_value_outcome2'] = search_value_outcome2 if search_value_outcome2
#
#         elements = GLOBAL_DATA['user_elements'] = get_network(df=GLOBAL_DATA['net_data'])
#         GLOBAL_DATA['forest_data'] = apply_r_func(func=run_NetMeta_r, df=data)
#         GLOBAL_DATA['forest_data_pairwise'] = apply_r_func(func=pairwise_forest_r, df=data)
#         leaguetable_r  = apply_r_func(func=league_table_r, df=data)
#         replace_and_strip = lambda x: x.replace(' (', '\n(').strip()
#         leaguetable = pd.DataFrame([[replace_and_strip(col) for col in list(row)]
#                                      for idx, row in leaguetable_r.iterrows()], columns=leaguetable_r.columns, index=leaguetable_r.index)
#         leaguetable.columns = leaguetable.index = leaguetable.values.diagonal()
#         leaguetable = leaguetable.reset_index().rename(columns={'index':'Treatments'})
#         GLOBAL_DATA['league_table_data'] = leaguetable
#     if filename is not None:
#         return data.to_json(orient='split'), elements, f'{filename}'
#     else:
#         return data.to_json(orient='split'), elements, 'No file added'
#     # def save_file(name, content):
#     #     data = content.encode("utf8").split(b";base64,")[1]
#     #     with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
#     #         fp.write(base64.decodebytes(data))
#     #
#     # if filename is not None and contents is not None:
#     #     for name, data in zip(filename, contents):
#     #         save_file(name, data)
#     # files = uploaded_files()
#     # if len(files) == 0:
#     #     return [html.Li("No files yet!")]
#     # else:
#     #     file_string = [html.Li(file_download_link(filename)) for filename in files]


### ----- 2nd version: upload main data file ------ ###
@app.callback([Output('__storage_netdata', 'children'),
               Output('cytoscape', 'elements'),
               Output("file-list", "children")],
              [Input('datatable-upload', 'contents'),
               Input('slider-year', 'value')
               ],
              [State('datatable-upload', 'filename')]
              )
def get_new_data(contents, slider_year, filename):
    if contents:
        GLOBAL_DATA['new_data_upload'] = parse_contents(contents, filename)
    data = GLOBAL_DATA['net_data']
    GLOBAL_DATA['user_elements'] = get_network(df=data)
    elements = get_network(df=data[data.year <= slider_year])

    if filename is not None:
        return data.to_json(orient='split'), elements, f'{filename}'  # TODO: remove filename frorm here
    else:
        return data.to_json(orient='split'), elements, 'No file added'

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
        GLOBAL_DATA['cinema_net_data'] = data = data.loc[:,
                                                ~data.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    if filename is not None:
        return data.to_json(orient='split'), f'{filename}'
    else:
        return data.to_json(orient='split'), 'No file added'


### ----- display Data Table and League Table ------ ###
@app.callback([Output('datatable-upload-container', 'data'),
               Output('datatable-upload-container', 'columns'),
               Output('datatable-upload-container-expanded', 'data'),
               Output('datatable-upload-container-expanded', 'columns'),
               Output('league_table', 'children'),
               Output('modal_league_table_data', 'children'),
               Output('league_table_legend', 'children'),
               Output('modal_league_table_legend', 'children'),
               Output('rob_vs_cinema', 'value'),
               Output('rob_vs_cinema_modal', 'value')
               ],
              [Input('cytoscape', 'selectedNodeData'),
               Input('__storage_netdata', 'children'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('rob_vs_cinema', 'value'),
               Input('rob_vs_cinema_modal', 'value'),
               Input('slider-year', 'value')
               ])
def update_output(store_node, data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value):
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'rob_vs_cinema.value' in triggered:
        toggle_cinema_modal = toggle_cinema
    elif 'rob_vs_cinema_modal.value' in triggered:
        toggle_cinema = toggle_cinema_modal

    data = pd.read_json(data, orient='split').round(3)
    leaguetable = GLOBAL_DATA['league_table_data'].copy(deep=True)
    treatments = np.unique(data[['treat1', 'treat2']].dropna().values.flatten())
    robs = (data.groupby(['treat1', 'treat2']).rob.mean().reset_index()
            .pivot_table(index='treat1', columns='treat2', values='rob')
            .reindex(index=treatments, columns=treatments, fill_value=np.nan))
    if toggle_cinema:
        confidence_map = {k: n for n, k in enumerate(['very low', 'low', 'medium', 'high'])}
        # GLOBAL_DATA['league_table_data']
        comparisons = GLOBAL_DATA['cinema_net_data'].Comparison.str.split(':', expand=True)
        confidence = GLOBAL_DATA['cinema_net_data']['Confidence rating'].str.lower().map(confidence_map)
        comprs_conf_ut = comparisons.copy()  # Upper triangle
        comparisons.columns = [1, 0]  # To get lower triangle
        comprs_conf_lt = comparisons[[0, 1]]  # Lower triangle
        comprs_conf_ut['Confidence'] = confidence
        comprs_conf_lt['Confidence'] = confidence
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

    g, y, lb, r = '#5aa469', '#f8d49d', '#75cfb8', '#d35d6e'
    # cmap = [clrs.to_hex(plt.get_cmap('RdYlGn_r', N_BINS)(n)) for n in range(N_BINS)]
    cmap = [g, y, r] if not toggle_cinema else [r, y, lb, g]
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

    df_max, df_min = leaguetable_colr.max().max(), leaguetable_colr.min().min()
    ranges = (df_max - df_min) * bounds + df_min
    ranges[-1] *= 1.001
    styles = []
    for treat_c in treatments:
        for treat_r in treatments:
            rob = robs.loc[treat_r, treat_c]
            indxs = np.where(rob < ranges)[0] if rob == rob else [0]
            clr_indx = indxs[0] - 1 if len(indxs) else 0
            diag, empty = treat_r == treat_c, rob != rob
            styles.append({'if': {'filter_query': f'{{Treatment}} = {{{treat_r}}}',
                                  'column_id': treat_c},
                           'backgroundColor': cmap[clr_indx] if not empty else '#40515e',
                           'color': 'rgb(26, 36, 43)' if not empty else '#d6d6d6' if diag else 'white'})
    styles.append({'if': {'column_id': 'Treatment'},
                   'backgroundColor': 'rgb(26, 36, 43)'})

    # Prepare for output
    tips = robs
    leaguetable = leaguetable.reset_index().rename(columns={'index': 'Treatment'})
    leaguetable_cols = [{"name": c, "id": c} for c in leaguetable.columns]
    leaguetable = leaguetable.to_dict('records')

    if store_edge or store_node:
        slctd_nods = {n['id'] for n in store_node} if store_node else set()
        slctd_edgs = [e['source'] + e['target'] for e in store_edge] if store_edge else []
        data = data[data.treat1.isin(slctd_nods) | data.treat2.isin(slctd_nods)
                    | (data.treat1 + data.treat2).isin(slctd_edgs) | (data.treat2 + data.treat1).isin(slctd_edgs)]

    data_cols = [{"name": c, "id": c} for c in data.columns]
    data.year = data.year
    data_output = data[data.year <= slider_value].to_dict('records')
    league_table_styles = {'output': {'overflow-y': 'scroll', 'overflow-wrap': 'break-word',
                                      'height': 'calc(100% - 25px)', 'border': 'thin lightgrey solid'},
                           'tab': {'height': 'calc(98vh - 115px)'}}
    league_table = build_league_table(leaguetable, leaguetable_cols, league_table_styles, tips)
    league_table_modal = build_league_table(leaguetable, leaguetable_cols, league_table_styles, tips, modal=True)
    return [data_output, data_cols] * 2 + [league_table, league_table_modal] + [legend] * 2 + [toggle_cinema,
                                                                                               toggle_cinema_modal]


def build_league_table(data, columns, style_data_conditional, tips, modal=False):
    return dash_table.DataTable(style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                            'color': 'white',
                                            'border': '1px solid #5d6d95',
                                            'font-family': 'sans-serif',
                                            'fontSize': 11,
                                            'textAlign': 'center',
                                            'whiteSpace': 'pre-line',  # 'inherit', nowrap
                                            'textOverflow': 'string'},  # 'ellipsis'
                                data=data,
                                columns=columns,
                                # export_format="csv", #xlsx
                                # state='active',
                                tooltip_data=[
                                    {col['id']: {
                                        'value': f"**Average ROB:** {tip[col['id']]}\n\n**Reason for Downgrading:**",
                                        'type': 'markdown'} if col['id'] != 'Treatment' else None
                                     for col in columns
                                     } for rn, (_, tip) in enumerate(tips.iterrows())
                                ],
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
                                             'max-height': '400px',
                                             'max-width': 'calc(52vw)'} if not modal else {
                                    'overflowX': 'scroll',
                                    'overflowY': 'scroll',
                                    'height': '90%',
                                    'max-height': 'calc(70vh)',
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


### - figures on edge click: transitivity boxplots  - ###
@app.callback(Output('tapEdgeData-fig', 'figure'),
              [Input('dropdown-effectmod', 'value'),
               Input('cytoscape', 'selectedEdgeData')])
def update_boxplot(value, edges):
    active, non_active = '#1B58E2', '#313539'  # '#4C5353'
    if value:
        df = GLOBAL_DATA['net_data'][['treat1', 'treat2', value, 'year']].copy()
        df = df.dropna(subset=[value])
        df['Comparison'] = df['treat1'] + ' vs ' + df['treat2']
        df = df.sort_values(by='Comparison').reset_index()
        df[value] = pd.to_numeric(df[value], errors='coerce')
        margin = (df[value].max() - df[value].min()) * .25  # 25%
        range1 = df[value].min() - margin
        range2 = df[value].max() + margin
        df['color'] = non_active
        df['selected'] = 'nonactive'

        slctd_comps = []
        for edge in edges or []:
            src, trgt = edge['source'], edge['target']
            slctd_comps += [f'{src} vs {trgt}']

        for ind, row in df.iterrows():
            df.loc[ind, 'color'] = active if row.Comparison in slctd_comps else non_active
            df.loc[ind, 'selected'] = 'active' if row.Comparison in slctd_comps else 'nonactive'

        unique_comparisons = df.Comparison.sort_values().unique()
        unique_comparisons = unique_comparisons[~pd.isna(unique_comparisons)]
        fig = go.Figure(data=[go.Box(y=df[df.Comparison == comp][value],
                                     visible=True,
                                     name=comp,
                                     # jitter=0.2,
                                     # width=0.6,
                                     marker_color=active if comp in slctd_comps else non_active,
                                     )
                              for comp in unique_comparisons]
                        )

        # fig = px.box(df, x='Comparison', y=value, #animation_frame='year')
        # TODO: Create and add slider

    else:
        df = pd.DataFrame([[0] * 3], columns=['Comparison', 'value', 'selected'])
        value = df['value']
        range1 = range2 = 0
        fig = go.Figure(data=[go.Box(y=df['value'])])
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80), xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, tick0=0, title=''))

    fig.update_layout(clickmode='event+select',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      font_color="black",
                      yaxis_range=[range1, range2],
                      showlegend=False,
                      autosize=True,
                      font=dict(  # family="sans serif", #size=11,
                          color='black'
                      ),
                      xaxis=dict(showgrid=False, tick0=0),
                      yaxis=dict(showgrid=False)
                      )

    fig.update_traces(boxpoints='outliers', quartilemethod="inclusive", hoverinfo="x+y",
                      selector=dict(mode='markers'), showlegend=False, opacity=1,
                      marker=dict(opacity=1, line=dict(color='black', outlierwidth=2))
                      )

    fig.update_xaxes(ticks="outside", tickwidth=1, tickcolor='black', ticklen=5, tickmode='linear',
                     showline=True, linecolor='black', type="category", autorange=True)  # tickangle=30,

    fig.update_yaxes(showgrid=False, ticklen=5, tickwidth=2, tickcolor='black',
                     showline=True, linecolor='black')

    if not any(value):
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(tickvals=[], ticktext=[], zerolinecolor='gray', zerolinewidth=1, tickangle=0, visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80), xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, tick0=0, title=''),
                          annotations=[{
                              "text": "Check whether transitivity holds in the network: compare the distributions  <br>"
                                      "of your potential effect modifiers across the different comparisons <br>"
                                      " by visual inspection of the effect modifiers box plots <br> <br>"
                                      "Effect modifiers should be similarly distributed across comparisons",
                              "font": {"size": 16, "color": "white", 'family': 'sans-serif'}}]
                          ),
        fig.update_traces(quartilemethod="exclusive", hoverinfo='skip', hovertemplate=None)

    return fig


### - figures on edge click: pairwise forest plots  - ###
@app.callback(Output('tapEdgeData-fig-pairwise', 'figure'),
              Input('cytoscape', 'selectedEdgeData'))
def update_forest_pairwise(edge):
    #### TODO : NEED DIAMOND FROM R PAIRWISE
    slctd_comps = []
    if edge:
        src, trgt = edge[0]['source'], edge[0]['target']
        slctd_comps += [f'{src} vs {trgt}']
        df = GLOBAL_DATA['forest_data_pairwise'].copy()
        df['Comparison'] = df['treat1'] + ' vs ' + df['treat2']
        df = df[df.Comparison.isin(slctd_comps)]
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] / 2
        effect_size = df.columns[1]
        df['CI_width_diamond'] = df.CI_upper_diamond - df.CI_lower_diamond
        df['CI_width_hf_diamond'] = df['CI_width_diamond'] / 2
        center = df['TE_diamond'].reset_index().TE_diamond[0]
        width = df['CI_width_diamond'].reset_index().CI_width_diamond[0]

    else:
        center = width = 0
        effect_size = ''
        df = pd.DataFrame([[0] * 11],
                          columns=[effect_size, "TE_diamond", "id", "studlab", "treat1", "treat2", "CI_lower",
                                   "CI_upper", "CI_lower_diamond", "CI_upper_diamond", "WEIGHT"])

    xlog = effect_size in ('RR', 'OR')

    # fig = px.scatter(df, x=effect_size, y="studlab",
    #              error_x_minus='CI_lower' if xlog else None,
    #              error_x='CI_width_hf' if edge else 'CI_width' if xlog else None,
    #              log_x=xlog,
    #              size=df.WEIGHT / 1.2 if edge else None)
    # center = width = 0

    def romb(center, width, height=0.2):
        return {'x': [center, center - width / 2, center, center + width / 2, center],
                'y': [-height, 0, height, 0, -height]}

    fig = go.Figure()
    if edge:
        from plotly.subplots import make_subplots
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=[center] + list(df[effect_size]), y=['Random effect model'] + list(df.studlab), mode='markers',
                       # error_x_minus=dict(type='data',  # value of error bar given in data coordinates
                       #                    array=df.CI_lower if xlog else None,
                       #                    visible=True),
                       error_x=dict(type='data', color='black',
                                    array=[0] + list(df.CI_width_hf),
                                    visible=True),
                       marker=dict(size=[0] + list(df.WEIGHT / .2), symbol='square', opacity=0.8,
                                   line=dict(color='black'), color='dimgray')
                       ))
        fig.update_yaxes(ticks="outside",
                         showgrid=False,
                         tickcolor='rgba(0,0,0,0)',
                         linecolor='rgba(0,0,0,0)',
                         linewidth=2,
                         zeroline=True, zerolinecolor='black', zerolinewidth=1),
        fig.update_layout(xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, title=''),
                          )
        fig.add_trace(go.Scatter(x=romb(center, width)['x'], y=romb(center, width)['y'],
                                 fill="toself", mode="lines", line=dict(color='black'), fillcolor='#1f77b4'),
                      secondary_y=True)
        fig.update_yaxes(range=[-.3, 1 + df.studlab.shape[0]],
                         tickfont=dict(color='rgba(0,0,0,0)'),
                         tickcolor='rgba(0,0,0,0)',
                         linecolor='rgba(0,0,0,0)',
                         secondary_y=True,
                         row=1, col=1, zeroline=False)
        fig.add_vline(
            x=center, line_width=1, line_dash='dash', line_color='black'
        )

        # if xlog:
        #     fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
        #               line=dict(color="black", width=1), layer='below')
        #
        # fig.update_traces(marker=dict(symbol='square',
        #                           opacity=0.8 if edge else 0,
        #                           line=dict(color='black', width=0), color='dimgrey',
        #                           ),
        #               error_x=dict(thickness=1.3, color="black")
        #               )
        fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5,
                         tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                         ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                         range=[0.1, 1] if xlog else None,
                         autorange=True, showline=True, linewidth=2, linecolor='black',
                         zeroline=True, zerolinecolor='black')


    else:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      clickmode='event+select',
                      font_color="black", showlegend=False,
                      # font=dict(size=11, text="bold"),
                      # margin=dict(l=5, r=10, t=12, b=80),
                      xaxis=dict(showgrid=False, tick0=0, title=''),
                      yaxis=dict(showgrid=False, title=''),
                      title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                      annotations=[
                          # dict(x=min(df.CI_lower), ax=0, y=0.2, ay=-0.1, xref='x', axref='x', yref='paper',
                          #      showarrow=False, text='Random effect model'),
                          # dict(x=min(df.CI_lower), ax=-3, y=0.1, ay=-0.1, xref='x', axref='x', yref='paper',
                          #      showarrow=False, text='Heterogeneity: '),
                          dict(x=0, ax=0, y=-0.15, ay=-0.1, xref='x', axref='x', yref='paper',
                               showarrow=False, text=effect_size)] if edge else None
                      )
    return fig


### -------------- toggle switch forest ---------------- ###
@app.callback([Output("forestswitchlabel1", "style"),
               Output("forestswitchlabel2", "style")],
              [Input("toggle_forest_direction", "value")])
def color_forest_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', }
    return style1, style2


### -------------- toggle switch league table ---------------- ###
@app.callback([Output("cinemaswitchlabel1", "style"),
               Output("cinemaswitchlabel2", "style")],
              [Input("rob_vs_cinema", "value")])
def color_leaguetable_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#b6e1f8', 'font-size': '12px',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '10px'}
    style2 = {'color': '#b6e1f8' if toggle_value else 'gray', 'font-size': '12px',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '0px', }
    return style1, style2


#################################################################
############ Bootstrap Dropdowns callbacks ######################
#################################################################

@app.callback([Output('dd_nds', 'children')],
              [Input('dd_nds_default', 'n_clicks_timestamp'), Input('dd_nds_default', 'children'),
               Input('dd_nds_tot_rnd', 'n_clicks_timestamp'), Input('dd_nds_tot_rnd', 'children')],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, tot_rnd_t, tot_rnd_v):
    values = [default_v, tot_rnd_v]
    dd_nds = [default_t or 0, tot_rnd_t or 0]
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
    values = [circle_v, breadthfirst_v, grid_v, spread_v, cose_v, cola_v, cose_bilkent_v,
              dagre_v, klay_v]
    times = [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, cola_t, cose_bilkent_t,
             dagre_t, klay_t]
    dd_ngl = [t or 0 for t in times]
    which = dd_ngl.index(max(dd_ngl))
    return [values[which]]


#################################################################
############### Bootstrap Modals callbacks ######################
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


# ----- data selector modal -------#
@app.callback(Output("modal_data", "is_open"),
              [Input("data-upload", "n_clicks"),
               Input("submit_modal_data", "n_clicks")],
              [State("modal_data", "is_open"),
               State({'type': 'dataselectors', 'index': ALL}, 'value'),
               State('datatable-upload', 'contents')],
              )
def data_modal(open, submit, is_open, dataselectors, data):
    if open:  # TODO: doesn't make sense given new inputs - but worrks anyways. Consider fixing when have time
        print('a')
        if submit:
            print("Submit button pressed - closing modal")
            new_df = GLOBAL_DATA['new_data_upload']
            print(new_df)
            # do your stuff  -> TODO: rename column variables and rrershape if needed (contrast/long)
            # data.to_json(orient='split').round(3)
            # data = pd.read_json(data, orient='split')
            # print(data)
        return not is_open


@app.callback(Output("submit_modal_data", "disabled"),
              Input({'type': 'dataselectors', 'index': ALL}, 'value'))
def modal_submit_button(dataselectors):
    return not all(dataselectors) if len(dataselectors) else True


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


##################################################################
########################### MAIN #################################
##################################################################

if __name__ == '__main__':
    app.run_server(debug=True, port=8888)
