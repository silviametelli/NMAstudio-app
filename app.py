# Title     :  Dash NMA app
# Objective :  visualization of network meta-analysis based on network interactivity
# Created by:  Silvia Metelli
# Created on: 10/11/2020
# --------------------------------------------------------------------------------------------------------------------#
import io, base64
from tools.utils import *
from tools.PATHS import SESSION_PICKLE, get_session_pickle_path, TODAY, SESSION_TYPE, get_new_session_id

create_sessions_folders()
clean_sessions_folders()
import warnings
warnings.filterwarnings("ignore")
# --------------------------------------------------------------------------------------------------------------------#
import dash
from dash.dependencies import Input, Output, State, ALL
from dash_extensions.snippets import send_file
from tools.layouts import *
from tools.functions_ranking_plots import __ranking_plot
from tools.functions_funnel_plot import __Tap_funnelplot
from tools.functions_nmaforest_plot import __TapNodeData_fig, __TapNodeData_fig_bidim
from tools.functions_pairwise_plots import __update_forest_pairwise
from tools.functions_boxplots import __update_boxplot
from tools.functions_project_setup import __update_options
from tools.functions_netsplit import __netsplit
from tools.functions_build_league_data_table import __update_output
from tools.functions_generate_stylesheet import __generate_stylesheet

# --------------------------------------------------------------------------------------------------------------------#

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
                     dcc.Store(id='consts_STORAGE',
                               data={'today': TODAY,
                                     'session_ID': SESSION_ID},
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
               Input("dropdown-outcome2", "value")],
              [State('datatable-upload', 'contents'),
              State('datatable-upload', 'filename')]
             )
def update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):
    return __update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename)


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
@app.callback(Output("cytoscape", "generateImage"),
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
            'scale': 3}}


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
def update_layour_year_slider(net_data, slider_year, out2_nma, out2_pair, out2_cons, out2_fun, reset_btn):
    YEARS_DEFAULT = np.array([1963, 1990, 1997, 2001, 2003, 2004, 2005, 2006, 2007, 2008, 2010,
                              2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020])
    years_dft_max = YEARS_DEFAULT.max()

    reset_btn_triggered = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'reset_project.n_clicks' in triggered: reset_btn_triggered = True

    net_data = pd.read_json(net_data, orient='split')

    if out2_nma or out2_pair or out2_cons or out2_fun:
        net_data2 =  net_data.drop(["TE", "seTE", "n1", "n2"], axis=1)
        net_data2 = net_data2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
        net_data = pd.DataFrame(net_data2)

        net_data = net_data[net_data.year <= slider_year] if not reset_btn_triggered else  net_data[net_data.year <= years_dft_max]
        elements = get_network(df=net_data)
    else:
        net_data = net_data[net_data.year <= slider_year] if not reset_btn_triggered else  net_data[net_data.year <= years_dft_max]
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
               Input('reset_project', 'n_clicks'),
               Input('ranking_data_STORAGE','data')
                ],
              [State('net_data_STORAGE', 'modified_timestamp'),
               State('league_table_data_STORAGE', 'modified_timestamp'),
               State('datatable-secondfile-upload', 'filename'),
               State('datatable-secondfile-upload-2', 'filename'),
               State('datatable-secondfile-upload-2','disabled')],
              prevent_initial_call=True)
def update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
                  league_table_data, cinema_net_data1, cinema_net_data2, data_and_league_table_DATA,
                  reset_btn, ranking_data, net_data_STORAGE_TIMESTAMP, league_table_data_STORAGE_TIMESTAMP,
                  filename_cinema1, filename_cinema2, filename_cinema2_disabled):
    return __update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
                        league_table_data, cinema_net_data1, cinema_net_data2, data_and_league_table_DATA,
                        reset_btn, ranking_data, net_data_STORAGE_TIMESTAMP, league_table_data_STORAGE_TIMESTAMP,
                        filename_cinema1, filename_cinema2, filename_cinema2_disabled)



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
                                    'Dagre', 'Klay']
                       ]),
              prevent_initial_call=True)
