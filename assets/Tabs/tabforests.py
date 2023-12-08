import dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq
from assets.COLORS import *


tab_forests = dcc.Tabs(id='', value='subtab1', vertical=False, persistence=True,
                             children=[
                         dcc.Tab(label='NMA', id='tab1', value='Tab1', className='control-tab',
                                 style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px', 'color': 'black', 'padding': '0'},
                                 selected_style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                 'align-items': 'center',
                                                 'font-size': '12px', 'padding': '0'},
                                 children=[html.Div([dbc.Row([
                                     dbc.Col(html.P(id='tapNodeData-info', className="box__title",
                                                    style={'font-size':'12px', 'margin-top':'0.8%',
                                                           'display': 'inline-block','flex-flow' : 'row nowrap',
                                                           'flex-grow': '0', 'justify-content': 'flex-start'}), style={'display': 'inline-block'}),
                                     dbc.Col(dbc.Row(
                                                 [html.P(f"Select outcomes",className="selectbox", 
                                                         style={'display': 'flex', "text-align": 'right','align-items': 'center',
                                                                'margin-right': '10px', 'font-size': 'small'}),
                                                 dcc.Dropdown(id='forest_outcome_select', searchable=True, placeholder="...", className="box", value=0,
                                                               clearable=False, 
                                                               style={'width': '80px',  # 'height': '30px',
                                                                      "height": '30px',
                                                                      'vertical-align': 'middle',
                                                                      "font-family": "sans-serif",
                                                                      'margin-bottom': '2px',
                                                                      'display': 'inline-block',
                                                                      'color': 'black',
                                                                      'font-size': '10px','margin-left':'-7px'})], className='slect-out-row'),
                                                                      className='slect-out-dropdown')],

                                                                className='tab_row_all'),
                                    html.Div([
                                     html.Div(dcc.Loading(
                                             dcc.Graph(
                                                id='tapNodeData-fig',
                                                style={'height': '100%',
                                                 #       'max-height': 'calc(100vh)',
                                                       'width': '98%',
                                                       'margin-top':'1%',
                                                        # 'max-width': 'calc(52vw)',
                                                        },
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
                                                         'scale': 3.5
                                                         # Multiply title/legend/axis/canvas sizes by this factor
                                                     },
                                                     'displaylogo': False})),style={'height': '450px', 'overflow':'scroll'}
                                                     )])
                                        ])

                                 ]),
                                 dcc.Tab(label='Pairwise', id='tab2', value='Tab2',  className='control-tab',
                                         style={'height':'30%', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                'font-size':'12px', 'color':'black','padding': '0'},
                                         selected_style={'height':'30%', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                         'font-size':'12px','padding': '0'},
                                         children=[html.Div([dbc.Row([
                                          dbc.Col(html.P(
                                             id='tapEdgeData-info', style={'font-size':'12px', 'margin-top':'0.8%'},
                                             className="box__title"),style={'display': 'inline-block'}),
                                          dbc.Col(dbc.Row(
                                                 [html.P(f"Select outcomes",className="selectbox", style={'display': 'flex', 
                                                                                                          "text-align": 'right',
                                                                                                          'align-items': 'center',
                                                                                                          'margin-right': '10px', 'font-size': 'small'}),
                                                 dcc.Dropdown(id='forestpaire_outcome_select', searchable=True, placeholder="...", className="box", value=0,
                                                               clearable=False, 
                                                               style={'width': '80px',  # 'height': '30px',
                                                                      "height": '30px',
                                                                      'vertical-align': 'middle',
                                                                      "font-family": "sans-serif",
                                                                      'margin-bottom': '2px',
                                                                      'display': 'inline-block',
                                                                      'color': 'black',
                                                                      'font-size': '10px','margin-left':'-7px'})], className='slect-out-row'),
                                                                      className='slect-out-dropdown'),
                                                                      html.Br()], className='tab_row_all')], style={'height':'35px'}),
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
                                                                 'scale': 3.5
                                                                 # Multiply title/legend/axis/canvas sizes by this factor
                                                             },
                                                             'displaylogo': False})], style={'height': '450px', 'overflow':'scroll'})

                                             ),
                                         ]),

                                 dcc.Tab(label='Bi-dimensional NMA', id='black', value='Tab3',  className='control-tab',
                                         style={'height':'30%', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                'font-size':'12px', 'color':'grey','padding': '0'},
                                         selected_style={'height':'30%', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                         'font-size':'12px','padding': '0'},
                                         children=[
                                             dbc.Row([dbc.Col(html.P([html.Div(id='tapNodeData-info-bidim', className="box__title",
                                                              style={'font-size':'12px', 'margin-top':'0.8%', 'display': 'inline','padding': '2px 2px 2px 2px'}),
                                                        html.Div([ html.P("Click on the color point of the treatment to remove the corresponding treatment in the plot.",
                                                        id='forest-instruction',),
                                                                  html.A( html.Img( src="/assets/icons/query.png",
                                                                                    style={ "width": "16px",
                                                                                            "margin-top": "0px",
                                                                                            "border-radius": "0px"},)),
                                                         ],style={'display': 'inline'},id="queryicon-forest"),              
                                                       html.Br()]),style={'display': 'inline-block'}),
                                              dbc.Col(dbc.Row(
                                                 [html.P(f"Select outcome 1",className="selectbox", style={'display': 'flex', 
                                                                                                          "text-align": 'right',
                                                                                                          'align-items': 'center',
                                                                                                          'margin-right': '12px', 'font-size': '12px'}),
                                                 dcc.Dropdown(id='biforest_outcome_select1', searchable=True, placeholder="...", className="box", value=0,
                                                               clearable=False, 
                                                               style={'width': '80px',  # 'height': '30px',
                                                                      "height": '30px',
                                                                      'vertical-align': 'middle',
                                                                      "font-family": "sans-serif",
                                                                      'margin-bottom': '2px',
                                                                      'display': 'inline-block',
                                                                      'color': 'black',
                                                                      'font-size': '10px','margin-left':'-7px'}),
                                                 html.P(f"Select outcome 2",className="selectbox", style={'display': 'flex', 
                                                                                                          "text-align": 'right',
                                                                                                          'align-items': 'center',
                                                                                                          'margin-left': '10px', 'font-size': '12px'}),
                                                 dcc.Dropdown(id='biforest_outcome_select2', searchable=True, placeholder="...", className="box", value=1,
                                                               clearable=False, 
                                                               style={'width': '80px',  # 'height': '30px',
                                                                      "height": '30px',
                                                                      'vertical-align': 'middle',
                                                                      "font-family": "sans-serif",
                                                                      'margin-bottom': '2px',
                                                                      'display': 'inline-block',
                                                                      'color': 'black',
                                                                      'font-size': '10px','margin-left':'-7px'})], className='slect-out-row'),
                                                                      style={'display': 'inline-grid', 'width': '450px'})],className='tab_row_all'),
                                             dcc.Loading(
                                                 html.Div([
                                                     dcc.Graph(
                                                         id='tapNodeData-fig-bidim',
                                                         style={'height': '99%',
                                                                'max-height': 'calc(52vw)',
                                                                'width': '99%',
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
                             ], colors={ "border": 'grey', "primary": "grey", 'background': 'white'})