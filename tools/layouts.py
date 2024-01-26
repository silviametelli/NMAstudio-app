from assets.dropdowns_values import *
from tools.navbar import Navbar
import dash_bootstrap_components as dbc, dash_html_components as html
from assets.Tabs.tabdata import tab_data, raw_data
from assets.Tabs.tabtransitivity import tab_trstvty
from assets.Tabs.tabforests import tab_forests
from assets.Tabs.tableaguetable import tab_league
from assets.Tabs.tabfunnel import tab_funnel
from assets.Tabs.tabranking import tab_ranking
from assets.Tabs.tabconsistency import tab_consistency
from assets.COLORS import *
from assets.storage import STORAGE
from assets.alerts import alert_outcome_type, alert_data_type, R_errors_data, R_errors_nma, R_errors_pair, R_errors_league, R_errors_funnel, dataupload_error
from dash_extensions import Download
from assets.Tabs.saveload_modal_button import saveload_modal


UP_LOGO = "/assets/logos/universite.jpeg"
CRESS_LOGO = "/assets/logos/cress_logo2.jpeg"
inserm_logo="/assets/logos/inserm_logo.png"
NMASTUDIO_art = '/assets/logos/nmastudio_art2.gif'
MAIN_PIC = '/assets/logos/mainpage.png'
LOAD = '/assets/logos/small.gif'
BOXPLOT = '/assets/logos/boxplot.gif'
NETPLOT = '/assets/logos/network.gif'
FOREST = '/assets/logos/forest.gif'
TABLE = '/assets/logos/table.gif'
CONS = '/assets/logos/consist.gif'
RANK = '/assets/logos/rank.gif'
FUNEL = '/assets/logos/funel.gif'


###################real homepage###############################
def realHomepage():
    return html.Div([Navbar(), real_homelayout()])

