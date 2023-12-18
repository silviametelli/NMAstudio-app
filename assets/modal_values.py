####### contains all lists of values for the app modals #######

#import dash_core_components as dcc
from dash import dcc
import dash_bootstrap_components as dbc, dash_html_components as html
import dash_table, dash_daq as daq
from assets.COLORS import *
import dash_cytoscape as cyto
from assets.cytoscape_styleesheeet import get_stylesheet
from assets.Tabs.tabtransitivity import tab_trstvty

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

file_upload_controls = [html.Br(),
                       dbc.Col([html.P("Note: before uploading your data, read our tutorial for details on variable requirements", className="graph__title2",
                               style={'display': 'inline-block', 'margin-left': '5px',
                                      'paddingLeft': '5px','font-size': '11px','vertical-alignment':'middle'})]),
                       html.Br(),
                       dbc.Col([html.P("Format*:", className="graph__title2",
                               style={'display': 'inline-block', 'margin-left': '5px',
                                      'paddingLeft': '5px','font-size': '11px','vertical-alignment':'middle'}),
                               html.Div(dcc.RadioItems(id='dropdown-format', options=options_format,
                                                       style={'width': '80px', 'margin-left': '-20px',
                                               'color': 'black', 'font-size': '11px'}, labelStyle = {'margin-right': 10}),
                                        style={'display': 'inline-block', 'margin-bottom': '0px'})],
                              width="auto", style={'display': 'inline-block'}),

                       dbc.Col([html.P(["1",html.Sup("st"), " outcome*:"], className="graph__title2",
                                    style={'display': 'inline-block', 'paddingLeft': '10px','font-size': '11px'}),
                           html.Div(dcc.RadioItems(id='dropdown-outcome1', options=options_outcomes,
                                                  style={'width': '80px', 'margin-left': '-20px',
                                                         'color': 'black', 'font-size': '11px',}),
                                     style={'display': 'inline-block', 'margin-bottom': '0px'})],
                              width="auto", style={'display': 'inline-block'}),

                       dbc.Col([html.P(["2",html.Sup("nd"), " outcome:"], className="graph__title2",
                              style={'display': 'inline-block', 'paddingLeft': '10px','font-size': '11px'}),
                       html.Div(dcc.RadioItems(id='dropdown-outcome2', options=options_outcomes,
                                            style={'width': '80px', 'margin-left': '-20px',
                                                   'color': 'black', 'font-size': '11px'}),
                               style={'display': 'inline-block', 'margin-bottom': '0px'})],
                              width="auto", style={'display': 'inline-block'})
                       ]


file_upload_controls2 = [
                       dbc.Row([html.P("Select the format of your dataset:", className="selcect_title",),
                               html.Div(dcc.RadioItems(id='radio-format', options=options_format, inline=True, className='upload_radio'))], 
                                        style={'display': 'grid', 
                                               'background-color': 'beige',
                                                'width': '500px',
                                                'justify-content': 'center'
                                               }),
                     #   html.Br(),
                     #   dbc.Row([html.P(["Select the type of the 1",html.Sup("st"), " outcome:"], className="selcect_title",),
                     #       html.Div(dcc.RadioItems(id='radio-outcome1', options=options_outcomes,inline=True,className='upload_radio'))],
                     #                   style={'display': 'grid',
                     #                          'background-color': 'antiquewhite',
                     #                          'width': '500px',
                     #                          'justify-content': 'center'
                     #                          }),
                     #   html.Br(),
                     #   dbc.Row([html.P(["Select the type of the2",html.Sup("nd"), " outcome (optional):"], className="selcect_optional",),
                     #   html.Div(dcc.RadioItems(id='radio-outcome2', options=options_outcomes,inline=True, className='upload_radio'))],
                     #             style={'display': 'grid',
                     #                    'background-color': 'khaki',
                     #                    'width': '500px',
                     #                    'justify-content': 'center'
                     #                    })
                       ]



model_transitivity = dbc.Modal([dbc.ModalHeader("Transitivity Check", style={'width':'1000px'}),
                                dbc.ModalBody(children=[tab_trstvty], style={'width':'1000px','display':'grid', 'justify-content':'center'}),
                                dbc.ModalFooter([dbc.Button('Go to the results', id='trans_to_results')],style={'width':'1000px'})
                                ], is_open=False , id='modal_transitivity', contentClassName="transitivity_class")

