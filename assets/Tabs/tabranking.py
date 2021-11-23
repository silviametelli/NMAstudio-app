import dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq
from assets.COLORS import *

tab_ranking= dcc.Tabs(id='subtabs-rank1', value='subtab-rank1', vertical=False, persistence=True,
                             children=[
                         dcc.Tab(label='P-scores Heatmap', id='tab-rank1', value='Tab-rank1', className='control-tab',
                                 style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px', 'color': 'grey', 'padding': '0'},
                                 selected_style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                 'align-items': 'center',
                                                 'font-size': '12px', 'padding': '0'},
                                 children=[html.Div([
                                     html.Div([
                                     dbc.Row([
                                         dbc.Col([html.P("Outcome 1", style={'display':'inline-block',
                                                                                          'color':'white', 'font-size':'13px',
                                                                                          'padding-left':'20px'}),
                                             html.P(
                                                 "Beneficial",
                                                 id='rankswitchlabel1',
                                                 style={'display': 'inline-block',
                                                        'margin': 'auto',
                                                        'font-size': '10px',
                                                        'padding-left': '5px'}),
                                                 daq.ToggleSwitch(
                                                     id='toggle_rank_direction',
                                                     color='', size=30, vertical=False,
                                                     label={'label': "",
                                                            'style': dict(color='white', font='0.5em')},
                                                     labelPosition="top",
                                                     style={'display': 'inline-block',
                                                            'margin': 'auto', 'font-size': '10px',
                                                            'padding-left': '5px',
                                                            'padding-right': '5px'}),
                                                 html.P('Harmful',
                                                        id='rankswitchlabel2',
                                                        style={'display': 'inline-block',
                                                               'margin': 'auto',
                                                               'font-size': '10px',
                                                               'padding-right': '5px'})])
                                     ])]),
                                     html.Div([
                                     dbc.Row([
                                         dbc.Col([html.P("Outcome 2", style={'display':'inline-block',
                                                                                          'color':'white', 'font-size':'13px',
                                                                                          'padding-left':'20px'}),
                                             html.P(
                                                 "Beneficial",
                                                 id='rank2switchlabel1',
                                                 style={'display': 'inline-block',
                                                        'margin': 'auto',
                                                        'font-size': '10px',
                                                        'padding-left': '5px'}),
                                                 daq.ToggleSwitch(
                                                     id='toggle_rank2_direction',
                                                     color='', size=30, vertical=False,
                                                     label={'label': "",
                                                            'style': dict(color='white', font='0.5em')},
                                                     labelPosition="top",
                                                     style={'display': 'inline-block',
                                                            'margin': 'auto', 'font-size': '10px',
                                                            'padding-left': '5px',
                                                            'padding-right': '5px'}),
                                                 html.P('Harmful',
                                                        id='rank2switchlabel2',
                                                        style={'display': 'inline-block',
                                                               'margin': 'auto',
                                                               'font-size': '10px',
                                                               'padding-right': '0px'})]),
                                              ])], style={'margin-top':'-3px'})

                                 ]),
                                     dcc.Loading(
                                         dcc.Graph(
                                             id='tab-rank1',
                                             style={'height': '98%',
                                                    'max-height': 'calc(50vh)',
                                                    'width': '99%',
                                                    'margin-top': '1%',
                                                    'max-width': 'calc(52vw)'},
                                             config={'editable': True,
                                                #     'showEditInChartStudio': True,
                                                #     'plotlyServerURL': "https://chart-studio.plotly.com",
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
                                                         'scale': 3
                                                         # Multiply title/legend/axis/canvas sizes by this factor
                                                     },
                                                     'displaylogo': False}))

                                 ]),


                         dcc.Tab(label='P-scores Scatter plot', id='tab-rank2', value='Tab-rank2', className='control-tab',
                                 style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px', 'color': 'grey', 'padding': '0'},
                                 selected_style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                 'align-items': 'center',
                                                 'font-size': '12px', 'padding': '0'},
                                 children=[html.Div([
                                     html.Div([
                                     dbc.Row([
                                         dbc.Col([html.P("Outcome 1", style={'display':'inline-block',
                                                                                          'color':'white', 'font-size':'13px',
                                                                                          'padding-left':'20px'}),
                                             html.P(
                                                 "Beneficial",
                                                 id='rank2switchlabel11',
                                                 style={'display': 'inline-block',
                                                        'margin': 'auto',
                                                        'font-size': '10px',
                                                        'padding-left': '5px'}),
                                                 daq.ToggleSwitch(
                                                     id='toggle_rank2_direction_outcome1',
                                                     color='', size=30, vertical=False,
                                                     label={'label': "",
                                                            'style': dict(color='white', font='0.5em')},
                                                     labelPosition="top",
                                                     style={'display': 'inline-block',
                                                            'margin': 'auto', 'font-size': '10px',
                                                            'padding-left': '5px',
                                                            'padding-right': '5px'}),
                                                 html.P('Harmful',
                                                        id='rank2switchlabel22',
                                                        style={'display': 'inline-block',
                                                               'margin': 'auto',
                                                               'font-size': '10px',
                                                               'padding-right': '5px'})])
                                     ])]),
                                     html.Div([
                                     dbc.Row([
                                         dbc.Col([html.P("Outcome 2", style={'display':'inline-block',
                                                                                          'color':'white', 'font-size':'13px',
                                                                                          'padding-left':'20px'}),
                                             html.P(
                                                 "Beneficial",
                                                 id='rankswitchlabel11',
                                                 style={'display': 'inline-block',
                                                        'margin': 'auto',
                                                        'font-size': '10px',
                                                        'padding-left': '5px'}),
                                                 daq.ToggleSwitch(
                                                     id='toggle_rank2_direction_outcome2',
                                                     color='', size=30, vertical=False,
                                                     label={'label': "",
                                                            'style': dict(color='white', font='0.5em')},
                                                     labelPosition="top",
                                                     style={'display': 'inline-block',
                                                            'margin': 'auto', 'font-size': '10px',
                                                            'padding-left': '5px',
                                                            'padding-right': '5px'}),
                                                 html.P('Harmful',
                                                        id='rankswitchlabel22',
                                                        style={'display': 'inline-block',
                                                               'margin': 'auto',
                                                               'font-size': '10px',
                                                               'padding-right': '0px'})]),
                                              ])], style={'margin-top':'-3px'})

                                 ]),

                                     dcc.Loading(
                                         dcc.Graph(
                                             id='tab-rank2',
                                             style={'height': '99%',
                                                    'max-height': 'calc(52vh)',
                                                    'width': '96%',
                                                    'margin-top': '1%',
                                                    'max-width': 'calc(52vw)'},
                                             config={'editable': True,
                                                  #   'showEditInChartStudio': True,
                                                  #   'plotlyServerURL': "https://chart-studio.plotly.com",
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
                                                         'scale': 3
                                                         # Multiply title/legend/axis/canvas sizes by this factor
                                                     },
                                                     'displaylogo': False}))

                                 ]),

                        ],  colors={ "border": 'grey', "primary": "grey", "background": CLR_BCKGRND})