def real_homelayout():
    return html.Div([
                     html.Div([html.H2([html.Span('Welcome ',className="title-word title-word-1"),
                                        html.Span('to ',className="title-word title-word-2"),
                                        html.Span('NMA', className="title-word title-word-3"),
                                        html.Span('studio 2.0', className="title-word title-word-4"),], className="title")],
                                    # style={"font-size": '40px',
                                    #        'text-align': 'center',
                                    #        'color':'#5c7780',
                                    #        'font-family':'sans-serif'}, 
                                           className='container'), 
                     html.Br(),
                    #  dcc.Markdown('NMAstudio serves as an interactive web application designed to simplifies the whole Network Meta-Analysis (NMA) procedures and enhances the visualization of results.',
                    #                 className="markdown_style", style={"color": "black", "margin-right":"10%"}),
                    #                 html.Div([dcc.Markdown("We strongly advise you to download and review the Tutorial prior to using it:", className="markdown_style",
                    #                 style={'margin-right':'5px', 'display':'inline-block', "color": "black"}),
                    #                 html.Button('Tutorial', id='full-tuto-pdf',
                    #                          style={'color': 'black',
                    #                                 'display': 'inline-block',
                    #                                 'margin-left':'-23px',
                    #                                 'padding': '4px'}),
                    #                 Download(id="download-tuto")]),
                                    # html.Br(),
                                    html.Div(html.Img(src=MAIN_PIC,
                                                      width="1200px",
                                                      className= 'main_pic')),
                                    html.Br(),
                                    # html.Div([html.Span('What', style={'--i':'1'}),
                                    #     html.Span('results',style={'--i':'2'}),
                                    #     html.Span('you', style={'--i':'3'}),
                                    #     html.Span('can', style={'--i':'4'}),
                                    #     html.Span('get', style={'--i':'5'}),
                                    #     html.Span('from', style={'--i':'6'}),
                                    #     html.Span('NMAstudio?', style={'--i':'7'}),],
                                    # # style={"font-size": '40px',
                                    # #        'text-align': 'center',
                                    # #        'color':'#5c7780',
                                    # #        'font-family':'sans-serif'}, 
                                    #        className='waviy'),

                                    dcc.Markdown('What results you can get from NMAstudio?',
                                                className="markdown_style_main",
                                                style={
                                                    "font-size": '30px',
                                                    'text-align': 'center',
                                                    'color':'#5c7780',
                                                       }),

                                    html.Br(), html.Br(),
                                    html.Div([dbc.Row([
                                                      dbc.Col([html.Img(src=BOXPLOT,
                                                      width="70px", style={'justify-self':'center'}),
                                                      html.Span('Boxplots for transitivity checks',className= 'main_results')], 
                                                      className='col_results'),
                                                      dbc.Col([html.Img(src=NETPLOT,
                                                      width="70px", style={'justify-self':'center'}),
                                                      html.Span('Network plot for interventions', className= 'main_results')],
                                                      className='col_results'),
                                                      dbc.Col([html.Img(src=FOREST,
                                                      width="70px", style={'justify-self':'center'}),
                                                      html.Span('Forest plots for NMA & PWMA', className= 'main_results')],
                                                      className='col_results'),
                                                      dbc.Col([html.Img(src=TABLE,
                                                      width="70px", style={'justify-self':'center'}),
                                                      html.Span('League Table for relative effects', className= 'main_results')],
                                                      className='col_results'),
                                                      dbc.Col([html.Img(src=CONS,
                                                      width="70px", style={'justify-self':'center'}),
                                                      html.Span('Global & Local consistency checks', className= 'main_results')],
                                                      className='col_results'),
                                                      dbc.Col([html.Img(src=RANK,
                                                      width="70px", style={'justify-self':'center'}),
                                                      html.Span('Ranking plots for interventions', className= 'main_results')],
                                                      className='col_results'),
                                                      dbc.Col([html.Img(src=FUNEL,
                                                      width="70px", style={'justify-self':'center'}),
                                                      html.Span('Funel plots for small-study effect', className= 'main_results')],
                                                      className='col_results')],
                                                      style={'width' : '-webkit-fill-available',
                                                                  'justify-content': 'center',}
                                                                  ),]),
                                    html.Br(), html.Br(),html.Br(),
                                    dcc.Markdown('Before uploading your data, you can:',
                                    className="markdown_style_main",
                                    style={
                                        "font-size": '25px',
                                        'text-align': 'center',
                                        'color':'#5c7780',
                                            }),
                                    html.Br(),
                                    dbc.Row([html.Button('Download Tutorial', id='full-tuto-pdf',
                                             style={'color': 'black',
                                                    'display': 'inline-block',
                                                    'justify-self':'center',
                                                    'padding': '4px'}),
                                    Download(id="download-tuto"),
                                    html.Span('or', style={'justify-self':'center','align-self': 'center'}),
                                    dbc.NavLink('See the embeded example', href="/results", external_link=True,
                                                className='go_to_example'),
                                    ], style={"display": 'grid', 'width':'450px', 'justify-self':'center','grid-template-columns': '1fr 1fr 1fr'}),
                                    html.Br(), html.Br(),
                                    html.Span('More tutorials coming soon...',style={'justify-self':'center','align-self': 'center'}),    
                                    html.Br(), html.Br(),html.Br(),

                                    dcc.Markdown('Now you are ready to:',
                                    className="markdown_style_main",
                                    style={
                                        "font-size": '25px',
                                        'text-align': 'center',
                                        'color':'#5c7780',
                                            }),
                                    html.Br(),
                                    dbc.Row(html.Button(dbc.NavLink('Start', href="/results",
                                                                     external_link=True,className='upload_data', n_clicks=0, id='upload_homepage'),
                                             style={'color': 'white',
                                                    'background-color':'orange',
                                                    'display': 'inline-block',
                                                    'justify-self':'center',
                                                    'border': 'unset',
                                                    'padding': '4px'}), style={"display": 'grid'}),
                                    html.Br(), html.Br(),html.Br(),

                                    dcc.Markdown('Any questions?',
                                    className="markdown_style_main",
                                    style={
                                        "font-size": '25px',
                                        'text-align': 'center',
                                        'color':'#5c7780',
                                            }),
                                    html.Br(),
                                    html.Span('Please get in touch at tianqi.yu@etu.u-paris.fr', style={ 'justify-self': 'center'}),
                                    html.Br(), html.Br(),html.Br(),
                                    dbc.Row([dbc.Col([
                                                dcc.Markdown('Contributor',
                                                className="markdown_style_main",
                                                style={
                                                        "font-size": '20px',
                                                        'text-align': 'center',
                                                        'color':'orange',
                                                        'border-bottom': '2px solid',
                                                        'font-weight': 'bold',
                                                        'height': 'fit-content',
                                                        'margin-right': '20px'
                                                        }),
                                                dcc.Link('Tianqi Yu', href='https://www.cer-methods.com/tianqi-yu/',
                                                        style={'color': '#5b7780',
                                                                'text-decoration': 'unset',
                                                                'font-size': 'large',
                                                                'display': 'block',
                                                                'margin-right': '20px' }),
                                                dcc.Link('Anna Chaimani', href='https://www.cer-methods.com/anna/',
                                                        style={'color': '#5b7780',
                                                                'text-decoration': 'unset',
                                                                'font-size': 'large',
                                                                'display': 'block',
                                                                'margin-right': '20px'}),
                                                dcc.Link('Silvia Metelli', href='https://www.cer-methods.com/team/',
                                                        style={'color': '#5b7780',
                                                                'text-decoration': 'unset',
                                                                'font-size': 'large',
                                                                'display': 'block',
                                                                'margin-right': '20px' }),
                                                ], style={'text-align': 'center', 
                                                        'display': 'grid',
                                                        'justify-content': 'space-around',
                                                        'border-right': '2px solid orange',
                                                        'margin-bottom': '2%'
                                                        }
                                              ),
                                              dbc.Col([
                                                dcc.Markdown('Other Information',
                                                className="markdown_style_main",
                                                style={
                                                        "font-size": '20px',
                                                        'text-align': 'center',
                                                        'color':'orange',
                                                        'border-bottom': '2px solid',
                                                        'font-weight': 'bold',
                                                        'height': 'fit-content',
                                                        'margin-left': '20px',
                                                        'width': '95%',
                                                        'margin-top': '0'
                                                        }),
                                                dcc.Markdown('Please cite us as: Tianqi Y, Chaimani A. NMAstudio: a fully interactive web-application for producing and visualising network meta-analyses. *Cochrane Colloquium 2023, London, UK.*',
                                                                className="markdown_style", style={"color": "black", "margin-right":"10%"}),
                                                html.Br(), 

                                                dcc.Markdown('NMAstudio is a web application to produce and visualise interactive outputs from network meta-analyses. NMAstudio is written in Python, and linked to the R-package netmeta for performing network meta analysis.',
                                                        className="markdown_style",style={"color": "black", "margin-right":"10%"}),

                                                dcc.Markdown('Balduzzi, S., Rücker, G., Nikolakopoulou, A., Papakonstantinou, T., Salanti, G., Efthimiou, O. and Schwarzer, G., 2023. netmeta: An R package for network meta-analysis using frequentist methods.'
                                                        ,className="markdown_style", style={"font-size":"14px", "color": "black"}),

                                                html.Br(),

                                                html.Div([dcc.Markdown("Demonstration data set (class level psoriasis treatments):",
                                                        className="markdown_style", style={'margin-right':'0px', 'display':'inline-block',"color": "black"}) ,
                                                html.Button("Download data", id="demodata", style={'display': 'inline-block',
                                                                                                'padding': '1px', 'margin-left':'-23px'}),
                                                                Download(id="download-demodata")]),

                                                dcc.Markdown("Sbidian E, Chaimani A, Garcia-Doval I, Doney L, Dressler C, Hua C, et al. Systemic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis. \n Cochrane Database Syst Rev. 2021 Apr 19;4:CD011535.",
                                                        className="markdown_style", style={"font-size":"14px", "color": "black", "margin-right":"10%"}),
                                                html.Br(),html.Br(),

                                                ], style={ 'width': '80%'}),],
                                              style={'height':'fit-content', 'background-color':'antiquewhite', 'justify-content': 'center'}),
                                    
                                #     html.Br(), html.Br(),html.Br(),
                                    html.Footer([html.P('Copyright © 2020. All rights reserved.', 
                                         style={'color':'white', 'margin-left':'45px', 'margin-top': '2%'}),
                                         dcc.Markdown('This project has received funding from the EU H2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 101031840 & the French National Research Agency under the project ANR-22-CE36-0013-01',
                                         className="markdown_style",style={"color": "white", "font-weight": "330", "font-size":"14px"}),
                                        #  dcc.Markdown('Project team members: \nAnna Chaimani  Silvia Metelli  Tianqi Yu',
                                        #  className="markdown_style",style={"color": "white", "font-weight": "330", "font-size":"14px", 'white-space': 'pre'}),

                                     dbc.Col([
                                                html.Img(src=UP_LOGO, height="57px"),
                                                html.Img(src=CRESS_LOGO, height="57px"), 
                                                html.Img(src=inserm_logo, height="57px"),
                                                ], style={'padding-right':'1%','padding-top':'0.3%',
                                                        'padding-bottom':'0.3%','border-top':'solid',
                                                        'display': 'flex','margin-left':'10px',
                                                        'justify-content': 'space-between',
                                                        'width':'500px','margin-left': '43px'},
                                            width="auto"),
                                         ], className='__footer'),
], style={'display':'grid'})