# modal_data = dbc.Modal([dbc.ModalHeader("Data selection"),
#                         dbc.ModalBody([
#                             dbc.Row([dbc.Col([html.Br(),
#                                                          html.Div(dcc.Upload(['Drag and Drop or ', html.A('Select a File')],
#                                                                 id='datatable-upload', multiple=False,
#                                                                 className='control-upload',
#                                                                 style={'width': '100%','height': '60px',
#                                                                        'lineHeight': '60px','borderWidth': '1px',
#                                                                        'borderStyle': 'dashed','borderRadius': '5px',
#                                                                        'textAlign': 'center', 'margin': '10px',
#                                                                        'color':'black'},
#                                                                 ), style={'display': 'inline-block'}),
#                                                          html.Div([html.P('', style={'padding-left':'10px'}),
#                                                          html.P('',id='uploaded_datafile', style={'color':'violet', 'padding-left':"20px"})],
#                                                                     style={'font-family':'italic', 'display': 'inline-block'})
#                                                          ],style={'display': 'inline-block'}),
#                                            dbc.Col([html.Br(),html.Ul(id="file-list", style={'margin-left': '15px', 'color':'white','opacity':'60%'})],
#                                                    style={'display': 'inline-block'})
#                                                  ]),
#                                   html.Div(dbc.Row(file_upload_controls),
#                                           style={'display': 'none'},
#                                           id="dropdowns-DIV",), 
#                                    html.Div([html.P("outcome 2 is optional",
#                                               id='outcome2-instruction',),
#                                               html.A(
#                                                html.Img(
#                                                  src="/assets/icons/query.png",
#                                                  style={
#                                                   "width": "12px",
#                                                   "margin-top": "0px",
#                                                   "border-radius": "0px",
#                                                   "float":"right",},)),
#                                                          ],
#                                                          style={'display': 'none'},
#                                                          id="queryicon-outcome2",), 
#                                    html.Div([ html.P("Data should be uploaded as CSV",
#                                               id='dataformat-instruction',),
#                                               html.A(
#                                                html.Img(
#                                                  src="/assets/icons/query.png",
#                                                  style={
#                                                   "width": "16px",
#                                                   "margin-top": "0px",
#                                                   "border-radius": "0px",
#                                                   "float":"right",
#                                                   'position':'relative'},)),
#                                                          ],id="queryicon-dataformat",),                            
#                                   html.Div(id='second-selection'),
#                                   html.Div([ html.P("study name or ID for each trial (numeric or string)",
#                                               id='studlb-instruction',),
#                                               html.A(
#                                                html.Img(
#                                                  src="/assets/icons/query.png",
#                                                  style={
#                                                   "width": "12px",
#                                                   "margin-top": "0px",
#                                                   "border-radius": "0px",
#                                                   "float":"right",},)),
#                                                          ],style={'display': 'none'},id="queryicon-studlb",),
#                                    html.Div([ html.P("study-level year of publication (numeric)",
#                                               id='year-instruction',),
#                                               html.A(
#                                                html.Img(
#                                                  src="/assets/icons/query.png",
#                                                  style={
#                                                   "width": "12px",
#                                                   "margin-top": "0px",
#                                                   "border-radius": "0px",
#                                                   "float":"right",},)),
#                                                          ],style={'display': 'none'},id="queryicon-year",),
#                                    html.Div([ html.P("should be encoded in your data file as either {1,2,3}, {l,m,h} or {L,M,H}",
#                                               id='rob-instruction',),
#                                               html.A(
#                                                html.Img(
#                                                  src="/assets/icons/query.png",
#                                                  style={
#                                                   "width": "12px",
#                                                   "margin-top": "0px",
#                                                   "border-radius": "0px",
#                                                   "float":"right",},)),
#                                                          ],style={'display': 'none'},id="queryicon-rob",),
#                                   html.Div(id='third-selection'),
#                                   ]),

       

#     dbc.ModalFooter([dbc.Col("Note:   the “Upload” button is activated only once all data selection fields are filled ",
#                                style={'display': 'block',
#                                        'color':'white',
#                                        'left':'-60px'}),
#                      dbc.Button("Upload", id="upload_modal_data", className="ml-auto", disabled=True), 
#                      ],)
#                   ], 
#                   id="modal_data", centered=False, style={'background-color':'#40515e',"max-width": "none", "width": "50%"})


