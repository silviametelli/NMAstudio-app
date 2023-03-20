# Title     :  Dash NMA app
# Objective :  visualisation of network meta-analysis based on network interactivity
# Created by:  Silvia Metelli
# Created on: 10/11/2020
# --------------------------------------------------------------------------------------------------------------------#
import secrets
# --------------------------------------------------------------------------------------------------------------------#
import warnings
warnings.filterwarnings("ignore")
# --------------------------------------------------------------------------------------------------------------------#
import dash
from dash.dependencies import Input, Output, State, ALL
from dash_extensions.snippets import send_file
from tools.utils import *
from tools.PATHS import SESSION_PICKLE, get_session_pickle_path, TODAY, SESSION_TYPE, get_new_session_id
from tools.layouts import *
from tools.functions_modal_SUBMIT_data import __modal_SUBMIT_button, __data_modal
from tools.functions_NMA_runs import __modal_submit_checks_DATACHECKS, __modal_submit_checks_NMA, __modal_submit_checks_PAIRWISE, __modal_submit_checks_LT, __modal_submit_checks_FUNNEL
from tools.functions_ranking_plots import __ranking_plot
from tools.functions_funnel_plot import __Tap_funnelplot
from tools.functions_nmaforest_plot import __TapNodeData_fig, __TapNodeData_fig_bidim
from tools.functions_pairwise_plots import __update_forest_pairwise
from tools.functions_boxplots import __update_boxplot
from tools.functions_project_setup import __update_options
from tools.functions_netsplit import __netsplit
from tools.functions_build_league_data_table import __update_output
from tools.functions_generate_stylesheet import __generate_stylesheet
from tools.functions_export import __generate_xlsx_netsplit, __generate_xlsx_league, __generate_csv_consistency
# --------------------------------------------------------------------------------------------------------------------#
create_sessions_folders()
clean_sessions_folders()

# Load extra layouts
cyto.load_extra_layouts()
GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                #external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
# app.config.suppress_callback_exceptions = True


def get_new_layout():
    SESSION_ID = get_new_session_id()
    return html.Div([dcc.Location(id='url', refresh=False),
                     html.Div(id='page-content'),
                     dcc.Store(id='consts_STORAGE',  data={'today': TODAY, 'session_ID': SESSION_ID},
                               storage_type='memory',
                               )
                     ])
server = app.server
app.layout = get_new_layout()


# ------------------------------ app interactivity ----------------------------------#

#####################################################################################
################################ MULTIPAGE CALLBACKS ################################
#####################################################################################

HOMEPAGE = Homepage()

# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':  return HOMEPAGE
    elif pathname == '/doc': return doc_layout
    elif pathname == '/news': return news_layout

    else:  return HOMEPAGE




# Update active link in the navbar
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
               Input("dropdown-outcome2", "value")],
              [State('datatable-upload', 'contents'),
              State('datatable-upload', 'filename')]
             )
def update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):
    return __update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename)


#update filename DIV and Store filename in Session
@app.callback([Output("dropdowns-DIV", "style"),
               Output("uploaded_datafile", "children"),
               Output("datatable-filename-upload","data"),
               ],
               [Input('datatable-upload', 'filename')]
              )
def is_data_file_uploaded(filename):
    show_DIV_style = {'display': 'inline-block', 'margin-bottom': '0px'}
    donot_show_DIV_style = {'display': 'none', 'margin-bottom': '0px'}
    if filename:
        return show_DIV_style, filename or '', filename
    else:
        return donot_show_DIV_style, '', filename


### -------------------------- ALL CYTOSCAPE CALLBACKS  ------------------------------- ###

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
               Output("net_download_activation", "data")
               ],
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
               Input("net_download_activation", "data")
               ]
              )
def generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, dd_nds, dd_egs,
                        dwld_button, net_download_activation):
    return __generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, dd_nds, dd_egs,
                        dwld_button, net_download_activation)

### ----- save network plot as png ------ ###
@app.callback([Output("cytoscape", "generateImage"),
               Output("modal-cytoscape", "generateImage")],
              Input("net_download_activation", "data"),
              State('exp-options', 'children'),
              prevent_initial_call=True)
