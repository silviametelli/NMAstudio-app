####### contains all lists of values for the app modals #######

#import dash_core_components as dcc
from dash import dcc
import dash_bootstrap_components as dbc, dash_html_components as html
import dash_table, dash_daq as daq
from assets.COLORS import *
import dash_cytoscape as cyto
from assets.cytoscape_styleesheeet import get_stylesheet

from assets.storage import USER_ELEMENTS


options_format = [dict(label='long',     value='long'),
                  dict(label='contrast', value='contrast'),
                  dict(label='iv',       value='iv')
                  ]
options_outcomes = [dict(label='continuous', value='continuous'),
                    dict(label='binary', value='binary')]


Input_color = dcc.Input(id="node_color_input",
                type="text",
                style={'background-color':'#40515e','margin-left':'-px', 'font-size':'10.5px', 'padding-left':'-2px',
                       'color':'white'},
                placeholder="Type color name / Hex")

Input_color_edge = dcc.Input(id="edge_color_input",
                type="text",
                style={'background-color':'#40515e','margin-left':'-px', 'font-size':'10.5px', 'padding-left':'-2px',
                       'color':'white'},
                placeholder="Type color name / Hex")


modal = dbc.Modal([dbc.ModalHeader("Node color selection"),
                   dbc.ModalBody(Input_color),
                   dbc.ModalFooter(dbc.Button("Close", id="close_modal_dd_nclr_input", n_clicks=0, className="ml-auto"))
                  ],
            id="modal",style={'background-color':'#40515e','margin-left':'-px', 'font-size':'10.5px', 'padding-left':'-2px'})

modal_edges = dbc.Modal([dbc.ModalHeader("Edge color selection"),
                   dbc.ModalBody(Input_color_edge),
                   dbc.ModalFooter(dbc.Button("Close", id="close_modal_dd_eclr_input", n_clicks=0, className="ml-auto"))
                  ],
            id="modal_edge",style={'background-color':'#40515e','margin-left':'-px', 'font-size':'10.5px', 'padding-left':'-2px'})

file_upload_controls=[html.Br(),
                      dbc.Col([html.P("Format*:", className="graph__title2",
                               style={'display': 'inline-block', 'margin-left': '5px',
                                      'paddingLeft': '5px','font-size': '11px','vertical-alignment':'middle'}),
                               html.Div(dcc.RadioItems(id='dropdown-format', options=options_format,
                                                       style={'width': '80px', 'margin-left': '-20px',
                                               'color': 'white', 'font-size': '11px',
                                               'background-color': CLR_BCKGRND}, labelStyle = {'margin-right': 10}),
                                        style={'display': 'inline-block', 'margin-bottom': '0px'})],
                              width="auto", style={'display': 'inline-block'}),

                      dbc.Col([html.P(["1",html.Sup("st"), " outcome*:"], className="graph__title2",
                                    style={'display': 'inline-block', 'paddingLeft': '10px','font-size': '11px'}),
                           html.Div(dcc.RadioItems(id='dropdown-outcome1', options=options_outcomes,
                                                  style={'width': '80px', 'margin-left': '-20px',
                                                         'color': 'white', 'font-size': '11px',
                                                         'background-color': CLR_BCKGRND}),
                                     style={'display': 'inline-block', 'margin-bottom': '0px'})],
                              width="auto", style={'display': 'inline-block'}),

                      dbc.Col([html.P(["2",html.Sup("nd"), " outcome:"], className="graph__title2",
                              style={'display': 'inline-block', 'paddingLeft': '10px','font-size': '11px'}),
                      html.Div(dcc.RadioItems(id='dropdown-outcome2', options=options_outcomes,
                                            style={'width': '80px', 'margin-left': '-20px',
                                                   'color': 'white', 'font-size': '11px',
                                                   'background-color': CLR_BCKGRND}),
                               style={'display': 'inline-block', 'margin-bottom': '0px'})],
                              width="auto", style={'display': 'inline-block'})
                      ]