###############################results page###########################
def Homepage():
    return html.Div([Navbar(), home_layout(), upload_data()], id='')

OPTIONS_results = [{'label': col, 'value': idx} for idx, col in enumerate(['Data & Transitivity', 'Forest plot', 'League table', 'Consistency & reporting bias', 'ranking'])]
def home_layout():
    return html.Div(id='result_page',className="app__container", children=STORAGE+[
                        html.Div(dataupload_error, style={'vertical-align': "top"}),
                        html.Div(R_errors_data, style={'vertical-align': "top"}),
                        html.Div(R_errors_nma, style={'vertical-align': "top"}),
                        html.Div(R_errors_pair, style={'vertical-align': "top"}),
                        html.Div(R_errors_league, style={'vertical-align': "top"}),
                        html.Div(R_errors_funnel, style={'vertical-align': "top"}),
                        html.Br(), html.Br(),
                        dbc.Row([
                                html.Span('Select results to display:', style={'justify-self':'center','align-self': 'center', 'font-size': 'medium'}),
                                dcc.Dropdown(placeholder="", options=OPTIONS_results, value = 0,
                                            style={'display': 'grid', 'justify-items': 'center', 'width':'160px'},
                                            id='result_selected'
                                                 ),
                                html.Span('or', style={'justify-self':'center','align-self': 'center'}),
                                html.Button(
                                        "Setup Analysis",
                                        "test_upload",
                                        n_clicks=0,
                                        ),
                                html.Div([html.A(html.Img(src="/assets/icons/reset.png",
                                                     style={'width': '40px', 'filter': 'invert()'}), ##DIV RESET  BUTTON
                                  id="reset_project", style={'display': 'grid', 'justify-items': 'center'}),
                                     dbc.Tooltip("Reset project - uploaded data will be lost",
                                                 style={'color': 'black', 'font-size': 9,
                                                        # "margin-left": "5px",
                                                        'letter-spacing': '0.2rem'},
                                                 placement='top',
                                                 target='reset_project'),
                                      ], style={"display":'inline-block', 'margin-left':'20px',
                                                'margin-bottom':'2px'}),
                                saveload_modal,

                                ], style={"display": 'grid', 'width':'850px', 'justify-self':'center','grid-template-columns': '0.9fr 0.2fr 0.2fr 0.5fr 0.5fr 0.5fr'}),

                        html.Br(), html.Br(),
                        html.Span('Click Setup Analysis button to upload your own dataset, otherwise the embedded example is shown below.', 
                                  style={'justify-self':'center',
                                         'align-self': 'center', 
                                         'font-size': 'medium', 'color': 'chocolate'}),
                        html.Hr(style = {'size' : '50', 'borderColor':'orange','borderHeight': "10vh", "width": "100%",'border-top': '3px solid #E1E1E1'}),
                        html.Br(), html.Br(),

        html.Div(id='main_page',
                        ### LEFT HALF OF THE PAGE
                         children=[

                            html.Div(  # NMA Graph
                                [html.Div([dbc.Row([html.Div(Dropdown_graphlayout,
                                                             style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_edges, style={'display': 'inline-block', 'font-size': '11px'}),
                                                #     html.Div(modal_data, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_checks,style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_data_table, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_league_table, id="modal_league_div", style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_network, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.A(html.Img(src="/assets/icons/NETD.png", style={'width': '50px'}),
                                                                    id="btn-get-png", style={'display': 'inline-block'}),
                                                    dbc.Tooltip("save graph", style={'color': 'black',
                                                                                     'font-size': 9,
                                                                                     'margin-left': '10px',
                                                                                     'letter-spacing': '0.3rem'
                                                                                     }, placement='top',
                                                                target='btn-get-png'),
                                                    html.A(html.Img(src="/assets/icons/expand.png",
                                                                    style={'width': '40px',
                                                                           'margin-top': '4px',
                                                                           'padding-left': '-5px',
                                                                           'padding-right': '15px',
                                                                           'margin-bottom': '2px',
                                                                           'border-radius': '1px', }),
                                                                    id="network-expand",
                                                                    style={'margin-left': '10px'}),
                                                    dbc.Tooltip("expand plot",
                                                                style={'color': 'black', 'font-size': 9,
                                                                       'margin-left': '10px',
                                                                       'letter-spacing': '0.3rem'},
                                                                placement='top',
                                                                target='network-expand'),
                                                    html.A(html.Img(src="/assets/icons/zoomout.png",
                                                                    style={'width': '40px',
                                                                           'margin-top': '4px',
                                                                           'padding-left': '-5px',
                                                                           'padding-right': '15px',
                                                                           'margin-bottom': '2px',
                                                                           'border-radius': '1px', }),
                                                                    id="network-zoomout",
                                                                    style={'margin-left': '10px'}),
                                                    dbc.Tooltip("zoomout plot",
                                                                style={'color': 'black', 'font-size': 9,
                                                                       'margin-left': '10px',
                                                                       'letter-spacing': '0.3rem'},
                                                                placement='top',
                                                                target='network-zoomout'),
                                                    
                                                    dbc.Col([html.H4("Label size:",style={'font-size':'13px', 
                                                                                                #     'margin-left':'60px',
                                                                                                    'font-family': 'system-ui','width': '90px'}),
                                                           dcc.Input(id="label_size_input",
                                                              type="text",
                                                              name='Label size',
                                                              style={'background-color':'white',
                                                                #      'margin-left':'60px',
                                                                       'font-size':'10.5px',
                                                                       'color':'gray','margin-top': '-6px',
                                                                       'width': '70px'}, 
                                                                       placeholder="e.g. 30px",),
                                                                       ], style={'padding-left':'20px','margin-top':'-40px'}),
                                                    dbc.Col([html.H4("Intervention:",style={'font-size':'13px', 
                                                                                                        #      'margin-left':'150px',
                                                                                                             'font-family': 'system-ui',
                                                                                                             'width': '90px'
                                                                                                        #      'margin-top':'-62px'
                                                                                                             }),
                                                           dcc.Input(id="treat_name_input",
                                                              type="text",
                                                              name='Label size',
                                                              style={'background-color':'white',
                                                                #      'margin-left':'150px',
                                                                       'font-size':'10.5px',
                                                                       'color':'gray','margin-top': '-6px',
                                                                       'width': '70px'}, 
                                                                       placeholder="e.g. PBO",)], style={'margin-top':'-40px','padding-right':'5px'}),
                                                    html.Div([
                                                        html.A(html.Img(src="/assets/icons/list.png",
                                                                           style={"width": "30px",
                                                                                  "float":"right",
                                                                                  'margin-top': '-2px'}),id='img_icon'),
                                                        # dbc.Toast([html.P("This is the content of the toast", className="mb-0")],
                                                        #           id="simple-toast",header="This is the header",
                                                        #           icon="primary",
                                                        #           dismissable=True,
                                                        #           is_open=True,style={"position": "fixed", "top": 66, "right": 10, "width": 350},),
                                                        
                                                        ],id="info_icon"),
                                                       html.Div(modal_info, style={'display': 'inline-block', 'font-size': '11px'}),
                                                        

                                                    

                                    ]),

                                           ], style={'margin-left': '-20px'}),
                         cyto.Cytoscape(id='cytoscape', responsive=False, autoRefreshLayout=True,
                                        minZoom=0.3,  maxZoom=1.5,      
                                elements=[],
                                style={ 
                                    'height': '70vh', 'width': '100%', 
                                       'margin-top': '10px',
                                        'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                                        'padding-left': '-10px', 
                                        'border-right': '3px solid rgb(165 74 97)'
                                        # 'max-width': 'calc(52vw)',
                                       },
                                layout={'name':'grid','animate': False, 'fit':True },
                                stylesheet=get_stylesheet())
                                ],
                          className="one-half column", id='one-half-1',
                  ),
                    ### RIGHT HALF OF THE PAGE
                     html.Div(id='one-half-2', className ="one-half-2 column",
                       children=[html.Div(  # Information box
                                  [
                                html.Div(
                                        dbc.Col([
                                         html.A(
                                                html.Img(
                                                    src="/assets/icons/expand.png",
                                                    style={
                                                        "width": "34px",
                                                        "margin-top": "15px",
                                                        "border-radius": "1px",
                                                    },
                                                ),
                                                id="data-expand",
                                                style={"display": "inline-block", "margin-left": "10px"},
                                            ),
                                            dbc.Tooltip(
                                                "expand window",
                                                style={
                                                    "color": "black",
                                                    "font-size": 9,
                                                    "margin-left": "10px",
                                                    "letter-spacing": "0.3rem",
                                                },
                                                placement="right",
                                                target="data-expand",
                                            ),
                                            html.A(
                                                html.Img(
                                                    src="/assets/icons/zoomout.png",
                                                    style={
                                                        "width": "34px",
                                                        "margin-top": "15px",
                                                        "border-radius": "1px",
                                                    },
                                                ),
                                                id="data-zoomout",
                                                style={"display": "none", "margin-left": "10px"},
                                            ),
                                            dbc.Tooltip(
                                                "Zoom out window",
                                                style={
                                                    "color": "black",
                                                    "font-size": 9,
                                                    "margin-left": "10px",
                                                    "letter-spacing": "0.3rem",
                                                },
                                                placement="right",
                                                target="data-zoomout",
                                            )], style={'display':'inline-block'}
                                     ),
                           ),   
                                  html.Div([dbc.Row([
                                                  html.H6("CLICK + SHIFT to select multiple network items", className="box__title2",
                                                         ),
                                                  ]),
                                          ]),
                                  html.Div([html.P(id='cytoscape-mouseTapEdgeData-output',  style={'margin-top':'-20px'},
                                                   className="info_box" )],
                                        )], className="info__container"),
                           # html.Div([html.Button('Reset Project', id='reset_project', n_clicks=0, className="reset",
                           #                       style={"font-type": "sans-serif"}),
                        #    html.Div([html.A(html.Img(src="/assets/icons/reset.png",
                        #                              style={'width': '40px', 'filter': 'invert()',
                        #                                     "margin-bottom":"15px", "margin-left":"10px"}), ##DIV RESET  BUTTON
                        #           id="reset_project", style={'display': 'inline-block'}),
                        #              dbc.Tooltip("Reset project - uploaded data will be lost",
                        #                          style={'color': 'black', 'font-size': 9,
                        #                                 "margin-left": "5px",
                        #                                 'letter-spacing': '0.2rem'},
                        #                          placement='right',
                        #                          target='reset_project'),
                        #               ], style={"display":'inline-block', 'margin-left':'20px',
                        #                         'margin-bottom':'2px'}),
                        
                           html.Div(
                                dbc.Col(
                                        [html.Span(f"Select outcome",className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                                        'margin-left': '0px', 'font-size': '16px','white-space': 'nowrap','color': '#5c7780'}),
                                        dcc.Dropdown(id='_outcome_select', searchable=True, placeholder="...", className="box",
                                                        clearable=False, value=0,
                                                        style={'width': '80px',  # 'height': '30px',
                                                            "height": '30px',
                                                            'vertical-align': 'middle',
                                                            "font-family": "sans-serif",
                                                            'margin-bottom': '2px',
                                                            'display': 'inline-block',
                                                            'color': 'black',
                                                            'font-size': '10px'})], style={'display': 'flex', 
                                                                                           'align-items': 'center',
                                                                                           'justify-content': 'space-around',
                                                                                           'width': '200px'
                                                                                           }),
                                    style={'display':'inline-block', 'margin-left': '20px'}),

                html.Div(
                    id='all-control-tabs',style={'background-color':'white'},
                    children=[
                        dcc.Tabs(id='results_tabs', persistence=True, children=[

                            dcc.Tab(id='data_tab', value= 'data_tab',style={'color':'grey','display': 'none', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center','background-color': '#f5c198',
                                                    'align-items': 'center'},
                                    label='Data',
                                    children=html.Div(className='control-tab', children=[
                                        dcc.Tabs(id='', value='new_data', vertical=False, persistence=True,
                                                 children=[
                                                     dcc.Tab(label='Converted Data', 
                                                             id='new_data', value='new_data',
                                                             className='control-tab',
                                                             children=[tab_data()],
                                                             style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                                    'align-items': 'center',
                                                                    'font-size': '12px', 'color': 'black', 'padding': '0'},
                                                             selected_style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                                                'align-items': 'center','background-color': '#f5c198',
                                                                                'font-size': '12px', 'padding': '0'},
                                                             ),
                                                     dcc.Tab(label='Raw Data', 
                                                             id='raw_data', value='raw_data',
                                                             className='control-tab',
                                                             children=[raw_data()],
                                                              style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                                    'align-items': 'center',
                                                                    'font-size': '12px', 'color': 'black', 'padding': '0'},
                                                             selected_style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                                                'align-items': 'center','background-color': '#f5c198',
                                                                                'font-size': '12px', 'padding': '0'},
                                                             ), 
                                                 ])],
                                                      style={'overflowX': 'auto',
                                                             'overflowY': 'auto',
                                                             'height': '99%',
                                                             })
                                    ),

                            # dcc.Tab(style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                            #         selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                            #                         'align-items': 'center'},
                            #         label='Transitivity checks',
                            #         children=html.Div(className='control-tab', children=[tab_trstvty])
                            #        ),

                            dcc.Tab(id='forest_tab',value= 'forest_tab',
                                    style={'color':'grey', 'display': 'none', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center','background-color': '#f5c198',
                                                    'align-items': 'center'},
                                    label='Forest plots', children=html.Div(className='control-tab', children=[tab_forests])
                            ),
                            dcc.Tab(id='league_tab',value= 'league_tab',style={'color':'grey', 'display': 'none', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center','background-color': '#f5c198',
                                                    'align-items': 'center'},
                                    label='League Table',
                                    children=html.Div(className='control-tab', children=[tab_league])
                            ),
                            dcc.Tab(id='consis_tab',value= 'consis_tab',style={'color': 'grey', 'display': 'none', 'justify-content': 'center', 'align-items': 'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center','background-color': '#f5c198',
                                                    'align-items': 'center'},
                                    label='Consistency checks',
                                    children=html.Div(className='control-tab', children=[tab_consistency()])
                                    ),
                        #     dcc.Tab(style={'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'},
                        #             selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                        #                             'align-items': 'center'},
                        #             label='Funnel plots',
                        #             children=html.Div(className='control-tab', children=[tab_funnel])
                        #     ),
                            dcc.Tab(id='ranking_tab',value= 'ranking_tab',style={'color':'grey', 'display': 'none', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center','background-color': '#f5c198',
                                                    'align-items': 'center'},
                                    label='Ranking plots',
                                    children=html.Div(className='control-tab', children=[tab_ranking])
                            ),


                        ],  colors={ "border": 'grey', "primary": "grey", "background": 'white',
                                #     "background": '#e8eaeb',
                                   }
                        ) #change border to CLR_BCKGRND to remove tabs borders
                    ]),

                ]),
                html.Br(),
            html.Div(id='one-half-3',className ="one-half-3 column", 
                       children=[

                html.Div(
                    id='all-control-tabs2',style={'background-color':'white'},
                    children=[
                        dbc.Col([
                                html.A(
                                html.Img(
                                        src="/assets/icons/expand.png",
                                        style={
                                        "width": "34px",
                                        "margin-top": "15px",
                                        "border-radius": "1px",
                                        },
                                ),
                                id="data-expand1",
                                style={"display": "none"},
                                ),
                                dbc.Tooltip(
                                "expand window",
                                style={
                                        "color": "black",
                                        "font-size": 9,
                                        "margin-left": "10px",
                                        "letter-spacing": "0.3rem",
                                },
                                placement="right",
                                target="data-expand1",
                                ),
                                html.A(
                                html.Img(
                                        src="/assets/icons/zoomout.png",
                                        style={
                                        "width": "34px",
                                        "margin-top": "15px",
                                        "border-radius": "1px",
                                        },
                                ),
                                id="data-zoomout1",
                                style={"display": "inline-block"},
                                ),
                                dbc.Tooltip(
                                "Zoom out window",
                                style={
                                        "color": "black",
                                        "font-size": 9,
                                        "margin-left": "10px",
                                        "letter-spacing": "0.3rem",
                                },
                                placement="right",
                                target="data-zoomout1",
                                )], style={'display':'inline-block'}
                                     ),
                        dcc.Tabs(id='results_tabs2', persistence=True, children=[
                            dcc.Tab(label='Pairwise', id='tab2', value='tab2', className='control-tab',
                                         style={'color':'grey', 'display': 'none', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center','background-color': '#f5c198',
                                                    'align-items': 'center'},
                                         children=[html.Div([dbc.Row([
                                          dbc.Col(html.P(
                                             id='tapEdgeData-info', style={'font-size':'12px', 'margin-top':'0.8%'},
                                             className="box__title"),style={'display': 'inline-block'}),
                                          html.Br()], className='tab_row_all')], style={'height':'35px'}),
                                             dcc.Loading(
                                                 html.Div([
                                                     dcc.Graph(
                                                         id='tapEdgeData-fig-pairwise',
                                                         style={
                                                                'height': '99%',
                                                                # 'max-height': 'calc(52vw)',
                                                                'width': '99%',
                                                                # 'margin-top': '-2.5%',
                                                                # 'max-width': 'calc(52vw)'
                                                                },
                                                         config={'editable': True,
                                                               #  'showEditInChartStudio': True,
                                                               #  'plotlyServerURL': "https://chart-studio.plotly.com",
                                                         'edits': dict(annotationPosition=True,
                                                                      annotationTail=True,
                                                                      annotationText=True, axisTitleText=False,
                                                                      colorbarPosition=False,
                                                                      colorbarTitleText=False,
                                                                      titleText=False,
                                                                      legendPosition=True, legendText=True,
                                                                      shapePosition=True),
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
                                                                 'scale': 3.5
                                                                 # Multiply title/legend/axis/canvas sizes by this factor
                                                             },
                                                             'displaylogo': False})], style={'height': '450px', 'overflow':'scroll'})

                                             ),
                                         ]),
                            dcc.Tab(id='trans_tab', value= 'trans_tab', style={'color':'grey', 'display': 'none', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center','background-color': '#f5c198',
                                                    'align-items': 'center'},
                                    label='Transitivity checks',
                                    children=html.Div(className='control-tab', children=[tab_trstvty])
                                   ),
                            dcc.Tab(style={'color':'grey', 'display': 'none'},
                                    label=''
                                   ),
                            dcc.Tab(id='funnel_tab',value= 'funnel_tab',style={'color':'grey','display': 'none', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center','background-color': '#f5c198',
                                                    'align-items': 'center'},
                                    label='Funnel plots',
                                    children=html.Div(className='control-tab', children=[tab_funnel])
                            ),


                        ],  colors={ "border": 'grey', "primary": "grey", "background": '#e8eaeb',
                                   }
                        ) #change border to CLR_BCKGRND to remove tabs borders
                    ]),

                ])    
            ]),
          ],
    )
