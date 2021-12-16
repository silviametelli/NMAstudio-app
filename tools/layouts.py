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
from assets.alerts import alert_outcome_type, alert_data_type, R_errors_nma, R_errors_pair, R_errors_league, R_errors_funnel

def Homepage():
    return html.Div([Navbar(), home_layout()])


def home_layout():
    return html.Div(className="app__container", children=STORAGE+[
                        html.Div(alert_data_type, style={'vertical-align':"top"}),
                        html.Div(alert_outcome_type, style={'vertical-align': "top"}),
                        html.Div(alert_data_type, style={'vertical-align': "top"}),
                        html.Div(R_errors_nma, style={'vertical-align': "top"}),
                        html.Div(R_errors_pair, style={'vertical-align': "top"}),
                        html.Div(R_errors_league, style={'vertical-align': "top"}),
                        html.Div(R_errors_funnel, style={'vertical-align': "top"}),
        html.Div(id='main_page',
                        ### LEFT HALF OF THE PAGE
                         children=[
                            html.Div(  # NMA Graph
                                [html.Div([dbc.Row([html.Div(Dropdown_graphlayout,
                                                             style={'display': 'inline-block', 'font-size': '11px'}),#TODO: ADJUST WIDTH INTERNAL DROPDOWN: was working before don't know what changed
                                                    html.Div(modal, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_edges, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_data, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_checks,style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_data_table, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_league_table, id="modal_league_div", style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.Div(modal_network, style={'display': 'inline-block', 'font-size': '11px'}),
                                                    html.A(html.Img(src="/assets/icons/NETD.png", style={'width': '50px', 'filter': 'invert()'}),
                                                                    id="btn-get-png", style={'display': 'inline-block'}),
                                                    dbc.Tooltip("save graph", style={'color': 'white',
                                                                                     'font-size': 9,
                                                                                     'margin-left': '10px',
                                                                                     'letter-spacing': '0.3rem'
                                                                                     }, placement='top',
                                                                target='btn-get-png'),
                                                    html.A(html.Img(src="/assets/icons/expand.png",
                                                                    style={'width': '40px',
                                                                           'filter': 'invert()',
                                                                           'margin-top': '2px',
                                                                           'padding-left': '-5px',
                                                                           'padding-right': '15px',
                                                                           'margin-bottom': '2px',
                                                                           'border-radius': '1px', }),
                                                                    id="network-expand",
                                                                    style={'margin-left': '10px'}),
                                                    dbc.Tooltip("expand plot",
                                                                style={'color': 'white', 'font-size': 9,
                                                                       'margin-left': '10px',
                                                                       'letter-spacing': '0.3rem'},
                                                                placement='right',
                                                                target='network-expand'),

                                    ]),

                                           ], style={'margin-left': '-20px'}),
                         cyto.Cytoscape(id='cytoscape',  responsive=True,
                                elements=[],
                                style={ 'height': '75vh', 'width': '99%', 'margin-top': '10px',
                                        'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                                        'padding-left': '-10px'
                                       },
                                layout={'name': 'circle', 'animate': True},
                                stylesheet=get_stylesheet()),

                        html.P('Copyright © 2020. All rights reserved.', className='__footer'),
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
                                        )], className="info__container"),
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
                    id='all-control-tabs',
                    children=[
                        dcc.Tabs(id='all-tabs', persistence=True, children=[

                            dcc.Tab(style={'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='Data',
                                    children=html.Div(className='control-tab', children=[tab_data()])
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


                        ],  colors={ "border": 'grey', "primary": "grey", "background": CLR_BCKGRND,
                                   })
                                     #change border to CLR_BCKGRND to remove tabs borders
                    ]),

                ])
            ]),
         ],
                           )


############################################  DOCUMENTATION PAGE  #######################################################

doc_layout = html.Div(id='docpage-link', children = [Navbar(), html.Br(),  html.Br(), html.Br(),

html.H1("NMAstudio (version 0.1)", style={'font-size':'20px', 'color':'white', 'padding-left':'3%',
                                          'padding-right':'3%', 'font-family':'sans-serif'}),  html.Br(),

dcc.Markdown('Please cite us as: Metelli S, Chaimani A. NMAstudio: a fully interactive web-application for producing and visualising network meta-analyses. *SRSM Annual Meeting 2021, Bern, Switzerland.*',
             className="markdown_style"),   html.Br(),   html.Br(),

dcc.Markdown('NMAstudio is a web application to produce and visualise interactive outputs from network meta-analyses',
             className="markdown_style"),
    html.Br(),
    dcc.Markdown('NMAstudio is a Plotly Dash app written in Python, and linked to the  R-package netmeta for performing analysis of the data',
                 className="markdown_style"),
dcc.Markdown('G. Rücker, G. Schwarzer, U. Krahn, and J. König. netmeta: Network Meta-Analysis using Frequentist Methods, 2017'
             ,className="markdown_style"),
    dcc.Markdown('R package version 6.6.6. https://CRAN.R-project.org/package=netmeta', className="markdown_style"),
                       html.Br(), html.Br(),

# dcc.Markdown('The methods are described in',className="markdown_style"),
#                        html.Br(), html.Br(),

                       html.Div([dcc.Markdown("Click the button beside to download a pdf copy of NMAstudio User Guide:", className="markdown_style",
                               style={'margin-right':'5px', 'display':'inline-block'}),
                       html.Button('Download documentation', id='full-docu-pdf', style={'color':'white', 'display':'inline-block','padding':'4px'})
                    ]),

    html.Br(), html.Br(), html.Br(), html.Br(),
    dcc.Markdown(
        'The full source code is freely available at [https://github.com/silviametelli/network-meta-analysis](https://github.com/silviametelli/network-meta-analysis)'
        , className="markdown_style"),


                       ]),



############################################  NEWS PAGE  #######################################################

list_forthcmg_features=['Flexible column data selection', 'R console printed for debugging', 'Sensitivity analyses',
                        'Fully connected network', 'More options for node size', 'More options for edge size']

list_future_features=['Option for Bayesian analysis', 'Option to upload a file containing NMA results']

news_layout = html.Div([

    Navbar(),

    html.Br(),html.Br(),


    html.H1("Forthcoming features", style={'font-size':'20px', 'color':'#76c0cf', 'padding-left':'3%',
                                          'padding-right':'3%', 'font-family':'sans-serif'}),
    html.Br(),
        html.Div(
           className="list-features",
           children=[
               html.Ul(id='my-list', children=[html.Li(i) for i in list_forthcmg_features])
                ],
            ),

    html.Br(),    html.Br(),


    html.H1("Future features", style={'font-size': '20px', 'color': '#76c0cf', 'padding-left': '3%',
                                               'padding-right': '3%', 'font-family': 'sans-serif'}),
    html.Br(),

    # html.Div(
       #     className="list-features",
       #     children=[
       #         html.Ul(id='my-list2', children=[html.Li(i) for i in list_future_features])],
       #     style={ "content":"\f138"}
       # ),

    html.Div(html.Ul([html.Li(i) for i in list_future_features])),

    html.Br(),

    html.Div([dcc.Markdown('',
                 className="markdown_style"),
                        html.Br(),html.Br(),


                        dcc.Markdown('Do you have any questions or suggestions for features you would like to see implemented in the next update of NMAstudio?'
                            , className="markdown_style"),
                        html.Br(),

                        dcc.Markdown('Get in touch at silvia.metelli@u-paris.fr'
                            , className="markdown_style"),
    ])

])
