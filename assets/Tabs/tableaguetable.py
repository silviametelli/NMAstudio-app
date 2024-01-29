from assets.dropdowns_values import *


tab_league = html.Div([
    dbc.Row([
       #   dbc.Col([
       #        html.A(
       #               html.Img(
       #                      src="/assets/icons/expand.png",
       #                      style={
       #                      "width": "34px",
       #                      "margin-top": "15px",
       #                      "border-radius": "1px",
       #                      },
       #               ),
       #               id="data-expand2",
       #               style={"display": "inline-block", "margin-left": "10px"},
       #               ),
       #               dbc.Tooltip(
       #               "expand window",
       #               style={
       #                      "color": "black",
       #                      "font-size": 9,
       #                      "margin-left": "10px",
       #                      "letter-spacing": "0.3rem",
       #               },
       #               placement="right",
       #               target="data-expand",
       #               ),
       #               html.A(
       #               html.Img(
       #                      src="/assets/icons/zoomout.png",
       #                      style={
       #                      "width": "34px",
       #                      "margin-top": "15px",
       #                      "border-radius": "1px",
       #                      },
       #               ),
       #               id="data-zoomout2",
       #               style={"display": "none", "margin-left": "10px"},
       #               ),
       #               dbc.Tooltip(
       #               "Zoom out window",
       #               style={
       #                      "color": "black",
       #                      "font-size": 9,
       #                      "margin-left": "10px",
       #                      "letter-spacing": "0.3rem",
       #               },
       #               placement="right",
       #               target="data-zoomout",
       #               )], style={'display':'inline-block'}
       #                               ),
       #  dbc.Col([
       #      html.A(html.Img(src="/assets/icons/expand.png",
       #                                style={'width': '34px',
       #                                       'margin-top': '0px',
       #                                       'margin-bottom': '2px',
       #                                       'border-radius': '1px', }),
       #                       id="league-expand",
       #                       style={'margin-left': '10px'}),
       #                dbc.Tooltip("expand table", style={'color': 'black', 'font-size': 9,
       #                                                   'margin-left': '10px', 'letter-spacing': '0.3rem'},
       #                            placement='bottom',
       #                            target='league-expand'), ])
                                  ]),

        dbc.Row([html.Div([
                             html.Button('Export', id='league-export', n_clicks=0, className="btn-export",
                                                   style={'margin-left': '5px', 'padding': '4px 4px 4px 4px',
                                                           'fontSize': 11, 'text-align': 'left',
                                                          'font-weight': '900', 'font-family': 'sans-serif',
                                                          'display': 'inline-block', 'vertical-align': 'top'}),
                             dcc.Download(id="download_leaguetable")

                                  ]),
              dbc.Col([html.Div([html.P("Upload the CINeMA report file in its original format, with mandatory columns “Comparison” and “Confidence rating”",
                         id='cinema-instruction',),
                     html.A(
                           html.Img(
                                   src="/assets/icons/query.png",
                                   style={
                                   "width": "16px",
                                   "float":"right",},)),],
                     id="queryicon-cinima"),
                     dcc.Upload(html.A('Upload CINeMA report 1 for outcome 1',
                      style={'margin-left': '5px', 'font-size':'12px','color':'rgb(90, 135, 196)'}),
               id='datatable-secondfile-upload', 
               multiple=False,
               style={'display': 'inline-block', 'font-size': '12px', 'padding-left': '45px'})],
               style={'display': 'inline-block'}),
              dbc.Col([html.Ul(id="file2-list", style={'margin-left': '15px', 'color':'#dae8e8',
                                                 'font-size':'11px'})],
            style={'display': 'inline-block'}
            ),
            dbc.Col([dcc.Upload(html.A('Upload CINeMA report 2 for outcome 2',
                                   style={'margin-left': '5px', 'margin-top': '1px', 'font-size': '12px',
                                          'padding-bottom': '4px','color':'rgb(90, 135, 196)'}),
                            id='datatable-secondfile-upload-2', multiple=False,
                            style={'display': 'inline-block', 'font-size': '12px'})],
                style={'display': 'inline-block'}),
            dbc.Col([html.Ul(id="file2-list-2", style={'margin-left': '15px', 'color': '#dae8e8',
                                                       'font-size': '11px', 'vertical-alignment':'middle'})],
                style={'display': 'inline-block', 'margin-top': '0px', 'margin-bottom': '0px'}
                )
              # dbc.Col(
              #        [html.P(f"Select outcomes",className="selectbox", style={'display': 'inline-block', "text-align": 'right',
              #                                                  'margin-left': '0px', 'font-size': '12px'}),
              #         dcc.Dropdown(id='league_outcome_select', searchable=True, placeholder="...", className="box",
              #               clearable=False, value=0,
              #               style={'width': '80px',  # 'height': '30px',
              #                      "height": '30px',
              #                      'vertical-align': 'middle',
              #                      "font-family": "sans-serif",
              #                      'margin-bottom': '2px',
              #                      'display': 'inline-block',
              #                      'color': 'black',
              #                      'font-size': '10px','margin-left':'-7px'})]
              #                      )
            ]),
       # dbc.Col(dbc.Row(
       #        [html.P(f"Select outcomes",className="selectbox", style={'display': 'inline-block', "text-align": 'right',
       #                                                         'margin-left': '0px', 'font-size': '12px'}),
       #        dcc.Dropdown(id='league_outcome_select', searchable=True, placeholder="...", className="box",
       #                      clearable=False, value=0,
       #                      style={'width': '80px',  # 'height': '30px',
       #                             "height": '30px',
       #                             'vertical-align': 'middle',
       #                             "font-family": "sans-serif",
       #                             'margin-bottom': '2px',
       #                             'display': 'inline-block',
       #                             'color': 'black',
       #                             'font-size': '10px','margin-left':'-7px'})]),
       #                             style={'margin-bottom': '0px'}),

        html.Div([html.P("Risk of Bias", id='cinemaswitchlabel1',
                              style={'display': 'inline-block',
                                     'font-size': '12px',
                                     'padding-left': '10px'}),
                       daq.ToggleSwitch(id='rob_vs_cinema',
                                        value=False,
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
       #  html.Br(),
       #  dbc.Row([dbc.Col([dcc.Upload(html.A('Upload CINeMA report 2 for outcome 2',
       #                             style={'margin-left': '5px', 'margin-top': '1px', 'font-size': '12px',
       #                                    'padding-bottom': '4px','color':'rgb(90, 135, 196)'}),
       #                      id='datatable-secondfile-upload-2', multiple=False,
       #                      style={'display': 'inline-block', 'font-size': '12px', 'padding-left': '100px'})],
       #          style={'display': 'inline-block', 'margin-top': '-4px'}),
       #      dbc.Col([html.Ul(id="file2-list-2", style={'margin-left': '15px', 'color': '#dae8e8',
       #                                                 'font-size': '11px', 'vertical-alignment':'middle'})],
       #          style={'display': 'inline-block', 'margin-top': '0px', 'margin-bottom': '0px'}
       #          ),]),

    html.Div(id='league_table_legend',
              style={
                     'display': 'flex',
                     'width':'100%',
                     'justify-content': 'end',
                     'padding': '5px 5px 5px 5px'}),
    html.Div(id='league_table'),
    html.Div(id='img_div')
]) #className="data__container")