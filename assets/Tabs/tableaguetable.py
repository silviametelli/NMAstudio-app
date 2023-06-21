from assets.dropdowns_values import *


tab_league = html.Div([
    dbc.Row([dbc.Col([html.A(html.Img(src="/assets/icons/expand.png",
                                      style={'width': '34px',
                                             'filter': 'invert()',
                                             'margin-top': '0px',
                                             'margin-bottom': '2px',
                                             'border-radius': '1px', }),
                             id="league-expand",
                             style={'margin-left': '10px'}),
                      dbc.Tooltip("expand table", style={'color': 'white', 'font-size': 9,
                                                         'margin-left': '10px', 'letter-spacing': '0.3rem'},
                                  placement='right',
                                  target='league-expand'), ])]),

        dbc.Row([dbc.Col([dcc.Upload(html.A('Upload CINeMA report 1',
                      style={'margin-left': '5px', 'font-size':'12px'}),
               id='datatable-secondfile-upload', multiple=False,
               style={'display': 'inline-block', 'font-size': '12px', 'padding-left': '100px'})],
               style={'display': 'inline-block', 'margin-top': '-10px'}),
        dbc.Col([html.Ul(id="file2-list", style={'margin-left': '15px', 'color':'#dae8e8',
                                                 'font-size':'11px'})],
            style={'display': 'inline-block', 'margin-top': '-5px'}
            ),]),
        html.Div([html.P("Upload the CINeMA report file in its original format, with mandatory columns “Comparison” and “Confidence rating”",
                         id='cinema-instruction',),
                     html.A(
                           html.Img(
                                   src="/assets/icons/query.png",
                                   style={
                                   "width": "16px",
                                   "margin-top": "0px",
                                   "border-radius": "0px",
                                   "float":"right",},)),],
                     id="queryicon-cinima",),

        html.Div([html.P("Risk of Bias", id='cinemaswitchlabel1',
                              style={'display': 'inline-block',
                                     'font-size': '12px',
                                     'padding-left': '10px'}),
                       daq.ToggleSwitch(id='rob_vs_cinema',
                                        color='', size=30,
                                        labelPosition="bottom",
                                        style={'display': 'inline-block',
                                               'margin': 'auto',
                                               'padding-left': '10px',
                                               'padding-right': '10px'}),
                       html.P('CINeMA rating', id='cinemaswitchlabel2',
                              style={'display': 'inline-block', 'margin': 'auto',
                                     'font-size': '12px',
                                     'padding-right': '0px'})
                       ],  style={'float': 'right', 'padding': '5px 5px 5px 5px',
                                  'display': 'inline-block', 'margin-top': '-2px' }),
        html.Br(),
        dbc.Row([dbc.Col([dcc.Upload(html.A('Upload CINeMA report 2',
                                   style={'margin-left': '5px', 'margin-top': '1px', 'font-size': '12px',
                                          'padding-bottom': '4px'}),
                            id='datatable-secondfile-upload-2', multiple=False,
                            style={'display': 'inline-block', 'font-size': '12px', 'padding-left': '144px'})],
                style={'display': 'inline-block', 'margin-top': '-4px'}),
            dbc.Col([html.Ul(id="file2-list-2", style={'margin-left': '15px', 'color': '#dae8e8',
                                                       'font-size': '11px', 'vertical-alignment':'middle'})],
                style={'display': 'inline-block', 'margin-top': '0px', 'margin-bottom': '0px'}
                ),]),

    html.Div(id='league_table_legend',
             style={'float': 'right',
                    'padding': '5px 5px 5px 5px'}),
    html.Div(id='league_table'),
    html.Div(id='img_div')
]) #className="data__container")