modal_data = dbc.Modal([dbc.ModalHeader("Data selection"),
                        dbc.ModalBody([
                            dbc.Row([dbc.Col([html.Br(),
                                                         html.Div(dcc.Upload(['Drag and Drop or ', html.A('Select a File')],
                                                                id='datatable-upload', multiple=False,
                                                                className='control-upload',
                                                                style={'width': '100%','height': '60px',
                                                                       'lineHeight': '60px','borderWidth': '1px',
                                                                       'borderStyle': 'dashed','borderRadius': '5px',
                                                                       'textAlign': 'center', 'margin': '10px',
                                                                       'color':'white'},
                                                                ), style={'display': 'inline-block'}),
                                                         html.Div([html.P('', style={'padding-left':'10px'}),
                                                         html.P('',id='uploaded_datafile', style={'color':'violet', 'padding-left':"20px"})],
                                                                    style={'font-family':'italic', 'display': 'inline-block'})
                                                         ],style={'display': 'inline-block'}),
                                           dbc.Col([html.Br(),html.Ul(id="file-list", style={'margin-left': '15px', 'color':'white','opacity':'60%'})],
                                                   style={'display': 'inline-block'})
                                                 ]),
                                  dbc.Row(file_upload_controls,
                                          style={'display': 'none'},
                                          id='dropdowns-DIV'),
                                  html.Div(id='second-selection'),
                                  html.Div(id='third-selection'),
                                  ]),
    dbc.ModalFooter([dbc.Button("Upload", id="upload_modal_data", className="ml-auto", disabled=True)])
                  ], id="modal_data", centered=False, style={'background-color':'#40515e',"max-width": "none", "width": "50%"})


