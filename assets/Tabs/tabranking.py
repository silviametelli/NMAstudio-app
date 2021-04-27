import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from assets.COLORS import *

tab_ranking= dcc.Tabs(id='subtabs-rank1', value='subtab-rank1', vertical=False, persistence=True,
                             children=[
                         dcc.Tab(label='Heatmap', id='tab-rank1', value='Tab-rank1', className='control-tab',
                                 selected_style={'height':'6px', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                                 'font-size':'12px', 'color':'grey'},
                                 style={'height':'6px', 'display': 'flex', 'justify-content':'center', 'align-items':'center',
                                        'font-size':'12px'},
                                 children=[html.Div()]),
                         dcc.Tab(label='Parallel plot', id='tab-rank2', value='Tab-rank2', className='control-tab',
                                 selected_style={'height': '6px', 'display': 'flex',
                                                 'justify-content': 'center', 'align-items': 'center',
                                                 'font-size': '12px', 'color': 'grey'},
                                 style={'height': '6px', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px'},
                                 children=[html.Div()]),

                        ],  colors={ "border": 'grey', "primary": "grey", "background": CLR_BCKGRND})