def get_image(net_download_activation, export):
    action = 'store'
    export_selection = export or 'as png'
    if net_download_activation:
        action = "download"
    return {'type': 'jpeg' if export_selection=='as jpeg' else ('png' if export_selection=='as png' else 'svg'),
            'action': action,
            'options': {  # 'bg':'#40515e',
            'scale': 3}}, {'type': 'jpeg' if export_selection=='as jpeg' else ('png' if export_selection=='as png' else 'svg'),
            'action': action,
            'options': {  # 'bg':'#40515e',
            'scale': 3}}

### ----- Update layout with slider ------ ###
@app.callback([Output('cytoscape', 'elements'),
               Output('modal-cytoscape', 'elements')],
              [Input('net_data_STORAGE', 'data'),
               Input('slider-year', 'value'),
               Input('toggle_forest_outcome', 'value'),
               Input('toggle_forest_pair_outcome', 'value'),
               Input('toggle_consistency_direction', 'value'),
               Input('toggle_funnel_direction', 'value'),
               Input('reset_project', 'n_clicks'),
               ])
def update_layout_year_slider(net_data, slider_year, out2_nma, out2_pair, out2_cons, out2_fun, reset_btn):

    YEARS_DEFAULT = np.array([1963, 1990, 1997, 2001, 2003, 2004, 2005, 2006, 2007, 2008, 2010,
                              2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
    years_dft_max = YEARS_DEFAULT.max()


    reset_btn_triggered = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'reset_project.n_clicks' in triggered: reset_btn_triggered = True

    try:
        net_datajs = pd.read_json(net_data, orient='split')
    except:
        net_datajs = pd.read_json(net_data, orient='split', encoding = 'utf-8')

    if out2_nma or out2_pair or out2_cons or out2_fun:
        net_data = pd.read_json(net_data, orient='split')
        net_data2 = net_data.drop(["TE", "seTE", "n1", "n2"], axis=1)
        net_data2 = net_data2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
        net_datajs2 = pd.DataFrame(net_data2)
        net_datajs2 = net_datajs2.dropna(subset=['TE', 'seTE'])
        net_datajs2 = net_datajs2[net_datajs2.year <= slider_year] if not reset_btn_triggered else net_datajs2[net_datajs2.year <= years_dft_max]
        elements = get_network(df=net_datajs2)

    else:
        net_datajs = net_datajs.dropna(subset=['TE', 'seTE'])
        net_datajs = net_datajs[net_datajs.year <= slider_year] if not reset_btn_triggered else net_datajs[net_datajs.year <= years_dft_max]
        elements = get_network(df=net_datajs)

    return elements, elements

### ---------------------------------- FOREST PLOTS CALLBACKS ---------------------------------- ###

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


### - display information box - ###
@app.callback(Output('cytoscape-mouseTapEdgeData-output', 'children'),
              [Input('cytoscape', 'selectedEdgeData')])
def TapEdgeData(edge):
    if edge:
        n_studies = edge[0]['weight_lab']
        studies_str = f"{n_studies}" + (' studies' if n_studies > 1 else ' study')
        return f"{edge[0]['source'].upper()} vs {edge[0]['target'].upper()}: {studies_str}"
    else:
        return "Click on an edge to get information."


### ----- display forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input("toggle_forest_outcome", "value"),
               Input("forest_data_STORAGE", "data"),
               Input("forest_data_out2_STORAGE", "data"),
               #Input("toggle_forest_direction", "value")
               ],
              State("net_data_STORAGE", "data")
              )
def TapNodeData_fig(data, outcome, forest_data, forest_data_out2, net_storage):
    return __TapNodeData_fig(data, outcome, forest_data, forest_data_out2, net_storage)


### ----- display dibim forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig-bidim', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input('forest_data_STORAGE', 'data'),
               Input('forest_data_out2_STORAGE', 'data')],
               State('ranking_data_STORAGE', 'data')
              )