modal_checks = dbc.Modal(is_open=False, children=[
                   dbc.ModalHeader("Running data analysis"),
                   dbc.ModalBody([html.Div(id='data_checks_div', style={"color":"white"}),
                                  html.Br(),
                                  html.P("Data check:",style={"color":"white"}),
                                  dcc.Loading(id="loading-data-checks",
                                              children=[html.Div(children=[html.P(" ...",style={"color":"white"})],
                                                                 id='para-check-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("Network meta-analysis:", style={"color": "white"}),
                                  dcc.Loading(id="loading-data-analysis",
                                              children=[html.Div(children=[html.P(" ...",style={"color":"white"})],
                                                                 id='para-anls-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("Pairwise meta-analysis:", style={"color": "white"}),
                                  dcc.Loading(id="loading-data-analysis2",
                                              children=[html.Div(children=[html.P(" ...", style={"color": "white"})],
                                                                 id='para-pairwise-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("League table, Consistency and Ranking:", style={"color": "white"}),
                                  dcc.Loading(id="loading-data-analysis3",
                                              children=[html.Div(children=[html.P(" ...",style={"color":"white"})],
                                                                 id='para-LT-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("Funnel plot:", style={"color": "white"}),
                                  dcc.Loading(id="loading-data-analysis4",
                                              children=[html.Div(children=[html.P(" ...",style={"color":"white"})],
                                                                 id='para-FA-data')],
                                              type="default"),


                                  html.Br()]),
                   dbc.ModalFooter([dbc.Button("Submit", id="submit_modal_data", n_clicks=0, className="ml-auto", disabled=True)])
                        ], id="modal_data_checks", centered=False, style={'background-color':'#40515e',"max-width": "none", "width": "50%"})


modal_data_table = dbc.Modal([
                   dbc.ModalHeader("Data"),
                   dbc.ModalBody([html.Div(id='data-expand-body'),
                                  dash_table.DataTable(
                                      id='datatable-upload-container-expanded',
                                      editable=False,
                                      #fixed_columns={'headers': True, 'data': 1},
                                      fixed_rows={'headers': True, 'data': 0},
                                      style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                                  'color': 'white',
                                                  'minWidth': '30px',
                                                  'textAlign': 'center',
                                                  'border': '1px solid #5d6d95',
                                                  'overflow': 'hidden', 'whiteSpace': 'no-wrap',
                                                  'textOverflow': 'ellipsis',
                                                  'font-family': 'sans-serif',
                                                  'fontSize': 11},
                                      style_data_conditional=[
                                          {'if': {'row_index': 'odd'},
                                           'backgroundColor': 'rgba(0,0,0,0.2)'},
                                          {'if': {'state': 'active'},
                                           'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                           'border': '1px solid rgb(0, 116, 217)'}],
                                      style_header={'backgroundColor': 'rgb(26, 36, 43)',
                                                    'fontWeight': 'bold',
                                                    'border': '1px solid #5d6d95'},
                                      style_table={'overflowX': 'scroll',
                                                   'overflowY': 'scroll',
                                                   'height': '99%',
                                                   'max-height': 'calc(90vh)',
                                                   'width': '99%',
                                                   'minWidth': '100%',
                                                   'margin-top': '10px',
                                                   'padding': '5px 5px 5px 5px'},
                                      css=[{'selector': 'tr:hover',
                                            'rule': 'background-color: rgba(0, 0, 0, 0);'},
                                           {'selector': 'td:hover',
                                            'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])
                                  ]),
                   dbc.ModalFooter([
                       html.Div([html.Button('Export', id='data-export', n_clicks=0, className="btn-export",
                                   style={'margin-left': '5px', 'padding': '4px 4px 4px 4px',
                                          'color': 'white', 'fontSize': 11, 'text-align':'left',
                                          'font-weight': '900', 'font-family': 'sans-serif',
                                          'display': 'inline-block', 'vertical-align': 'top'}),
                                 dcc.Download(id="download_datatable")
                           ]),
                            dbc.Button("Close", id="close-data-expanded", className="ml-auto")])
                             ],
                             id="modal_data_table", centered=False, style={'background-color':'#40515e',
                                                                           "max-width": "none", "width": "90%"})



modal_league_table = dbc.Modal([
                     dbc.ModalHeader([html.Div("League Table",  style={'display': 'inline-block'}),
                                      html.Div([html.P("Risk of Bias", id='cinemaswitchlabel1_modal',
                                                       style={'display': 'inline-block',
                                                              'font-size': '12px',
                                                              'padding-left': '10px'}),
                                                daq.ToggleSwitch(id='rob_vs_cinema_modal',
                                                                 color='', size=30,
                                                                 labelPosition="bottom",
                                                                 style={'display': 'inline-block',
                                                                        'margin': 'auto',
                                                                        'padding-left': '10px',
                                                                        'padding-right': '10px'}),
                                                html.P('CINeMA rating', id='cinemaswitchlabel2_modal',
                                                       style={'display': 'inline-block', 'margin': 'auto',
                                                              'font-size': '12px',
                                                              'padding-right': '0px'})
                                                ], style={'float': 'right', 'padding': '5px 5px 5px 5px',
                                                          'display': 'inline-block', 'margin-top': '0px'}),
                                      html.Br(),
                                      ], style={'width': '100%', "max-width": "none"}), # Closes Header
                     dbc.ModalBody([html.Div(id='league-expand-body'),
                                    html.Div(id='modal_league_table_legend',
                                             style={'float': 'right',
                                             'padding': '5px 5px 5px 5px'}),
                                    html.Br(),
                                    html.Div(id='modal_league_table_data')
                                  ]),
                     dbc.ModalFooter([
                         html.Div([
                             html.Button('Export', id='league-export', n_clicks=0, className="btn-export",
                                                   style={'margin-left': '5px', 'padding': '4px 4px 4px 4px',
                                                          'color': 'white', 'fontSize': 11, 'text-align': 'left',
                                                          'font-weight': '900', 'font-family': 'sans-serif',
                                                          'display': 'inline-block', 'vertical-align': 'top'}),
                             dcc.Download(id="download_leaguetable")

                                  ]),
                         dbc.Button("Close", id="close-league-expanded", className="ml-auto")])
                     ],
                     id="modal_league_table", centered=False, style={'background-color': '#40515e',
                     "max-width": "none", "width": "90%"})



modal_network = dbc.Modal([
                     dbc.ModalBody([html.Div(id='network-expand-body'),
                                    html.Br(),
                                    html.Div(cyto.Cytoscape(id='modal-cytoscape',  responsive=True,
                                elements=[],
                                style={ 'height': '93vh', 'width': '100%',  'margin-top':'-30px', 'margin-bottom': '-30px',
                                        'padding-left':'-30px', 'margin-left': '-30px','margin-right': '-30px',  'z-index': '999',
                                        'z-compound-depth': 'orphan'
                                       },
                                stylesheet=get_stylesheet()),)
                                  ]),
                     dbc.ModalFooter([html.A(html.Img(src="/assets/icons/NETD.png",
                                                    style={'width': '50px', 'filter': 'invert()'}),
                                           id="btn-get-png-modal", style={'display': 'inline-block'}),
                         dbc.Button("Close", id="close-network-expanded", className="ml-auto")])
                     ],
                     id="modal_network", centered=False, style={'background-color': '#40515e',
                     "max-width": "none", "width": "70%",  "max-height":"100%", "height":"99%"})
