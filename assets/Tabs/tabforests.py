import dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq
from assets.COLORS import *

tab_forests = dcc.Tabs(id='subtabs1', value='subtab1', vertical=False, persistence=True,
                             children=[
                         dcc.Tab(label='NMA', id='tab1', value='Tab1', className='control-tab',
                                 style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px', 'color': 'grey', 'padding': '0'},
                                 selected_style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                 'align-items': 'center',
                                                 'font-size': '12px', 'padding': '0'},
                                 children=[html.Div([dbc.Row([
                                     dbc.Col(html.P(id='tapNodeData-info', className="box__title",
                                                    style={'font-size':'12px', 'margin-top':'0.8%',
                                                           'display': 'flex','flex-flow' : 'row nowrap',
                                                           'flex-grow': '0', 'justify-content': 'flex-start'})),
                                 ]),
                                    html.Div([dbc.Col([html.P(
                                                 "Outcome 1",
                                                 id='forestswitchlabel_outcome1',
                                                 style={'display': 'inline-block',
                                                        'margin': 'auto',
                                                        'font-size': '10px',
                                                        'padding-left': '0px'}),
                                                 daq.ToggleSwitch(
                                                     id='toggle_forest_outcome',
                                                     color='', size=30, vertical=False,
                                                     label={'label': "",
                                                            'style': dict(color='white', font='0.5em')},
                                                     labelPosition="top",
                                                     style={'display': 'inline-block',
                                                            'margin': 'auto', 'font-size': '10px',
                                                            'padding-left': '2px',
                                                            'padding-right': '2px'}),
                                                 html.P('Outcome 2',
                                                        id='forestswitchlabel_outcome2',
                                                        style={'display': 'inline-block',
                                                               'margin': 'auto',
                                                               'font-size': '10px',
                                                               'padding-right': '0px'})
                                             ], style={'flex-grow': '1', 'justify-content': 'flex-end',
                                                       'display': 'flex', 'margin-left': '70%',
                                                       'font-size': '0.8em', 'margin-top': '-2.5%'},
                                             ),
                                             dbc.Col([
                                                 html.P(
                                                 "Beneficial",
                                                 id='forestswitchlabel1',
                                                 style={'display': 'inline-block',
                                                        'margin': 'auto',
                                                        'font-size': '10px',
                                                        'padding-left': '-1px'}),
                                                 daq.ToggleSwitch(
                                                     id='toggle_forest_direction',
                                                     color='', size=30, vertical=False,
                                                     label={'label': "",
                                                            'style': dict(color='white', font='0.5em')},
                                                     labelPosition="top",
                                                     style={'display': 'inline-block',
                                                            'margin': 'auto', 'font-size': '10px',
                                                            'padding-left': '2px',
                                                            'padding-right': '2px'}),
                                                 html.P('Harmful',
                                                        id='forestswitchlabel2',
                                                        style={'display': 'inline-block',
                                                               'margin': 'auto',
                                                               'font-size': '10px',
                                                               'padding-right': '0px'})
                                             ], style={'flex-grow': '1', 'justify-content': 'flex-end',
                                                       'display': 'flex', 'margin-left': '70%',
                                                       'font-size': '0.8em', 'margin-top': '0.5%'},
                                             ),
                                     dcc.Loading(
                                             dcc.Graph(
                                                id='tapNodeData-fig',
                                                style={'height': '99%',
                                                       'max-height': 'calc(52vw)',
                                                       'width': '98%',
                                                       'margin-top':'1%',
                                                        'max-width': 'calc(52vw)'},
                                                 config={'editable': True,
                                                       #  'showEditInChartStudio': True,
                                                       #  'plotlyServerURL': "https://chart-studio.plotly.com",
                                                         'edits': dict(annotationPosition=True,
                                                                      annotationTail=True,
                                                                      annotationText=True, axisTitleText=False,
                                                                      colorbarPosition=False,
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
                                                         'scale': 3
                                                         # Multiply title/legend/axis/canvas sizes by this factor
                                                     },
                                                     'displaylogo': False}))])
                                        ])

                                 ]),
                                 dcc.Tab(label='Pairwise', id='tab2', value='Tab2',  className='control-tab',
                                         style={'height':'30%', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                'font-size':'12px', 'color':'grey','padding': '0'},
                                         selected_style={'height':'30%', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                         'font-size':'12px','padding': '0'},
                                         children=[html.Div([html.P(
                                             id='tapEdgeData-info', style={'font-size':'12px', 'margin-top':'0.8%'},
                                             className="box__title"),
                                             dbc.Col([html.P(
                                                 "Outcome 1",
                                                 id='forest_pair_switchlabel_outcome1',
                                                 style={'display': 'inline-block',
                                                        'margin': 'auto',
                                                        'font-size': '10px',
                                                        'padding-left': '0px'}),
                                                 daq.ToggleSwitch(
                                                     id='toggle_forest_pair_outcome',
                                                     color='', size=30, vertical=False,
                                                     label={'label': "",
                                                            'style': dict(color='white', font='0.5em')},
                                                     labelPosition="top",
                                                     style={'display': 'inline-block',
                                                            'margin': 'auto', 'font-size': '10px',
                                                            'padding-left': '2px',
                                                            'padding-right': '2px'}),
                                                 html.P('Outcome 2',
                                                        id='forest_pair_switchlabel_outcome2',
                                                        style={'display': 'inline-block',
                                                               'margin': 'auto',
                                                               'font-size': '10px',
                                                               'padding-right': '0px'})
                                             ], style={'flex-grow': '1', 'justify-content': 'flex-end',
                                                       'display': 'flex', 'margin-left': '70%',
                                                       'font-size': '0.8em', 'margin-top': '-1.5%'},
                                             ),
                                             html.Br()]),
                                             dcc.Loading(
                                                 html.Div([
                                                     dcc.Graph(
                                                         id='tapEdgeData-fig-pairwise',
                                                         style={'height': '99%',
                                                                'max-height': 'calc(52vw)',
                                                                'width': '99%',
                                                                'margin-top': '-2.5%',
                                                                'max-width': 'calc(52vw)'},
                                                         config={'editable': True,
                                                               #  'showEditInChartStudio': True,
                                                               #  'plotlyServerURL': "https://chart-studio.plotly.com",
                                                         'edits': dict(annotationPosition=True,
                                                                      annotationTail=True,
                                                                      annotationText=True, axisTitleText=False,
                                                                      colorbarPosition=False,
                                                                      colorbarTitleText=False,
                                                                      titleText=False,
                                                                      legendPosition=True, legendText=True,
                                                                      shapePosition=True),
                                                             'modeBarButtonsToRemove': [
                                                                 'toggleSpikelines',
                                                                 "pan2d",
                                                                 "select2d",
                                                                 "lasso2d",
                                                                 "autoScale2d",
                                                                 "hoverCompareCartesian"],
                                                             'toImageButtonOptions': {
                                                                 'format': 'png',
                                                                 # one of png, svg,
                                                                 'filename': 'custom_image',
                                                                 'scale': 3
                                                                 # Multiply title/legend/axis/canvas sizes by this factor
                                                             },
                                                             'displaylogo': False})])

                                             ),
                                         ]),

                                 dcc.Tab(label='Bi-dimensional NMA', id='tab3', value='Tab3',  className='control-tab',
                                         style={'height':'30%', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                'font-size':'12px', 'color':'grey','padding': '0'},
                                         selected_style={'height':'30%', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                         'font-size':'12px','padding': '0'},
                                         children=[
                                             html.Div([html.P(id='tapNodeData-info-bidim', className="box__title",
                                                              style={'font-size':'12px', 'margin-top':'0.8%'}),
                                                       html.Br()]),
                                             dcc.Loading(
                                                 html.Div([
                                                     dcc.Graph(
                                                         id='tapNodeData-fig-bidim',
                                                         style={'height': '99%',
                                                                'max-height': 'calc(52vw)',
                                                                'width': '99%',
                                                                'margin-top': '-2.5%',
                                                                'max-width': 'calc(52vw)'},
                                                         config={'editable': True,
                                                               #  'showEditInChartStudio': True,
                                                               #  'plotlyServerURL': "https://chart-studio.plotly.com",
                                                                 'showTips': True,
                                                                 'edits': dict(annotationPosition=True,
                                                                               annotationTail=True, annotationText=True,
                                                                               axisTitleText=True,
                                                                               colorbarPosition=True,
                                                                               colorbarTitleText=True, titleText=False,
                                                                               legendPosition=True, legendText=True,
                                                                               shapePosition=True),
                                                                 'modeBarButtonsToRemove': [
                                                                     'toggleSpikelines',
                                                                     "pan2d",
                                                                     "select2d",
                                                                     "lasso2d",
                                                                     "autoScale2d",
                                                                     "hoverCompareCartesian"],
                                                                 'toImageButtonOptions': {
                                                                     'format': 'png',
                                                                     # one of png, svg,
                                                                     'filename': 'custom_image',
                                                                     'scale': 2.5
                                                                     # Multiply title/legend/axis/canvas sizes by this factor
                                                                 },
                                                                 'displaylogo': False})])
                                             )],
                                         )
                             ], colors={ "border": 'grey', "primary": "grey", "background": CLR_BCKGRND})