####################################Data Upload###########################################


def upload_data():
    return html.Div(id='upload_page',style={'display':'none'},children=[
        dbc.Row( [html.Img(src="/assets/icons/back_arrow.png",n_clicks=0,
                style={'width': '40px'}, id='back_plot'), html.P('Back to the results', id='back_result')], id='arrow_back'),
        dbc.Row([dbc.Col([
                        html.Div(dcc.Upload(['Drag and Drop or ', html.A('Select a File')],
                            id='datatable-upload2', multiple=False,
                            className='control-upload',
                            style={'width': '100%','height': '60px',
                                    'lineHeight': '60px','borderWidth': '1px',
                                    'borderStyle': 'dashed','borderRadius': '5px',
                                    'textAlign': 'center', 'margin': '10px',
                                    'color':'black'},
                            ), style={'display': 'inline-block'}),
                        html.Div([html.P('', style={'padding-left':'10px'}),
                        html.P('',id='uploaded_datafile2', style={'color':'violet', 'padding-left':"20px"})],
                                style={'font-family':'italic', 'display': 'inline-block'})
                        ],style={'display': 'inline-block', 'justify-self': 'center'}),
        # dbc.Col([html.Br(),html.Ul(id="file-list2", style={'margin-left': '15px', 'color':'white','opacity':'60%'})],
        #         style={'display': 'inline-block'}),
        dbc.Col(html.Div(html.Span('* The dataset should be uploaded as the csv format',className='upload_instuspan',
                            )), className='upload_instrucol')
                ], className= 'upload_row'),
        dbc.Row( html.Img(src="/assets/icons/arrow.png",
                style={'width': '60px'}), 
                style={'display':'none', 'justify-content': 'center'}, id='arrow_step1'),
        html.Br(),
        html.Div(dbc.Row([dbc.Col(file_upload_controls2),
                          dbc.Col(html.Div([html.Span('*You can click the link the see the differences between the formats:',className='upload_instuspan',
                            ), dbc.NavLink('Link', active=True, external_link=True, href= "assets/data format.pdf", style={'color': 'blue'})]), className='upload_instrucol')
                          ],className= 'upload_row' ),
                 style={'display': 'none', 'justify-content': 'center'},
                 id="dropdowns-DIV2"), 
        html.Br(),

        dbc.Row( html.Img(src="/assets/icons/arrow.png",
                style={'width': '60px'}), 
                style={'display':'none', 'justify-content': 'center'}, id='arrow_step_2'),
        html.Br(),
        html.Div([dbc.Row([dbc.Col(id="select-box-1"),
                  dbc.Col(html.Div(html.Span('*studlab: study ID or study name \n*rob: risk of bias should be encoded in your data file as either {1,2,3}, {l,m,h} or {L,M,H} \n*year: year of publication',className='upload_instuspan',
                            )), className='upload_instrucol')        
                           ], className= 'upload_row')],
                 style={'display': 'none', 'justify-content': 'center'}, id='select-overall'), 

        html.Br(),
        dbc.Row( html.Img(src="/assets/icons/arrow.png",
                style={'width': '60px'}), 
                style={'display':'none', 'justify-content': 'center'}, id='arrow_step_3'),
        html.Br(),
        dbc.Row([dbc.Col([html.P("Enter the number of outcomes:", className="selcect_title",),
                         html.Div(
                                [dcc.Input(id='number-outcomes', className='upload_radio', style={'width':'100px'}),
                                 dbc.Button("OK", n_clicks=0, id='num_outcomes_button',disabled=True,
                                    style={'color': 'white',
                                            'background-color':'orange',
                                            'display': 'inline-block',
                                            'justify-self':'center',
                                            'border': 'unset',
                                            'padding': '4px'})],
                                        style={'display': 'flex',
                                                'justify-content': 'space-evenly',
                                                'width': '150px',
                                                'justify-self': 'center'
                                               }),
                                               ],
                                       style={'display': 'grid', 
                                               'background-color': 'beige',
                                                'width': '500px',
                                                'justify-content': 'center',
                                                'height': '100px',
                                                'align-items': 'center'
                                               }),
                dbc.Col(html.Div(html.Span('*NMAStudio now support outcomes as many as you want.',className='upload_instuspan',
                            )), className='upload_instrucol')], 
                                         id="number-outcomes-input", className= 'upload_row'),

        html.Br(),
        dbc.Row( html.Img(src="/assets/icons/arrow.png",
                style={'width': '60px'}), 
                style={'display':'none', 'justify-content': 'center'}, id='arrow_step_4'),
        html.Br(),
        html.Div(dbc.Row([dbc.Col(id='outcomes_type'),
                dbc.Col(html.Div(html.Span('*Select binary or continuous and enter the corresponding name for each outcome',className='upload_instuspan',
                            )), className='upload_instrucol')   
                          ], className= 'upload_row')
        , style={'display':'none', 'justify-content': 'center'}, id='select-out-type'),
        html.Br(),

        dbc.Row( html.Img(src="/assets/icons/arrow.png",
                style={'width': '60px'}), 
                style={'display':'none', 'justify-content': 'center'}, id='arrow_step_5'),
        html.Br(),
        html.Div(dbc.Row([dbc.Col(id='variable_selection'),
                          dbc.Col(html.Div(html.Span('* In this box, each variable should refer to a unique coulum in your dataset. For example, if you have two outcomes and the number of participants are the same in each study for two outcomes. The number of participants refer to column "N" in your dataset. Do not select "N" for both outcome 1 and 2. In this case, you need to create another column "N2" for outcome 2. ',className='upload_instuspan',
                            )), className='upload_instrucol') 
                          ],  className= 'upload_row')
        , style={'display':'none', 'justify-content': 'center'}, id='select_variables'),
        html.Br(),

        # dbc.Row( html.Img(src="/assets/icons/arrow.png",
        #         style={'width': '60px'}), 
        #         style={'display':'none', 'justify-content': 'center'}, id='arrow_step2'),
        # html.Br(),
        # html.Div(id='upload_selection_second', style={'display':'grid', 'justify-content': 'center'}),
        # html.Br(),
        dbc.Row( html.Img(src="/assets/icons/arrow.png",
                style={'width': '60px'}), 
                style={'display':'none', 'justify-content': 'center'}, id='arrow_step3'),
        html.Br(),
        html.Div(dbc.Row([dbc.Col(id='select_effect_modifier'),
                          dbc.Col(html.Div(html.Span('*Select potential effect modifiers you want to check. If you do not want to check, please tick "skip" ',className='upload_instuspan',
                            )), className='upload_instrucol') 
                          ], className= 'upload_row'),
                  style={'display':'none', 'justify-content': 'center'}, id='effect_modifier_select'),
        html.Br(),
        dbc.Row( html.Img(src="/assets/icons/arrow.png",
                style={'width': '60px'}), 
                style={'display':'none', 'justify-content': 'center'}, id='arrow_step4'),
        html.Br(), 
        dbc.Row(dbc.Button("Run Analysis", id="upload_modal_data2", className="", disabled=True, 
                   style={'color': 'white',
                        'background-color':'orange',
                        'display': 'inline-block',
                        'justify-self':'center',
                        'border': 'unset',
                        'padding': '4px'}), style={"display": 'none'}, id='run_button'),
        html.Br(),html.Br(),
        # html.Div(model_transitivity,
        #          style={'display': 'circle', 'justify-content': 'center'}),
        
    ],)



