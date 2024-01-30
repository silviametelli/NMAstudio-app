import dash_table, dash_daq as daq
import dash_html_components as html, dash_bootstrap_components as dbc
import dash_core_components as dcc

from assets.storage import CONSISTENCY_DATA

def tab_consistency(consistency_data=CONSISTENCY_DATA):
    return html.Div([
        html.Div([
       #      dbc.Col([
       #                       html.P(
       #                       "Outcome 1",
       #                       id='consistencyswitchlabel1',
       #                       style={'display': 'inline-block',
       #                              'margin': 'auto',
       #                              'font-size': '10px',
       #                              'padding-left': '0px'}),
       #                       daq.ToggleSwitch(
       #                           id='toggle_consistency_direction',
       #                           color='', size=30, vertical=False,
       #                           label={'label': "",
       #                                  'style': dict(color='white', font='0.5em')},
       #                           labelPosition="top",
       #                           style={'display': 'inline-block',
       #                                  'margin': 'auto', 'font-size': '10px',
       #                                  'padding-left': '2px',
       #                                  'padding-right': '2px'}),
       #                       html.P('Outcome 2',
       #                              id='consistencyswitchlabel2',
       #                              style={'display': 'inline-block',
       #                                     'margin': 'auto',
       #                                     'font-size': '10px',
       #                                     'padding-right': '0px'})],
       #                       style={'flex-grow': '1', 'justify-content': 'flex-end',
       #                             'display': 'flex', 'margin-left': '70%',
       #                             'font-size': '0.8em', 'margin-top': '2%'},
       #                       ),
       # dbc.Col(
       #  dbc.Row(
       #        [html.P(f"Select outcomes",className="selectbox", style={'display': 'inline-block', "text-align": 'right',
       #                                                         'margin-left': '0px', 'font-size': '12px'}),
       #        dcc.Dropdown(id='consistency_outcome_select', searchable=True, placeholder="...", className="box",
       #                      clearable=False, value=0,
       #                      style={'width': '80px',  # 'height': '30px',
       #                             "height": '30px',
       #                             'vertical-align': 'middle',
       #                             "font-family": "sans-serif",
       #                             'margin-bottom': '2px',
       #                             'display': 'inline-block',
       #                             'color': 'black',
       #                             'font-size': '10px','margin-left':'-7px'})]),
       #                             style={'margin-bottom': '0px', 'justify-content': 'end', 'display': 'flex'}
       #                             ),
        html.Br(), html.Br(),
        html.P("Design-by-treatment interaction model", style={'font-size': '12px', 'margin-top': '-0.6%'},
                     className="box__title")]),
        dash_table.DataTable(
        id='consistency-table',
        export_format="csv",
        columns=[{"name": i, "id": i} for i in consistency_data.columns],
        data=consistency_data.round(decimals=4).to_dict('records'),
        style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                'color': 'black',
                'textAlign': 'center',
                'minWidth': '35px',
                'maxWidth': '40px',
                'border': '1px solid #5d6d95',
                'overflow': 'hidden', 'whiteSpace': 'no-wrap',
                'textOverflow': 'ellipsis',
                'font-family': 'sans-serif',
                'fontSize': 11},
        style_data_conditional=[
        {'if': {
                'filter_query': '{p-value} > 0 && {p-value} < 0.10',
                'column_id': 'p-value'},
                'color': 'tomato',
                'fontWeight': 'bold'
         },
        {'if': {'row_index': 'odd'},
         'backgroundColor': 'rgba(0,0,0,0.2)'},
        {'if': {'state': 'active'},
         'backgroundColor': 'rgba(0, 116, 217, 0.3)',
         'border': '1px solid rgb(0, 116, 217)'}],
        style_header={'backgroundColor': 'slategrey',
                  'fontWeight': 'bold',
                  'border': '1px solid #5d6d95'},
        style_table={'overflowX': 'scroll',
                 'overflowY': 'scroll',
                 'height': '99%',
                 'max-height': '400px',
                 'minWidth': '100%',
                 'width': '99%',
                 'max-width': 'calc(52vw)',
                 'padding': '5px 5px 5px 5px'},
        css=[
        {'selector': 'tr:hover',
         'rule': 'background-color: rgba(0, 0, 0, 0);'},
        {'selector': 'td:hover',
         'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}]
    ),
    html.Br(),
    html.Div([ html.Div([ html.P("Node-splitting model",
                     style={'font-size': '12px', 'margin-top': '0.8%', 'display': 'inline-block'},
                     className="box__title"),html.Br(),
              html.P("Select edge(s) to display specific comparison(s)",
                     style={'font-size': '12px', 'margin-top': '-1.2%', 'display': 'inline-block'},
                     className="box__title") ]),
              html.Div([html.Button('Export', id='consistency-export', n_clicks=0, className="btn-export2",
                                    style={'margin-right': '31%', 'padding': '4px 4px 4px 4px',
                                           'color': 'black', 'fontSize': 10, 'margin-top': '-7%',
                                           'font-weight': '900', 'font-family': 'sans-serif', 'display': 'inline-block',
                                           }),
                        html.P(id='export-cons-button-hidden', style={'display': 'none'}),
                        dcc.Download(id="download_consistency")]),
              html.Div([html.Button('Save all', 'btn-netsplit-all', n_clicks=0,className="btn-export2",
                          style={'padding': '0px 4px 0px 4px','margin-right': '20%',
                                 'margin-bottom': '2px', 'fontSize': 10,'margin-top': '-7%',
                                 'font-weight': '900', 'font-family': 'sans-serif', 'display': 'inline-block',
                                 }),
                        html.P(id='export-cons-all-button-hidden', style={'display': 'none'}),
                        dcc.Download(id="download_consistency_all"),
                        dbc.Tooltip("All net-split results with indirect comparisons",
                                    style={'color': 'black', 'font-size': 9,
                                           'margin-left': '10px',
                                           'letter-spacing': '0.3rem'},
                                    placement='top',
                                    target='btn-netsplit-all'),
                        ]),
              html.Div(dash_table.DataTable(
            id='netsplit_table-container',
            fixed_rows={'headers': True, 'data': 0},
            #export_format="csv", #xlsx
            #columns=[{"name": i, "id": i} for i in df.columns],
            #data=df.to_dict('records'),
            style_cell={'backgroundColor': 'rgba(0,0,0,0)',
                'color': 'black',
                'textAlign': 'center',
                'minWidth': '35px',
                'maxWidth': '40px',
                'border': '1px solid #5d6d95',
                'overflow': 'hidden', 'whiteSpace': 'no-wrap',
                'textOverflow': 'ellipsis',
                'font-family': 'sans-serif',
                'fontSize': 11},
             style_data_conditional=[
            {'if': {'filter_query': '{p-value} <= 0.05',
                'column_id': 'p-value'},
            'color': 'tomato',
            'fontWeight': 'bold'
            },
            {'if': {'filter_query': '{p-value} > 0.05 && {p-value} <= 0.10',
            'column_id': 'p-value'},
             'color': '#f2940',
             'fontWeight': 'bold'
             },
             {'if': {'filter_query': '{p-value} > 0.10 && {p-value} <= 0.15',
                         'column_id': 'p-value'},
                  'color': 'blue',
                  'fontWeight': 'bold'
             },
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgba(0,0,0,0.1)'},
            {'if': {'state': 'active'},
            'backgroundColor': 'rgba(0, 116, 217, 0.3)',
            'border': '1px solid rgb(0, 116, 217)'}],
            style_header={'backgroundColor': 'grey',
                  'fontWeight': 'bold',
                  'border': '1px solid #5d6d95'},
            style_table={'overflowX': 'scroll',
                 'overflowY': 'scroll',
                 'height': '97%',
                 'max-height': 'calc(30vh)',
                 'minWidth': '100%',
                 'width': '90%',
                 'max-width': 'calc(50vw)',
                 'padding': '5px 5px 5px 5px'},
            css=[
            {'selector': 'tr:hover',
            'rule': 'background-color: rgba(0, 0, 0, 0);'},
            {'selector': 'td:hover',
             'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}])),
              ]),
    html.Br(),
    ])