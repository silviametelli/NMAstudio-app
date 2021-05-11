import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc


tab_funnel = html.Div([html.P("Click nodes sequentially to get the desired treatment ordering",
                                         className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",
                                                'font-size': '12px',
                                                'margin-bottom': '-10px'}),

                       dcc.Loading(
                           dcc.Graph(
                               id='tab-funnel',
                               style={'height': '99%',
                                      'max-height': 'calc(49vw)',
                                      'width': '98%',
                                      'margin-top': '1%',
                                      'max-width': 'calc(52vw)'},
                               config={'editable': True,
                                       'showEditInChartStudio': True,
                                       'plotlyServerURL': "https://chart-studio.plotly.com",
                                       'edits': dict(annotationPosition=True,
                                                     annotationTail=True,
                                                     annotationText=True, axisTitleText=True,
                                                     colorbarPosition=True,
                                                     colorbarTitleText=False,
                                                     titleText=False,
                                                     legendPosition=True, legendText=True,
                                                     shapePosition=True),
                                       'modeBarButtonsToRemove': [
                                           'toggleSpikelines',
                                           'resetScale2d',
                                           "pan2d",
                                           "select2d",
                                           "lasso2d",
                                           "autoScale2d",
                                           "hoverCompareCartesian"],
                                       'toImageButtonOptions': {
                                           'format': 'png',
                                           # one of png, svg,
                                           'filename': 'custom_image',
                                           'scale': 10
                                           # Multiply title/legend/axis/canvas sizes by this factor
                                       },
                                       'displaylogo': False}))
                       ])