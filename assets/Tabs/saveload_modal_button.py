import dash_bootstrap_components as dbc
from dash import html, dcc

saveload_modal = html.Div(
        [
            dbc.Button("Save/Load Project", id="open_saveload", n_clicks=0, style={'margin-top':'-8.5px', 'padding-top':'0px'}),
            dbc.Modal(dcc.Tabs(id='all-tabs-saveload', persistence=True, children=[

                            dcc.Tab(style={'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'},
                                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                                    'align-items': 'center'},
                                    label='Save Project',
                                    children=html.Div(className='control-tab', children=[

                 dbc.ModalBody("Please upload your data first. You can generate your own username and click on the button Generate Token Your Project to get a sharable token for your NMA analysis.\n "
                               "\n Please note the analysis will be publicly accessible to anyone you have shared the link with."
                                         ),
                 html.Br(),
                 dbc.ModalBody("Username must be at least 6 characters"),
                 html.Br(),

                 html.Div([html.H4("USERNAME:", style={'display': 'inline-block', 'margin-left': '1%', 'color':'white'}),
                           dcc.Input(id='input-username', type="text", placeholder="",
                                     style={'margin-left': '2%', 'display': 'inline-block', 'width': "20%"}),
                           html.Div(id="output_username", style={'margin-left': '1%', 'width': "45%"}),
                           ],
                          style={'font-size': '20px', 'color': '#587485', 'padding-left': '3%',
                                 'padding-right': '3%', 'font-family': 'sans-serif', "font-weight": "530"}
                          ),

                 html.Br(), html.Br(),

                 html.Div([html.Button("CREATE TOKEN", id='button-token',
                                       style={'display': 'inline-block', 'margin-left': '1%', "color": "#dbe5be",
                                              'background-color': '#708c98'}),

                           html.Div(id="output_token", style={'font-size': '22px', 'padding-left': '4%',
                                                              'padding-right': '3%', 'display': 'inline-block',
                                                              'font-family': 'sans-serif',
                                                              "font-weight": "410", "color": "white"}),
                           ],
                          style={'font-size': '20px', 'color': '#587485', 'padding-left': '3%',
                                 'padding-right': '3%', 'font-family': 'sans-serif', "font-weight": "530"}
                          ),

                 html.Br(), html.Br(),

                 dbc.ModalFooter(dbc.Button("Close", id="close_saveload", className="ms-auto", n_clicks=0)),

                                    ],
                                                      style={'overflowX': 'auto',
                                                             'overflowY': 'auto',
                                                             'height': '99%', 'font-family': 'sans-serif', 'font-size': '20px',  "color": "white",
                                                             })
                                    ),

                dcc.Tab(
                    style={'color': 'grey', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                    selected_style={'color': 'grey', 'display': 'flex', 'justify-content': 'center',
                                    'align-items': 'center'},
                    label='Load Project',
                    children=html.Div(className='control-tab', children=[

                 dbc.ModalBody("You can retrieve a project by entering the associated Token that has been shared with you.",style={'font-size': '20px', 'margin-left': '1%', 'color': 'white'}),
                 html.Br(),
                 dbc.ModalBody(""),
                 html.Br(),
                        html.Div([html.H4("ENTER YOUR TOKEN:",
                                          style={'display': 'inline-block', 'margin-left': '1%', 'color': 'white'}),
                                  dcc.Input(id='input-token-load', type="text", placeholder="",
                                            style={'margin-left': '2%', 'display': 'inline-block', 'width': "20%"}),
                                  html.Div(id="output_token_entered", style={'margin-left': '1%', 'width': "45%", 'color': 'white'}),

                                  ],
                                 style={'font-size': '20px', 'color': '#587485', 'padding-left': '3%',
                                        'padding-right': '3%', 'font-family': 'sans-serif', "font-weight": "530"}
                                 ),

                        html.Br(), html.Br(),

                        html.Div([html.Button("LOAD EXISTING PROJECT", id='load-project',
                                              style={'display': 'inline-block', 'margin-left': '1%', "color": "#dbe5be",
                                                     'background-color': '#708c98'}),

                                  html.Div(id="output_load_project", style={'font-size': '22px', 'padding-left': '4%',
                                                                     'padding-right': '3%', 'display': 'inline-block',
                                                                     'font-family': 'sans-serif',
                                                                     "font-weight": "410", "color": "white"}),
                                  ],
                                 style={'font-size': '20px', 'color': '#587485', 'padding-left': '3%',
                                        'padding-right': '3%', 'font-family': 'sans-serif', "font-weight": "530"}
                                 ),

                        html.Br(), html.Br(),

                        dbc.ModalFooter(dbc.Button("Close", id="close_saveload_2", className="ms-auto", n_clicks=0)),

                    ],
                                      style={'overflowX': 'auto',
                                             'overflowY': 'auto',
                                             'height': '99%',
                                             }),
                    )


            ]), #close dcc.Tabs

                id="modal_saveload",
                is_open=False,
                size="xl",
                style={"max-width": "none", "width": "70%", "font-size":"16px", "border": "1px solid gray",
                            "color": "white",'font-family':'sans-serif',
                             "background-color": "#d7dbda"},
            ),
        ]
    )