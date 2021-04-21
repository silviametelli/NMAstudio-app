from assets.dropdowns_values import *


tab_league = html.Div([dbc.Row([
        dbc.Col([dcc.Upload(html.A('Upload CINeMA file',
                      style={'margin-left': '5px', 'margin-top': '10px'}),
               id='datatable-secondfile-upload', multiple=False,
               style={'display': 'inline-block', 'font-size': '12px','margin-top': '10px'})],
               style={'display': 'inline-block'}),
        dbc.Col([html.Ul(id="file2-list", style={'margin-left': '15px', 'color':'grey'})],
            style={'display': 'inline-block', 'margin-top': '10px', 'margin-bottom': '10px'}
            ),
        dbc.Col([html.Div([html.P("Risk of Bias", id='cinemaswitchlabel1',
                              style={'display': 'inline-block', 'margin': 'auto',
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
                       ], style={'float':'right','margin-left': '50%',
                                 'width': '100%', 'margin-top': '10px'})

             ], style={'display': 'inline-block'})]),
            html.Br(),
            html.A(html.Img(src="/assets/icons/expand.png",
                    style={'width': '34px',
                           'filter': 'invert()',
                           'margin-top': '-10px',
                           'margin-bottom': '2px',
                           'border-radius': '1px', }),
                    id="league-expand",
                    style={'margin-left': '10px'}),
             dbc.Tooltip("expand table", style={'color': 'white', 'font-size': 9,
                                                'margin-left': '10px', 'letter-spacing': '0.3rem'},
                placement='right',
                target='league-expand'),
    html.Div(id='league_table_legend',
             style={'float': 'right',
                    'padding': '5px 5px 5px 5px'}),
    html.Div(id='league_table')]) #className="data__container")