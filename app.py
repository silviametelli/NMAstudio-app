# Title     :  Dash NMA app
# Objective :  visualization tabs based on network interactivity
# Created by:  Silvia Metelli
# Created on: 10/11/2020
# --------------------------------------------------------------------------------------------------------------------#
import os, io, base64, shutil
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
from flask_caching import Cache
import plotly.express as px, plotly.graph_objects as go
import plotly.figure_factory as ff
from sklearn.cluster import KMeans
from tools.layouts import *
# --------------------------------------------------------------------------------------------------------------------#
from tools.utils import *

shutil.rmtree(TEMP_PATH, ignore_errors=True)
os.makedirs(TEMP_PATH, exist_ok=True)

EMPTY_SELECTION_NODES = {'active': {'ids': dict()}}
EMPTY_SELECTION_EDGES = {'id': None}
write_node_topickle(EMPTY_SELECTION_NODES)
write_edge_topickle(EMPTY_SELECTION_EDGES)

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                #external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# cache = Cache(app.server, config={
#     # try 'filesystem' if you don't want to setup redis
#     'CACHE_TYPE': 'filesystem',
#     # 'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
# })
# __TIME_OUT_CACHE = 20  # in seconds
app.config.suppress_callback_exceptions = True

server = app.server
app.layout = html.Div([dcc.Location(id='url', refresh=False),
                       html.Div(id='page-content')])


# Load extra layouts
cyto.load_extra_layouts()

GLOBAL_DATA = dict()

options_effect_size_cont = [{'label':'MD',  'value':'MD'},
                             {'label':'SMD',     'value':'SMD'}]
options_effect_size_bin = [{'label':'OR',  'value':'OR'},
                             {'label':'RR',     'value':'RR'}]


# ------------------------------ app interactivity ----------------------------------#

#####################################################################################
################################ MULTIPAGE CALLBACKS ################################
#####################################################################################


# Update the index
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':  return Homepage()
    elif pathname == '/doc': return doc_layout
    elif pathname == '/news': return news_layout
    else:  return Homepage()

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
                                                                              or edge[
                                                                                  'target'] in selected_nodes_id] + [
                         {"selector": 'node[id = "{}"]'.format(id),
                          "style": {"opacity": 1}}
                         for id in all_nodes_id if id not in slct_nodesdata and id in all_slct_src_trgt]
    if slct_edgedata and False:  #TODO: Not doing anything at the moment
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


### ----- display forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input("toggle_forest_direction", "value"),
               Input("toggle_forest_outcome", "value"),
               Input("forest_data_STORAGE", "data"),
               Input("forest_data_out2_STORAGE", "data")
               ])