############################################  DOCUMENTATION PAGE  #######################################################



doc_layout = html.Div(id='docpage-link', className="markdown_style",
                      children = [Navbar(), html.Br(),

html.Div(style={"width": "98%","border": "1px solid gray", "padding": "10px", "color": "black",'font-family':'sans-serif',
                                         "margin": "15px", "background-color": "#d7dbda", "font-weight": "550"},
children = [
html.Br(),
html.H1("NMAstudio (version 0.1)", style={'font-size':'22px',  'padding-left':'3%',#'color':'white',
                                          'padding-right':'3%'}),  html.Br(),

dcc.Markdown('Please cite us as: Metelli S, Chaimani A. NMAstudio: a fully interactive web-application for producing and visualising network meta-analyses. *SRSM Annual Meeting 2021, Bern, Switzerland.*',
             className="markdown_style", style={"color": "black", "margin-right":"10%"}),

html.Br(), 

dcc.Markdown('NMAstudio is a web application to produce and visualise interactive outputs from network meta-analyses. NMAstudio is written in Python, and linked to the R-package netmeta for performing network meta analysis.',
             className="markdown_style",style={"color": "black", "margin-right":"10%"}),

dcc.Markdown('G. Rücker, U. Krahn, J. König, O. Efthimiou, A. Davies, T. Papakonstantinou & G. Schwarzer. netmeta: Network Meta-Analysis using Frequentist Methods, 2021. R package version 2.0-1.'
             ,className="markdown_style", style={"font-size":"14px", "color": "black"}),

html.Br(),

html.Div([dcc.Markdown("Demonstration data set (class level psoriasis treatments):",
             className="markdown_style", style={'margin-right':'0px', 'display':'inline-block',"color": "black"}) ,
    html.Button("Download data", id="demodata", style={'display': 'inline-block',
                                                       'padding': '1px', 'margin-left':'-23px'}),
                Download(id="download-demodata")]),

dcc.Markdown("Sbidian E, Chaimani A, Garcia-Doval I, Doney L, Dressler C, Hua C, et al. Systemic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis. \n Cochrane Database Syst Rev. 2021 Apr 19;4:CD011535.",
             className="markdown_style", style={"font-size":"14px", "color": "black", "margin-right":"10%"}),

 html.Br(), 


# dcc.Markdown('The methods are described in',className="markdown_style"),
#                        html.Br(), html.Br(),

                       html.Div([dcc.Markdown("Click beside to download a pdf copy of NMAstudio Tutorial:", className="markdown_style",
                               style={'margin-right':'5px', 'display':'inline-block', "color": "black"}),

                      html.Button('Tutorial', id='full-tuto-pdf',
                                             style={'color': 'black',
                                                    'display': 'inline-block',
                                                    'margin-left':'-23px',
                                                    'padding': '4px'}),
                                 Download(id="download-tuto"),
                       # html.Button('Download User Guide', id='full-docu-pdf',
                       #             style={'color':'white', 'margin-left':'10px', 'display':'inline-block','padding':'4px'}),
                       #           Download(id="download-guide")
                    ]),


    html.Br(), 
    dcc.Markdown(
        'The full source code is freely available at [https://github.com/silviametelli/network-meta-analysis](https://github.com/silviametelli/network-meta-analysis)'
        , className="markdown_style",style={"color": "black"}),

html.Br(), html.Br(),
    dcc.Markdown('This project has received funding from the EU H2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 101031840 & the French National Research Agency under the project ANR-22-CE36-0013-01',
                 className="markdown_style",style={"color": "black", "font-weight": "330", "font-size":"14px"}),

    dbc.Col([
                                 html.Img(src=UP_LOGO, height="57px"),
                                 html.Img(src=CRESS_LOGO, height="57px"), 
                                 html.Img(src=inserm_logo, height="57px"),
                                 ], style={'padding-right':'1%','padding-top':'0.3%',
                                           'padding-bottom':'0.3%','border-top':'solid',
                                           'display': 'flex','margin-left':'10px',
                                           'justify-content': 'space-between',
                                           'width':'500px','margin-left': '43px'},
                    width="auto"),


])
                       ]),



