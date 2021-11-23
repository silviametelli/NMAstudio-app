import dash_table, dash_daq as daq
import dash_html_components as html, dash_bootstrap_components as dbc

from assets.storage import CONSISTENCY_DATA

def tab_consistency(consistency_data=CONSISTENCY_DATA):
    return html.Div([
        html.Div([dbc.Col([
                             html.P(
                             "Outcome 1",
                             id='consistencyswitchlabel1',
                             style={'display': 'inline-block',
                                    'margin': 'auto',
                                    'font-size': '10px',
                                    'padding-left': '0px'}),
                             daq.ToggleSwitch(
                                 id='toggle_consistency_direction',
                                 color='', size=30, vertical=False,
                                 label={'label': "",
                                        'style': dict(color='white', font='0.5em')},
                                 labelPosition="top",
                                 style={'display': 'inline-block',
                                        'margin': 'auto', 'font-size': '10px',
                                        'padding-left': '2px',
                                        'padding-right': '2px'}),
                             html.P('Outcome 2',
                                    id='consistencyswitchlabel2',
                                    style={'display': 'inline-block',
                                           'margin': 'auto',
                                           'font-size': '10px',
                                           'padding-right': '0px'})],
                             style={'flex-grow': '1', 'justify-content': 'flex-end',
                                   'display': 'flex', 'margin-left': '70%',
                                   'font-size': '0.8em', 'margin-top': '2%'},
                             ),
        html.P("Design-by-treatment interaction model", style={'font-size': '12px', 'margin-top': '-0.6%'},
                     className="box__title")]),
        dash_table.DataTable(
        id='consistency-table',
        export_format="csv",
        columns=[{"name": i, "id": i} for i in consistency_data.columns],
        data=consistency_data.round(decimals=4).to_dict('records'),
        style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                'color': 'white',
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
    html.Div([html.P("Node-splitting model",
                     style={'font-size': '12px', 'margin-top': '0.8%', 'display': 'inline-block'},
                     className="box__title"),html.Br(),
              html.P("Select edge(s) to display specific comparison(s) test(s)",
                     style={'font-size': '12px', 'margin-top': '-1.2%', 'display': 'inline-block'},
                     className="box__title"),

              # html.Button('Show  all', 'btn-netsplit', n_clicks=0,
              #             style={'margin-left': '15px', 'padding': '0px 4px 0px 4px',
              #                    'margin-bottom': '2px', 'color': 'white', 'fontSize': 10,
              #                    'font-weight': '900', 'font-family': 'sans-serif',
              #                    'display': 'inline-block', 'vertical-align': 'middle'}),
              html.Div(dash_table.DataTable(
            id='netsplit_table-container',
            fixed_rows={'headers': True, 'data': 0},
            export_format="csv", #xlsx
            #columns=[{"name": i, "id": i} for i in df.columns],
            #data=df.to_dict('records'),
            style_cell={'backgroundColor': 'rgba(0,0,0,0.1)',
                'color': 'white',
                'textAlign': 'center',
                'minWidth': '35px',
                'maxWidth': '40px',
                'border': '1px solid #5d6d95',
                'overflow': 'hidden', 'whiteSpace': 'no-wrap',
                'textOverflow': 'ellipsis',
                'font-family': 'sans-serif',
                'fontSize': 11},
             style_data_conditional=[
            {'if': {'filter_query': '{p-value} <= 0.10',
                'column_id': 'p-value'},
            'color': 'tomato',
            'fontWeight': 'bold'
            },
            {'if': {'filter_query': '{p-value} > 0.10 && {p-value} <= 0.15',
            'column_id': 'p-value'},
             'color': 'yellow',
             'fontWeight': 'bold'
             },
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgba(0,0,0,0.2)'},
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
             'rule': 'background-color: rgba(0, 116, 217, 0.3) !important;'}]))]),
    html.Br(),
    ])