def TapNodeData_fig(data, outcome_direction, outcome, forest_data, forest_data_out2):
    if data:
        treatment = data[0]['label']
        forest_data = pd.read_json(forest_data_out2, orient='split') if outcome else pd.read_json(forest_data, orient='split')
        df = forest_data[forest_data.Reference == treatment]
        effect_size = df.columns[1]
        tau2 = round(df['tau2'].iloc[1], 2)
        df['Treatment'] += ' ' * 23
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['lower_error'] = df[effect_size] - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] / 2
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        CI_lower, CI_upper = df["CI_lower"].map('{:,.2f}'.format), df["CI_upper"].map('{:,.2f}'.format),
        df['CI'] = '(' + CI_lower.astype(str) + ', ' + CI_upper.astype(str) + ')'
        df = df.sort_values(by=effect_size, ascending=False)
    else:
        effect_size = ''
        df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf'])


    xlog = effect_size in ('RR', 'OR')
    up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
    up_rng = 10**np.floor(np.log10(up_rng)) if xlog else None
    low_rng = 10 ** np.floor(np.log10(low_rng)) if xlog else None
    fig = px.scatter(df, x=effect_size, y="Treatment",
                     error_x_minus='lower_error' if xlog else None,
                     error_x='CI_width_hf' if xlog else 'CI_width' if data else None,
                     log_x=xlog,
                     size_max=5,
                     range_x=[min(low_rng, 0.1), max([up_rng, 10])] if xlog else None,
                     range_y=[-1, len(df.Treatment)],
                     size=df.WEIGHT if data else None)

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)')
    if xlog:
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                      line=dict(color="black", width=1), layer='below')

    fig.update_traces(marker=dict(symbol='circle',
                                  opacity=0.8 if data else 0,
                                  line=dict(color='DarkSlateGrey'),
                                  color='green'),
                      error_x=dict(thickness=2.1, color='#313539')  # '#ef563b' nice orange trace
                      )
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black',
                     ticklen=5,
                     categoryorder='category descending' if outcome_direction else 'category ascending',
                     # dtick=1,
                     autorange=False,
                     showline=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinecolor='black')

    if data:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          modebar= dict(orientation = 'v', bgcolor = 'rgba(0,0,0,0)'),
                          autosize=True,
                          #width=500,
                          margin=dict(l=5, r=10, t=12, b=80),
                          xaxis=dict(showgrid=False, autorange=True,
                                     #tick0=0, # TODO: JUST EXPLAIN IT!!!
                                     title=''),
                          yaxis=dict(showgrid=False, title=''),
                          annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                             showarrow=False, text=effect_size),
                                       dict(x=np.floor(np.log10(min(low_rng, 0.1))) if xlog else df.CI_lower.min(),
                                            ax=0, y=-0.14, ay=-0.1,
                                            xref='x', axref='x', yref='paper',
                                            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                            arrowcolor='green' if outcome_direction else 'black'),
                                       dict(x= np.floor(np.log10(max([up_rng, 10]))) if xlog else df.CI_upper.max(),
                                            ax=0, y=-0.14, ay=-0.1,
                                            xref='x', axref='x', yref='paper',
                                            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                            arrowcolor='black' if outcome_direction else 'green'),  #'#751225'
                                       dict(x=np.floor(np.log10(min(low_rng, 0.1)))/2 if xlog else df.CI_lower.min()/2,
                                            y=-0.22,  xref='x', yref='paper',
                                            text='Favours treatment' if outcome_direction else f'Favours {treatment}',
                                            showarrow=False),
                                       dict(x=np.floor(np.log10(max([up_rng, 10])))/2 if xlog else df.CI_upper.max()/2, y=-0.22,
                                            xref='x', yref='paper',
                                            text=f'Favours {treatment}'if outcome_direction else 'Favours treatment',
                                            showarrow=False),
                                       dict(x=-0.47, y=1.03, align='center',
                                            xref='paper', yref='paper',
                                            text='<b>Treatment</b>',
                                            showarrow=False),
                                       dict(x=-0.52, y=-0.033, align='center',
                                            xref='paper', yref='paper',
                                            text='<b>RE model:</b> ' u"\u03C4" '<sup>2</sup>=' f'{tau2}',
                                            showarrow=False),
                                 ]
                          )


        fig.add_trace(go.Scatter(x=[], y=[],
                                 marker=dict(opacity=0),
                                 showlegend=False, mode='markers',
                                 yaxis="y2"))

        fig.update_layout(
            autosize=True,
            yaxis2=dict(tickvals = [*range(df.shape[0])],
                        ticktext=[' '*8 + '{:.2f}   {:<17}'.format(x,y)
                                  for x, y in zip(df[effect_size].values, df['CI'].values)],
                        showgrid=False,  zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        type='category',
                        range=[-1.4, df.shape[0]],
                        anchor="x", overlaying="y",
                        side="right"),
        ),

        fig.add_annotation(x=1.19, y=1.03, align='center',
             xref='paper', yref='y domain',
             text=f'<b>{effect_size}</b>',
             showarrow=False)


        fig.add_annotation(x=1.44, y=1.03, align='center',
                           xref='paper', yref='y2 domain',
                           text='<b>95% CI</b>',
                           showarrow=False)

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
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          modebar= dict(orientation = 'v', bgcolor = 'rgba(0,0,0,0)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig


### ----- display dibim forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig-bidim', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input('forest_data_STORAGE', 'data'),
               Input('forest_data_out2_STORAGE', 'data')])