def TapNodeData_fig_bidim(data, forest_data, forest_data_out2, ranking_data):
    return __TapNodeData_fig_bidim(data, forest_data, forest_data_out2, ranking_data)


### - figures on edge click: pairwise forest plots  - ###
@app.callback(Output('tapEdgeData-fig-pairwise', 'figure'),
              [Input('cytoscape', 'selectedEdgeData'),
               Input("toggle_forest_pair_outcome", "value"),
               Input('forest_data_prws_STORAGE', 'data'),
               Input('forest_data_prws_out2_STORAGE', 'data')],
              State("net_data_STORAGE", "data")
              )

def  update_forest_pairwise(edge, outcome, forest_data_prws, forest_data_prws_out_2, net_storage):
    return __update_forest_pairwise(edge, outcome, forest_data_prws, forest_data_prws_out_2, net_storage)



### ----------------------------------  TRANSITIVITY CALLBACK ---------------------------------- ###


@app.callback(Output('tapEdgeData-fig', 'figure'),
              [Input('dropdown-effectmod', 'value'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('net_data_STORAGE','data')])
def update_boxplot(value, edges, net_data):
    return __update_boxplot(value, edges, net_data)


### ----------------------------------  DATA TABLE, LEAGUE TABLE CALLBACKS ---------------------------------- ###


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
               Output('slider-year', 'marks'),
               Output('data_and_league_table_DATA', 'data')],
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
               Input('data_and_league_table_DATA', 'data'),
               Input("forest_data_STORAGE", "data"),
               Input("forest_data_out2_STORAGE", "data"),
               Input('reset_project', 'n_clicks'),
               Input('ranking_data_STORAGE','data'),
                ],
              [State('net_data_STORAGE', 'data'),
               State('net_data_STORAGE', 'modified_timestamp'),
               State('datatable-upload', 'filename'),
               State('league_table_data_STORAGE', 'modified_timestamp'),
               State('datatable-secondfile-upload', 'filename'),
               State('datatable-secondfile-upload-2', 'filename'),
               State('datatable-secondfile-upload-2','disabled')],
              prevent_initial_call=True)
def update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
                  league_table_data, cinema_net_data1, cinema_net_data2, data_and_league_table_DATA,
                  forest_data, forest_data_out2, reset_btn, ranking_data, net_storage, net_data_STORAGE_TIMESTAMP,
                  data_filename, league_table_data_STORAGE_TIMESTAMP, filename_cinema1, filename_cinema2, filename_cinema2_disabled):
    return __update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
                          league_table_data, cinema_net_data1, cinema_net_data2, data_and_league_table_DATA,
                          forest_data, forest_data_out2, reset_btn, ranking_data, net_storage, net_data_STORAGE_TIMESTAMP,
                          data_filename, league_table_data_STORAGE_TIMESTAMP, filename_cinema1, filename_cinema2, filename_cinema2_disabled)



### ---------------------------------- FUNNEL, CONSISTENCY, RANKING  CALLBACKS ---------------------------------- ###


#### ----- consistency table and netsplit table ----- ####
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
   return __netsplit(edges, outcome, net_split_data, net_split_data_out2, consistency_data)

### ----- upload CINeMA data file 1 ------ ###
@app.callback([Output("cinema_net_data1_STORAGE", "data"),
               Output("file2-list", "children"),
               ],
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
               Output("file2-list-2", "children")],
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


### ----- update node info on funnel plot  ------ ###
@app.callback(Output('tapNodeData-info-funnel', 'children'),
              [Input('cytoscape', 'tapNodeData')],
              # prevent_initial_call=True
              )
def TapNodeData_info(data):
    if data: return 'Reference treatment selected: ', data['label']
    else:    return 'Click on a node to choose reference treatment'


############ - Funnel plot  - ###############
@app.callback(Output('funnel-fig', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input("toggle_funnel_direction", "value"),
               Input("funnel_data_STORAGE", "data"),
               Input("funnel_data_out2_STORAGE", "data")]
               )
