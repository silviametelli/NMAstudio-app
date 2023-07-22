from assets.dropdowns_values import *
from tools.navbar import Navbar
import dash_bootstrap_components as dbc, dash_html_components as html
from assets.Tabs.tabdata import tab_data
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

UP_LOGO = "/assets/logos/universite.jpeg"
CRESS_LOGO = "/assets/logos/logocress.png"
inserm_logo="/assets/logos/inserm.png"

def Homepage():
    return html.Div([Navbar(), home_layout()])


def home_layout():
    return html.Div(className="app__container", children=STORAGE+[
                        html.Div(dataupload_error, style={'vertical-align': "top"}),
                        html.Div(R_errors_data, style={'vertical-align': "top"}),
                        html.Div(R_errors_nma, style={'vertical-align': "top"}),
                        html.Div(R_errors_pair, style={'vertical-align': "top"}),
                        html.Div(R_errors_league, style={'vertical-align': "top"}),
                        html.Div(R_errors_funnel, style={'vertical-align': "top"}),
        html.Div(id='main_page',
                        ### LEFT HALF OF THE PAGE
                         children=[

                            html.Div(  # NMA Graph
                                [html.Div([dbc.Row([html.Div(Dropdown_graphlayout,
                                                             style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_edges, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_data, style={'display': 'inline-block', 'font-size': '11px'}),
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
                                                    
                                                    dbc.Col([html.H4("Enter the label size:",style={'font-size':'13px', 
                                                                                                #     'margin-left':'60px',
                                                                                                    'font-family': 'system-ui','width': '101px'}),
                                                           dcc.Input(id="label_size_input",
                                                              type="text",
                                                              name='Label size',
                                                              style={'background-color':'white',
                                                                #      'margin-left':'60px',
                                                                       'font-size':'10.5px',
                                                                       'padding-left':'-2px',
                                                                       'color':'gray','margin-top': '-6px'}, 
                                                                       placeholder="e.g. 30px",),
                                                                       ], style={'margin-left':'20px','margin-top':'-25px'}),
                                                    dbc.Col([html.H4("Search the intervention:",style={'font-size':'13px', 
                                                                                                        #      'margin-left':'150px',
                                                                                                             'font-family': 'system-ui',
                                                                                                        #      'margin-top':'-62px'
                                                                                                             }),
                                                           dcc.Input(id="treat_name_input",
                                                              type="text",
                                                              name='Label size',
                                                              style={'background-color':'white',
                                                                #      'margin-left':'150px',
                                                                       'font-size':'10.5px',
                                                                       'padding-left':'-2px','color':'gray','margin-top': '-6px'}, 
                                                                       placeholder="e.g. PBO",)], style={'margin-top':'-25px'})
                                                    

                                    ]),

                                           ], style={'margin-left': '-20px'}),
                         cyto.Cytoscape(id='cytoscape', responsive=True, autoRefreshLayout=True,
                                elements=[],
                                style={ 
                                    'height': '70vh', 'width': '600px', 
                                       'margin-top': '10px',
                                        'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                                        'padding-left': '-10px', 
                                        'max-width': 'calc(52vw)',
                                       },
                                layout={'name': 'circle', 'animate': True},
                                stylesheet=get_stylesheet()),
                        html.P('Copyright © 2020. All rights reserved.', className='__footer'),
                        dbc.Col([
                                 html.Img(src=UP_LOGO, height="57px"),
                                 html.Img(src=CRESS_LOGO, height="57px"), 
                                 html.Img(src=inserm_logo, height="57px"),
                                 ], style={'padding-right':'1%','padding-top':'0.3%',
                                           'padding-bottom':'0.3%','border-top':'solid',
                                           'display': 'table','margin-left':'10px'},
                    width="auto"),

                        # html.P('Copyright © 2020. All rights reserved.', className='__footer'),
                                ],
                          className="one-half column",
                  ),
                    ### RIGHT HALF OF THE PAGE
                     html.Div(className ="one-half-2 column", style={'margin-top': '20px'},
                       children=[html.Div(  # Information box
                                  [html.Div([dbc.Row([
                                                  html.H6("CLICK + SHIFT to select multiple network items", className="box__title2",
                                                         ),
                                                  ]),
                                          ]),
                                  html.Div([html.P(id='cytoscape-mouseTapEdgeData-output',  style={'margin-top':'-20px'},
                                                   className="info_box" )],
                                        )], className="info__container",style={'background-color':'#9fb5bd'}),
                           # html.Div([html.Button('Reset Project', id='reset_project', n_clicks=0, className="reset",
                           #                       style={"font-type": "sans-serif"}),
                           html.Div([html.A(html.Img(src="/assets/icons/reset.png",
                                                     style={'width': '40px', 'filter': 'invert()',
                                                            "margin-bottom":"15px", "margin-left":"10px"}), ##DIV RESET  BUTTON
                                  id="reset_project", style={'display': 'inline-block'}),
                                     dbc.Tooltip("Reset project - uploaded data will be lost",
                                                 style={'color': 'white', 'font-size': 9,
                                                        "margin-left": "5px",
                                                        'letter-spacing': '0.2rem'},
                                                 placement='right',
                                                 target='reset_project'),
                                      ], style={"display":'inline-block', 'margin-left':'20px',
                                                'margin-bottom':'2px'}),

                html.Div(
                    id='all-control-tabs',style={'background-color':'#e6e9eb'},
                    children=[
                        dcc.Tabs(id='', persistence=True, children=[

                            dcc.Tab(style={'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='Data',
                                    children=html.Div(className='control-tab', children=[tab_data()],
                                                      style={'overflowX': 'auto',
                                                             'overflowY': 'auto',
                                                             'height': '99%',
                                                             })
                                    ),

                            dcc.Tab(style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='Transitivity checks',
                                    children=html.Div(className='control-tab', children=[tab_trstvty])
                                   ),

                            dcc.Tab(value='mainTabForest',
                                    style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='Forest plots', children=html.Div(className='control-tab', children=[tab_forests])
                            ),
                            dcc.Tab(style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='League Table',
                                    children=html.Div(className='control-tab', children=[tab_league])
                            ),
                            dcc.Tab(style={'color': 'grey', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='Consistency checks',
                                    children=html.Div(className='control-tab', children=[tab_consistency()])
                                    ),
                            dcc.Tab(style={'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='Funnel plots',
                                    children=html.Div(className='control-tab', children=[tab_funnel])
                            ),
                            dcc.Tab(style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='Ranking plots',
                                    children=html.Div(className='control-tab', children=[tab_ranking])
                            ),


                        ],  colors={ "border": 'grey', "primary": "grey", "background": '#e8eaeb',
                                   }
                        ) #change border to CLR_BCKGRND to remove tabs borders
                    ]),

                ])
            ]),
          ],
    )


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

html.Br(), html.Br(),

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

 html.Br(), html.Br(),


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


    html.Br(), html.Br(),
    dcc.Markdown(
        'The full source code is freely available at [https://github.com/silviametelli/network-meta-analysis](https://github.com/silviametelli/network-meta-analysis)'
        , className="markdown_style",style={"color": "black"}),

html.Br(), html.Br(),
    dcc.Markdown('This project has received funding from the EU H2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 101031840 ',
                 className="markdown_style",style={"color": "black", "font-weight": "330", "font-size":"14px"}),


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
    dcc.Markdown('Please get in touch at silvia.metelli@u-paris.fr',
                 className="markdown_style_black",
                 style={"font-size": '20px', "margin-right":"10%", "margin-left":"30%", "margin-bottom":"1%"}),

                         html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br()

                     ])
    ])