def TapNodeData_fig_bidim(data, forest_data, forest_data_out2):
    """If click on node uss node to produce forst plot."""
    if data:
        forest_data = pd.read_json(forest_data, orient='split')
        forest_data_out2 = pd.read_json(forest_data_out2, orient='split')
        treatment = data[0]['label']
        df = forest_data[forest_data.Reference == treatment]
        effect_size = df.columns[1]
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['lower_error_1'] = df[effect_size] - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] / 2
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        df = df.sort_values(by=effect_size, ascending=False)
        #second outcome
        df_second = forest_data_out2[forest_data_out2.Reference == treatment]
        df_second['CI_width'] = df_second.CI_upper - df_second.CI_lower
        df_second['lower_error_2'] = df_second[effect_size] - df_second.CI_lower
        df_second['CI_width_hf'] = df_second['CI_width'] / 2
        effect_size_2 = df_second.columns[1]
    else:
        effect_size = effect_size_2 = ''
        df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf'])
        df_second = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                                     'CI_width', 'CI_width_hf'])

    xlog = effect_size in ('RR', 'OR')
    up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
    up_rng = 10**np.floor(np.log10(up_rng)) if xlog else None
    low_rng = 10 ** np.floor(np.log10(low_rng)) if xlog else None

    if len(df_second.Treatment) > len(df.Treatment):
        trts_rmd = set(df_second.Treatment).difference(df.Treatment)
        df_second[df_second['Treatment'].isin(trts_rmd) == False]
    else:
        trts_rmd = set(df.Treatment).difference(df_second.Treatment)
        df[df['Treatment'].isin(trts_rmd) == False]

    df['size'] = df.Treatment.astype("category").cat.codes
    fig = px.scatter(df, x=df[effect_size], y=df_second[effect_size_2],
                     color=df.Treatment,
                     error_x_minus=df['lower_error_1'] if xlog else None,
                     error_x='CI_width_hf' if xlog else 'CI_width' if data else None,
                     error_y_minus=df_second['lower_error_2'] if xlog else None,
                     error_y=df_second.CI_width_hf if data else df_second.CI_width if xlog else None,
                     log_x=xlog,
                     log_y=xlog,
                     size_max = 10,
                     color_discrete_sequence = px.colors.qualitative.Light24,
                     range_x = [min(low_rng, 0.1), max([up_rng, 10])] if xlog else None
                     )

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      autosize=True,
                      modebar=dict(orientation='v', bgcolor='rgba(0,0,0,0)'),
                      legend=dict(itemsizing='trace', itemclick="toggle",
                                  itemdoubleclick="toggleothers",
                                  # orientation='v', xanchor='auto',
                                  traceorder='normal',
                                  orientation='h', y=1.25, xanchor='auto',
                                  font=dict(size=10)) if df['Treatment'].unique().size > 10 else
                                            dict(itemsizing='trace', itemclick="toggle", itemdoubleclick="toggleothers", orientation='v',
                          font=dict(size=10))
                      )

    if xlog:
        fig.add_hline(y=1,line=dict(color="black", width=1, dash='dashdot'))
        fig.add_vline(x=1,line=dict(color="black", width=1, dash='dashdot'))

    fig.update_traces(marker=dict(symbol='circle',
                                  size=9,
                                  opacity=1 if data else 0,
                                  line=dict(color='black'),
                                  # color='Whitesmoke'
                                  ),
                      error_y=dict(thickness=1.3),
                      error_x=dict(thickness=1.3), ),

    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5, dtick=1,
                  #   tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                  #   ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                  #   range=[0.1, 1] if xlog else None,
                     autorange=True, showline=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinecolor='gray', zerolinewidth=1),

    fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5, dtick=1,
                   #  tickvals=[0.1, 0.5, 1, 5] if xlog else None,
                   #  ticktext=[0.1, 0.5, 1, 5] if xlog else None,
                   #  range=[0.1, 1] if xlog else None,
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
    comparisons = df.comparison.str.split(':', expand=True)
    if df is not None:
        df['Comparison'] = comparisons[0] + ' vs ' + comparisons[1]
        df = df.loc[:, ~df.columns.str.contains("comparison")]
        df = df.sort_values(by='Comparison').reset_index()
        df = df[['Comparison', "direct", "indirect", "p-value"]]
        df = df.round(decimals=4)

    slctd_comps = []
    for edge in edges or []:
        src, trgt = edge['source'], edge['target']
        slctd_comps += [f'{src} vs {trgt}']
    if edges and df:
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
@app.callback([Output('cytoscape', 'elements')],
              [Input('net_data_STORAGE', 'data'),
               Input('slider-year', 'value')])
def update_layour_year_slider(net_data, slider_year):
    net_data = pd.read_json(net_data, orient='split')
    net_data = net_data[net_data.year <= slider_year]
    elements = get_network(df=net_data)
    return [elements]

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
                ])
def update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
                  league_table_data, cinema_net_data1, cinema_net_data2):
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
            .pivot_table(index='treat1', columns='treat2', values='rob')
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



### - figures on edge click: transitivity boxplots  - ###
@app.callback(Output('tapEdgeData-fig', 'figure'),
              [Input('dropdown-effectmod', 'value'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('net_data_STORAGE','data')])
def update_boxplot(value, edges, net_data):
    active, non_active = '#1B58E2', '#313539'  # '#4C5353'
    if value:
        net_data  = pd.read_json(net_data, orient='split')
        df = net_data[['treat1', 'treat2', value, 'year']].copy()
        df = df.dropna(subset=[value])
        df['Comparison'] = df['treat1'] + ' vs ' + df['treat2']
        df = df.sort_values(by='Comparison').reset_index()
        df[value] = pd.to_numeric(df[value], errors='coerce')
        margin = (df[value].max() - df[value].min()) * .1  # 10%
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
                      modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
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
                     autorange=True,
                     showline=True, linecolor='black', type="category")  # tickangle=30,

    fig.update_yaxes(showgrid=False, ticklen=5, tickwidth=2, tickcolor='black', autorange=True,
                     showline=True, linecolor='black', zeroline=False)

    if not any(value):
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80), xaxis=dict(showgrid=False, tick0=0, title=''),
                          modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
                          yaxis=dict(showgrid=False, tick0=0, title=''),
                          annotations=[{
                              "text": "Check whether transitivity holds in the network: compare the distributions  <br>"
                                      "of your potential effect modifiers across the different comparisons <br>"
                                      " by visual inspection of the effect modifiers box plots <br> <br>"
                                      "Effect modifiers should be similarly distributed across comparisons",
                              "font": {"size": 15, "color": "white", 'family': 'sans-serif'}}]
                          ),
        fig.update_annotations(align="center")
        fig.update_traces(quartilemethod="exclusive", hoverinfo='skip', hovertemplate=None)

    return fig