def which_dd_nds(circle_t, circle_v, breadthfirst_t, breadthfirst_v,
                 grid_t, grid_v, spread_t, spread_v, cose_t, cose_v,
                 cola_t, cola_v, dagre_t, dagre_v, klay_t, klay_v):
    values = [circle_v, breadthfirst_v, grid_v, spread_v, cose_v, cola_v,
              dagre_v, klay_v]
    times = [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, cola_t,
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

#--------------------------------------------------------------------------------#
# ------------------------------ data selector modal ----------------------------#
#--------------------------------------------------------------------------------#

@app.callback([Output("modal_data", "is_open"),
               Output("modal_data_checks", "is_open"),
               Output("TEMP_net_data_STORAGE", "data"),
               Output("uploaded_datafile_to_disable_cinema", "data")
               ],
              [Input("upload_your_data", "n_clicks_timestamp"),
               Input("upload_modal_data", "n_clicks_timestamp"),
               Input("submit_modal_data", "n_clicks_timestamp"),
               Input("uploaded_datafile_to_disable_cinema", "data"),
               ],
              [State("dropdown-format","value"),
               State("dropdown-outcome1","value"),
               State("dropdown-outcome2","value"),
               State("modal_data", "is_open"),
               State("modal_data_checks", "is_open"),
               State('datatable-upload', 'contents'),
               State('datatable-upload', 'filename'),
               State({'type': 'dataselectors', 'index': ALL}, 'value'),
               State("TEMP_net_data_STORAGE", "data"),
               ]
              )
def data_modal(open_modal_data, upload, submit, filename_exists,
               search_value_format, search_value_outcome1, search_value_outcome2,
               modal_data_is_open, modal_data_checks_is_open,
               contents, filename, dataselectors, TEMP_net_data_STORAGE,
               ):
    ctx = dash.callback_context
    if not ctx.triggered: button_id = 'No clicks yet'
    else:                 button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    filename_exists = True if filename is not None else False

    if open_modal_data:
        if upload and button_id=='upload_modal_data':
            filename_exists = True if filename is not None else False

            try:
                data_user = parse_contents(contents, filename)

            except:
                raise ValueError('data upload failed: Likely UnicodeDecodeError or multiple type Error, check your variables characters and type')
            var_dict = dict()

            if search_value_format == 'iv':
                if search_value_outcome2 is None:
                    studlab, treat1, treat2, rob, year, TE, seTE, n1, n2 = dataselectors[1: ] # first dataselector is the effect size
                    var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2',  rob: 'rob', year: 'year',
                                TE: 'TE', seTE: 'seTE', n1: 'n1', n2:'n2'}
                else:
                    studlab, treat1, treat2, rob, year, TE, seTE, n1, n2, TE2, seTE2, n21, n22 = dataselectors[2: ]
                    var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2',  rob: 'rob', year: 'year',
                                TE: 'TE', seTE: 'seTE', n1: 'n1', n2:'n2',
                                TE2: 'TE2', seTE2: 'seTE2', n21: 'n2.1', n22:  'n2.2'}
            elif search_value_format == 'contrast':
                if search_value_outcome1 == 'continuous':
                    if search_value_outcome2 is None:
                        studlab, treat1, treat2, rob, year, y1, sd1, y2, sd2, n1, n2 = dataselectors[1: ]  # first dataselector is the effect size
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    y1: 'y1', sd1: 'sd1',
                                    y2: 'y2', sd2: 'sd2', n1: 'n1', n2: 'n2'}
                    elif search_value_outcome2 == 'continuous':
                        studlab, treat1, treat2, rob, year, y1, sd1, y2, sd2, n1, n2, y21, sd12, y22, sd22, n21, n22 = dataselectors[2: ]
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    y1: 'y1', sd1: 'sd1', y2: 'y2', sd2: 'sd2', n1: 'n1', n2: 'n2', y21: 'y2.1', sd12: 'sd1.2', y22: 'y2.2', sd22: 'sd2.2',
                                    n21: 'n2.1', n22: 'n2.2'}
                    else:
                        studlab, treat1, treat2, rob, year, y1, sd1, y2, sd2, n1, n2, z1, z2, n21, n22 = dataselectors[2: ]
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    y1: 'y1', sd1: 'sd1', y2: 'y2', sd2: 'sd2', n1: 'n1', n2: 'n2', z1: 'z1', z2: 'z2',
                                    n21: 'n2.1', n22: 'n2.2'}

                if search_value_outcome1 == 'binary':
                    if search_value_outcome2 is None:
                        studlab, treat1, treat2, rob, year, r1, n1, r2, n2 = dataselectors[1: ]  # first dataselector is the effect size
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    r1: 'r1', r2: 'r2', n1: 'n1', n2: 'n2'}
                    elif search_value_outcome2 == 'continuous':
                        studlab, treat1, treat2, rob, year, r1, r2, n1, n2, y21, sd12, y22, sd22, n21, n22 = dataselectors[2: ]  # first dataselector is the effect size
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    r1: 'r1', r2: 'r2', n1: 'n1', n2: 'n2',  y21: 'y2.1', sd12: 'sd1.2', y22: 'y2.2', sd22: 'sd2.2', n21: 'n2.1', n22: 'n2.2'}
                    else:
                        studlab, treat1, treat2, rob, year, r1, r2, n1, n2, z1, z2, n21, n22 = dataselectors[2: ]  # first dataselector is the effect size
                        var_dict = {studlab: 'studlab', treat1: 'treat1', treat2: 'treat2', rob: 'rob', year: 'year',
                                    r1: 'r1', r2: 'r2', n1: 'n1', n2: 'n2',
                                    z1: 'z1', z2: 'z2', n21: 'n2.1', n22: 'n2.2',
                                    }
            else:  #long format
                if search_value_outcome1 == 'continuous':
                    if search_value_outcome2 is None:

                        studlab, treat, rob, year, y, sd, n = dataselectors[1: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    y: 'y', sd: 'sd', n: 'n'}
                    elif search_value_outcome2 == 'continuous':
                        studlab, treat, rob, year, y, sd, n, y2, sd2, n2 = dataselectors[2: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    y: 'y', sd: 'sd', n: 'n', y2: 'y2', sd2: 'sd2', n2: 'n2'}
                    else:
                        studlab, treat, rob, year, y, sd, n, z1, nz = dataselectors[2: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    y: 'y', sd: 'sd', n: 'n', z1: 'z1', nz: 'nz'}
                if search_value_outcome1 == 'binary':
                    if search_value_outcome2 is None:

                        studlab, treat, rob, year, r, n = dataselectors[1: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    r: 'r', n: 'n'}

                    elif search_value_outcome2 == 'continuous':
                        studlab, treat, rob, year, r, n, y2, sd2, n2 = dataselectors[2: ]
                        var_dict = {studlab: 'studlab', treat: 'treat', rob: 'rob', year: 'year',
                                    r: 'r', n: 'n', y2: 'y2', sd2: 'sd2', n2:'n2'}


            data_user.rename(columns=var_dict, inplace=True)

            try:
                data = adjust_data(data_user, dataselectors, search_value_format ,search_value_outcome1, search_value_outcome2)
                TEMP_net_data_STORAGE = data.to_json(orient='split')

            except:
                 TEMP_net_data_STORAGE = {}
                 raise ValueError('Data conversion failed')

            return not modal_data_is_open, not modal_data_checks_is_open, TEMP_net_data_STORAGE,  filename_exists

        if submit and button_id == 'submit_modal_data':
                return modal_data_is_open, not modal_data_checks_is_open and (not modal_data_is_open), TEMP_net_data_STORAGE, filename_exists

        return not modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE, filename_exists
    else:
        return modal_data_is_open, modal_data_checks_is_open and (modal_data_is_open), TEMP_net_data_STORAGE, filename_exists



