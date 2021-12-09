import dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq

tab_funnel = html.Div([dbc.Row([dbc.Col(html.P("Click treatment sequentially to get desired ordering",
                                         className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",
                                                'font-size': '12px',
                                                'margin-bottom': '-10px'}))
                                ]),
                    dbc.Col([
                             html.P(
                             "Outcome 1",
                             id='funnelswitchlabel1',
                             style={'display': 'inline-block',
                                    'margin': 'auto',
                                    'font-size': '10px',
                                    'padding-left': '0px'}),
                             daq.ToggleSwitch(
                                 id='toggle_funnel_direction',
                                 color='',
                                 size=30, vertical=False,
                                 label={'label': "",
                                        'style': dict(color='white', font='0.5em')},
                                 labelPosition="top",
                                 style={'display': 'inline-block',
                                        'margin': 'auto', 'font-size': '10px',
                                        'padding-left': '2px',
                                        'padding-right': '2px'}),
                             html.P('Outcome 2',
                                    id='funnelswitchlabel2',
                                    style={'display': 'inline-block',
                                           'margin': 'auto',
                                           'font-size': '10px',
                                           'padding-right': '0px'})],
                             style={'flex-grow': '1', 'justify-content': 'flex-end',
                                   'display': 'flex', 'margin-left': '70%',
                                   'font-size': '0.8em', 'margin-top': '-5.5%'},
                             ),
                       dcc.Loading(
                           dcc.Graph(
                               id='funnel-fig',
                               style={'height': '99%',
                                      'max-height': 'calc(50vw)',
                                      'width': '98%',
                                      'margin-top': '1%',
                                      'max-width': 'calc(52vw)'},
                               config={'editable': True,
                                      # 'showEditInChartStudio': True,
                                      # 'plotlyServerURL': "https://chart-studio.plotly.com",
                                       'edits': dict(annotationPosition=True,
                                                     annotationTail=True,
                                                    # annotationText=True, axisTitleText=True,
                                                     colorbarPosition=True,
                                                     colorbarTitleText=False,
                                                     titleText=False,
                                                     legendPosition=True, legendText=True,
                                                     shapePosition=False),
                                       'modeBarButtonsToRemove': [
                                           'toggleSpikelines',
                                           'resetScale2d',
                                           "pan2d",
                                           "select2d",
                                           "lasso2d",
                                           "autoScale2d",
                                           "hoverCompareCartesian"],
                                       'toImageButtonOptions': {
                                           'format': 'png',  # one of png, svg,
                                           'filename': 'custom_image',
                                           'scale': 5
                                       },
                                       'displaylogo': False}))
                       ])
