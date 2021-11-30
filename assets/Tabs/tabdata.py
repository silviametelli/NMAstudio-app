import numpy as np
from assets.dropdowns_values import *
from tools.utils import set_slider_marks
YEARS_DEFAULT = np.array([1963,1990,1997,2001,2003,2004,2005,2006,2007,2008,2010,
                          2011,2012,2013,2014,2015,2016,2017,2018,2019,2020])


def tab_data(years=YEARS_DEFAULT):
    y_max, y_min = years.max(), years.min()
    return html.Div([
                    html.Button('Upload your data', 'upload_your_data', n_clicks=0,
                        style={'margin-left': '5px', 'padding': '4px 4px 4px 4px',
                               'margin-top': '15px', 'color': 'violet', 'fontSize': 11,
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
                     html.Div(dcc.Slider(min=y_min, max=y_max,
                                         step=None,
                                         marks=set_slider_marks(y_min, y_max, years),
                                         value=y_max,
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
                         fixed_rows={'headers': True, 'data': 0 },
                         style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                                    'color': 'white',
                                    'minWidth': '45px',
                                    'textAlign': 'center',
                                    'border': '1px solid #5d6d95',
                                    'overflow': 'hidden','whiteSpace': 'no-wrap',
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
                                     'overflowY': 'scroll',
                                     'height': '99%',
                                     'max-height': '420px',
                                     'minWidth':'100%',
                                     'width': '99%',
                                     'max-width': 'calc(52vw)',
                                     'padding': '5px 5px 5px 5px'},
                         css=[
                           {'selector': 'tr:hover',
                             'rule': 'background-color: rgba(0, 0, 0, 0);'},
                            {'selector': 'td:hover',
                             'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])
                     ])
