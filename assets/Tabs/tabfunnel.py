import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc


tab_funnel = html.Div([html.P("Click nodes sequentially to get the desired treatment ordering",
                                         className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",
                                                'font-size': '12px',
                                                'margin-bottom': '-10px'})])