### - figures on edge click: pairwise forest plots  - ###
@app.callback(Output('tapEdgeData-fig-pairwise', 'figure'),
              [Input('cytoscape', 'selectedEdgeData'),
               Input("toggle_forest_pair_outcome", "value"),
               Input('forest_data_prws_STORAGE', 'data'),
               Input('forest_data_prws_out2_STORAGE', 'data')])
def update_forest_pairwise(edge, outcome, forest_data_prws, forest_data_prws_out_2):
    _HEIGHT_ROMB = 0.3
    slctd_comps = []
    if edge:
        src, trgt = edge[0]['source'], edge[0]['target']
        slctd_comps += [f'{src} vs {trgt}']
        df = pd.read_json(forest_data_prws_out_2, orient='split') if outcome else pd.read_json(forest_data_prws, orient='split')
        df['Comparison'] = df['treat1'] + ' vs ' + df['treat2']
        df = df[df.Comparison.isin(slctd_comps)]
        df['studlab'] += ' ' * 10
        effect_size = df.columns[1]
        tau2 = round(df['tau2'].iloc[0], 2) if df['tau2'].iloc[0] is not np.nan else "NA"
        I2 = round(df['I2'].iloc[0], 2)
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['lower_error'] = df[effect_size] - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] / 2
        df['CI_width_diamond'] = df.CI_upper_diamond - df.CI_lower_diamond
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        df['CI_width_hf_diamond'] = df['CI_width_diamond'] / 2
        CI_lower, CI_upper = df["CI_lower"].map('{:,.2f}'.format), df["CI_upper"].map('{:,.2f}'.format)
        df['CI'] = '(' + CI_lower.astype(str) + ', ' + CI_upper.astype(str) + ')'
        CI_lower_diamond, CI_upper_diamond = df["CI_lower_diamond"].map('{:,.2f}'.format), df["CI_upper_diamond"].map('{:,.2f}'.format)
        CI_d = '(' + CI_lower_diamond.astype(str) + ', ' + CI_upper_diamond.astype(str) + ')'
        df = df.sort_values(by=effect_size, ascending=False)
        pred_lo  = df['Predict_lo'].reset_index().Predict_lo[0]
        pred_up  = df['Predict_up'].reset_index().Predict_up[0]
        center = df['TE_diamond'].reset_index().TE_diamond[0]
        width = df['CI_width_diamond'].reset_index().CI_width_diamond[0]

    else:
        center = width = 0
        effect_size = ''
        df = pd.DataFrame([[0] * 11],
                          columns=[effect_size, "TE_diamond", "id", "studlab", "treat1", "treat2", "CI_lower",
                                   "CI_upper", "CI_lower_diamond", "CI_upper_diamond", "WEIGHT"])

    xlog = effect_size in ('RR', 'OR')
    up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
    up_rng = 10 ** np.floor(np.log10(up_rng)) if xlog else None
    low_rng = 10 ** np.floor(np.log10(low_rng)) if xlog else None

    fig = px.scatter(df, x= df[effect_size], y= df.studlab,
                       error_x_minus='lower_error' if xlog else None,
                       error_x='CI_width_hf' if xlog else 'CI_width' if edge else None,
                       log_x=xlog,
                       size_max=10,
                       range_x=[min(low_rng, 0.1), max([up_rng, 10])] if xlog else None,
                       range_y=[-1,len(df.studlab)+2],
                       size=df.WEIGHT if edge else None)

    if xlog:
            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                          line=dict(color="black", width=1), layer='below')

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                          plot_bgcolor='rgba(0,0,0,0)',
                          showlegend=False,
                          xaxis_type="log",
                          modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0)'),
                          xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, title=''),
                          )

    fig.update_yaxes(ticks="outside",
                         type='category',
                         showgrid=False,
                         tickcolor='rgba(0,0,0,0)',
                         linecolor='rgba(0,0,0,0)',
                         linewidth=1,
                         zeroline=True, zerolinecolor='black', zerolinewidth=1),

    fig.update_xaxes(ticks="outside",
                         showgrid=False,
                         autorange=True, showline=True,
                         tickcolor='rgba(0,0,0,0)',
                         linecolor='rgba(0,0,0,0)'),

    fig.update_traces(marker=dict(symbol='square',
                                          opacity=0.8 if edge else 0,
                                          line=dict(color='DarkSlateGrey'),
                                          color='grey'),
                              error_x=dict(thickness=2, color='#313539'))  # '#ef563b' nice orange trace
        #
    if edge:
        fig.update_layout(clickmode='event+select',
                              font_color="black",
                              modebar=dict(orientation='v', bgcolor='rgba(0,0,0,0)'),
                              autosize=True,
                              # width=500,
                              margin=dict(l=5, r=10, t=12, b=80),
                              xaxis=dict(showgrid=False, autorange=True,
                                        showline=True, linewidth=1, linecolor='black',
                                         zeroline=True, zerolinecolor='gray', zerolinewidth=1,
                                         # tick0=0, # TODO: JUST EXPLAIN IT!!!
                                         title=''),
                              yaxis=dict(showgrid=False, title=''),
                              annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                                showarrow=False, text=effect_size),
                                           dict(x=np.floor(np.log10(min(low_rng, 0.1))) if xlog else df.CI_lower.min(),
                                                ax=0, y=-0.14, ay=-0.1,
                                                xref='x', axref='x', yref='paper',
                                                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                                arrowcolor='black'),
                                           dict(x=np.floor(np.log10(max([up_rng, 10]))) if xlog else df.CI_upper.max(),
                                                ax=0, y=-0.14, ay=-0.1,
                                                xref='x', axref='x', yref='paper',
                                                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                                arrowcolor='black'),  # '#751225'
                                           dict(x=np.floor(
                                               np.log10(min(low_rng, 0.1))) / 2 if xlog else df.CI_lower.min() / 2,
                                                y=-0.22, xref='x', yref='paper',
                                                text=f'Favours {df.treat1.iloc[0]}',
                                                showarrow=False),
                                           dict(x=np.floor(
                                               np.log10(max([up_rng, 10]))) / 2 if xlog else df.CI_upper.max() / 2,
                                                y=-0.22,
                                                xref='x', yref='paper',
                                                text=f'Favours {df.treat2.iloc[0]}',
                                                showarrow=False),
                                           dict(x=-0.63, y=1, align='center',
                                                xref='paper', yref='paper',
                                                text='<b>Study</b>',
                                                showarrow=False),
                                           dict(x=-0.85, y=-0.04, align='center',
                                                xref='paper', yref='paper',
                                                text='<b>RE model:</b> ' 'I' '<sup>2</sup>=' f'{I2}%, ' u"\u03C4" '<sup>2</sup>=' f'{tau2}' if ~np.isnan(df.tau2.iloc[0]) else "",
                                                showarrow=False),
                                           ]
                              )
        fig.add_vline(x=center, line_width=1, line_dash='dash', line_color='black')

        def romb(center, low=None, up=None, width=None, height=_HEIGHT_ROMB):
            if width:
                low, up =  center - width/2, center + width/2
            return {'x': [center, low, center, up, center],
                    'y': [-height/2, 0, height/2, 0, -height/2]}
        fig.add_trace(go.Scatter(x=romb(center, low=CI_lower_diamond.iloc[0],
                                        up=CI_upper_diamond.iloc[0])['x'],
                                 y=romb(center, low=CI_lower_diamond.iloc[0],
                                        up=CI_upper_diamond.iloc[0])['y'],
                                 fill="toself", mode="lines", line=dict(color='black'),
                                 fillcolor='#1f77b4', yaxis="y2", showlegend=False))

        # fig.update_layout(shapes=[dict(type='line', x0=df.Predict_lo, x1=df.Predict_up,
        #                                y0=0, y1=0,
        #                                xref='paper', yref='y',
        #                                line_width=4, line_color='#8B0000'),
        #                           ])
        fig.add_trace(
            go.Scatter(x=[pred_lo, pred_up],
                       y=[-_HEIGHT_ROMB*2] * 2, #["Prediction Interval"],
                       mode="lines",
                       line=dict( color='#8B0000', width=4), showlegend=False, yaxis="y3",
                     ))

        fig.update_yaxes(range=[-.3, 1 + df.studlab.shape[0]],
                         autorange=True,ticks="outside", tickwidth=2, tickcolor='black',
                        ticklen=5,
                         tickfont=dict(color='rgba(0,0,0,0)'),
                         linecolor='rgba(0,0,0,0)',
                         secondary_y=True,
                         zeroline=False)

        fig.add_trace(go.Scatter(x=[], y=[],
                                 marker=dict(opacity=0),
                                 showlegend=False, mode='markers',
                                 yaxis="y4"))

        fig.update_traces(overwrite=False)

        fig.update_layout(
            autosize=True,
            yaxis2=dict(tickvals=[], ticktext=[],
                        showgrid=False, zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        range=[-1,len(df.studlab)+1],
                        anchor="free", overlaying="y"
                        ),
            yaxis3=dict(tickvals=[], ticktext=[],
                        showgrid=False, zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        range=[-1, len(df.studlab) + 1],
                        scaleanchor = 'y',
                        anchor="x",  overlaying="y2"
                        ),
            yaxis4=dict(tickvals=[*range(df.shape[0])],
                        ticktext=[' ' * 5 + '{:.2f}   {:<17}'.format(x, y)
                                  # for x, y in zip(df[effect_size].values, df['CI'].values)],
                                  for x, y in zip(np.append(df[effect_size].values, center),
                                                  np.append(df['CI'].values, CI_d.iloc[0]))],
                        showgrid=False, zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        type='category',
                        range=[-2.4, df.shape[0]+1],
                        anchor="x", overlaying="y",
                        side="right"),
        ),

        fig.update_layout(yaxis_range=[-2.4, len(df.studlab)+1])

        fig.add_annotation(x=1.18, y=1, align='center',
                           xref='paper', yref='y domain',
                           text=f'<b>{effect_size}</b>',
                           showarrow=False)

        fig.add_annotation(x=1.52, y=1, align='center',
                           xref='paper', yref='y3 domain',
                           text='<b>95% CI</b>',
                           showarrow=False)

    else:
        fig.update_layout(clickmode='event+select',
                  font_color="black",
                  margin=dict(l=5, r=10, t=12, b=80),
                  xaxis=dict(showgrid=False, tick0=0, title=''),
                  yaxis=dict(showgrid=False, title=''),
                  title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                  annotations=[]
                  )
    if not edge:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          modebar=dict(orientation='v', bgcolor='rgba(0,0,0,0)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig


############ - Funnel plot  - ###############
@app.callback(Output('funnel-fig', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input("toggle_funnel_direction", "value"),
               Input("funnel_data_STORAGE", "data"),
               Input("funnel_data_out2_STORAGE", "data"),
               ])
def Tap_funnelplot(node, outcome2, funnel_data, funnel_data_out2):
    EMPTY_DF = pd.DataFrame([[0] * 9],
                            columns=[ 'index', 'studlab', 'treat1', 'treat2', '',
                                      'TE_direct', 'TE_adj', 'seTE', 'Comparison'])
    if node:
        treatment = node[0]['label']
        funnel_data = pd.read_json(funnel_data, orient='split')
        funnel_data_out2 = pd.read_json(funnel_data_out2, orient='split')
        df = (funnel_data_out2[funnel_data_out2.treat2 == treatment].copy()
              if outcome2 else
              funnel_data[funnel_data.treat2 == treatment].copy())
        df['Comparison'] = (df['treat1'] + ' vs ' + df['treat2']).astype(str)
        effect_size = df.columns[4]
        df = df.sort_values(by='seTE', ascending=False)
    else:
        effect_size = ''
        df = EMPTY_DF

    max_y = df.seTE.max()+0.2

    fig = px.scatter(df if df is not None else EMPTY_DF,
                     x="TE_adj", y="seTE",#log_x=xlog,
                     range_x=[min(df.TE_adj)-3, max(df.TE_adj)+3],
                     range_y=[0.01, max_y+10],
                     symbol="Comparison", color="Comparison",
                     color_discrete_sequence = px.colors.qualitative.Light24)

    fig.update_traces(marker=dict(size=6, # #symbol='circle',
                      line=dict(width=1, color='black')),
                       )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)')

    if node:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          coloraxis_showscale=False,
                          showlegend=True,
                          modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0)'),
                          autosize=True,
                          margin=dict(l=10, r=5, t=20, b=60),
                          xaxis=dict(showgrid=False, autorange=False, zeroline=False,
                                     title='',showline=True, linewidth=1, linecolor='black'),
                          yaxis=dict(showgrid=False, autorange=False, title='Standard Error',
                                     showline=True, linewidth=1, linecolor='black',
                                     zeroline=False,
                                     ),
                          annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=False, text= 'Log' f'{effect_size} ' 'centered at comparison-specific pooled effect')],

                          )
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=0, x1=0,
                      line=dict(color="black", width=1), layer='below')

        fig.add_shape(type='line', y0=max_y, x0= -1.96 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dashdot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= 1.96 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dashdot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= -2.58 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= 2.58 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dot', width=1.5))


        fig.update_yaxes(autorange="reversed", range=[max_y,0])


    if not node:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zeroline=False, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          coloraxis_showscale=False,
                          showlegend=False,
                          modebar = dict(orientation='h', bgcolor='rgba(0,0,0,0)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig


############ - ranking plots  - ###############
@app.callback([Output('tab-rank1', 'figure'),
               Output('tab-rank2', 'figure')],
              [Input('toggle_rank_direction', 'value'),
               Input('toggle_rank2_direction', 'value'),
               Input('toggle_rank2_direction_outcome1', 'value'),
               Input('toggle_rank2_direction_outcome2', 'value'),
               Input('net_data_STORAGE', 'data'),
               Input('ranking_data_STORAGE', 'data')])
def ranking_plot(outcome_direction_1, outcome_direction_2, outcome_direction_11, outcome_direction_22,
                 net_data, ranking_data):

    net_data = pd.read_json(net_data, orient='split')  if net_data else None
    df = pd.read_json(ranking_data, orient='split')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    outcomes = ["Outcome 1", "Outcome 2"]

    # True=harmful
    df1 = df.copy(deep=True)
    if "pscore2" in df1.columns:
        if outcome_direction_1:
            df1.pscore1 = 1 - df1.pscore1.values
        if outcome_direction_2:
            df1.pscore2 = 1 - df1.pscore2.values
        df1.sort_values(by=["pscore1", "pscore2"],
                       ascending=[False, False], inplace=True)
        z_text = [df1.pscore1.round(2).astype(str).values,
                  df1.pscore2.round(2).astype(str).values]
        pscores = [list(df1.pscore1), list(df1.pscore2)]
    else:
        outcomes = "Outcome"
        if outcome_direction_1:
            pscore = 1 - df1.pscore
        pscore.sort_values(ascending=False, inplace=True) # TODO: check if it works
        z_text = pscore.round(2).astype(str).values
        pscores = list(pscore)

    #################### heatmap ####################
    fig = ff.create_annotated_heatmap(pscores, x=list(df1.treatment), y=outcomes,
                                      reversescale=True,
                                      annotation_text=z_text, colorscale= 'Viridis',
                                      hoverongaps=False)

    for annotation in fig.layout.annotations:
        annotation.font.size = 9

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)',
                      modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0)'),
                      xaxis=dict(showgrid=False, autorange=True, title='',
                                 tickmode='linear', type="category"),
                      yaxis=dict(showgrid=False, autorange=True, title='', range=[0,len(outcomes)]),
                      )

    fig['layout']['xaxis']['side'] = 'bottom'
    fig['data'][0]['showscale'] = True
    fig['layout']['yaxis']['autorange'] = "reversed"
    #fig['layout']['xaxis']['autorange'] = "reversed"
    fig.layout.margin = dict(l=0, r=0, t=70, b=180)

    ######################### scatter plot #########################
    if 'pscore2' in df.columns:
        if outcome_direction_11:
            df.pscore1 = 1 - df.pscore1
        if outcome_direction_22:
            df.pscore2 = 1 - df.pscore2

        kmeans = KMeans(n_clusters=int(round(len(df.treatment)/float(5.0),0)),
                         init='k-means++', max_iter=300, n_init=10, random_state=0)
        labels = kmeans.fit(df[['pscore1', 'pscore2']])
        df['Trt groups'] = labels.labels_.astype(str)
        df_full = net_data.groupby(['treat1', 'treat2']).TE.count().reset_index()
        df_full_2 = net_data.groupby(['treat1', 'treat2']).TE2.count().reset_index()
        node_weight, node_weight_2 = {}, {}
        for treat in df.treatment:
             n1 = df_full[df_full.treat1 == treat].TE.sum()
             n2 = df_full[df_full.treat2 == treat].TE.sum()
             node_weight[treat] = (n1 + n2)/float(np.shape(df)[0])

             n1 = df_full_2[df_full_2.treat1 == treat].TE2.sum()
             n2 = df_full_2[df_full_2.treat2 == treat].TE2.sum()
             node_weight_2[treat] = (n1 + n2)/float(np.shape(df)[0])

        sum_weight = dict((Counter(node_weight)+Counter(node_weight_2)))
        mean_weight = {k: v / 2.0 for k, v in sum_weight.items()}  # Node size prop to mean count of node size in outcome 1 and outcome 2
        df["node weight"] = df["treatment"].map(mean_weight)

        fig2 = px.scatter(df, x="pscore1", y="pscore2",
                          color="Trt groups",
                          size='node weight',
                          hover_data=["treatment"],
                          text='treatment')

        fig2.update_layout(coloraxis_showscale=True,
                            showlegend=False,
                            paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)',
                            modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
                            xaxis=dict(showgrid=False, autorange=True,dtick = 0.1,
                                       tickcolor='black',ticks="outside", tickwidth=1,
                                       showline=True, linewidth=1, linecolor='black',
                                       zeroline=False, zerolinecolor='black', zerolinewidth=1,
                                        range=[0,1]),
                            yaxis=dict(showgrid=False, autorange=True, dtick = 0.1,
                                       showline=True, linewidth=1, linecolor='black',
                                       tickcolor='black',ticks="outside", tickwidth=1,
                                       zeroline=False, zerolinecolor='black', zerolinewidth=1,
                                       range=[0, 1]
                                      ))

        fig2.update_traces(textposition='top center',  textfont_size=10,
                            marker=dict(line=dict(width=1, color='black'))
                            )
        fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        fig2.layout.margin = dict(l=30, r=30, t=10, b=80)

    else:
        df = pd.DataFrame([[0] * 2], columns=['pscore1', 'pscore2'])
        fig2 = px.scatter(df, x="pscore1", y="pscore2")
        fig2.update_shapes(dict(xref='x', yref='y'))
        fig2.update_xaxes(tickvals=[], ticktext=[], visible=False)
        fig2.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig2.update_layout(margin=dict(l=100, r=100, t=12, b=80), xaxis=dict(showgrid=False, tick0=0, title=''),
                          modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
                          yaxis=dict(showgrid=False, tick0=0, title=''),
                          annotations=[{"text": "Please provide a second outcome",
                                        "font": {"size": 15, "color": "white", 'family': 'sans-serif'}}]
                          ),
        fig2.update_annotations(align="center")
        fig2.update_traces(quartilemethod="exclusive", hoverinfo='skip', hovertemplate=None)

    return fig, fig2

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
def data_modal(open_modal_data, upload,
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
            return not modal_data_is_open, not modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE
        return not modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE
    else:
        return modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE



@app.callback(Output("upload_modal_data", "disabled"),
              Input({'type': 'dataselectors', 'index': ALL}, 'value'),
              )
def modal_ENABLE_UPLOAD_button(dataselectors):
    return not all(dataselectors) if len(dataselectors) else True


from assets.storage import DEFAULT_DATA

OUTPUTS_STORAGE_IDS = list(DEFAULT_DATA.keys())[1:-2]

@app.callback([Output(id, 'data') for id in OUTPUTS_STORAGE_IDS],
              [Input("submit_modal_data", "n_clicks")],
              [State('TEMP_'+id, 'data') for id in OUTPUTS_STORAGE_IDS],
              prevent_initial_call=True)
def modal_SUBMIT_button(submit,
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
        OUT_DATA = [TEMP_consistency_data_STORAGE, TEMP_user_elements_STORAGE, TEMP_forest_data_STORAGE,
                    TEMP_forest_data_out2_STORAGE, TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2_STORAGE,
                    TEMP_ranking_data_STORAGE, TEMP_funnel_data_STORAGE, TEMP_funnel_data_out2_STORAGE,
                    TEMP_league_table_data_STORAGE, TEMP_net_split_data_STORAGE, TEMP_net_split_data_out2_STORAGE]
        OUT_DATA = OUT_DATA or [None] * len(OUTPUTS_STORAGE_IDS)
        return OUT_DATA
    else:
        return list(DEFAULT_DATA.values())[1:-2]




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
              State("TEMP_net_data_STORAGE", "data"),
              State("TEMP_forest_data_STORAGE", "data")
              )
def modal_submit_checks_NMA(modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_STORAGE):
    if modal_data_checks_is_open:
        net_data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
        NMA_data = run_network_meta_analysis(net_data)
        TEMP_forest_data_STORAGE = NMA_data.to_json( orient='split')
        TEMP_user_elements_STORAGE = get_network(df=net_data)
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
               Output('TEMP_league_table_data_STORAGE', 'data')],
              Input('TEMP_forest_data_prws_STORAGE', 'modified_timestamp'),
              State("modal_data_checks", "is_open"),
              State("TEMP_net_data_STORAGE", "data"),
              State('TEMP_league_table_data_STORAGE', 'data')
              )
def modal_submit_checks_LT(pw_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, LEAGUETABLE_data):
    """ produce new league table from R """
    if modal_data_checks_is_open:
        LEAGUETABLE_data = generate_league_table(pd.read_json(TEMP_net_data_STORAGE, orient='split'))
        LEAGUETABLE_data = [f.to_json( orient='split') for f in LEAGUETABLE_data]
        return (html.P(u"\u2713" + " Successfully generated league table.", style={"color":"green"}),
                '__Para_Done__', LEAGUETABLE_data)
    else:
        return None, '', LEAGUETABLE_data

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
########################### MAIN #################################
##################################################################


if __name__ == '__main__':
    app._favicon = ("assets/favicon.ico")
    app.title = 'NMAstudio'
    app.run_server(debug=True)
