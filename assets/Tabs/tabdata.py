import numpy as np
from app import  GLOBAL_DATA
from assets.dropdowns_values import *

tab_data = html.Div([
                    html.Button('Upload your data', 'data-upload', n_clicks=0,
                        style={'margin-left': '5px', 'padding': '4px 4px 4px 4px',
                               'margin-top': '15px', 'color': 'white', 'fontSize': 11,
                               'font-weight': '900', 'font-family': 'sans-serif',
                                'display': 'inline-block','vertical-align': 'middle'}),
                    html.A(html.Img(src="/assets/icons/expand.png",
                                    style={'width': '34px', 'filter': 'invert()',
                                           'margin-top': '15px', 'border-radius': '1px'}),
                            id="data-expand", style={'display': 'inline-block', 'margin-left': '10px'}),
                     dbc.Tooltip("expand table", style={'color': 'white',
                                                       'font-size': 9,
                                                       'margin-left': '10px',
                                                       'letter-spacing': '0.3rem'},
                                                 placement='right', target='data-expand'),
                     html.Div(dcc.Slider(min=GLOBAL_DATA["y_min"], max=GLOBAL_DATA["y_max"],
                                         step=None,
                                         marks = {int(x): {'label': str(x),
                                                           'style': {'color': 'white', 'font-size':'10px',
                                                                     'opacity':1 if x in (GLOBAL_DATA['y_min'],
                                                                                          GLOBAL_DATA['y_max']) else 0
                                                                     }}
                                                    for x in np.unique(GLOBAL_DATA['net_data']['year'].dropna()).astype('int')
                                                 },
                                         value=GLOBAL_DATA['y_max'],
                                         updatemode='drag',
                                         id='slider-year',
                                         tooltip=dict(placement='top')),
                              style={'display': 'inline-block',
                                     'width': '50%',
                                     'float': 'right',
                                     'color': CLR_BCKGRND2,
                                     'padding-top': '25px',
                                     'margin-right': '10px',
                                     'margin-left': '15px'}),
                     html.Br(),

                     dash_table.DataTable(
                         id='datatable-upload-container',
                         editable=False,
                        # export_format="csv",
                         style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                    'color': 'white',
                                    'border': '1px solid #5d6d95',
                                    'textOverflow': 'ellipsis',
                                    'font-family': 'sans-serif',
                                    'fontSize': 11},
                         style_data_conditional=[
                            {'if': {'row_index': 'odd'},
                             'backgroundColor': 'rgba(0,0,0,0.2)'},
                            {'if': {'state': 'active'},
                             'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                             'border': '1px solid rgb(0, 116, 217)'}],
                         style_header={'backgroundColor': 'rgb(26, 36, 43)',
                                      'fontWeight': 'bold',
                                      'border': '1px solid #5d6d95'},
                         style_table={'overflowX': 'scroll',
                                     'overflowY': 'auto',
                                     'height': '99%',
                                     'max-height': '400px',
                                     'width': '99%',
                                     'max-width': 'calc(52vw)',
                                     'padding': '5px 5px 5px 5px'},
                         css=[
                           {'selector': 'tr:hover',
                             'rule': 'background-color: rgba(0, 0, 0, 0);'},
                            {'selector': 'td:hover',
                             'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])
                     ])