def Tap_funnelplot(node, outcome2, funnel_data, funnel_data_out2):
    return __Tap_funnelplot(node, outcome2, funnel_data, funnel_data_out2)


############ - Ranking plots  - ###############
@app.callback([Output('tab-rank1', 'figure'),
               Output('tab-rank2', 'figure')],
              Input('ranking_data_STORAGE', 'data'),
              State('net_data_STORAGE', 'data'))
def ranking_plot(ranking_data, net_data):
    return __ranking_plot(ranking_data, net_data)

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
def which_dd_export(default_t, default_v, png_t, png_v, svg_t, svg_v):
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
                                    'Dagre', 'Klay']
                       ]), prevent_initial_call=True)
def which_dd_nds(circle_t, circle_v, breadthfirst_t, breadthfirst_v,
                 grid_t, grid_v, spread_t, spread_v, cose_t, cose_v,
                 cola_t, cola_v, dagre_t, dagre_v, klay_t, klay_v):
    values =  [circle_v, breadthfirst_v, grid_v, spread_v, cose_v, cola_v, dagre_v, klay_v]
    times  =  [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, cola_t, dagre_t, klay_t]
    dd_ngl =  [t or 0 for t in times]
    which  =  dd_ngl.index(max(dd_ngl))
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

#---------------------------------- INITIAL DATA SELECTION and ALL NMA RUNS (in MODALS) ---------------------------------------#

@app.callback([Output("modal_data", "is_open"),
               Output("modal_data_checks", "is_open"),
               Output("TEMP_net_data_STORAGE", "data"),
               Output("uploaded_datafile_to_disable_cinema", "data"),
               Output('Rconsole-error-data', 'children'),
               Output('R-alert-data', 'is_open'),
               ],
              [Input("upload_your_data", "n_clicks_timestamp"),
               Input("upload_modal_data", "n_clicks_timestamp"),
               Input("submit_modal_data", "n_clicks_timestamp"),
               Input('uploaded_datafile_to_disable_cinema','data')
               ],
              [State("dropdown-format", "value"),
               State("dropdown-outcome1", "value"),
               State("dropdown-outcome2", "value"),
               State("modal_data", "is_open"),
               State("modal_data_checks", "is_open"),
               State('datatable-upload', 'contents'),
               State('datatable-upload', 'filename'),
               State({'type': 'dataselectors', 'index': ALL}, 'value'),
               State("TEMP_net_data_STORAGE", "data")
               ]
              )
def data_modal(open_modal_data, upload, submit, filename2,
               search_value_format, search_value_outcome1, search_value_outcome2,
               modal_data_is_open, modal_data_checks_is_open,
               contents, filename, dataselectors, TEMP_net_data_STORAGE,
               ):
    return __data_modal(open_modal_data, upload, submit, filename2,
               search_value_format, search_value_outcome1, search_value_outcome2,
               modal_data_is_open, modal_data_checks_is_open,
               contents, filename, dataselectors, TEMP_net_data_STORAGE,
               )


@app.callback(Output("upload_modal_data", "disabled"),
              Input({'type': 'dataselectors', 'index': ALL}, 'value'),
              )
def modal_ENABLE_UPLOAD_button(dataselectors):
    return not all(dataselectors) if len(dataselectors) else True



from assets.storage import DEFAULT_DATA
OUTPUTS_STORAGE_IDS = list(DEFAULT_DATA.keys())[:-2]
@app.callback([Output(id, 'data') for id in OUTPUTS_STORAGE_IDS],
              [Input("submit_modal_data", "n_clicks"),
               Input('reset_project','n_clicks'),
               Input("username-token-upload", "data"),
               Input("button-token", "n_clicks"),
               Input("input-token-load", "value"),
               Input("load-project", "n_clicks"),
               Input("datatable-filename-upload", "data"),
               ],
              [State('TEMP_'+id, 'data') for id in OUTPUTS_STORAGE_IDS],
              prevent_initial_call=True
              )
