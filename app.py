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
import itertools
import json
from dash.dependencies import Input, Output, State, ALL
from dash_extensions.snippets import send_file
from tools.utils import *
from tools.PATHS import SESSION_PICKLE, get_session_pickle_path, TODAY, SESSION_TYPE, get_new_session_id
from tools.layouts import *
from tools.skt_layout import *
from tools.functions_modal_SUBMIT_data import __modal_SUBMIT_button_new, __data_modal, __data_trans
from tools.functions_NMA_runs import __modal_submit_checks_DATACHECKS, __modal_submit_checks_NMA,__modal_submit_checks_NMA_new, __modal_submit_checks_PAIRWISE,__modal_submit_checks_PAIRWISE_new, __modal_submit_checks_LT,__modal_submit_checks_LT_new, __modal_submit_checks_FUNNEL,__modal_submit_checks_FUNNEL_new
from tools.functions_ranking_plots import __ranking_plot
from tools.functions_funnel_plot import __Tap_funnelplot
from tools.functions_nmaforest_plot import __TapNodeData_fig, __TapNodeData_fig_bidim
from tools.functions_pairwise_plots import __update_forest_pairwise
from tools.functions_boxplots import __update_boxplot
from tools.functions_project_setup import __update_options, __second_options, __effect_modifier_options,__selectbox1_options, __outcomes_type,__variable_selection
from tools.functions_netsplit import __netsplit
from tools.functions_build_league_data_table import __update_output, __update_output_new
from tools.functions_generate_stylesheet import __generate_stylesheet
from tools.functions_export import __generate_xlsx_netsplit, __generate_xlsx_league, __generate_csv_consistency
from tools.functions_show_forest_plot import __show_forest_plot
from dash import ctx, no_update
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
# app.scripts.append_script({'external_url':'https://NMAstudio.com/assets/gtag.js'})
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y7P5T0R3ML"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-Y7P5T0R3ML');
        </script>
        {%metas%}
        <title>NMAstudio</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div></div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div></div>
    </body>