modal_checks = dbc.Modal(is_open=False, children=[
                   dbc.ModalHeader("Running data analysis"),
                   dbc.ModalBody([html.Div(id='data_checks_div', style={"color":"black"}),
                                  html.Br(),
                                  html.P("Data check:",style={"color":"black"}),
                                  dcc.Loading(id="loading-data-checks",
                                              children=[html.Div(children=[html.P(" ...",style={"color":"black"})],
                                                                 id='para-check-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("Network meta-analysis:", style={"color": "black"}),
                                  dcc.Loading(id="loading-data-analysis",
                                              children=[html.Div(children=[html.P(" ...",style={"color":"black"})],
                                                                 id='para-anls-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("Pairwise meta-analysis:", style={"color": "black"}),
                                  dcc.Loading(id="loading-data-analysis2",
                                              children=[html.Div(children=[html.P(" ...", style={"color": "black"})],
                                                                 id='para-pairwise-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("League table, Consistency and Ranking:", style={"color": "black"}),
                                  dcc.Loading(id="loading-data-analysis3",
                                              children=[html.Div(children=[html.P(" ...",style={"color":"black"})],
                                                                 id='para-LT-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("Funnel plot:", style={"color": "black"}),
                                  dcc.Loading(id="loading-data-analysis4",
                                              children=[html.Div(children=[html.P(" ...",style={"color":"black"})],
                                                                 id='para-FA-data')],
                                              type="default"),
                                  html.Br(),
                                  html.P("*Please check the treatment names within the dropdown list:", style={"color": "red"}),
                                  dcc.Dropdown(id='dropdown-intervention', 
                                               clearable=True, placeholder="",
                                               className="tapEdgeData-fig-class",
                                               style={'width': '150px', 'height': '30px',
                                                      'display': 'inline-block', 
                                                      }),

                                  html.Br()]),
                   dbc.ModalFooter([dbc.Button("Submit", id="submit_modal_data", className="ml-auto", disabled=True)])
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
                                                  'color': 'black',
                                                  'minWidth': '60px',
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
                                      style_header={'backgroundColor': '#738789',
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
                                          'color': 'black', 'fontSize': 11, 'text-align':'left',
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
                                             style={
                                                 'display': 'flex',
                                                 'width':'100%',
                                                 'justify-content': 'end',
                                                 'padding': '5px 5px 5px 5px'}),
                                    html.Br(),
                                    html.Div(id='modal_league_table_data')
                                  ]),
                     dbc.ModalFooter([
                         html.Div([
                             html.Button('Export', id='league-export', n_clicks=0, className="btn-export",
                                                   style={'margin-left': '5px', 'padding': '4px 4px 4px 4px',
                                                           'fontSize': 11, 'text-align': 'left',
                                                          'font-weight': '900', 'font-family': 'sans-serif',
                                                          'display': 'inline-block', 'vertical-align': 'top'}),
                             dcc.Download(id="download_leaguetable")

                                  ]),
                         dbc.Button("Close", id="close-league-expanded", className="ml-auto")])
                     ],
                     id="modal_league_table", centered=False, style={'background-color': '#40515e',
                     "max-width": "none", "width": "90%"})

cytoscape_main = cyto.Cytoscape(id='cytoscape', responsive=True, autoRefreshLayout=False,
                                        
                                elements=[],
                                style={ 
                                    'height': '70vh', 'width': '100%', 
                                       'margin-top': '10px',
                                        'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                                        'padding-left': '-10px', 
                                        'max-width': 'calc(52vw)',
                                       },
                                layout={'animate': False},
                                stylesheet=get_stylesheet())

modal_network = dbc.Modal([
                     dbc.ModalBody([html.Div(id='network-expand-body'),
                                    html.Br(),
                                    html.Div(cyto.Cytoscape(id='modal-cytoscape',  responsive=True, autoRefreshLayout=False,
                                elements=[],
                                style={ 'height': '93vh', 'width': '100%',  
                                       'margin-top':'-30px', 'margin-bottom': '-30px',
                                        'padding-left':'-30px', 'margin-left': '-30px','margin-right': '-30px',  'z-index': '999',
                                        'z-compound-depth': 'orphan'
                                       },
                                layout={'animate': False},
                                stylesheet=get_stylesheet()),)
                                  ]),
                     dbc.ModalFooter([html.A(html.Img(src="/assets/icons/NETD.png",
                                                    style={'width': '50px'}),
                                           id="btn-get-png-modal", style={'display': 'inline-block'}),
                         dbc.Button("Close", id="close-network-expanded", className="ml-auto")])
                     ],
                     id="modal_network", centered=False, style={'background-color': '#40515e',
                     "max-width": "none", "width": "70%",  "max-height":"100%", "height":"99%"})



modal_info = dbc.Toast([
                   dbc.ModalHeader([html.P("Overall Information",style={'font':'caption',
                                                                        'margin-top': '-12px',
                                                                        'margin-left': '-3px',
                                                                        'color':'black',
                                                                        }),
                                   html.Img(src="/assets/icons/cancel.png", 
                                            style={"width": "30px",
                                                   "float":"right",
                                                   'margin-top': '-27px','margin-right': '-60px','width':'18px'}, id ='close_modal_info')], 
                                   style={
                                       'height':'24px',
                                       'background-color':'#c4c7c9'
                                   }),
                   dbc.ModalBody([html.P( id='numstudies'),
                                  html.P( id='numtreat'),
                                  html.P(id='numcompar'),
                                  html.P(id='numcom_without')],style={'border': 'solid #c4c7c9 1px','font-size': 'small'}),
              #      dbc.ModalFooter(
              #          dbc.Button(html.P("close", style={"margin-left":'-17px'}), id="close_modal_info", n_clicks=0, className="ml-auto",
              #                                 style={'height':'20px',
              #                                        'width':'25px'}),style={'height':'24px','background-color':'#c4c7c9'}
              #                                        )
                  ],
            id="modal_info",style={'background-color':'white',
                                   'font-size':'10.5px', 
                                   'position':'absolute',
                                   'width':'200px'
                                   })

