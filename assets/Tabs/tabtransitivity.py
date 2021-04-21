import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from app import OPTIONS_VAR

tab_trstvty = html.Div([dbc.Row([html.P("Choose effect modifier:", className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",
                                                'font-size': '12px',
                                                'margin-bottom': '-10px'}),
                                  dcc.Dropdown(id='dropdown-effectmod', options=OPTIONS_VAR,
                                               clearable=True, placeholder="",
                                               className="tapEdgeData-fig-class",
                                               style={'width': '150px', 'height': '30px',
                                                      'display': 'inline-block', # 'background-color': '#40515e'
                                                      })
                                  ])], style={'margin-top':'4px'})

boxplot = html.Div([dcc.Graph(id='tapEdgeData-fig',
                     style={'height': '99%',
                           'max-height': '400px',
                           'width': '99%',
                           'max-width': 'calc(52vw)'},
                                  config={'editable': True,
                                          'edits': dict(annotationPosition=True,
                                                    annotationTail=True,
                                                    annotationText=True, axisTitleText=True,
                                                    colorbarPosition=True,
                                                    colorbarTitleText=True,
                                                    titleText=False,
                                                    legendPosition=True, legendText=True,
                                                    shapePosition=True),
                                          'modeBarButtonsToRemove': ['toggleSpikelines', "pan2d",
                                                                 "select2d", "lasso2d",
                                                                 "autoScale2d",
                                                                 "hoverCompareCartesian"],
                                          'toImageButtonOptions': {'format': 'png', # one of png, svg,
                                                               'filename': 'custom_image',
                                                               'scale': 10 # Multiply title/legend/axis/canvas sizes by this factor
                                                               },
                                          'displaylogo': False})
                    ], style={'margin-top':'-25px'})