</html>
'''

def get_new_layout():
    SESSION_ID = get_new_session_id()
    return html.Div([dcc.Location(id='url', refresh=False),
                     html.Div(id='page-content', style={
                         'background-color':'#fff'
                        #  'background-color':'#5c7780'
                         }),
                     dcc.Store(id='consts_STORAGE',  data={'today': TODAY, 'session_ID': SESSION_ID},
                               storage_type='memory',
                               ),
                     ])
server = app.server
app.layout = get_new_layout()


# ------------------------------ app interactivity ----------------------------------#

#####################################################################################
################################ MULTIPAGE CALLBACKS ################################
#####################################################################################

HOMEPAGE = Homepage()
RealHomepage = realHomepage()
SKTPAGE = Sktpage()
# SKT = Sktpage()

# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':  return RealHomepage
    elif pathname == '/results':  return HOMEPAGE
    elif pathname == '/skt':  return SKTPAGE
    # elif pathname == '/doc': return doc_layout
    # elif pathname == '/news': return news_layout

    else:  return RealHomepage

# @app.callback(Output('results_page', 'children'),
#               [Input('test_upload', 'n_clicks_timestamp'),
#                State('results_page', 'children')]
#                )
# def result_page(click, children):
#     if click:
#         return [Navbar(), upload_data()]
#     else:
#         return children

@app.callback([Output('result_page', 'style'),
              Output('upload_page', 'style'),],
              [Input('test_upload', 'n_clicks_timestamp'),
               Input('back_plot', 'n_clicks_timestamp'),
               Input('submit_modal_data','n_clicks_timestamp')
               ]
               )
def result_page(click, click_back, click_trans):
    if ctx.triggered_id == "back_plot":
        return {'display':'grid'}, {'display':'none'}

    if ctx.triggered_id == "test_upload":
        return {'display':'none'}, {'display':'grid'}
    
    if ctx.triggered_id == "submit_modal_data":
        return {'display':'grid'}, {'display':'none'}

    return no_update, no_update





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

@app.callback([Output("upload_selection_second", "children"),
              Output("arrow_step2", "style")
              ],
              [Input("radio-format", "value"),
               Input("radio-outcome1", "value"),
               Input("radio-outcome2", "value")],
              [State('datatable-upload2', 'contents'),
              State('datatable-upload2', 'filename')]
             )
def update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):
    return __second_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename)


@app.callback([Output("outcomes_type", "children"),
              Output("arrow_step_4", "style"),
              Output("select-out-type", "style")
              ],
              [Input("number-outcomes", "value"),
               Input("num_outcomes_button", "n_clicks"),
               ]
             )
def update_options(number_outcomes, click):
    return __outcomes_type(number_outcomes,click)




@app.callback([Output("variable_selection", "children"),
              Output("arrow_step_5", "style"),
              Output("select_variables", "style"),
              ],
              [Input("number-outcomes", "value"),
               Input({'type': 'outcometype', 'index': ALL}, "value"),
               Input('radio-format', 'value')
               ],
               [State('datatable-upload2', 'contents'),
              State('datatable-upload2', 'filename')]
             )
def update_options(number_outcomes, outcometype, data_format, contents, filename):
    return __variable_selection(number_outcomes,outcometype,data_format,contents, filename)



@app.callback(
    [Output({'type': 'outcomebutton', 'index': ALL}, "disabled")],
    [
        Input("number-outcomes", "value"),
        Input({'type': 'effectselectors', 'index': ALL}, "value"),
        Input({'type': 'directionselectors', 'index': ALL}, "value"),
        Input({'type': 'variableselectors', 'index': ALL}, "value")
    ]
)
def next_outcome(number_outcomes, effect, direction, variables):
    if number_outcomes and effect:
        number_outcomes = int(number_outcomes)
        disables = [True] * (number_outcomes)  # Initialize with True for all outcomes
        for i in range(number_outcomes):
            if effect[i] and direction[i] and variables[i]:
                disables[i] = False  # Enable the outcome button if all conditions are met
        disables[number_outcomes-1]= True
        return [disables]
    return [[True] * number_outcomes]
                
             




@app.callback(
    [Output({'type': 'displayvariable', 'index': ALL}, "style")],
    [Input("number-outcomes", "value"),
     Input({'type': 'outcomebutton', 'index': ALL}, "n_clicks"),
     Input({'type': 'outcomeprevious', 'index': ALL}, "n_clicks")
     ],
    [State({'type': 'displayvariable', 'index': ALL}, "style")]
)
def next_outcome(number_outcomes, click, click_previous,style):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if number_outcomes:
        number_outcomes = int(number_outcomes)
        if number_outcomes > 0:
            style = [{'display': 'grid' if i==0 else 'none'} for i in range(number_outcomes)]
            for i in range(number_outcomes-1):    
                if click[i]>0 and "outcomebutton" in changed_id and f'{i}' in changed_id:
                    style = [{'display': 'none'} for _ in range(number_outcomes)]
                    style[i]= {'display': 'none'}
                    style[i+1] = {'display': 'grid'}
            
            for i in range(1,number_outcomes):
                if click_previous[i]>0 and "outcomeprevious" in changed_id and f'{i}' in changed_id:
                    style = [{'display': 'none'} for _ in range(number_outcomes)]
                    style[i-1]= {'display': 'grid'}
                    style[i] = {'display': 'none'}
            return [style]
    
    return style




@app.callback([Output("select-box-1", "children"),
              Output("arrow_step_2", "style"),
              Output("select-overall", "style")],
              [Input("radio-format", "value")],
              [State('datatable-upload2', 'contents'),
              State('datatable-upload2', 'filename')]
             )
def update_options(search_value_format, contents, filename):
    return __selectbox1_options(search_value_format,contents, filename)


@app.callback([Output("number-outcomes-input", "style"),
              Output("arrow_step_3", "style")],
              Input({'type': 'dataselectors_1', 'index': ALL}, 'value'),
              )
def modal_ENABLE_UPLOAD_button(dataselectors):
    if len(dataselectors):
        if all(dataselectors):
            return {"display": 'grid', 'justify-content': 'center',}, {'display':'grid', 'justify-content': 'center'}
        else:
            return {"display": 'none'}, {'display':'none', 'justify-content': 'center'}
    else:
        return {"display": 'none'}, {'display':'none', 'justify-content': 'center'}

@app.callback(
        Output('num_outcomes_button', 'disabled'),
        Input('number-outcomes', 'value')
)
def enable(value):
    if value:
        return False
    return True



@app.callback(Output("select_effect_modifier", "children"),
              [Input("radio-format", "value")],
              [State('datatable-upload2', 'contents'),
              State('datatable-upload2', 'filename')]
             )
def update_options(search_value_format, contents, filename):
    return __effect_modifier_options(search_value_format, contents, filename)






######## second instruction icon showup############
@app.callback(Output("queryicon-studlb","style"),
              Output("queryicon-year","style"),
              Output("queryicon-rob","style"),
              Input("dropdown-format", "value"),
              Input("dropdown-outcome1", "value"))

def is_secondicon_show(search_value_format,search_value_outcome1):
    show_studlb={'display': 'block'}
    donotshow_studlb={'display': 'none'}
    if search_value_format and search_value_outcome1 is not None:
        return show_studlb, show_studlb, show_studlb
    else:
        return donotshow_studlb, donotshow_studlb, donotshow_studlb




#update filename DIV and Store filename in Session
# @app.callback([Output("queryicon-outcome2", "style"),
#                Output("dropdowns-DIV", "style"),
#                Output("uploaded_datafile", "children"),
#                Output("datatable-filename-upload","data"),
#                ],
#                [Input('datatable-upload', 'filename')]
#               )
# def is_data_file_uploaded(filename):
#     show_outcome2_icon = {'display': 'block'}
#     show_DIV_style = {'display': 'inline-block', 'margin-bottom': '0px'}
#     donot_show_DIV_style = {'display': 'none', 'margin-bottom': '0px'}
#     donotshow_outcome2_icon = {'display': 'none'}
#     if filename:
#         return show_outcome2_icon, show_DIV_style, filename or '', filename
#     else:
#         return donotshow_outcome2_icon, donot_show_DIV_style, '', filename

@app.callback([
               Output("dropdowns-DIV2", "style"),
               Output("uploaded_datafile2", "children"),
               Output("arrow_step1", "style"),
               Output("datatable-filename-upload","data"),
               ],
               [Input('datatable-upload2', 'filename')]
              )
def is_data_file_uploaded(filename):
    show_DIV_style = {'display': 'grid', 'justify-content': 'center'}
    donot_show_DIV_style = {'display': 'none', 'justify-content': 'center'}
    arrow1_show={'display':'grid', 'justify-content': 'center'}
    arrow1_notshow={'display':'none', 'justify-content': 'center'}

    if filename:
        return  show_DIV_style, filename or '', arrow1_show, filename
    else:
        return  donot_show_DIV_style, '', arrow1_notshow, filename


### -------------------------- ALL CYTOSCAPE CALLBACKS  ------------------------------- ###

# @app.callback(Output("forest_outcome_select", "options"),
#               Output("forestpaire_outcome_select", "options"),
#               Output("league_outcome_select", "options"),
#               Output("consistency_outcome_select", "options"),
#               Output("funnel_outcome_select", "options"),
#               Output("biforest_outcome_select1", "options"),
#               Output("biforest_outcome_select2", "options"),
#               Output("ranking_outcome_select1", "options"),
#               Output("ranking_outcome_select2", "options"),
#               Input("number-outcomes", "value"),
#               Input({'type': 'nameoutcomes', 'index': ALL}, "value"),
#               State("forest_outcome_select", "options")
#              )

# def update_options(number_outcomes, nameoutcomes, options_var):
#     out_names = ['PASI90',"Death"]
#     if not nameoutcomes or not all(nameoutcomes):
#         if number_outcomes:
#             number_outcomes = int(number_outcomes)
#             options_var = [{'label': f'outcome{i+1}', 'value': i} for i in range(number_outcomes)]
#             return (options_var,) * 9
#         options_var = [{'label': f'{out_names[i]}', 'value': i} for i in range(2)]
#         return (options_var,) * 9
    
#     if number_outcomes:
#         number_outcomes = int(number_outcomes)
#         options_var = [{'label': f'{nameoutcomes[i]}', 'value': i} for i in range(number_outcomes)]
#         return (options_var,) * 9
    
#     options_var = [{'label': f'{out_names[i]}', 'value': i} for i in range(2)]
#     return (options_var,) * 9

@app.callback(
              Output("_outcome_select", "options"),
            #   Output("biforest_outcome_select1", "options"),
              Output("biforest_outcome_select2", "options"),
            #   Output("ranking_outcome_select1", "options"),
              Output("ranking_outcome_select2", "options"),
              Input("number-outcomes", "value"),
              Input({'type': 'nameoutcomes', 'index': ALL}, "value"),
              State("_outcome_select", "options")
             )

def update_options(number_outcomes, nameoutcomes, options_var):
    out_names = ['PASI90',"SAE"]
    if not nameoutcomes or not all(nameoutcomes):
        if number_outcomes:
            number_outcomes = int(number_outcomes)
            options_var = [{'label': f'outcome{i+1}', 'value': i} for i in range(number_outcomes)]
            return (options_var,) * 3
        options_var = [{'label': f'{out_names[i]}', 'value': i} for i in range(2)]
        return (options_var,) * 3
    
    if number_outcomes:
        number_outcomes = int(number_outcomes)
        options_var = [{'label': f'{nameoutcomes[i]}', 'value': i} for i in range(number_outcomes)]
        return (options_var,) * 3
    
    options_var = [{'label': f'{out_names[i]}', 'value': i} for i in range(2)]
    return (options_var,) * 3


### --- update graph layout with dropdown: graph layout --- ###
@app.callback([Output('cytoscape', 'layout'),
               Output('modal-cytoscape', 'layout')],
              [Input('graph-layout-dropdown', 'children'),],
              prevent_initial_call=False)
def update_cytoscape_layout(layout):
    ctx = dash.callback_context
    if layout:
       return {'name': layout.lower(),'fit':True },{'name': layout.lower(), 'fit':True}
    
    return {'name': 'circle','fit':True },{'name': 'circle', 'fit':True}

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
               Input('label_size_input', 'value'),
               Input('treat_name_input', 'value'),
               Input('dd_nds', 'children'),
               Input('dd_egs', 'children'),
               Input("btn-get-png", "n_clicks"),
               Input("btn-get-png-modal", "n_clicks"),
               Input("net_download_activation", "data")
               ]
              )
def generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, label_size,treat_name,dd_nds, dd_egs,
                        dwld_button, dwld_button2,net_download_activation):
    return __generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, label_size,treat_name,dd_nds, dd_egs,
                        dwld_button, dwld_button2,net_download_activation)

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

# ## ----- Update layout with slider ------ ###
# @app.callback([Output('cytoscape', 'elements'),
#                Output('modal-cytoscape', 'elements'),],
#               [Input('net_data_STORAGE', 'data'),
#                Input('slider-year', 'value'),
#                Input('toggle_forest_outcome', 'value'),
#                Input('toggle_forest_pair_outcome', 'value'),
#                Input('toggle_consistency_direction', 'value'),
#                Input('toggle_funnel_direction', 'value'),
#                Input('reset_project', 'n_clicks'),
#             #    Input('node_size_input', 'value'),
#                ])
# def update_layout_year_slider(net_data, slider_year, out2_nma, out2_pair, out2_cons, out2_fun, reset_btn,):

#     YEARS_DEFAULT = np.array([1963, 1990, 1997, 2001, 2003, 2004, 2005, 2006, 2007, 2008, 2010,
#                               2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
#     years_dft_max = YEARS_DEFAULT.max()


#     reset_btn_triggered = False
#     triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
#     if 'reset_project.n_clicks' in triggered: reset_btn_triggered = True

#     try:
#         net_datajs = pd.read_json(net_data, orient='split')
#     except:
#         net_datajs = pd.read_json(net_data, orient='split', encoding = 'utf-8')

#     if out2_nma or out2_pair or out2_cons or out2_fun:
#         net_data = pd.read_json(net_data, orient='split')
#         net_data2 = net_data.drop(["TE", "seTE", "n1", "n2"], axis=1)
#         net_data2 = net_data2.rename(columns={"TE2": "TE", "seTE2": "seTE", "n2.1": "n1", "n2.2": "n2"})
#         net_datajs2 = pd.DataFrame(net_data2)
#         net_datajs2 = net_datajs2.dropna(subset=['TE', 'seTE'])
#         net_datajs2 = net_datajs2[net_datajs2.year <= slider_year] if not reset_btn_triggered else net_datajs2[net_datajs2.year <= years_dft_max]
#         elements = get_network(df=net_datajs2)

#     else:
#         net_datajs = net_datajs.dropna(subset=['TE', 'seTE'])
#         net_datajs = net_datajs[net_datajs.year <= slider_year] if not reset_btn_triggered else net_datajs[net_datajs.year <= years_dft_max]
#         elements = get_network(df=net_datajs)

#     return elements, elements


# @app.callback([Output('cytoscape', 'elements'),
#                Output('modal-cytoscape', 'elements'),],
#               [
#                Input('net_data_STORAGE', 'data'),
#                Input('slider-year', 'value'),
#                Input('forest_outcome_select', 'value'),
#                Input('forestpaire_outcome_select', 'value'),
#                Input('consistency_outcome_select', 'value'),
#                Input('funnel_outcome_select', 'value'),
#                Input("league_outcome_select", "value"),
#                Input('reset_project', 'n_clicks'),
#             #    Input('node_size_input', 'value'),
#                ])
# def update_layout_year_slider(net_data, slider_year, out_nma, out_pair, out_cons, out_fun, out_league,reset_btn,):
    
#     YEARS_DEFAULT = np.array([1963, 1990, 1997, 2001, 2003, 2004, 2005, 2006, 2007, 2008, 2010,
#                               2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
#     years_dft_max = YEARS_DEFAULT.max()


#     reset_btn_triggered = False
#     triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
#     if 'reset_project.n_clicks' in triggered: reset_btn_triggered = True

#     try:
#         net_datajs = pd.read_json(net_data[0], orient='split')
#     except:
#         net_datajs = pd.read_json(net_data[0], orient='split', encoding = 'utf-8')
    
#     outcome = out_nma or out_pair or out_cons or out_fun or out_league
#     if outcome:
#         outcome = int(outcome)
#         net_data = pd.read_json(net_data[0], orient='split')
#         net_datajs2 = net_data[net_data.year <= slider_year] if not reset_btn_triggered else net_data[net_data.year <= years_dft_max]
#         elements = get_network_new(df=net_datajs2, i = outcome )

#     else:
#         net_datajs = net_datajs[net_datajs.year <= slider_year] if not reset_btn_triggered else net_datajs[net_datajs.year <= years_dft_max]
#         elements = get_network_new(df=net_datajs,i = 0)

#     return elements, elements



@app.callback([Output('cytoscape', 'elements'),
               Output('modal-cytoscape', 'elements'),],
              [
               Input('net_data_STORAGE', 'data'),
               Input('slider-year', 'value'),
               Input('_outcome_select', 'value'),
               Input('reset_project', 'n_clicks'),
            #    Input('node_size_input', 'value'),
               ])
def update_layout_year_slider(net_data, slider_year, out_fun,reset_btn):
    
    YEARS_DEFAULT = np.array([1963, 1990, 1997, 2001, 2003, 2004, 2005, 2006, 2007, 2008, 2010,
                              2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
    years_dft_max = YEARS_DEFAULT.max()


    reset_btn_triggered = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'reset_project.n_clicks' in triggered: reset_btn_triggered = True

    try:
        net_datajs = pd.read_json(net_data[0], orient='split')
    except:
        net_datajs = pd.read_json(net_data[0], orient='split', encoding = 'utf-8')
    
    outcome = out_fun 
    if outcome:
        outcome = int(outcome)
        net_data = pd.read_json(net_data[0], orient='split')
        net_datajs2 = net_data[net_data.year <= slider_year] if not reset_btn_triggered else net_data[net_data.year <= years_dft_max]
        elements = get_network_new(df=net_datajs2, i = outcome )

    else:
        net_datajs = net_datajs[net_datajs.year <= slider_year] if not reset_btn_triggered else net_datajs[net_datajs.year <= years_dft_max]
        elements = get_network_new(df=net_datajs,i = 0)

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

# @app.callback(Output('queryicon-forest', 'style'),
#               Input('cytoscape', 'selectedNodeData'))
# def showquer_forest(data):
#     if data:
#         return {'display': 'inline'}
#     else:
#         return {'display': 'none'}



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
# @app.callback(Output('tapNodeData-fig', 'figure'),
#               Output('tapNodeData-fig', 'style'),
#               [Input('cytoscape', 'selectedNodeData'),
#                Input("toggle_forest_outcome", "value"),
#                Input("forest_data_STORAGE", "data"),
#                Input("forest_data_out2_STORAGE", "data"),
#                Input('tapNodeData-fig', 'style')
#                ],
#               State("net_data_STORAGE", "data")
#               )
# def TapNodeData_fig(data, outcome, forest_data, forest_data_out2,style,net_storage):
#     return __TapNodeData_fig(data, outcome, forest_data, forest_data_out2,style,net_storage)



@app.callback(Output('tapNodeData-fig', 'figure'),
              Output('tapNodeData-fig', 'style'),
              [Input('cytoscape', 'selectedNodeData'),
               Input('_outcome_select', 'value'),
               Input("forest_data_STORAGE", "data"),
               Input('tapNodeData-fig', 'style')
               ],
              State("net_data_STORAGE", "data")
              )
def TapNodeData_fig(data, outcome_idx, forest_data, style,net_storage):
    return __TapNodeData_fig(data, outcome_idx, forest_data,style,net_storage)




### ----- display dibim forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig-bidim', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input('forest_data_STORAGE', 'data'),
               Input('_outcome_select', 'value'),
               Input('biforest_outcome_select2', 'value'),
               ]
              )
def TapNodeData_fig_bidim(data, forest_data_store, out_idx1, out_idx2):
    return __TapNodeData_fig_bidim(data, forest_data_store, out_idx1, out_idx2)


### - figures on edge click: pairwise forest plots  - ###
@app.callback([Output('tapEdgeData-fig-pairwise', 'figure'),
              Output('tapEdgeData-fig-pairwise', 'style')],
              [Input('cytoscape', 'selectedEdgeData'),
               Input("_outcome_select", "value"),
               Input('forest_data_prws_STORAGE', 'data'),
               Input('tapEdgeData-fig-pairwise', 'style')],
              State("net_data_STORAGE", "data")
              )

def  update_forest_pairwise(edge, outcome_idx, forest_data_prws, style_pair, net_storage):
    return __update_forest_pairwise(edge, outcome_idx, forest_data_prws,style_pair,net_storage)



### ----------------------------------  TRANSITIVITY CALLBACK ---------------------------------- ###


@app.callback(Output('tapEdgeData-fig', 'figure'),
              [Input('dropdown-effectmod', 'value'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('net_data_STORAGE','data')])
def update_boxplot(value, edges, net_data):
    return __update_boxplot(value, edges, net_data)


### ----------------------------------  DATA TABLE, LEAGUE TABLE CALLBACKS ---------------------------------- ###


# @app.callback([
#                Output('datatable-upload-container', 'data'),
#                Output('datatable-upload-container', 'columns'),
#                Output('datatable-upload-container-expanded', 'data'),
#                Output('datatable-upload-container-expanded', 'columns'),
#                Output('league_table', 'children'),
#                Output('modal_league_table_data', 'children'),
#                Output('league_table_legend', 'children'),
#                Output('modal_league_table_legend', 'children'),
#                Output('rob_vs_cinema', 'value'),
#                Output('rob_vs_cinema_modal', 'value'),
#                Output('slider-year', 'min'),
#                Output('slider-year', 'max'),
#                Output('slider-year', 'marks'),
#                Output('data_and_league_table_DATA', 'data')],
#               [Input('cytoscape', 'selectedNodeData'),
#                Input('net_data_STORAGE', 'data'),
#                Input('cytoscape', 'selectedEdgeData'),
#                Input('rob_vs_cinema', 'value'),
#                Input('rob_vs_cinema_modal', 'value'),
#                Input('slider-year', 'value'),
#                #Input('datatable-secondfile-upload-2', 'contents')
#                Input('league_table_data_STORAGE', 'data'),
#                Input('cinema_net_data1_STORAGE', 'data'),
#                Input('cinema_net_data2_STORAGE', 'data'),
#                Input('data_and_league_table_DATA', 'data'),
#                Input("forest_data_STORAGE", "data"),
#                Input("forest_data_out2_STORAGE", "data"),
#                Input('reset_project', 'n_clicks'),
#                Input('ranking_data_STORAGE','data'),
#                 ],
#               [State('net_data_STORAGE', 'data'),
#                State('net_data_STORAGE', 'modified_timestamp'),
#                State('datatable-upload', 'filename'),
#                State('league_table_data_STORAGE', 'modified_timestamp'),
#                State('datatable-secondfile-upload', 'filename'),
#                State('datatable-secondfile-upload-2', 'filename'),
#                State('datatable-secondfile-upload-2','disabled')],
#               prevent_initial_call=True)
# def update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
#                   league_table_data, cinema_net_data1, cinema_net_data2, data_and_league_table_DATA,
#                   forest_data, forest_data_out2, reset_btn, ranking_data, net_storage, net_data_STORAGE_TIMESTAMP,
#                   data_filename, league_table_data_STORAGE_TIMESTAMP, filename_cinema1, filename_cinema2, filename_cinema2_disabled):
#     return __update_output(store_node, net_data, store_edge, toggle_cinema, toggle_cinema_modal, slider_value,
#                           league_table_data, cinema_net_data1, cinema_net_data2, data_and_league_table_DATA,
#                           forest_data, forest_data_out2, reset_btn, ranking_data, net_storage, net_data_STORAGE_TIMESTAMP,
#                           data_filename, league_table_data_STORAGE_TIMESTAMP, filename_cinema1, filename_cinema2, filename_cinema2_disabled)


# @app.callback([
#                Output('datatable-upload-container', 'data'),
#                Output('datatable-upload-container', 'columns'),
#                Output('datatable-upload-container-expanded', 'data'),
#                Output('datatable-upload-container-expanded', 'columns'),
#                Output('slider-year', 'min'),
#                Output('slider-year', 'max'),
#                Output('slider-year', 'marks'),
#                Output('data_and_league_table_DATA', 'data')],
#               [Input('cytoscape', 'selectedNodeData'),
#                Input('net_data_STORAGE', 'data'),
#                Input('cytoscape', 'selectedEdgeData'),
#                Input('slider-year', 'value'),
#                Input('reset_project', 'n_clicks'),
#                Input('data_and_league_table_DATA', 'data')
#                 ],
#                 [State('net_data_STORAGE', 'data'),
#                State('net_data_STORAGE', 'modified_timestamp'),
#                State('datatable-upload', 'filename'),
#                State('league_table_data_STORAGE', 'modified_timestamp'),
#                State('datatable-secondfile-upload', 'filename')],
#               prevent_initial_call=True)
# def update_output(store_node, net_data, store_edge,slider_value,reset_btn, 
#                   data_and_league_table_DATA, net_storage, net_data_STORAGE_TIMESTAMP,
#                   data_filename, league_table_data_STORAGE_TIMESTAMP, filename_cinema1):
#     return __update_output_new(store_node, net_data, store_edge,slider_value,reset_btn,data_and_league_table_DATA,
#                                net_storage, net_data_STORAGE_TIMESTAMP,
#                   data_filename, league_table_data_STORAGE_TIMESTAMP, filename_cinema1)

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
               Output('data_and_league_table_DATA', 'data'),
               Output('datatable-raw-container', 'data'),
               Output('datatable-raw-container', 'columns')
               ],
              [               
               Input('slider-year', 'value'),
               Input('cytoscape', 'selectedNodeData'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('net_data_STORAGE', 'data'),
               Input('raw_data_STORAGE', 'data'),
               Input('rob_vs_cinema', 'value'),
               Input('rob_vs_cinema_modal', 'value'),
               Input('league_table_data_STORAGE', 'data'),
               Input('cinema_net_data_STORAGE', 'data'),
               Input('data_and_league_table_DATA', 'data'),
               Input("forest_data_STORAGE", "data"),
               Input('reset_project', 'n_clicks'),
            #    Input('ranking_data_STORAGE','data'),
               Input('_outcome_select','value'),
                ],
               State('net_data_STORAGE', 'data'),
               State('raw_data_STORAGE', 'data'),
              prevent_initial_call=True)
def update_output(slider_value, store_node,store_edge,net_data, raw_data,toggle_cinema, toggle_cinema_modal,
                  league_table_data, cinema_net_data, data_and_league_table_DATA,
                  forest_data,  reset_btn,  outcome_idx, net_storage, raw_storage):
    return __update_output_new(slider_value, store_node,store_edge,net_data,raw_data, toggle_cinema, toggle_cinema_modal,
                  league_table_data, cinema_net_data, data_and_league_table_DATA,
                  forest_data,  reset_btn,  outcome_idx, net_storage,raw_storage)



### ---------------------------------- FUNNEL, CONSISTENCY, RANKING  CALLBACKS ---------------------------------- ###


#### ----- consistency table and netsplit table ----- ####
# @app.callback([Output('netsplit_table-container', 'data'),
#               Output('netsplit_table-container', 'columns'),
#                Output('consistency-table', 'data'),
#                Output('consistency-table', 'columns')],
#               [Input('cytoscape', 'selectedEdgeData'),
#                Input("toggle_consistency_direction", "value"),
#                Input('net_split_data_STORAGE', 'data'),
#                Input('net_split_data_out2_STORAGE', 'data'),
#                Input('consistency_data_STORAGE', 'data'),]
#               )
# def netsplit(edges, outcome, net_split_data, net_split_data_out2, consistency_data):
#    return __netsplit(edges, outcome, net_split_data, net_split_data_out2, consistency_data)


@app.callback([Output('netsplit_table-container', 'data'),
              Output('netsplit_table-container', 'columns'),
               Output('consistency-table', 'data'),
               Output('consistency-table', 'columns')],
              [Input('cytoscape', 'selectedEdgeData'),
               Input("_outcome_select", "value"),
               Input('net_split_data_STORAGE', 'data'),
               Input('consistency_data_STORAGE', 'data'),]
              )
def netsplit(edges, outcome_idx, net_split_data, consistency_data):
   return __netsplit(edges, outcome_idx, net_split_data, consistency_data)




### ----- upload CINeMA data file 1 ------ ###
@app.callback([Output("cinema_net_data_STORAGE", "data"),
               Output("file2-list", "children"),
               ],
              [Input('datatable-secondfile-upload', 'contents'),
               Input('cinema_net_data_STORAGE', 'data')],
              [State('datatable-secondfile-upload', 'filename')])
def get_new_data_cinema1(contents, cinema_net_data, filename):
    if contents is None:
        cinema_net_data = pd.read_json(cinema_net_data[0], orient='split')
    else:
        cinema_net_data = parse_contents(contents, filename)
    if filename is not None:
        return [cinema_net_data.to_json(orient='split')], 'loaded'
    else:
        return [cinema_net_data.to_json(orient='split')], ''

### ----- upload CINeMA data file 2 ------ ###
# @app.callback([Output("cinema_net_data2_STORAGE", "data"),
#                Output("file2-list-2", "children")],
#               [Input('datatable-secondfile-upload-2', 'contents'),
#                Input('cinema_net_data2_STORAGE', 'data'),],
#               [State('datatable-secondfile-upload-2', 'filename')])
# def get_new_data_cinema2(contents, cinema_net_data2, filename):
#     if contents is None:
#         cinema_net_data2 = pd.read_json(cinema_net_data2, orient='split')
#     else:
#         cinema_net_data2 = parse_contents(contents, filename)

#     if filename is not None:
#         return cinema_net_data2.to_json(orient='split'), 'loaded'
#     else:
#         return cinema_net_data2.to_json(orient='split'), ''


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
               Input("_outcome_select", "value"),
               Input("funnel_data_STORAGE", "data")]
               )
def Tap_funnelplot(node, outcome_idx, funnel_data):
    return __Tap_funnelplot(node, outcome_idx, funnel_data)

# @app.callback([Output('tab-rank1', 'figure'),
#                Output('tab-rank2', 'figure')],
#               Input('ranking_data_STORAGE', 'data'),
#               State('net_data_STORAGE', 'data'))
# def ranking_plot(ranking_data, net_data):
#     return __ranking_plot(ranking_data, net_data)

############ - Ranking plots  - ###############
@app.callback([Output('tab-rank1', 'figure'),
              Output('tab-rank2', 'figure')],
              Input('ranking_data_STORAGE', 'data'),
              Input('number-outcomes', 'value'),
            #   Input("submit_modal_data", "n_clicks_timestamp"),
              Input("_outcome_select", "value"),
              Input("ranking_outcome_select2", "value"),
              State('net_data_STORAGE', 'data'))
def ranking_plot(ranking_data, out_number, out_idx1, out_idx2,net_data):
    return __ranking_plot(ranking_data, out_number, out_idx1,out_idx2,net_data)

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

# @app.callback([
#             #   Output("modal_data", "is_open"),
#                Output("modal_transitivity", "is_open"),
#                Output("modal_data_checks", "is_open"),
#                Output("TEMP_net_data_STORAGE", "data"),
#                Output("uploaded_datafile_to_disable_cinema", "data"),
#                Output('Rconsole-error-data', 'children'),
#                Output('R-alert-data', 'is_open'),
#                Output('dropdown-intervention', 'options'),
#                ],
#               [
#                 # Input("upload_your_data", "n_clicks_timestamp"),
#                Input('trans_to_results', 'n_clicks_timestamp'),
#                Input("upload_modal_data2", "n_clicks_timestamp"),
#                Input("submit_modal_data", "n_clicks_timestamp"),
#                Input('uploaded_datafile_to_disable_cinema','data')
#                ],
#               [State("radio-format", "value"),
#                State("radio-outcome1", "value"),
#                State("radio-outcome2", "value"),
#                State("modal_transitivity", "is_open"),
#                State("modal_data_checks", "is_open"),
#                State('datatable-upload2', 'contents'),
#                State('datatable-upload2', 'filename'),
#                State({'type': 'dataselectors', 'index': ALL}, 'value'),
#                State("TEMP_net_data_STORAGE", "data")
#                ]
#               )
# def data_modal(
#             #   open_modal_data, 
#              trans_to_results,
#               upload, submit, filename2,
#                search_value_format, search_value_outcome1, search_value_outcome2,modal_transitivity_is_open,
#             #    modal_data_is_open, 
#                modal_data_checks_is_open,
#                contents, filename, dataselectors, TEMP_net_data_STORAGE,
#                ):
#     return __data_modal(
#         # open_modal_data, 
#         trans_to_results,
#         upload, submit, filename2,
#                search_value_format, search_value_outcome1, search_value_outcome2,modal_transitivity_is_open,
#             #    modal_data_is_open, 
#                modal_data_checks_is_open,
#                contents, filename, dataselectors, TEMP_net_data_STORAGE,
#                )



@app.callback([
            #   Output("modal_data", "is_open"),
            #    Output("modal_transitivity", "is_open"),
               Output("modal_data_checks", "is_open"),
               Output("TEMP_raw_data_STORAGE", "data"),
               Output("TEMP_net_data_STORAGE", "data"),
               Output("uploaded_datafile_to_disable_cinema", "data"),
               Output('Rconsole-error-data', 'children'),
               Output('R-alert-data', 'is_open'),
               Output('dropdown-intervention', 'options'),
               ],
              [
            #    Input('trans_to_results', 'n_clicks_timestamp'),
               Input("upload_modal_data2", "n_clicks_timestamp"),
               Input('uploaded_datafile_to_disable_cinema','data'),
               Input("submit_modal_data", "n_clicks_timestamp")
               ],
              [
               State("radio-format", "value"),
               State({'type': 'dataselectors_1', 'index':ALL}, "value"),
               State('number-outcomes', "value"),
               State({'type': 'outcometype', 'index': ALL}, 'value'),
               State({'type': 'effectselectors', 'index': ALL}, 'value'),
               State({'type': 'directionselectors', 'index': ALL}, 'value'),
               State({'type': 'variableselectors', 'index': ALL}, 'value'),
            #    State("modal_transitivity", "is_open"),
               State("modal_data_checks", "is_open"),
               State('datatable-upload2', 'contents'),
               State('datatable-upload2', 'filename'),
               State("TEMP_net_data_STORAGE", "data"),
               State("TEMP_raw_data_STORAGE", "data")
               ]
              )
def data_trans( 
            #  trans_to_results,
              upload, filename2,
              submit,
               search_value_format, overall_variables, number_outcomes, outcome_type,
               effectselectors, directionselectors, variableselectors,
               modal_data_checks_is_open,
               contents, filename, 
               TEMP_net_data_STORAGE,
               TEMP_raw_data_STORAGE
               ):
    return __data_trans( 
        #  trans_to_results,
              upload,  filename2,
              submit,
               search_value_format, overall_variables, number_outcomes,outcome_type,
               effectselectors, directionselectors, variableselectors,
               modal_data_checks_is_open,
               contents, filename, 
               TEMP_net_data_STORAGE,
               TEMP_raw_data_STORAGE
               )



@app.callback([Output("select_effect_modifier", "style"),
              Output("arrow_step3", "style"),
              Output("effect_modifier_select", "style")
              ],
              Input({'type': 'variableselectors', 'index': ALL}, 'value'),
              )
def modal_ENABLE_UPLOAD_button(variableselectors):
    if len(variableselectors):
        if all(variableselectors):
            return {"display": 'grid', 'justify-content': 'center'}, {'display':'grid', 'justify-content': 'center'},{'display':'grid', 'justify-content': 'center'}
        else:
            return {"display": 'none'}, {'display':'none', 'justify-content': 'center'}, {'display':'none', 'justify-content': 'center'}
    else:
        return {"display": 'none'}, {'display':'none', 'justify-content': 'center'}, {'display':'none', 'justify-content': 'center'}







# @app.callback([Output("upload_modal_data2", "disabled"),
#               Output("run_button", "style"),],
#               Input({'type': 'dataselectors', 'index': ALL}, 'value'),
#               )
# def modal_ENABLE_UPLOAD_button(dataselectors):
#     if len(dataselectors):
#         return not all(dataselectors),  {'display':'grid', 'justify-content': 'center'}
#     else:
#         return True,  {'display':'none', 'justify-content': 'center'}


    # return not all(dataselectors) if len(dataselectors) else True

@app.callback([Output("upload_modal_data2", "disabled"),
               Output("run_button", "style"),
               Output("arrow_step4", "style")],
               [Input('effect_modifier_checkbox', 'value'),
                Input('no_effect_modifier', 'value')]
)
def modal_ENABLE_UPLOAD_button(effect_mod, no_effect_mod):
    if effect_mod or no_effect_mod:
        return False, {'display':'grid', 'justify-content': 'center'}, {'display':'grid', 'justify-content': 'center'}
    else:
        return True, {'display':'none', 'justify-content': 'center'}, {'display':'none', 'justify-content': 'center'}






from assets.storage import DEFAULT_DATA
OUTPUTS_STORAGE_IDS = list(DEFAULT_DATA.keys())[:-1]
# @app.callback([Output(id, 'data') for id in OUTPUTS_STORAGE_IDS] + [Output('token-not-found-alert','children')],
#               [Input("submit_modal_data", "n_clicks"),
#                Input('reset_project','n_clicks'),
#                Input("username-token-upload", "data"),
#                Input("button-token", "n_clicks"),
#                Input("input-token-load", "value"),
#                Input("load-project", "n_clicks"),
#                Input("datatable-filename-upload", "data"),
#                ],
#               [State('TEMP_'+id, 'data') for id in OUTPUTS_STORAGE_IDS],
#               prevent_initial_call=True
#               )
# def modal_SUBMIT_button(submit, reset_btn,
#                         token_data, token_btn,
#                         token_data_load, token_load_btn,
#                         filename,
#                         TEMP_net_data_STORAGE,
#                         TEMP_net_data_out2_STORAGE,
#                         TEMP_consistency_data_STORAGE,
#                         TEMP_user_elements_STORAGE,
#                         TEMP_user_elements_out2_STORAGE,
#                         TEMP_forest_data_STORAGE,
#                         TEMP_forest_data_out2_STORAGE,
#                         TEMP_forest_data_prws_STORAGE,
#                         TEMP_forest_data_prws_out2_STORAGE,
#                         TEMP_ranking_data_STORAGE,
#                         TEMP_funnel_data_STORAGE,
#                         TEMP_funnel_data_out2_STORAGE,
#                         TEMP_league_table_data_STORAGE,
#                         TEMP_net_split_data_STORAGE,
#                         TEMP_net_split_data_out2_STORAGE,
#                         TEMP_net_split_ALL_data_STORAGE,
#                         TEMP_net_split_ALL_data_out2_STORAGE,
#                         ):
#     return __modal_SUBMIT_button(submit, reset_btn,
#                         token_data, token_btn,
#                         token_data_load, token_load_btn,
#                         filename,
#                         TEMP_net_data_STORAGE,
#                         TEMP_net_data_out2_STORAGE,
#                         TEMP_consistency_data_STORAGE,
#                         TEMP_user_elements_STORAGE,
#                         TEMP_user_elements_out2_STORAGE,
#                         TEMP_forest_data_STORAGE,
#                         TEMP_forest_data_out2_STORAGE,
#                         TEMP_forest_data_prws_STORAGE,
#                         TEMP_forest_data_prws_out2_STORAGE,
#                         TEMP_ranking_data_STORAGE,
#                         TEMP_funnel_data_STORAGE,
#                         TEMP_funnel_data_out2_STORAGE,
#                         TEMP_league_table_data_STORAGE,
#                         TEMP_net_split_data_STORAGE,
#                         TEMP_net_split_data_out2_STORAGE,
#                         TEMP_net_split_ALL_data_STORAGE,
#                         TEMP_net_split_ALL_data_out2_STORAGE,
#                         )

@app.callback([Output(id, 'data') for id in OUTPUTS_STORAGE_IDS] + [Output('token-not-found-alert','children'),
                                                                    Output("output_username", "children"),
                                                                    Output("output_token", "children"),
                                                                    Output('button-token','disabled')],
              [Input("submit_modal_data", "n_clicks"),
               Input('reset_project','n_clicks'),
            #    Input("username-token-upload", "data"),
               Input("button-token", "n_clicks"),
               Input("input-token-load", "value"),
               Input("load-project", "n_clicks"),
               Input("datatable-filename-upload", "data"),
               ],
              [ State("input-username", "value")]+[State('TEMP_'+id, 'data') for id in OUTPUTS_STORAGE_IDS]+[State('number-outcomes', 'value')],
              prevent_initial_call=True
              )
def modal_SUBMIT_button(submit, reset_btn,
                        # token_data, 
                        token_btn,
                        token_data_load, token_load_btn,
                        filename,
                        input_token,
                        TEMP_raw_data_STORAGE,
                        TEMP_net_data_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        # TEMP_user_elements_STORAGE,
                        TEMP_forest_data_STORAGE,
                        TEMP_forest_data_prws_STORAGE,
                        TEMP_ranking_data_STORAGE,
                        TEMP_funnel_data_STORAGE,
                        TEMP_league_table_data_STORAGE,
                        TEMP_net_split_data_STORAGE,
                        TEMP_net_split_ALL_data_STORAGE,
                        num_out
                        ):
    return __modal_SUBMIT_button_new(submit, reset_btn,
                        # token_data, 
                        token_btn,
                        token_data_load, token_load_btn,
                        filename,
                        input_token,
                        TEMP_raw_data_STORAGE,
                        TEMP_net_data_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        # TEMP_user_elements_STORAGE,
                        TEMP_forest_data_STORAGE,
                        TEMP_forest_data_prws_STORAGE,
                        TEMP_ranking_data_STORAGE,
                        TEMP_funnel_data_STORAGE,
                        TEMP_league_table_data_STORAGE,
                        TEMP_net_split_data_STORAGE,
                        TEMP_net_split_ALL_data_STORAGE,
                        num_out
                        )







@app.callback(Output('number-outcomes', 'value'),
               Input("input-token-load", "value"),
               Input("load-project", "n_clicks"),
              [State('number-outcomes', 'value')],
              prevent_initial_call=True
              )
def modal_SUBMIT_button(
                        input_load,
                        load_trigger,
                        num_out
                        ):
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    load_btn_triggered = False
    if 'load-project.n_clicks' in triggered: load_btn_triggered = True
    if load_btn_triggered:
        usr_token_load_ = input_load
        # parent_dir_load = "USR_DATASETS/"
        # directory_load = f"{usr_token_load_}"
        # path = os.path.join(parent_dir_load, directory_load)
        token_outnum = usr_token_load_.split('_')
        out_num = int(token_outnum[1])
        return out_num
    return num_out




# @app.callback(Output("dropdown-effectmod", "options"),
#               Input("net_data_STORAGE", "data"),
#               )
# def update_dropdown_effect_mod(new_data):
#     new_data = pd.read_json(new_data, orient='split')
#     OPTIONS_VAR = [{'label': '{}'.format(col), 'value': col}
#                    for col in new_data.columns] #new_data.select_dtypes(['number']).columns
#     # options_intervention = [{'label': '{}'.format(treat), 'value': treat}
#     #                for treat in new_data.columns]
#     return OPTIONS_VAR


@app.callback(Output("dropdown-effectmod", "options"),
              [Input("effect_modifier_checkbox", "value"),
              Input("no_effect_modifier", "value")],
              State("dropdown-effectmod", "options")
              )
def update_dropdown_effect_mod(effect_modifier, no_effect_modifier, origin_effctm):
    if effect_modifier:
        options_modifier = [{'label': '{}'.format(modifier), 'value': modifier} 
                                for modifier in effect_modifier]
        return options_modifier
    if no_effect_modifier:

        return []
    return origin_effctm
    

##################bugs
@app.callback([Output("para-check-data", "children"),
               Output('para-check-data', 'data')],
              Input("modal_data_checks", "is_open"),
              [State('number-outcomes', "value"),
              State("TEMP_net_data_STORAGE", "data")],
              )
def modal_submit_checks_DATACHECKS(modal_data_checks_is_open, num_outcomes,TEMP_net_data_STORAGE):
    return __modal_submit_checks_DATACHECKS(modal_data_checks_is_open, num_outcomes,TEMP_net_data_STORAGE)

# @app.callback([Output('R-alert-nma', 'is_open'),
#                Output('Rconsole-error-nma', 'children'),
#                Output("para-anls-data", "children"),
#                Output('para-anls-data', 'data'),
#                Output("TEMP_forest_data_STORAGE", "data"),
#                Output("TEMP_forest_data_out2_STORAGE", "data"),
#                Output("TEMP_user_elements_STORAGE", "data"),
#                Output("TEMP_user_elements_out2_STORAGE", 'data')],
#                Input("modal_data_checks", "is_open"),
#                State("TEMP_net_data_STORAGE", "data"),
#                State("TEMP_forest_data_STORAGE", "data"),
#                State("TEMP_forest_data_out2_STORAGE", "data"),
#               )
# def modal_submit_checks_NMA(modal_data_checks_is_open, TEMP_net_data_STORAGE,
#                             TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE):
#     return __modal_submit_checks_NMA(modal_data_checks_is_open, TEMP_net_data_STORAGE,
#                             TEMP_forest_data_STORAGE, TEMP_forest_data_out2_STORAGE)

@app.callback([Output('R-alert-nma', 'is_open'),
               Output('Rconsole-error-nma', 'children'),
               Output("para-anls-data", "children"),
               Output('para-anls-data', 'data'),
               Output("TEMP_forest_data_STORAGE", "data"),
            #    Output("TEMP_user_elements_STORAGE", "data")
               ],
               Input("modal_data_checks", "is_open"),
               [State('number-outcomes', "value"),
               State("TEMP_net_data_STORAGE", "data"),
               State("TEMP_forest_data_STORAGE", "data")]
              )
def modal_submit_checks_NMA_new(modal_data_checks_is_open,num_outcome, TEMP_net_data_STORAGE,
                            TEMP_forest_data_STORAGE):
    return __modal_submit_checks_NMA_new(modal_data_checks_is_open, num_outcome,TEMP_net_data_STORAGE,
                            TEMP_forest_data_STORAGE)



# @app.callback([Output('R-alert-pair', 'is_open'),
#                Output('Rconsole-error-pw', 'children'),
#                Output("para-pairwise-data", "children"),
#                Output('para-pairwise-data', 'data'),
#                Output("TEMP_forest_data_prws_STORAGE", "data"),
#                Output("TEMP_forest_data_prws_out2_STORAGE", "data")],
#                Input('TEMP_forest_data_STORAGE', 'modified_timestamp'),
#                State("modal_data_checks", "is_open"),
#                State("TEMP_net_data_STORAGE", "data"),
#                State("TEMP_forest_data_prws_STORAGE", "data"),
#                State("TEMP_forest_data_prws_out2_STORAGE", "data"),
#               )
# def modal_submit_checks_PAIRWISE(nma_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2):
#     return __modal_submit_checks_PAIRWISE(nma_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE, TEMP_forest_data_prws_out2)



@app.callback([Output('R-alert-pair', 'is_open'),
               Output('Rconsole-error-pw', 'children'),
               Output("para-pairwise-data", "children"),
               Output('para-pairwise-data', 'data'),
               Output("TEMP_forest_data_prws_STORAGE", "data")],
               Input('TEMP_forest_data_STORAGE', 'modified_timestamp'),
               State('number-outcomes', "value"),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State("TEMP_forest_data_prws_STORAGE", "data")
              )
def modal_submit_checks_PAIRWISE(nma_data_ts, num_outcome, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE):
    return __modal_submit_checks_PAIRWISE_new(nma_data_ts, num_outcome, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE)


# @app.callback([Output('R-alert-league', 'is_open'),
#                Output('Rconsole-error-league', 'children'),
#                Output("para-LT-data", "children"),
#                Output('para-LT-data', 'data'),
#                Output('TEMP_league_table_data_STORAGE', 'data'),
#                Output('TEMP_ranking_data_STORAGE', 'data'),
#                Output('TEMP_consistency_data_STORAGE', 'data'),
#                Output('TEMP_net_split_data_STORAGE', 'data'),
#                Output('TEMP_net_split_data_out2_STORAGE', 'data'),
#                Output('TEMP_net_split_ALL_data_STORAGE', 'data'),
#                Output('TEMP_net_split_ALL_data_out2_STORAGE', 'data')
#                ],
#                Input('TEMP_forest_data_prws_STORAGE', 'modified_timestamp'),
#                State("modal_data_checks", "is_open"),
#                State("TEMP_net_data_STORAGE", "data"),
#                State('TEMP_league_table_data_STORAGE', 'data'),
#                State('TEMP_ranking_data_STORAGE', 'data'),
#                State('TEMP_consistency_data_STORAGE', 'data'),
#                State('TEMP_net_split_data_STORAGE', 'data'),
#                State('TEMP_net_split_data_out2_STORAGE', 'data'),
#                State('TEMP_net_split_ALL_data_STORAGE', 'data'),
#                State('TEMP_net_split_ALL_data_out2_STORAGE', 'data'),
#                State({'type': 'dataselectors', 'index': ALL}, 'value')
#               )
# def modal_submit_checks_LT(pw_data_ts, modal_data_checks_is_open,
#                            TEMP_net_data_STORAGE, LEAGUETABLE_data,
#                            ranking_data, consistency_data, net_split_data, net_split_data2,
#                            netsplit_all, netsplit_all2, dataselectors):
#     return  __modal_submit_checks_LT(pw_data_ts, modal_data_checks_is_open,
#                            TEMP_net_data_STORAGE, LEAGUETABLE_data,
#                            ranking_data, consistency_data, net_split_data, net_split_data2,
#                            netsplit_all, netsplit_all2, dataselectors)



@app.callback([Output('R-alert-league', 'is_open'),
               Output('Rconsole-error-league', 'children'),
               Output("para-LT-data", "children"),
               Output('para-LT-data', 'data'),
               Output('TEMP_league_table_data_STORAGE', 'data'),
               Output('TEMP_ranking_data_STORAGE', 'data'),
               Output('TEMP_consistency_data_STORAGE', 'data'),
               Output('TEMP_net_split_data_STORAGE', 'data'),
               Output('TEMP_net_split_ALL_data_STORAGE', 'data')
               ],
               Input('TEMP_forest_data_prws_STORAGE', 'modified_timestamp'),
               State('number-outcomes', "value"),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State('TEMP_league_table_data_STORAGE', 'data'),
               State('TEMP_ranking_data_STORAGE', 'data'),
               State('TEMP_consistency_data_STORAGE', 'data'),
               State('TEMP_net_split_data_STORAGE', 'data'),
               State('TEMP_net_split_ALL_data_STORAGE', 'data'),
            #    State({'type': 'dataselectors', 'index': ALL}, 'value')
              )
def modal_submit_checks_LT(pw_data_ts, num_outcome,modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data,
                           netsplit_all):
    return  __modal_submit_checks_LT_new(pw_data_ts,num_outcome, modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data,
                           netsplit_all)


# @app.callback([Output('R-alert-funnel', 'is_open'),
#                Output('Rconsole-error-funnel', 'children'),
#                Output("para-FA-data", "children"),
#                Output('para-FA-data', 'data'),
#                Output('TEMP_funnel_data_STORAGE', 'data'),
#                Output('TEMP_funnel_data_out2_STORAGE', 'data')],
#                Input("TEMP_league_table_data_STORAGE", "modified_timestamp"),
#                State("modal_data_checks", "is_open"),
#                State("TEMP_net_data_STORAGE", "data"),
#                State('TEMP_funnel_data_STORAGE', 'data'),
#                State('TEMP_funnel_data_out2_STORAGE', 'data')

#               )
# def modal_submit_checks_FUNNEL(lt_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data, FUNNEL_data2):
#     return __modal_submit_checks_FUNNEL(lt_data_ts, modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data, FUNNEL_data2)

@app.callback([Output('R-alert-funnel', 'is_open'),
               Output('Rconsole-error-funnel', 'children'),
               Output("para-FA-data", "children"),
               Output('para-FA-data', 'data'),
               Output('TEMP_funnel_data_STORAGE', 'data')],
               Input("TEMP_league_table_data_STORAGE", "modified_timestamp"),
               State('number-outcomes', "value"),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State('TEMP_funnel_data_STORAGE', 'data')

              )
def modal_submit_checks_FUNNEL(lt_data_ts, num_outcome,modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data):
    return __modal_submit_checks_FUNNEL_new(lt_data_ts,num_outcome, modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data)





@app.callback(Output("submit_modal_data", "disabled"),
              [Input(id, 'data') for id in ['para-check-data','para-anls-data','para-pairwise-data',
                                            'para-LT-data', 'para-FA-data']])
def modal_submit_button(para_check_data_DATA, para_anls_data_DATA, para_prw_data_DATA, para_LT_data_DATA, para_FA_data_DATA):
    return not (para_check_data_DATA==para_anls_data_DATA==para_prw_data_DATA==para_LT_data_DATA==para_FA_data_DATA=='__Para_Done__')



### -------------------------------------------- EXPAND CALLBACKS ----------------------------------------------- ###

# ----- data expand modal -----#
# @app.callback(
#     Output("modal_data_table", "is_open"),
#     [Input("data-expand", "n_clicks"),
#      Input("close-data-expanded", "n_clicks")],
#     [State("modal_data_table", "is_open")],
# )
# def toggle_modal(open, close, is_open):
#     if open or close:
#         return not is_open
#     return is_open

@app.callback(
    Output("one-half-1", "style"),
    Output("one-half-2", "style"),
    Output('data-expand', 'style'),
    Output('data-zoomout', 'style'),
    Output('data-expand1', 'style'),
    Output('data-zoomout1', 'style'),
    Output('network-expand', 'style'),
    Output('network-zoomout', 'style'),
    Output("one-half-3", "style"),
    Output("cytoscape", "style"),
    Input("data-expand", "n_clicks_timestamp"),
    Input("data-zoomout", "n_clicks_timestamp"),
    Input("data-expand1", "n_clicks_timestamp"),
    Input("data-zoomout1", "n_clicks_timestamp"),
    Input("network-expand", "n_clicks_timestamp"),
    Input("network-zoomout", "n_clicks_timestamp"),

)
def toggle_modal(expand, zoomout, expand1, zoomout1, expand_plot, zoomout_plot):
    style_display = {'display': 'block'}
    style_no_display = {'display': 'none'}
    style_expand_width = {'width': '93.4%', 'margin-left': '3.3%'}
    style_width = {'width': '50.6%'}
    style = {"display": "inline-block"}
    style_no = {"display": "none"}
    style_height = {'display': 'block','height': '100%'}
    style_neplot={
            'height': '70vh', 'width': '100%', 
                'margin-top': '10px',
                'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                'padding-left': '-10px', 'border-right': '3px solid rgb(165 74 97)'}
    style_neplot_expand={
            'height': '70vh', 'width': '100%', 
                'margin-top': '10px',
                'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                'padding-left': '-10px', 'border-right': '3px solid rgb(165 74 97)'}
    style_neplot_down={
        'height': '140vh', 'width': '100%', 
            'margin-top': '10px',
            'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
            'padding-left': '-10px', 'border-right': '3px solid rgb(165 74 97)'}

    if not ctx.triggered_id:
        return style_display, style_width, style, style_no, style_no, style, style, style_no,style_expand_width,style_neplot

    triggered_button_id = ctx.triggered_id.split(".")[0]
    if triggered_button_id =='network-expand':
        return style_expand_width, style_no_display, style, style_no, style_no, style, style_no, style, style_expand_width,style_neplot_expand
    
    if triggered_button_id =='network-zoomout':
        return style_display, style_width, style, style_no, style_no, style, style, style_no, style_expand_width,style_neplot
    
    if triggered_button_id =='data-expand':
        return style_no_display, style_expand_width, style_no, style, style_no, style_no, style, style_no,style_expand_width,style_neplot
    
    elif triggered_button_id =='data-zoomout':
        return style_display, style_width, style, style_no, style_no, style, style, style_no,style_expand_width,style_neplot
    
    elif triggered_button_id =='data-zoomout1':
        return style_height, style_width, style, style_no, style, style_no, style, style_no,style_width, style_neplot_down 
    elif triggered_button_id =='data-expand1':
        return style_display, style_width, style, style_no, style_no, style, style, style_no,style_expand_width, style_neplot




# ----- league expand modal -----#
# @app.callback(
#     Output("modal_league_table", "is_open"),
#     [Input("league-expand", "n_clicks"),
#      Input("close-league-expanded", "n_clicks")],
#     [State("modal_league_table", "is_open")],
# )
# def toggle_modal(open, close, is_open):
#     if open or close:
#         return not is_open
#     return is_open

# ----- network expand modal -----# #TODO: this needs fixing: eg. node coloring and options not working in expand mode
# @app.callback(
#     Output("modal_network", "is_open"),
#     [Input("network-expand", "n_clicks"),
#      Input("close-network-expanded", "n_clicks")],
#     [State("modal_network", "is_open")],
# )
# def toggle_modal(open, close, is_open):
#     if open or close:
#         return not is_open
#     return is_open


@app.callback(
    Output("modal_info", "is_open"),
    [Input("info_icon", "n_clicks"),
     Input("close_modal_info", "n_clicks")],
    [State("modal_info", "is_open")],
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
               Input('consistency_outcome_select','value'),
               State("net_split_ALL_data_STORAGE", "data")],
               prevent_initial_call=True)
def generate_csv_consistency(n_nlicks, outcome_idx, consistencydata_all):
    return __generate_csv_consistency(n_nlicks, outcome_idx, consistencydata_all)

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
# @app.callback([Output("forestswitchlabel_outcome1", "style"),
#                Output("forestswitchlabel_outcome2", "style")],
#               [Input("toggle_forest_outcome", "value")])
# def color_funnel_toggle(toggle_value):
#     style1 = {'color': 'gray' if toggle_value else '#5a87c4',
#               'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
#     style2 = {'color': '#5a87c4' if toggle_value else 'gray',
#               'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
#     return style1, style2

### -------------- toggle switch forest pairwise outcome1/outcome2 ---------------- ###
# @app.callback([Output("forest_pair_switchlabel_outcome1", "style"),
#                Output("forest_pair_switchlabel_outcome2", "style")],
#               [Input("toggle_forest_pair_outcome", "value")])
# def color_funnel_toggle(toggle_value):
#     style1 = {'color': 'gray' if toggle_value else '#5a87c4',
#               'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
#     style2 = {'color': '#5a87c4' if toggle_value else 'gray',
#               'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
#     return style1, style2


### -------------- toggle switch league table ---------------- ###
@app.callback([Output("cinemaswitchlabel1", "style"),
               Output("cinemaswitchlabel2", "style")],
              [Input("rob_vs_cinema", "value")])
def color_leaguetable_toggle(toggle_value):
    style1 = {'color': '#808484' if toggle_value else '#5a87c4', 'font-size': '12px',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '10px'}
    style2 = {'color': '#5a87c4' if toggle_value else '#808484', 'font-size': '12px',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '0px', }
    return style1, style2

### -------------- toggle switch funnel plot ---------------- ###
@app.callback([Output("funnelswitchlabel1", "style"),
               Output("funnelswitchlabel2", "style")],
              [Input("toggle_funnel_direction", "value")])
def color_funnel_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#5a87c4',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#5a87c4' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

### -------------- toggle switch consistency ---------------- ###
@app.callback([Output("consistencyswitchlabel1", "style"),
               Output("consistencyswitchlabel2", "style")],
              [Input("toggle_consistency_direction", "value")])
def color_funnel_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#5a87c4',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#5a87c4' if toggle_value else 'gray',
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
# @app.callback([Output('toggle_funnel_direction', 'disabled'),
#               Output('toggle_forest_outcome', 'disabled'),
#               Output('toggle_forest_pair_outcome', 'disabled'),
#               Output('toggle_consistency_direction', 'disabled'),
#               Output('datatable-secondfile-upload-2','disabled')
#               ],
#               Input('ranking_data_STORAGE','data')
#               )
# def disable_out2_toggle(ranking_data):
#     df_ranking = pd.read_json(ranking_data, orient='split')
#     df_ranking = df_ranking.loc[:, ~df_ranking.columns.str.contains('^Unnamed')]  # Remove unnamed columns
#     if "pscore2" not in df_ranking.columns:
#         return True, True, True, True, True
#     else: return False, False, False, False, False


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
# @app.callback(
#     [Output("output_username", "children"),
#      Output("output_token", "children"),
#      Output('button-token','disabled'),
#      Output("username-token-upload", "data"),
#      ],
#      State("input-username", "value"),
#      Input("button-token", "n_clicks"),
#      Input("number-outcomes", "value"),
#      )
# def save_project_user_token(input, n_clicks, num_out):
#     token_btn_triggered = False
#     triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
#     num_out = int(num_out) if num_out else 1
#     if 'button-token.n_clicks' in triggered: token_btn_triggered = True

#     if input and token_btn_triggered:
#             if len(input) >= 6:
#                 password = secrets.token_urlsafe(8)
#                 token = input + "-" + password + '_'+ str(num_out)
#                 token_data = {'token': token}
#                 if n_clicks > 0 :
#                     return html.P(u"\u2713" + " Successfully generated user",style={"color": "#B1D27B", "font-size":"11px","font-weight": "530"}), f'{token}', True, token_data
#             else:
#                 return html.P(u"\u274C" + " Username must be at least 6 characters", style={"color": "red"}), None, False, None

#     else:
#         return None, None, False, None

###############overall information##################

@app.callback([Output('numstudies', 'children'),
              Output('numtreat', 'children'),
              Output('numcompar', 'children'),
              Output('numcom_without', 'children')],
              Input('net_data_STORAGE', 'data'))
def infor_overall(data):
    net_data = pd.read_json(data[0], orient='split').round(3)
    n_studies = len(net_data.studlab.unique())
    num_study = f"Number of studies: {n_studies}"

    combined_treats = pd.concat([net_data['treat1'], net_data['treat2']])
    n_treat= combined_treats.nunique()
    num_treat = f"Number of treatments: {n_treat}"

    unique_combinations = list(itertools.combinations(combined_treats.unique(), 2))
    num_unique_combinations = len(unique_combinations)

    net_data['treat_combine'] = list(zip(net_data['treat1'], net_data['treat2']))
    unique_combinations = set(net_data['treat_combine'])
    n_com = len(unique_combinations)

    num_com = f"Number of comparisons with direct evidence: {n_com}"

    n_com_without = num_unique_combinations - n_com
    num_com_without = f"Number of comparisons without direct evidence: {n_com_without}"

    return [num_study],[num_treat],[num_com],[num_com_without]

###########################results selection###########################################
@app.callback([
              Output('data_tab', 'style'),
              Output('trans_tab', 'style'),
              Output('forest_tab', 'style'),
              Output('tab2', 'style'),
              Output('league_tab', 'style'),
              Output('consis_tab', 'style'),
              Output('funnel_tab', 'style'),
              Output('ranking_tab', 'style'),
              Output('results_tabs', 'value'),
              Output('results_tabs2', 'value')
              ],
              Input('result_selected', 'value'))
def results_display(selected):
    style_display = {'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'}
    style_no_display = {'color':'grey','display': 'none', 'justify-content':'center', 'align-items':'center'}

    if selected == 0:
        return [style_display] * 2 + [style_no_display] * 6 +['data_tab']+['trans_tab']
    if selected == 1:
        return [style_no_display]*2 + [style_display]*2 + [style_no_display]*4 +['forest_tab']+['tab2']
    if selected == 2:
        return [style_no_display]*4 + [style_display] + [style_no_display]*3+['league_tab']+['']
    if selected == 3:
        return [style_no_display]*5 + [style_display]*2 + [style_no_display]+['consis_tab']+['funnel_tab']
    if selected == 4:
        return [style_no_display]*7 + [style_display]+['ranking_tab']+['']


   

####################################################################
####################################################################
############################ SKT TOOL ##############################

@app.callback(
    [Output("quickstart-grid", "rowData"),
    Output("quickstart-grid", "style")],
    [Input("ref_selected", "value"),
    Input("base_risk_input", "value")],
)

def selected(value, value_risk):
    # pw_data = pd.read_csv('db/forest_data_pairwise.csv')
    # slctd_comps = []
    # slctd_compsinv = []

    dfc = df.copy()
    round(dfc,2)
    dfc = dfc[dfc['Reference'] == value]
    dfc = dfc.sort_values(by='RR')
    dfc.reset_index(drop=True, inplace=True)  
    dfc['Reference'] = [f'{value} \n {value_risk} per 1000'] + [''] * (dfc.shape[0] - 1)
    value_risk = int(value_risk)
    for i in range(dfc.shape[0]):
        risk_treat = value_risk*dfc['RR'].loc[i]
        risk_treat =int(risk_treat)
        abrisk = risk_treat-value_risk
        dfc.loc[i,'Treatment'] = f"{dfc.loc [i,'Treatment']}" + f"\n{risk_treat} per 1000"
        dfc.loc[i,'RR'] = str(dfc.loc[i,'RR'])+ '\n(' + str(dfc.loc[i,'CI_lower']) + ', ' + str(dfc.loc[i,'CI_upper']) + ')'
        dfc.loc[i,'RR'] = f"{dfc.loc [i,'RR']}" + (f"\n{abrisk} more per 1000" if abrisk > 0 else f"\n{abs(abrisk)} less per 1000")
        dfc.loc[i,'direct'] = f"{dfc.loc [i,'direct']}" + f"\n({dfc.loc[i,'direct_low']}, {dfc.loc[i,'direct_up']})" if pd.notna(dfc['direct'].iloc[i]) else ""
        dfc.loc[i,'indirect'] = f"{dfc.loc[i,'indirect']}" + f"\n({dfc.loc[i,'indirect_low']}, {dfc.loc[i,'indirect_up']})" if pd.notna(dfc['indirect'].iloc[i]) else ""
    
    dfc = pd.DataFrame(dfc)
    n_row = dfc.shape[0]
    style = { "width": "100%",'height':f'{48 + 95 * n_row}px'}
    return dfc.to_dict("records"), style


@app.callback(
    Output("modal_forest", "is_open"), 
    Input("quickstart-grid", "cellClicked"),
    Input("close_forest", "n_clicks"),
)

def display_forestplot(cell, _):
    if ctx.triggered_id == "close_forest":
        return False
    if cell is not None and cell['value'] is not None and 'colId' in cell and cell['colId'] == "direct":
        return True
    return no_update


@app.callback(
    Output("skt_modal_copareinfo", "is_open"), 
    Input("quickstart-grid", "cellClicked"),
    Input("close_compare", "n_clicks"),
)

def display_forestplot(cell, _):
    if ctx.triggered_id == "close_compare":
        return False
    if (cell is not None and 'colId' in cell and cell['colId'] == "Treatment"):
        return True
    return no_update



@app.callback(
   [ Output('forest-fig-pairwise', 'figure'),
    Output('forest-fig-pairwise', 'style')],
    [Input("quickstart-grid", "cellClicked"),
    Input("ref_selected", "value"),
    Input("quickstart-grid", "selectedRows"),
    Input('forest-fig-pairwise', 'style')]
)

def show_forest_plot(cell, reference, row_select, style_pair):
    return __show_forest_plot(cell, reference, row_select, style_pair)




@app.callback(
    [Output('grid_type', 'children'),
     Output('treatment_toast', 'children')],
    Input('toggle_grid_select','value')
)
def display_grid(value):
    if value:
        return [grid2],[checklist, button_clear]
    return [grid, model_skt_stand1, model_skt_stand2],[radio_treattment]


@app.callback(
    Output('checklist_treat','value'),
    Input('clear-val','n_clicks'),
    State('checklist_treat','value')
)
def clear_treat(click, orig_value):
    if click:
        value = df_league.columns[1:].values
    else:
        value = orig_value
    return value



@app.callback(
    [Output('grid2', 'rowData'),
    Output('grid2', 'columnDefs'),
    Output("grid2", "style")],
    [Input('checklist_treat','value'),
    Input("base_risk_input", "value")]
)
def display_only_selected(values, absolute_risk):
    values = sorted(values)
    absolute_risk = int(absolute_risk)
    values_t = ['Treatment'] + values
    df_league_c = df_league.copy()
    df_league_c = df_league_c[df_league_c['Treatment'].isin (values)]
    df_league_c =df_league_c[values_t]
    # df_league_c =df_league_c.sort_index(axis=1)
    n_row2 = len(values)
    column_update = df_league_c.columns.tolist()

    for idx, column in enumerate(column_update):
        if idx < 2:
            pass   
        for row_idx in range(idx-1):
            treat1 = column
            treat2 = df_league_c['Treatment'].iloc[row_idx]
            absolute_info = df[(df['Treatment'] == treat2) & (df['Reference'] == treat1)]
            absolute_risk = int(absolute_risk)
            absolute = int(absolute_info['RR'].iloc[0]*absolute_risk)-20
            text_ab1 = f"{treat2} VS. {treat1} \n{absolute} more per 1000" if absolute > 0 else f"{treat2} VS. {treat1} \n{abs(absolute)} less per 1000"
            text_ab2 = "\n Randomize control studies: 3\n Total participants in arm: xxx \n Mean age: xxx \nMean male percentage: XXX"
            text_ab = text_ab1 + text_ab2
            df_league_c.iloc[row_idx,idx] = text_ab
            

    column1 = ['ADA','ADA', 'BIME']
    column2 = ['ETA', 'FUM', 'GUSEL']

    column_low1 = ['PBO','PBO', 'SECU']
    column_low2 = ['RISAN', 'IFX', 'IFX']

    # # # Number of pairs to select (in this case, 6 pairs)
    
    treatments_list = df_league_c['Treatment'].tolist()


    columnDefs=[
    {"field": "Treatment", 
    "headerName": "Treatment",
     "tooltipField": 'ticker',
     "tooltipComponentParams": { "color": '#d8f0d3' },
    "sortable": False,
    "filter": True, 
    'cellStyle': {'font-weight':'bold',
                    'background-color':'#B85042','color':'white','font-size':'12px', **default_style}}  
    ]+[{"field": i,
        "cellRenderer": "DCC_GraphClickData",
        "maxWidth": 500,
        "minWidth": 300,
        "tooltipField": 'ticker',
        "tooltipComponentParams": { "color": '#d8f0d3' },
        'cellStyle': {"styleConditions":[{"condition": f"params.value === '{i}'", 
                                    "style": {"backgroundColor": "antiquewhite", **default_style}},
                                    {
                                    "condition": f"{column1}.includes('{i}') &&" 
                                    f"{[treatments_list.index(column2[index]) if (i in column1) and (column2[index] in treatments_list) else -1 for index, item in enumerate(column1)]}.includes(params.rowIndex)",
                                    "style": {"backgroundColor": "rgb(0, 128, 0, 0.5)", **default_style}
                                    },

                                    {
                                    "condition": f"{column2}.includes('{i}') &&" 
                                    f"{[treatments_list.index(column1[index]) if (i in column2) and (column1[index] in treatments_list) else -1 for index, item in enumerate(column2)]}.includes(params.rowIndex)",
                                    "style": {"backgroundColor": "rgb(0, 128, 0, 0.5)", **default_style}
                                    },

                                    {
                                    "condition": f"{column_low1}.includes('{i}') &&" 
                                    f"{[treatments_list.index(column_low2[index]) if (i in column_low1) and (column_low2[index] in treatments_list) else -1 for index, item in enumerate(column_low1)]}.includes(params.rowIndex)",
                                    "style": {"backgroundColor": "rgb(184, 80, 66, 0.5)", **default_style}
                                    },

                                    {
                                    "condition": f"{column_low2}.includes('{i}') &&" 
                                    f"{[treatments_list.index(column_low1[index]) if (i in column_low2) and (column_low1[index] in treatments_list) else -1 for index, item in enumerate(column_low2)]}.includes(params.rowIndex)",
                                    "style": {"backgroundColor": "rgb(184, 80, 66, 0.5)", **default_style}
                                    },

                                    {"condition": f"params.value !== '{i}'", 
                                    "style": {**default_style}},
                                    ]},}  for i in values]
    style={'width': '1200px','height': f'{48 + 163 * n_row2}px'}


    return df_league_c.to_dict("records"), columnDefs, style


@app.callback(
    Output('pass_model','is_open'),
    Output('skt_all','style'),
    Input('password_ok','n_clicks'),
    Input('password','value'),
    State('pass_model','is_open'),
    State('skt_all','style'),
)
def clear_treat(click, password, pass_model, skt_style):
    if password =='777' and click:
        skt_style = {'diaplay': 'block'}
        return not pass_model, skt_style
    else:
        return pass_model, skt_style








####################################################################
####################################################################
############################ MAIN ##################################
####################################################################
####################################################################


if __name__ == '__main__':
    app._favicon = ("assets/favicon.ico")
    # app.title = 'NMAstudio' #TODO: title works fine locally, does not on Heroku
    # context = generate_ssl_perm_and_key(cert_name='cert.pem', key_name='key.pem')
    # app.run_server(debug=False, ssl_context=context)
    app.run_server(port=8080, debug=True) #change port or remove if needed




