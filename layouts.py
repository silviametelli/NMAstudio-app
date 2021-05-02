import dash_cytoscape as cyto
from assets.cytoscape_styleesheeet import get_stylesheet
from assets.dropdowns_values import *
from navbar import Navbar
from assets.Tabs.tabdata import tab_data
from assets.Tabs.tabtransitivity import tab_trstvty
from assets.Tabs.tabforests import tab_forests
from assets.Tabs.tableaguetable import tab_league
from assets.Tabs.tabfunnel import tab_funnel
from assets.Tabs.tabranking import tab_ranking
from assets.COLORS import *

def home_layout(GLOBAL_DATA):
    return html.Div(className="app__container", children=[
                        ### STORAGE DATA
                        html.Div(id='__storage_netdata', style={'display': 'none'}),
                        html.Div(id='__storage_netdata_cinema', style={'display': 'none'}),

                        html.Div(
                          id='main_page',

                        ### LEFT HALF OF THE PAGE
                         children=[
                            html.Div(  # NMA Graph
                               [html.Div([dbc.Row([html.Div(Dropdown_graphlayout, style={'display': 'inline-block', 'font-size': '11px'}),
                                    html.Div(modal, style={'display': 'inline-block', 'font-size': '11px'}),
                                    html.Div(modal_data, style={'display': 'inline-block', 'font-size': '11px'}),
                                    html.Div(modal_data_table, style={'display': 'inline-block', 'font-size': '11px'}),
                                    html.Div(modal_league_table, style={'display': 'inline-block', 'font-size': '11px'}),
                                    html.A(html.Img(src="/assets/icons/NETD.png",
                                                    style={'width': '50px', 'filter': 'invert()'}),
                                           id="btn-get-png", style={'display': 'inline-block'}),
                                    dbc.Tooltip("save graph", style={'color': 'white',
                                                                     'font-size': 9,
                                                                     'margin-left': '10px',
                                                                     'letter-spacing': '0.3rem'
                                                                     }, placement='right',
                                                target='btn-get-png')
                                    ]),

                                           ], style={'margin-left': '-20px'}),
                         cyto.Cytoscape(id='cytoscape',  responsive=True,
                                elements=GLOBAL_DATA['user_elements'],
                                style={ 'height': '75vh', 'width': '99%', 'margin-top': '10px',
                                        'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                                       },
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
                html.Div(
                    id='all-control-tabs',
                    children=[
                        dcc.Tabs(id='all-tabs',  persistence=True, children=[

                            dcc.Tab(style={'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                label='Data',
                                children=html.Div(className='control-tab', children=[tab_data])
                                ),

                            dcc.Tab(style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                label='Transitivity boxplots',
                                children=html.Div(className='control-tab', children=[tab_trstvty])
                                   ),

                            dcc.Tab(value='mainTabForest',
                                    style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                label='Forest plots', children=html.Div(className='control-tab', children=[tab_forests])
                            ),
                            dcc.Tab(style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                label='League Table',
                                children=html.Div(className='control-tab', children=[tab_league])
                            ),
                            dcc.Tab(style={'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                label='Funnel plot',
                                children=html.Div(className='control-tab', children=[tab_funnel])
                            ),
                            dcc.Tab(style={'color':'grey', 'display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                label='Ranking plots',
                                children=html.Div(className='control-tab', children=[tab_ranking])
                            ),


                        ],  colors={ "border": 'grey', "primary": "grey", "background": CLR_BCKGRND})
                                     #change border to CLR_BCKGRND to remove tabs borders
                    ]),

                ])
            ]),
         ],
                           )

def Homepage(GLOBAL_DATA):
    return html.Div([Navbar(), home_layout(GLOBAL_DATA)])
############################################  DOCUMENTATION PAGE  #######################################################

doc_layout = html.Div([Navbar(), html.Br(),  html.Br(),

dcc.Markdown('NMAstudio is a web application to produce and visualise interactive outputs from network meta-analyses',
             className="markdown_style"),
    html.Br(),
        html.Div([dcc.Markdown("Download a pdf version with full documentation guidelines here", className="markdown_style",
                               style={'margin-right':'10px', 'display':'inline-block'}),
                       html.Button('Full documentation pdf', id='full-docu-pdf', style={'color':'white', 'display':'inline-block','padding':'4px'})
                    ]),
     html.Br(), html.Br(),
       dcc.Markdown('The full source code is available at [https://github.com/silviametelli/network-meta-analysis](https://github.com/silviametelli/network-meta-analysis)'
                           , className="markdown_style"),
                ])
