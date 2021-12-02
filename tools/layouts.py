from assets.dropdowns_values import *
from tools.navbar import Navbar
from assets.Tabs.tabdata import tab_data
from assets.Tabs.tabtransitivity import tab_trstvty
from assets.Tabs.tabforests import tab_forests
from assets.Tabs.tableaguetable import tab_league
from assets.Tabs.tabfunnel import tab_funnel
from assets.Tabs.tabranking import tab_ranking
from assets.Tabs.tabconsistency import tab_consistency
from assets.COLORS import *
from assets.storage import STORAGE
from assets.alerts import alert_data_type

def Homepage():
    return html.Div([Navbar(), home_layout()])


def home_layout():
    return html.Div(className="app__container", children=STORAGE+[
                        html.Div(id='img_div', style={'display': 'none'}),
                        html.Div(alert_data_type),
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

                       html.Div([dcc.Markdown("Please click the button beside to download a pdf copy of the NMAstudio User Guide:", className="markdown_style",
                               style={'margin-right':'5px', 'display':'inline-block'}),
                       html.Button('Download documentation', id='full-docu-pdf', style={'color':'white', 'display':'inline-block','padding':'4px'})
                    ]),

    html.Br(), html.Br(), html.Br(), html.Br(),
    dcc.Markdown(
        'The full source code is freely available at [https://github.com/silviametelli/network-meta-analysis](https://github.com/silviametelli/network-meta-analysis)'
        , className="markdown_style"),


                       ]),



############################################  NEWS PAGE  #######################################################

news_layout = html.Div([Navbar(), html.Br(),  html.Br(), html.Br(),

    html.H1("Upcoming new features", style={'font-size':'20px', 'color':'white', 'padding-left':'3%',
                                          'padding-right':'3%', 'font-family':'sans-serif'}),  html.Br(),

       dcc.Markdown('Upcoming features',
             className="markdown_style"),
       html.Br(),
    dcc.Markdown('',
                 className="markdown_style"),
                        html.Br(),
                        html.Br(),
                        html.Br(),

                        dcc.Markdown('Do you have any questions or suggestions for features you would like to see implemented in the next update of NMAstudio?'
                            , className="markdown_style"),
                        html.Br(),

                        dcc.Markdown('Get in touch at silvia.metelli@u-paris.fr'
                            , className="markdown_style"),
    ])