############################################  NEWS PAGE  #######################################################
ICON  = "/assets/icons/favicon_nmastudio.ico"

list_forthcmg_features=['A system of warnings', 'Sensitivity analyses',
                        'Fully connected network', 'More options for node size', 'More options for edge size']
list_future_features=['Option for Bayesian analysis', 'Permanent link to project']

news_layout = \
    html.Div(id='newspage-link', className="markdown_style",
            children = [Navbar(), html.Br(),

            html.Div(style={"width": "98%","border": "1px solid gray", "padding": "10px",
                            "color": "black",'font-family':'sans-serif',
                            "margin": "15px", "background-color": "#d7dbda", "font-weight": "530"},
                     children = [
                         html.Div(className="one-half-news-1 column",
                          children=[
                              html.Br(), html.Br(),
                              html.Div(dbc.Col([html.H1("NEW!",
                                   style={'font-size':'20px', 'color':'#587485','padding-left':'3%',
                                          'padding-right':'3%', 'font-family':'sans-serif', "font-weight": "530"}),
             html.H3("nmastudio Python package", style={'font-size':'20px', #'color':'white',
                                                        'padding-left':'3%', 'padding-right':'3%',
                                                        'font-family':'sans-serif', 'display':'inline-block'}),

    html.Img(src=ICON, height="30px", style={'display':'inline-block',  'margin-left':'-8px'} ) ])),
    html.Br(), html.Br(),
    html.H1("Forthcoming features", style={'font-size':'20px', 'color':'#587485', 'padding-left':'3%',
                                           "font-weight": "530", 'padding-right':'3%', 'font-family':'sans-serif'}),
        html.Div(
           className="list-features",
           children=[html.Ul(id='my-list',  style={"color": "black", "font-weight": "450", "font-size": "18px"},
                             children=[html.Li(i) for i in list_forthcmg_features])]),
    html.Br(), html.Br(),
    html.H1("Future features", style={'font-size': '20px', 'color': '#587485', 'padding-left': '3%',
                                      "font-weight": "560",
                                      'padding-right': '3%', 'font-family': 'sans-serif'}),
    html.Div(html.Ul( style={"color": "black", "font-weight": "450", "font-size": "18px"},
                      children= [html.Li(i) for i in list_future_features])),
    html.Br(), html.Br()
    ]),


    html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),

    dcc.Markdown('Do you have any questions or suggestions for features you would '
                 'like to see implemented in the next update of NMAstudio?',
                 className="markdown_style_black",
                 style={"font-size": '20px', "font-style": "italic", "margin-right":"10%", "margin-left":"30%"}),
    html.Br(),
    dcc.Markdown('Please get in touch at tianqi.yu@etu.u-paris.fr',
                 className="markdown_style_black",
                 style={"font-size": '20px', "margin-right":"10%", "margin-left":"30%", "margin-bottom":"1%"}),

                         html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br()

                     ])
    ])