def modal_SUBMIT_button(submit,  reset_btn,
                        token_data, token_btn,
                        token_data_load, token_load_btn,
                        filename,
                        TEMP_net_data_STORAGE,
                        TEMP_net_data_out2_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        TEMP_user_elements_STORAGE,
                        TEMP_user_elements_out2_STORAGE,
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
                        TEMP_net_split_ALL_data_STORAGE,
                        TEMP_net_split_ALL_data_out2_STORAGE,
                        ):
    return __modal_SUBMIT_button(submit,  reset_btn,
                        token_data, token_btn,
                        token_data_load, token_load_btn,
                        filename,
                        TEMP_net_data_STORAGE,
                        TEMP_net_data_out2_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        TEMP_user_elements_STORAGE,
                        TEMP_user_elements_out2_STORAGE,
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
                        TEMP_net_split_ALL_data_STORAGE,
                        TEMP_net_split_ALL_data_out2_STORAGE,
                        )



@app.callback(Output("dropdown-effectmod", "options"),
              Input("net_data_STORAGE", "data"),
              )
def update_dropdown_effect_mod(new_data):
    new_data = pd.read_json(new_data, orient='split')
    OPTIONS_VAR = [{'label': '{}'.format(col), 'value': col}
                   for col in new_data.columns] #new_data.select_dtypes(['number']).columns
    return OPTIONS_VAR



@app.callback([Output("para-check-data", "children"),
               Output('para-check-data', 'data')],
              Input("modal_data_checks", "is_open"),
              State("TEMP_net_data_STORAGE", "data"),
              )
def modal_submit_checks_DATACHECKS(modal_data_checks_is_open, TEMP_net_data_STORAGE):
    return __modal_submit_checks_DATACHECKS(modal_data_checks_is_open, TEMP_net_data_STORAGE)

