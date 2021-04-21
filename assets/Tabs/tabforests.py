import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq
from assets.COLORS import *

tab_forests = dcc.Tabs(id='subtabs1', value='subtab1', vertical=False, persistence=True,
                             children=[
                         dcc.Tab(label='NMA', id='tab1', value='Tab1', className='control-tab',
                                 selected_style={'height':'6px', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                 'font-size':'12px', 'color':'grey'},
                                 style={'height':'6px', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                        'font-size':'12px'},
                                 children=[html.Div([dbc.Row([
                                     dbc.Col(html.P(id='tapNodeData-info', className="box__title",
                                                    style={'display': 'inline-block', 'font-size':'12px'})),
                                     dbc.Col([html.P(
                                         "Beneficial",
                                         id='forestswitchlabel1',
                                         style={'display': 'inline-block',
                                                'margin': 'auto',
                                                'font-size': '10px',
                                                'padding-left': '50px'}),
                                         daq.ToggleSwitch(
                                             id='toggle_forest_direction',
                                             color='', size=30, vertical=False,
                                             label={'label': "Outcome",
                                                    'style': dict(color='white', font='10px')},
                                             labelPosition="top",
                                             style={'display': 'inline-block',
                                                    'margin': 'auto', 'font-size': '10px',
                                                    'padding-left': '20px',
                                                    'padding-right': '20px'}),
                                         html.P('Harmful',
                                                id='forestswitchlabel2',
                                                style={'display': 'inline-block',
                                                       'margin': 'auto',
                                                       'font-size': '10px',
                                                       'padding-right': '20px'})
                                     ], style={'margin-left': '52%','margin-top':'-2%', 'font-size':'0.8em'})

                                 ]),
                                 ]),
                                     html.Div([
                                         dcc.Loading(
                                             dcc.Graph(
                                                id='tapNodeData-fig',
                                                style={'height': '99%',
                                                       'max-height': '300px',
                                                        'width': '99%',
                                                        'max-width': 'calc(52vw)'},
                                                 config={
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
                                                         'scale': 10
                                                         # Multiply title/legend/axis/canvas sizes by this factor
                                                     },
                                                     'displaylogo': False}))])

                                 ]),
                                 dcc.Tab(label='Pairwise', id='tab2', value='Tab2',  className='control-tab',
                                         style={'height':'6px', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                'font-size':'12px', 'color':'grey'},
                                         selected_style={'height':'6px', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                         'font-size':'12px'},
                                         children=[html.Div([html.P(
                                             id='tapEdgeData-info', style={'font-size':'12px'},
                                             className="box__title"),
                                             html.Br()]),
                                             dcc.Loading(
                                                 html.Div([
                                                     dcc.Graph(
                                                         id='tapEdgeData-fig-pairwise',
                                                         style={'height': '99%',
                                                                'max-height': '400px',
                                                                'width': '99%',
                                                                'max-width': 'calc(52vw)'},
                                                         config={
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
                                                                 'scale': 10
                                                                 # Multiply title/legend/axis/canvas sizes by this factor
                                                             },
                                                             'displaylogo': False})])

                                             ),
                                         ]),

                                 dcc.Tab(label='Two-dimensional', id='tab3', value='Tab3',  className='control-tab',
                                         style={'height':'6px', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                'font-size':'12px', 'color':'grey'},
                                         selected_style={'height':'6px', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                         'font-size':'12px'},
                                         children=[
                                             html.Div([html.P(id='tapNodeData-info-bidim', className="box__title", style={'font-size':'12px'}),
                                                       html.Br()]),
                                             dcc.Loading(
                                                 html.Div([
                                                     dcc.Graph(
                                                         id='tapNodeData-fig-bidim',
                                                         style={'height': '99%',
                                                                'max-height': '300px',
                                                                'width': '99%',
                                                                'max-width': 'calc(52vw)'},
                                                         config={'editable': True,
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
                                                                     'scale': 10
                                                                     # Multiply title/legend/axis/canvas sizes by this factor
                                                                 },
                                                                 'displaylogo': False})])
                                             )],
                                         )
                             ], colors={ "border": 'grey', "primary": "grey", "background": CLR_BCKGRND})