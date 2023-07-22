import dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq
from assets.COLORS import *

tab_ranking= dcc.Tabs(id='subtabs-rank1', value='subtab-rank1', vertical=False, persistence=True,
                             children=[
                         dcc.Tab(label='P-scores Heatmap', id='tab-rank1', value='Tab-rank1', className='control-tab',
                                 style={'height': '40%', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px', 'color': 'grey', 'padding': '0'},
                                 selected_style={'height': '40%', 'display': 'flex', 'justify-content': 'center',
                                                 'align-items': 'center',
                                                 'font-size': '12px', 'padding': '0'},
                                 children=[
                                     dcc.Loading(
                                         dcc.Graph(
                                             id='tab-rank1',
                                             style={'height': '99%',
                                                    'max-height': 'calc(51vh)',
                                                    'width': '99%',
                                                    'margin-top': '5%',
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
                                                         'scale': 5
                                                         # Multiply title/legend/axis/canvas sizes by this factor
                                                     },
                                                     'displaylogo': False}))

                                 ]),


                         dcc.Tab(label='P-scores Scatter plot', id='tab-rank2', value='Tab-rank2', className='control-tab',
                                 style={'height': '40%', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px', 'color': 'grey', 'padding': '0'},
                                 selected_style={'height': '40%', 'display': 'flex', 'justify-content': 'center',
                                                 'align-items': 'center',
                                                 'font-size': '12px', 'padding': '0'},
                                 children=[
                                     dcc.Loading(
                                         dcc.Graph(
                                             id='tab-rank2',
                                             style={'height': '99%',
                                                    'max-height': 'calc(51vh)',
                                                    'width': '96%',
                                                    'margin-top': '5%',
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
                                                         'scale': 5                                                         # Multiply title/legend/axis/canvas sizes by this factor
                                                     },
                                                     'displaylogo': False}))

                                 ]),

                        ],  colors={ "border": 'grey', "primary": "grey", "background": 'white'})