@app.callback([Output('R-alert-nma', 'is_open'),
               Output('Rconsole-error-nma', 'children'),
               Output("para-anls-data", "children"),
               Output('para-anls-data', 'data'),
               Output("TEMP_forest_data_STORAGE", "data"),
               Output("TEMP_forest_data_out2_STORAGE", "data"),
               Output("TEMP_user_elements_STORAGE", "data"),
               Output("TEMP_user_elements_out2_STORAGE", 'data')],
               Input("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State("TEMP_forest_data_STORAGE", "data"),
               State("TEMP_forest_data_out2_STORAGE", "data"),
              )
def modal_submit_checks_NMA(modal_data_checks_is_open, TEMP_net_data_STORAGE,
                            TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE):
    return __modal_submit_checks_NMA(modal_data_checks_is_open, TEMP_net_data_STORAGE,
                            TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE)


@app.callback([Output('R-alert-pair', 'is_open'),
               Output('Rconsole-error-pw', 'children'),
               Output("para-pairwise-data", "children"),
               Output('para-pairwise-data', 'data'),
               Output("TEMP_forest_data_prws_STORAGE", "data"),
               Output("TEMP_forest_data_prws_out2_STORAGE", "data")],
               Input('TEMP_forest_data_STORAGE', 'modified_timestamp'),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State("TEMP_forest_data_prws_STORAGE", "data"),
               State("TEMP_forest_data_prws_out2_STORAGE", "data"),
              )
def modal_submit_checks_PAIRWISE(nma_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2):
    return __modal_submit_checks_PAIRWISE(nma_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2)


@app.callback([Output('R-alert-league', 'is_open'),
               Output('Rconsole-error-league', 'children'),
               Output("para-LT-data", "children"),
               Output('para-LT-data', 'data'),
               Output('TEMP_league_table_data_STORAGE', 'data'),
               Output('TEMP_ranking_data_STORAGE', 'data'),
               Output('TEMP_consistency_data_STORAGE', 'data'),
               Output('TEMP_net_split_data_STORAGE', 'data'),
               Output('TEMP_net_split_data_out2_STORAGE', 'data'),
               Output('TEMP_net_split_ALL_data_STORAGE', 'data'),
               Output('TEMP_net_split_ALL_data_out2_STORAGE', 'data')
               ],
               Input('TEMP_forest_data_prws_STORAGE', 'modified_timestamp'),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State('TEMP_league_table_data_STORAGE', 'data'),
               State('TEMP_ranking_data_STORAGE', 'data'),
               State('TEMP_consistency_data_STORAGE', 'data'),
               State('TEMP_net_split_data_STORAGE', 'data'),
               State('TEMP_net_split_data_out2_STORAGE', 'data'),
               State('TEMP_net_split_ALL_data_STORAGE', 'data'),
               State('TEMP_net_split_ALL_data_out2_STORAGE', 'data'),
               State({'type': 'dataselectors', 'index': ALL}, 'value')
              )
def modal_submit_checks_LT(pw_data_ts, modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data, net_split_data2,
                           netsplit_all, netsplit_all2, dataselectors):
    return  __modal_submit_checks_LT(pw_data_ts, modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data, net_split_data2,
                           netsplit_all, netsplit_all2, dataselectors)

@app.callback([Output('R-alert-funnel', 'is_open'),
               Output('Rconsole-error-funnel', 'children'),
               Output("para-FA-data", "children"),
               Output('para-FA-data', 'data'),
               Output('TEMP_funnel_data_STORAGE', 'data'),
               Output('TEMP_funnel_data_out2_STORAGE', 'data')],
               Input("TEMP_league_table_data_STORAGE", "modified_timestamp"),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State('TEMP_funnel_data_STORAGE', 'data'),
               State('TEMP_funnel_data_out2_STORAGE', 'data')

              )
def modal_submit_checks_FUNNEL(lt_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data, FUNNEL_data2):
    return __modal_submit_checks_FUNNEL(lt_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data, FUNNEL_data2)

@app.callback(Output("submit_modal_data", "disabled"),
              [Input(id, 'data') for id in ['para-check-data','para-anls-data','para-pairwise-data',
                                            'para-LT-data', 'para-FA-data']])
def modal_submit_button(para_check_data_DATA, para_anls_data_DATA, para_prw_data_DATA, para_LT_data_DATA, para_FA_data_DATA):
    return not (para_check_data_DATA==para_anls_data_DATA==para_prw_data_DATA==para_LT_data_DATA==para_FA_data_DATA=='__Para_Done__')




### -------------------------------------------- EXPAND CALLBACKS ----------------------------------------------- ###

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

# ----- network expand modal -----# #TODO: this needs some fixing: eg. node coloring and options not working in expand mode
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


###############################################################################
################### EXPORT TO CSV ON CLICK BUTTON ############################
###############################################################################

@app.callback(Output("download_datatable", "data"),
              [Input('data-export', "n_clicks"),
               State('datatable-upload-container', 'data')],
               prevent_initial_call=True)
def generate_csv(n_nlicks, data):
    df = pd.DataFrame(data)
    return dash.dcc.send_data_frame(df.to_csv, filename="data_wide.csv")


@app.callback(Output("download_consistency_all", "data"),
              [Input('btn-netsplit-all', "n_clicks"),
               Input('toggle_consistency_direction','value'),
               State("net_split_ALL_data_STORAGE", "data"),
               State("net_split_ALL_data_out2_STORAGE", "data")],
               prevent_initial_call=True)
def generate_csv_consistency(n_nlicks, outcome2, consistencydata_all,  consistencydata_all_out2):
    return __generate_csv_consistency(n_nlicks, outcome2, consistencydata_all,  consistencydata_all_out2)

#### xlsx colors netsplit table
@app.callback(Output("download_consistency", "data"),
              [Input('consistency-export', "n_clicks"),
               State("netsplit_table-container", "data")],
               prevent_initial_call=True)
def generate_xlsx_netsplit(n_nlicks, consistencydata):
    return __generate_xlsx_netsplit(n_nlicks, consistencydata)

#### xlsx colors league table
@app.callback(Output("download_leaguetable", "data"),
              [Input('league-export', "n_clicks"),
               State("league_table", "children")],
               prevent_initial_call=True)
def generate_xlsx_league(n_clicks, leaguedata):
    return __generate_xlsx_league(n_clicks, leaguedata)


#############################################################################
############################# TOGGLE SECTION ################################
#############################################################################


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


#############################################################################
######################### DISABLE TOGGLE SWITCHES ###########################
#############################################################################

## disable cinema coloring toggle if no cinema files are passed
@app.callback([Output('rob_vs_cinema', 'disabled'),
              Output('rob_vs_cinema_modal', 'disabled')],
              [Input('datatable-secondfile-upload', 'filename'),
               Input("uploaded_datafile_to_disable_cinema", "data"),
               ]
              )
def disable_cinema_toggle(filename_cinema1, filename_data):

    if filename_cinema1 is None and filename_data: return True, True
    else: return False, False


## disable outcome 2 toggle if no outcome 2 is given in data
@app.callback([Output('toggle_funnel_direction', 'disabled'),
              Output('toggle_forest_outcome', 'disabled'),
              Output('toggle_forest_pair_outcome', 'disabled'),
              Output('toggle_consistency_direction', 'disabled'),
              Output('datatable-secondfile-upload-2','disabled')
              ],
              Input('ranking_data_STORAGE','data')
              )
def disable_out2_toggle(ranking_data):
    df_ranking = pd.read_json(ranking_data, orient='split')
    df_ranking = df_ranking.loc[:, ~df_ranking.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    if "pscore2" not in df_ranking.columns:
        return True, True, True, True, True
    else: return False, False, False, False, False


#### download pdfs ####
@app.callback(Output("download-demodata", "data"),
              Input("demodata", "n_clicks"),
              prevent_initial_call=True)
def func(n_clicks):
     return send_file("Documentation/psoriasis class data.csv")

@app.callback(Output("download-tuto", "data"),
              Input("full-tuto-pdf", "n_clicks"),
              prevent_initial_call=True)
def func(n_clicks):
     return send_file("Documentation/NMAstudio_tutorial.pdf")

@app.callback(Output("download-guide", "data"),
              Input("full-docu-pdf", "n_clicks"),
              prevent_initial_call=True)
def func(n_clicks):
     return send_file("Documentation/NMAstudio_tutorial.pdf")


#################### save project/generate token/laod project ###################

#modal Save/Load Project
@app.callback(
    Output("modal_saveload", "is_open"),
    [Input("open_saveload", "n_clicks"),
     Input("close_saveload", "n_clicks"),
     Input("close_saveload_2", "n_clicks")
     ],
    [State("modal_saveload", "is_open")],
)
def toggle_modal(n1, n2, n2_close, is_open):
    if n1 or n2 or n2_close:
        return not is_open
    return is_open

#### generate username and token
@app.callback(
    [Output("output_username", "children"),
     Output("output_token_entered", "children"),
     Output('button-token','disabled'),
     Output("username-token-upload", "data")
     ],
     State("input-username", "value"),
     Input("button-token", "n_clicks")
     )
def save_project_user_token(input, n_clicks):
    token_btn_triggered = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'button-token.n_clicks' in triggered: token_btn_triggered = True

    if input and token_btn_triggered:
            if len(input) >= 6:
                password = secrets.token_urlsafe(8)
                token = input + "-" + password
                token_data = {'token': token}
                if n_clicks > 0 :
                    return html.P(u"\u2713" + " Successfully generated user",style={"color": "#B1D27B", "font-size":"11px","font-weight": "530"}), f'{token}', True, token_data
            else:
                return html.P(u"\u274C" + " Username must be at least 6 characters", style={"color": "red"}), None, False, None

    else:
        return None, None, False, None


#### load project using token




####################################################################
####################################################################
############################ MAIN ##################################
####################################################################
####################################################################


if __name__ == '__main__':
    app._favicon = ("assets/favicon.ico")
    app.title = 'NMAstudio' #TODO: title works fine locally, does not on Heroku
    # from flask_talisman import Talisman
    # Talisman(app.server, content_security_policy=None)
    # context = generate_ssl_perm_and_key(cert_name='cert.pem', key_name='key.pem')
    # app.run_server(debug=False, ssl_context=context)
    app.run_server(debug=True)





