####### contains all lists of values for the app modals #######

import dash_core_components as dcc
import dash_bootstrap_components as dbc, dash_html_components as html
import dash_table, dash_daq as daq
from assets.COLORS import *


options_format = [{'label':'long',      'value':'long'},
                  {'label':'contrast',  'value':'contrast'}
                  ]
options_outcomes = [{'label':'continuous',      'value':'continuous'},
                   {'label':'binary',  'value':'binary'}
                   ]


Input_color = dcc.Input(id="node_color_input",
                type="text",
                style={'background-color':'#40515e','margin-left':'-px', 'font-size':'10.5px', 'padding-left':'-2px',
                       'color':'white'},
                placeholder="Type color name / Hex")


modal = dbc.Modal([dbc.ModalHeader("Node color selection"),
                   dbc.ModalBody(Input_color),
                   dbc.ModalFooter(dbc.Button("Close", id="close_modal_dd_nclr_input", className="ml-auto"))
                  ],
            id="modal",style={'background-color':'#40515e','margin-left':'-px', 'font-size':'10.5px', 'padding-left':'-2px'})

modal_data = dbc.Modal([
                   dbc.ModalHeader("Data selection"),
                   dbc.ModalBody([dbc.Row([dbc.Col([html.Br(),
                                                     dcc.Upload(html.A('Upload main data file*',
                                                                            style={'margin-left': '5px'}),
                                                                     id='datatable-upload', multiple=False,
                                                                     style={'display': 'inline-block'})
                                                 ],style={'display': 'inline-block'}),
                                           dbc.Col([html.Ul(id="file-list", style={'margin-left': '15px', 'color':'white','opacity':'60%'})],
                                                   style={'display': 'inline-block'})
                                                 ]),
                                                 dbc.Row([html.Br(),
                                                     dbc.Col([html.P("Format*:", className="graph__title2",
                                                              style={'display': 'inline-block', 'margin-left': '5px',
                                                                     'paddingLeft': '5px','font-size': '11px','vertical-alignment':'middle'}),
                                                              html.Div(dcc.RadioItems(id='dropdown-format',
                                                                                      options=options_format,
                                                                                      style={'width': '80px', 'margin-left': '-20px',
                                                                              'color': 'white', 'font-size': '11px',
                                                                              'background-color': CLR_BCKGRND}),
                                                                       style={'display': 'inline-block', 'margin-bottom': '0px'})],
                                                             width="auto", style={'display': 'inline-block'}),

                                                     dbc.Col([html.P(["1",html.Sup("st"), " outcome*:"], className="graph__title2",
                                                                   style={'display': 'inline-block', 'paddingLeft': '10px','font-size': '11px'}),
                                                          html.Div(dcc.RadioItems(id='dropdown-outcome1', options=options_outcomes,
                                                                                 style={'width': '80px', 'margin-left': '-20px',
                                                                                        'color': 'white', 'font-size': '11px',
                                                                                        'background-color': CLR_BCKGRND}),
                                                                    style={'display': 'inline-block', 'margin-bottom': '0px'})],width="auto", style={'display': 'inline-block'}),

                                                     dbc.Col([html.P(["2",html.Sup("nd"), " outcome:"], className="graph__title2",
                                                             style={'display': 'inline-block', 'paddingLeft': '10px','font-size': '11px'}),
                                                     html.Div(dcc.RadioItems(id='dropdown-outcome2', options=options_outcomes,
                                                                           style={'width': '80px', 'margin-left': '-20px',
                                                                                  'color': 'white', 'font-size': '11px',
                                                                                  'background-color': CLR_BCKGRND}),
                                                              style={'display': 'inline-block',
                                                                     'margin-bottom': '0px'
                                                                     })],width="auto", style={'display': 'inline-block'})
                                                 ]),html.Div(id='second-selection')
                                           ]),
                    dbc.ModalFooter([dbc.Button("Submit", id="submit_modal_data", className="ml-auto", disabled=True)])
                  ], id="modal_data", centered=False, style={'background-color':'#40515e',"max-width": "none", "width": "50%"})


modal_data_table = dbc.Modal([
                   dbc.ModalHeader("Data"),
                   dbc.ModalBody([html.Div(id='data-expand-body'),
                                  dash_table.DataTable(
                                      id='datatable-upload-container-expanded',
                                      editable=False,
                                      style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                                  'color': 'white',
                                                  'border': '1px solid #5d6d95',
                                                  'textOverflow': 'ellipsis',
                                                  'font-family': 'sans-serif',
                                                  'fontSize': 11,
                                                  },
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
                                                   'overflowY': 'auto',
                                                   'height': '90%',
                                                   'max-height': 'calc(70vh)',
                                                   'width': '99%',
                                                   'margin-top': '10px',
                                                   'padding': '5px 5px 5px 5px'},
                                      css=[{'selector': 'tr:hover',
                                            'rule': 'background-color: rgba(0, 0, 0, 0);'},
                                           {'selector': 'td:hover',
                                            'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])
                                  ]),
                   dbc.ModalFooter([dbc.Button("Close", id="close-data-expanded", className="ml-auto")])
                             ],
                             id="modal_data_table", centered=False, style={'background-color':'#40515e',
                                                                           "max-width": "none", "width": "90%"})


modal_league_table = dbc.Modal([
                     dbc.ModalHeader([dbc.Row([html.Div("League Table", style={'display': 'inline-block'}),
                                               html.Div([html.P("Risk of Bias", id='cinemaswitchlabel1_modal',
                                                                  style={'display': 'inline-block', 'margin': 'auto',
                                                                         'font-size': '12px',
                                                                         'padding-left': '10px'}),
                                                        daq.ToggleSwitch(id='rob_vs_cinema_modal',
                                                                         color='', size=30,
                                                                         labelPosition="bottom",
                                                                         style={'display': 'inline-block',
                                                                                'margin': 'auto',
                                                                                'padding-left': '10px',
                                                                                'padding-right': '10px'}),
                                                        html.P('CINeMA grade', id='cinemaswitchlabel2_modal',
                                                                style={'display': 'inline-block', 'margin': 'auto',
                                                                       'font-size': '12px',
                                                                       'padding-right': '0px'})
                                                ], style={'display': 'inline-block', 'float':'right'})
                                              ],style={'width': '100%'})
                                      ], style={'width': '100%'}),
                     dbc.ModalBody([html.Div(id='league-expand-body'),
                                    html.Div(id='modal_league_table_legend',
                                             style={'float': 'right',
                                             'padding': '5px 5px 5px 5px'}),
                                    html.Br(),
                                    html.Div(id='modal_league_table_data')
                                  ]),
                     dbc.ModalFooter([dbc.Button("Close", id="close-league-expanded", className="ml-auto")])
                     ],
                     id="modal_league_table", centered=False, style={'background-color': '#40515e',
                     "max-width": "none", "width": "90%"})