@app.callback(Output("upload_modal_data", "disabled"),
              Input({'type': 'dataselectors', 'index': ALL}, 'value'),
              )
def modal_ENABLE_UPLOAD_button(dataselectors):
    return not all(dataselectors) if len(dataselectors) else True


from assets.storage import DEFAULT_DATA

OUTPUTS_STORAGE_IDS = list(DEFAULT_DATA.keys())[:-2]

@app.callback([Output(id, 'data') for id in OUTPUTS_STORAGE_IDS],
              [Input("submit_modal_data", "n_clicks"),
               Input('reset_project','n_clicks')
               ],
              [State('TEMP_'+id, 'data') for id in OUTPUTS_STORAGE_IDS],
              prevent_initial_call=True)
def modal_SUBMIT_button(submit,  reset_btn,
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
    """ reads in temporary data for all analyses and outputs them in non-temp storages """
    submit_modal_data_trigger = False

    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'submit_modal_data.n_clicks' in triggered: submit_modal_data_trigger = True

    if submit_modal_data_trigger:  # Is triggered by submit_modal_data.n_clicks
        OUT_DATA = [TEMP_net_data_STORAGE, TEMP_net_data_out2_STORAGE, TEMP_consistency_data_STORAGE, TEMP_user_elements_STORAGE,
                    TEMP_user_elements_out2_STORAGE, TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE, TEMP_forest_data_prws_STORAGE,
                    TEMP_forest_data_prws_out2_STORAGE, TEMP_ranking_data_STORAGE, TEMP_funnel_data_STORAGE, TEMP_funnel_data_out2_STORAGE,
                    TEMP_league_table_data_STORAGE, TEMP_net_split_data_STORAGE, TEMP_net_split_data_out2_STORAGE,TEMP_net_split_ALL_data_STORAGE,
                    TEMP_net_split_ALL_data_out2_STORAGE]
        return OUT_DATA
    else:  # Must be triggered by reset_project.n_clicks
        return [data.to_json(orient='split')
                if label not in ['user_elements_STORAGE', 'user_elements_out2_STORAGE']
                else data
                for label, data in DEFAULT_DATA.items()][:-2]



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
    if modal_data_checks_is_open:
        try:
            data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
            passed_checks = data_checks(data)
        except:
            passed_checks = data_checks(data)
            passed_checks["Conversion to wide format failed"] = False
        if all(passed_checks.values()):
                return html.P(u"\u2713" + " All data checks passed.", style={"color":"green"}), '__Para_Done__'
        else:
            return (html.P(["WARNING - some data checks failed:"]+sum([[html.Br(), f'{k}']
                                                                        for k,v in passed_checks.items()
                                                                            if not v], []), style={"color": "orange"}),
                                '__Para_Done__')
    else:
        return None, ''


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
    if modal_data_checks_is_open:
        net_data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
        try:
            TEMP_user_elements_STORAGE = get_network(df=net_data)
            TEMP_user_elements_out2_STORAGE = []
            NMA_data = run_network_meta_analysis(net_data)
            TEMP_forest_data_STORAGE = NMA_data.to_json( orient='split')

            if "TE2" in net_data.columns:
                net_data_out2 = net_data.drop(["TE", "seTE",  "n1",  "n2"], axis=1)
                net_data_out2 = net_data_out2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
                NMA_data2 = run_network_meta_analysis(net_data_out2)
                TEMP_forest_data_out2_STORAGE = NMA_data2.to_json(orient='split')
                TEMP_user_elements_out2_STORAGE = get_network(df=net_data_out2)


            return (False,  '', html.P(u"\u2713" + " Network meta-analysis run successfully.", style={"color":"green"}),
                    '__Para_Done__', TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE, TEMP_user_elements_STORAGE, TEMP_user_elements_out2_STORAGE)
        except Exception as Rconsole_error_nma:
            return (True, str(Rconsole_error_nma), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                        '__Para_Done__', TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE, TEMP_user_elements_STORAGE, TEMP_user_elements_out2_STORAGE)

    else:
        return False, '', None, '', TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE, None, None



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


    if modal_data_checks_is_open:

        data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
        try:
            PAIRWISE_data = run_pairwise_MA(data)
            TEMP_forest_data_prws_STORAGE = PAIRWISE_data.to_json( orient='split')
            TEMP_forest_data_prws_out2 = []

            if "TE2" in data.columns:
                pair_data_out2 = data.drop(["TE", "seTE",  "n1",  "n2"], axis=1)
                pair_data_out2 = pair_data_out2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
                PAIRWISE_data2 = run_pairwise_MA(pair_data_out2)
                TEMP_forest_data_prws_out2 = PAIRWISE_data2.to_json(orient='split')

            return (False, '', html.P(u"\u2713" + " Pairwise meta-analysis run successfully.", style={"color":"green"}),
                               '__Para_Done__', TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2)
        except Exception as Rconsole_error_pw:
                return (True, str(Rconsole_error_pw), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                              '__Para_Done__', TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2)

    else:
        return False, '', None, '', TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2


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
    """ produce new league table from R """
    if modal_data_checks_is_open:
        data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
        try:
            LEAGUETABLE_OUTS =  generate_league_table(data, outcome2=False) if "TE2" not in data.columns or dataselectors[1] not in ['MD','SMD','OR','RR'] else generate_league_table(data, outcome2=True)

            if "TE2" not in data.columns or dataselectors[1] not in ['MD','SMD','OR','RR']:
                (LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, netsplit_all) = [f.to_json( orient='split') for f in LEAGUETABLE_OUTS]
                net_split_data2 = {}
                netsplit_all2 = {}
            else:
                (LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2, netsplit_all, netsplit_all2) = [f.to_json( orient='split') for f in LEAGUETABLE_OUTS]

            return (False, '', html.P(u"\u2713" + " Successfully generated league table, consistency tables, ranking data.", style={"color":"green"}),
                         '__Para_Done__', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2, netsplit_all, netsplit_all2)
        except Exception as Rconsole_error_league:
            return (True, str(Rconsole_error_league), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                    '__Para_Done__', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, netsplit_all) if "TE2" not in data.columns else \
                                    (False, html.P(u"\u274C" + "An error occurred when computing analyses in R: check your data", style={"color":"red"}),
                    '__Para_Done__', Rconsole_error_league, LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2, netsplit_all, netsplit_all2)
    else:
        net_split_data2 = {}
        netsplit_all2 = {}
        return False, '', None, '', LEAGUETABLE_data, ranking_data, consistency_data, net_split_data, net_split_data2, netsplit_all, netsplit_all2


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
    if modal_data_checks_is_open:
        try:
            data = pd.read_json(TEMP_net_data_STORAGE, orient='split')
            FUNNEL_data = generate_funnel_data(data)
            FUNNEL_data = FUNNEL_data.to_json(orient='split')

            if "TE2" in data.columns:
                data_out2 = data.drop(["TE", "seTE",  "n1",  "n2"], axis=1)
                data_out2 = data_out2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
                FUNNEL_data2 = generate_funnel_data(data_out2)
                FUNNEL_data2 = FUNNEL_data2.to_json(orient='split')

            return (False, '', html.P(u"\u2713" + " Successfully generated funnel plot data.", style={"color": "green"}),
            '__Para_Done__', FUNNEL_data, FUNNEL_data2)
        except Exception as Rconsole_error_funnel:
            return (True, str(Rconsole_error_funnel), html.P(u"\u274C" + " An error occurred when computing analyses in R: check your data", style={"color": "red"}),
                    '__Para_Done__', FUNNEL_data, FUNNEL_data2)

    else:
        return False, '', None, '', FUNNEL_data, FUNNEL_data2


@app.callback(Output("submit_modal_data", "disabled"),
              [Input(id, 'data') for id in ['para-check-data','para-anls-data','para-pairwise-data',
                                            'para-LT-data', 'para-FA-data']])
def modal_submit_button(para_check_data_DATA, para_anls_data_DATA, para_prw_data_DATA, para_LT_data_DATA, para_FA_data_DATA):
    return not (para_check_data_DATA==para_anls_data_DATA==para_prw_data_DATA==para_LT_data_DATA==para_FA_data_DATA=='__Para_Done__')




##############################  expand callbacks ###################################

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

#####################################################################
######################## ALERTS/ERRORS ##############################
#####################################################################


# @app.callback(Output('data-type-danger', 'displayed'),
#               [Input('datatable-upload', 'filename'),
#               Input("net_data_STORAGE", "data"),
#               Input("modal_data", "is_open"),
#               Input("dropdown-format", "value"),
#               Input("dropdown-outcome1", "value"),
#               Input("dropdown-outcome2", "value")],
#               )
# def display_confirm(filename, data, modal_data_open, value_format, value_outcome1, value_outcome2):
#     data_ = pd.read_json(data, orient='split')
#     if modal_data_open and filename is not None and value_outcome1 is not None:
#         if value_format == 'contrast':
#             if value_outcome2 is None:
#                 return True if ('y1' in data_.columns and value_outcome1=="continuous") or ('r1' in data_.columns and value_outcome1=="binary") else False
#             else:
#                 return True if ('y1' in data_.columns and value_outcome1=="continuous") or ('r1' in data_.columns and value_outcome1=="binary") or \
#                                ('y2' in data_.columns and value_outcome2=="continuous") or ('r2' in data_.columns and value_outcome2=="binary") else False
#         elif value_format == 'long':
#             if value_outcome2 is None:
#                 return True if ('y1' in data_.columns and value_outcome1=="binary") or ('r1' in data_.columns and value_outcome1=="continuous") else False
#             else:
#                 return True if ('y1' in data_.columns and value_outcome1=="binary") or ('r1' in data_.columns and value_outcome1=="continuous") or \
#                                ('y2' in data_.columns and value_outcome2=="binary") or ('r2' in data_.columns and value_outcome2=="continuous") else False
#     else: return False


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


@app.callback(Output("download_consistency_all", "data"),
              [Input('btn-netsplit-all', "n_clicks"),
               Input('toggle_consistency_direction','value'),
               State("net_split_ALL_data_STORAGE", "data"),
               State("net_split_ALL_data_out2_STORAGE", "data")],
               prevent_initial_call=True)
def generate_csv(n_nlicks, outcome2, consistencydata_all,  consistencydata_all_out2):

    button_trigger  = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'btn-netsplit-all.n_clicks' in triggered: button_trigger = True

    df = (pd.read_json(consistencydata_all, orient='split') if not outcome2
          else  pd.read_json(consistencydata_all_out2, orient='split') if consistencydata_all_out2 else None)

    if button_trigger:
        if df is not None:
            comparisons = df.comparison.str.split(':', expand=True)
            df['Comparison'] = comparisons[0] + ' vs ' + comparisons[1]
            df = df.loc[:, ~df.columns.str.contains("comparison")]
            df = df.sort_values(by='Comparison').reset_index()
            df = df[['Comparison', 'k', "direct", 'nma', "indirect", "p-value"]].round(decimals=4)
            df = df.set_index('Comparison')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
            return dash.dcc.send_data_frame(df.to_csv, filename="consistency_table_full.csv")

    else: return None


#### xlsx colors netsplit table
@app.callback(Output("download_consistency", "data"),
              [Input('consistency-export', "n_clicks"),
               State("netsplit_table-container", "data")],
               prevent_initial_call=True)
def generate_xlsx(n_nlicks, consistencydata):
    df = pd.DataFrame(consistencydata)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    def to_xlsx(bytes_io):
        writer = pd.ExcelWriter(bytes_io, engine='xlsxwriter')  # Create a Pandas Excel writer using XlsxWriter as the engine.
        df.to_excel(writer, sheet_name='Netsplit_Table', index=False)  # Convert the dataframe to an XlsxWriter Excel object.
        workbook, worksheet = writer.book, writer.sheets['Netsplit_Table']  # Get the xlsxwriter workbook and worksheet objects.
        wrap_format = workbook.add_format({'text_wrap': True,
                                           'border':1})
        wrap_format.set_align('center')
        wrap_format.set_align('vcenter')

        col_pval=3
        start_row, end_row =0, df.shape[0]
        #worksheet.write(r+1, col_pval, df.loc[rl, cl], wrap_format) # Overwrite both the value and the format of each header cell
        worksheet.conditional_format(first_row=0, first_col=col_pval,
                                             last_row=end_row, last_col=col_pval,
                                             options={'type': 'cell',
                                                      'format': workbook.add_format({
                                                          'bg_color': 'white',
                                                          'font_color': 'blue',
                                                          'text_wrap': True
                                                           }),
                                                      'criteria': 'between',
                                                      'minimum': 0.10001,
                                                      'maximum': 0.15,
                                                      })
        worksheet.conditional_format(first_row=0, first_col=col_pval,
                                             last_row=end_row, last_col=col_pval,
                                             options={'type': 'cell',
                                                      'format': workbook.add_format({
                                                          'bg_color': 'white',
                                                          'font_color': 'orange',
                                                          'text_wrap': True
                                                           }),
                                                      'criteria': 'between',
                                                      'minimum': 0.05001,
                                                      'maximum': 0.10,
                                                      })
        worksheet.conditional_format(first_row=0, first_col=col_pval,
                                             last_row=end_row, last_col=col_pval,
                                             options={'type': 'cell',
                                                      'format': workbook.add_format({
                                                          'bg_color': 'white',
                                                          'font_color': 'red',
                                                          'text_wrap': True
                                                           }),
                                                      'criteria': '<=',
                                                      'value': 0.05
                                                      })
        worksheet.set_default_row(30)  # Set the default height of Rows to 20.
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col].astype(str).str.split('\n').str[-1]
            max_len = max((
                series.map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 0  # adding a little extra space
            worksheet.set_column(idx+1, idx+1, max_len)  # set column width
        writer.save()  # Close the Pandas Excel writer and output the Excel file.

    return dash.dcc.send_bytes(to_xlsx, filename="Netsplit_Table.xlsx")
    ###########return dash.dcc.send_data_frame(writer.save(), filename="Netsplit_Table_table.xlsx")


#### xlsx colors league table
@app.callback(Output("download_leaguetable", "data"),
              [Input('league-export', "n_clicks"),
               State("league_table", "children")],
               prevent_initial_call=True)
def generate_xlsx(n_clicks, leaguedata):
    df = pd.DataFrame(leaguedata['props']['data'])
    style_data_conditional = leaguedata['props']['style_data_conditional']

    conditional_df = {r: {c: None for c in df.columns} for r in  df.columns}
    for d in style_data_conditional:
        col_k = d['if']['column_id']
        if 'filter_query' in d['if']:
            row_string = d['if']['filter_query'].split('=')[-1]
            row_k = row_string[row_string.find("{") + 1: row_string.find("}")]
            conditional_df[row_k][col_k] = d['backgroundColor']

    df = df.set_index('Treatment')[df.Treatment]

    def to_xlsx(bytes_io):
        writer = pd.ExcelWriter(bytes_io, engine='xlsxwriter')  # Create a Pandas Excel writer using XlsxWriter as the engine.
        df.to_excel(writer, sheet_name='League_Table')  # Convert the dataframe to an XlsxWriter Excel object.
        workbook, worksheet = writer.book, writer.sheets['League_Table']  # Get the xlsxwriter workbook and worksheet objects.
        wrap_format = workbook.add_format({'text_wrap': True,
                                           'border':1})
        wrap_format.set_align('center')
        wrap_format.set_align('vcenter')

        for r, rl in enumerate(df.columns):
            for c, cl in enumerate(df.columns):
                worksheet.write(r+1, c+1, df.loc[rl, cl], wrap_format) # Overwrite both the value and the format of each header cell
                worksheet.conditional_format(first_row=r+1, first_col=c+1,
                                             last_row=r+1, last_col=c+1,
                                             options={'type': 'cell',
                                                      'format': workbook.add_format({
                                                          'bg_color': (conditional_df[rl][cl]
                                                                       if conditional_df[rl][cl]!=CLR_BCKGRND2
                                                                       else 'white'),
                                                          'text_wrap': True
                                                           }),
                                                      'criteria': '>',
                                                      'value': -int(1e8)
                                                      })
        worksheet.set_default_row(30)  # Set the default height of Rows to 20.
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col].astype(str).str.split('\n').str[-1]
            max_len = max((
                series.map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 0  # adding a little extra space
            worksheet.set_column(idx+1, idx+1, max_len)  # set column width
        writer.save()  # Close the Pandas Excel writer and output the Excel file.

    return dash.dcc.send_bytes(to_xlsx, filename="League_Table.xlsx")

    ######### return dash.dcc.send_data_frame(writer.save(), filename="league_table.xlsx")


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
              Output('toggle_rank2_direction', 'disabled'),
              Output('toggle_rank2_direction_outcome1', 'disabled'),
              Output('toggle_rank2_direction_outcome2', 'disabled'),
              Output('toggle_consistency_direction', 'disabled'),
              Output('datatable-secondfile-upload-2','disabled')
               ],
              Input('ranking_data_STORAGE','data')
              )
def disable_out2_toggle(ranking_data):
    df_ranking = pd.read_json(ranking_data, orient='split')
    df_ranking = df_ranking.loc[:, ~df_ranking.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    if "pscore2" not in df_ranking.columns:
        return True, True, True, True, True, True, True, True
    else: return False, False, False, False, False, False, False, False



#### download pdfs ####

@app.callback(Output("download-tuto", "data"),
              Input("full-tuto-pdf", "n_clicks"),
              prevent_initial_call=True
              )
def func(n_clicks):
     return send_file("Documentation/NMAstudio_tutorial.pdf")

@app.callback(Output("download-guide", "data"),
              Input("full-docu-pdf", "n_clicks"),
              prevent_initial_call=True
              )
def func(n_clicks):
     return send_file("Documentation/NMAstudio_tutorial.pdf")


####################################################################
####################################################################
############################ MAIN ##################################
####################################################################
####################################################################


if __name__ == '__main__':
    app._favicon = ("assets/favicon.ico")
    app.title = 'NMAstudio'
    # from flask_talisman import Talisman
    # Talisman(app.server, content_security_policy=None)
    # context = generate_ssl_perm_and_key(cert_name='cert.pem', key_name='key.pem')
    # app.run_server(debug=False, ssl_context=context)
    app.run_server(debug=False)


