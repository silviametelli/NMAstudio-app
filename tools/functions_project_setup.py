import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.COLORS import *
from tools.utils import parse_contents
import dash_core_components as dcc

options_outcomes = [dict(label='continuous', value='continuous'),
                    dict(label='binary', value='binary')] 

options_effect_size_cont = [{'label':'MD', 'value':'MD'},  {'label':'SMD', 'value':'SMD'}]
options_effect_size_bin  = [{'label':'OR',  'value':'OR'}, {'label':'RR',  'value':'RR'}]
options_outcome_direction =[{'label':'beneficial',  'value':'beneficial'}, {'label':'harmful',  'value':'harmful'}]

def __update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):

    if search_value_format is None: return None
    if search_value_outcome1 is None: return None

    data_user = parse_contents(contents, filename)

    name_outcomes = ['1st outcome*', '2nd outcome'] if search_value_outcome2 is not None else ['1st outcome*']
    search_values = [search_value_outcome1, search_value_outcome2] if search_value_outcome2 is not None else [search_value_outcome1]
    options_var = [{'label': '{}'.format(col, col), 'value': col} for col in data_user.columns]

    if search_value_format is None: return None
    col_vars = [[]] * 3
    if search_value_format == 'long':
        col_vars[0] = ['study ID', 'treat', 'rob', 'year']
        if search_value_outcome1 == 'continuous':
            col_vars[1] = ['y', 'sd', 'n']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2', 'sd2', 'n2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n.z']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['No. of events', 'No. participants']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2', 'sd2', 'n2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n.z']

        else:
            return None
    elif search_value_format == 'contrast':
        col_vars[0] = ['studlab', 'treat 1', 'treat 2', 'rob', 'year']
        if search_value_outcome1 == 'continuous':
            col_vars[1] = ['y1', 'sd1', 'y2', 'sd2']
            col_vars[1] += ['n1', 'n2']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2.1', 'sd1.2', 'y2.2', 'sd2.2', 'n2.1', 'n2.2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n2.1', 'z2', 'n2.2']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['r1', 'n1', 'r2', 'n2']
            if search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n2.1', 'z2', 'n2.2']
            elif search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2.1', 'sd1.2', 'y2.2', 'sd2.2', 'n2.1', 'n2.2']

        else:
            return None
    elif search_value_format == 'iv':
        col_vars[0] = ['studlab', 'treat 1', 'treat 2', 'rob', 'year']
        col_vars[1] = ['TE', 'seTE', 'n1', 'n2']
        if search_value_outcome2 is not None:
            col_vars[2] = ['TE2', 'seTE2', 'n2.1', 'n2.2']


    vars_names = [[f'{search_value_format}.{c}' for c in col_vars[0]],
                  [f'{search_value_outcome1}.{c}' for c in col_vars[1]],
                  [f'{search_value_outcome2}.{c}' for c in col_vars[2]]]


    selectors_ef = html.Div([html.Div(
        [dbc.Row([html.P("Select effect size", style={'color': 'black', 'vertical-align': 'middle'})])] +
         [dbc.Row([dbc.Col(dbc.Row(
                  [html.P(f"{name}", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                   'margin-left': '5px', 'font-size': '12px', 'color':'black'}),
                  dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-{name_outcomes}'},
                               options=options_effect_size_cont if val=='continuous' else options_effect_size_bin,
                               searchable=True, placeholder="...",
                               clearable=False, style={'width': '60px', "height":'30px',
                                                       'vertical-align': 'middle',
                                                       "font-family": "sans-serif",
                                                       'margin-bottom': '2px',
                                                       'display': 'inline-block',
                                                       'color': 'black',
                                                       'font-size': '10px'} )]
          ),  style={'margin-left': '55px', 'margin-right': '5px'}) for name, val in zip(name_outcomes, search_values)]
        )],
     ),

        html.Div(
            [dbc.Row([html.P("Outcome direction", style={'color': 'black', 'vertical-align': 'middle'})])] +
            [dbc.Row([dbc.Col(dbc.Row(
                [html.P(f"{name}", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                 'margin-left': '-1.5px', 'font-size': '12px',
                                                                 'color': 'black'}),
                 dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-outcome-{name_outcomes}'},
                              options=options_outcome_direction,
                              searchable=True, placeholder="...",
                              clearable=False, style={'width': '60px', "height": '30px',
                                                      'vertical-align': 'middle',
                                                      "font-family": "sans-serif",
                                                      'margin-bottom': '2px',
                                                      'display': 'inline-block',
                                                      'color': 'black',
                                                      'font-size': '10px'})]
            ), style={'margin-left': '55px', 'margin-right': '5px'}) for name, val in zip(name_outcomes, search_values)]
            )],
        ),

    html.Div([html.Div(

    ),
        html.Div(
            [dbc.Row([html.P("Select variables", style={'color': 'black', 'vertical-align': 'top'})])] +
            [dbc.Row([dbc.Col(dbc.Row(
                [html.P(f"{name}:", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                  'margin-left': '0px', 'font-size': '12px'}),
                 dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-{var_name}'},
                              options=options_var, searchable=True, placeholder="...", className="box",
                              clearable=False, style={'width': '80px',  # 'height': '30px',
                                                      "height": '30px',
                                                      'vertical-align': 'middle',
                                                      "font-family": "sans-serif",
                                                      'margin-bottom': '2px',
                                                      'display': 'inline-block',
                                                      'color': 'black',
                                                      'font-size': '10px','margin-left':'-7px'})]),
                style={'margin-bottom': '0px'})
                for var_name, name in zip(var_names, col_var)],
                style={'display': 'inline-block'})
                for var_names, col_var in zip(vars_names, col_vars)],

        )
    ])
        ])


    return selectors_ef







def __second_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):

    if search_value_format is None: return None, {'display':'none', 'justify-content': 'center'}
    if search_value_outcome1 is None: return None, {'display':'none', 'justify-content': 'center'}

    data_user = parse_contents(contents, filename)

    name_outcomes = ['1st outcome*', '2nd outcome'] if search_value_outcome2 is not None else ['1st outcome*']
    search_values = [search_value_outcome1, search_value_outcome2] if search_value_outcome2 is not None else [search_value_outcome1]
    options_var = [{'label': '{}'.format(col, col), 'value': col} for col in data_user.columns]

    if search_value_format is None: return None, {'display':'none', 'justify-content': 'center'}
    col_vars = [[]] * 3
    if search_value_format == 'long':
        col_vars[0] = ['study ID', 'treat', 'rob', 'year']
        if search_value_outcome1 == 'continuous':
            col_vars[1] = ['y', 'sd', 'n']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2', 'sd2', 'n2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n.z']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['No. of events', 'No. participants']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2', 'sd2', 'n2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n.z']

        else:
            return None, {'display':'none', 'justify-content': 'center'}
    elif search_value_format == 'contrast':
        col_vars[0] = ['studlab', 'treat 1', 'treat 2', 'rob', 'year']
        if search_value_outcome1 == 'continuous':
            col_vars[1] = ['y1', 'sd1', 'y2', 'sd2']
            col_vars[1] += ['n1', 'n2']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2.1', 'sd1.2', 'y2.2', 'sd2.2', 'n2.1', 'n2.2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n2.1', 'z2', 'n2.2']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['r1', 'n1', 'r2', 'n2']
            if search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n2.1', 'z2', 'n2.2']
            elif search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2.1', 'sd1.2', 'y2.2', 'sd2.2', 'n2.1', 'n2.2']

        else:
            return None, {'display':'none', 'justify-content': 'center'}
    elif search_value_format == 'iv':
        col_vars[0] = ['studlab', 'treat 1', 'treat 2', 'rob', 'year']
        col_vars[1] = ['TE', 'seTE', 'n1', 'n2']
        if search_value_outcome2 is not None:
            col_vars[2] = ['TE2', 'seTE2', 'n2.1', 'n2.2']
    
    vars_names = [[f'{search_value_format}.{c}' for c in col_vars[0]],
                  [f'{search_value_outcome1}.{c}' for c in col_vars[1]],
                  [f'{search_value_outcome2}.{c}' for c in col_vars[2]]]

    selectors_ef = html.Div([html.Div(
        [dbc.Row([html.P("Select effect size", className="selcect_title",)],style={'justify-content': 'center', 'display': 'grid'})] +
         [dbc.Row([dbc.Col(dbc.Row(
                  [html.P(f"{name}", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                   'margin-left': '5px', 'font-size': '12px', 'color':'black'}),
                  dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-{name_outcomes}'},
                               options=options_effect_size_cont if val=='continuous' else options_effect_size_bin,
                               searchable=True, placeholder="...",
                               clearable=False, style={'width': '60px', "height":'30px',
                                                       'vertical-align': 'middle',
                                                       "font-family": "sans-serif",
                                                       'margin-bottom': '2px',
                                                       'display': 'inline-block',
                                                       'color': 'black',
                                                       'font-size': '10px'} )]
          ),  style={'margin-left': '55px', 'margin-right': '5px'}) for name, val in zip(name_outcomes, search_values)]
        )], style={'justify-content': 'center', 'display': 'grid'}
     ),

        html.Div(
            [dbc.Row([html.P("Outcome direction",  className="selcect_title")], style={'justify-content': 'center', 'display': 'grid'})] +
            [dbc.Row([dbc.Col(dbc.Row(
                [html.P(f"{name}", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                 'margin-left': '-1.5px', 'font-size': '12px',
                                                                 'color': 'black'}),
                 dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-outcome-{name_outcomes}'},
                              options=options_outcome_direction,
                              searchable=True, placeholder="...",
                              clearable=False, style={'width': '60px', "height": '30px',
                                                      'vertical-align': 'middle',
                                                      "font-family": "sans-serif",
                                                      'margin-bottom': '2px',
                                                      'display': 'inline-block',
                                                      'color': 'black',
                                                      'font-size': '10px'})]
            ), style={'margin-left': '55px', 'margin-right': '5px'}) for name, val in zip(name_outcomes, search_values)]
            )], style={'justify-content': 'center', 'display': 'grid'}
        ),
        html.Br(),
        html.Div([
        html.Div(
            [dbc.Row([html.P("Select variables", className="selcect_title")], style={'justify-content': 'center', 'display': 'grid'})] +
            [dbc.Row([dbc.Col(dbc.Row(
                [html.P(f"{name}:", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                  'margin-left': '0px', 'font-size': '12px'}),
                 dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-{var_name}'},
                              options=options_var, searchable=True, placeholder="...", className="box",
                              clearable=False, style={'width': '80px',  # 'height': '30px',
                                                      "height": '30px',
                                                      'vertical-align': 'middle',
                                                      "font-family": "sans-serif",
                                                      'margin-bottom': '2px',
                                                      'display': 'inline-block',
                                                      'color': 'black',
                                                      'font-size': '10px','margin-left':'-7px'})]),
                style={'margin-bottom': '0px'})
                for var_name, name in zip(var_names, col_var)],
                style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'width': '400px', 'justify-content': 'center'})
                for var_names, col_var in zip(vars_names, col_vars)],
                style={'justify-content': 'center', 'display': 'grid'}
        )
        ])], className='upload_second_select')


    return selectors_ef, {'display':'grid', 'justify-content': 'center'}




def __selectbox1_options(search_value_format, contents, filename):

    if search_value_format is None: return None, {'display':'none', 'justify-content': 'center'}
    

    data_user = parse_contents(contents, filename)

    options_var = [{'label': '{}'.format(col, col), 'value': col} for col in data_user.columns]

    if search_value_format is None: return None, {'display':'none', 'justify-content': 'center'}
    col_vars = [[]] 
    if search_value_format == 'long':
        col_vars[0] = ['study ID', 'treat', 'rob', 'year']
    elif search_value_format == 'contrast':
        col_vars[0] = ['studlab', 'treat 1', 'treat 2', 'rob', 'year']
        
    elif search_value_format == 'iv':
        col_vars[0] = ['studlab', 'treat 1', 'treat 2', 'rob', 'year']
        
    
    vars_names = [[f'{search_value_format}.{c}' for c in col_vars[0]]]

    selectors_ef = html.Div([
        html.Div([
        html.Div(
            [dbc.Row([html.P("Select overall variables", className="selcect_title")], style={'justify-content': 'center', 'display': 'grid'})] +
            [dbc.Row([dbc.Col(dbc.Row(
                [html.P(f"{name}:", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                  'margin-left': '0px', 'font-size': '12px'}),
                 dcc.Dropdown(id={'type': 'dataselectors_1', 'index': f'dropdown-{var_name}'},
                              options=options_var, searchable=True, placeholder="...", className="box",
                              clearable=False, style={'width': '80px',  # 'height': '30px',
                                                      "height": '30px',
                                                      'vertical-align': 'middle',
                                                      "font-family": "sans-serif",
                                                      'margin-bottom': '2px',
                                                      'display': 'inline-block',
                                                      'color': 'black',
                                                      'font-size': '10px','margin-left':'-7px'})]),
                style={'margin-bottom': '0px'})
                for var_name, name in zip(var_names, col_var)],
                style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'width': '400px', 'justify-content': 'center'})
                for var_names, col_var in zip(vars_names, col_vars)],
                style={'justify-content': 'center', 'display': 'grid'}
        )
        ])], className='upload_second_select')


    return selectors_ef, {'display':'grid', 'justify-content': 'center'}


def __outcomes_type(number_outcomes, click):
    if click:
        number_outcomes = int(number_outcomes)
        outcomes_type_selection = [
            html.Div(
                [
                    dbc.Row(
                        [
                            html.P(f"Select the type of outcome {i+1}:", className="selcect_title"),
                            html.Div(
                                dcc.RadioItems(
                                    id={'type': 'outcometype', 'index': f"{i}"},
                                    options=options_outcomes,
                                    inline=True,
                                    className='upload_radio'
                                )
                            )
                        ],
                        style={
                            'display': 'grid',
                            'background-color': 'beige',
                            'width': '500px',
                            'justify-content': 'center'
                        }
                    )
                ], 
                style={'display': 'grid'},
                id= {'type': 'outcometype_display', 'index': f"{i}"}
            ) for i in range(number_outcomes)
        ]
        
        return outcomes_type_selection, {'display': 'grid', 'justify-content': 'center'}
    
    return None, {'display': 'none', 'justify-content': 'center'}



def __variable_selection(number_outcomes,outcometype, data_format, contents, filename):

    if not outcometype or not all(outcometype): return None, {'display':'none', 'justify-content': 'center'}

    data_user = parse_contents(contents, filename)
    number_outcomes = int(number_outcomes)
    options_var = [{'label': '{}'.format(col, col), 'value': col} for col in data_user.columns]

    col_vars = [[]] * number_outcomes

    for i in range(number_outcomes):

        if data_format == 'long':
            if outcometype[i] == 'continuous':
                col_vars[i] = ['y', 'sd', 'n']
            elif outcometype[i] == 'binary':
                col_vars[i] = ['No. of events', 'No. participants']
            else:
                col_vars[i] = ['No. of events', 'No. participants']
            
        elif data_format == 'contrast':
            if outcometype[i] == 'continuous':
                col_vars[i] = ['y1', 'sd1', 'y2', 'sd2']
                col_vars[i] += ['n1', 'n2']
            elif outcometype[i] == 'binary':
                col_vars[i] = ['r1', 'n1', 'r2', 'n2']

            else:
                col_vars[i] = ['r1', 'n1', 'r2', 'n2']

        elif data_format == 'iv':
            col_vars[i] = ['TE', 'seTE', 'n1', 'n2']


    # vars_names = [[f'{outcometype[i+1]}.{c}' for c in col_vars[i]]]

    selectors_ef = [html.Div([html.Div(
        [dbc.Row([html.P(f"Select effect size for outcome {i+1}", className="selcect_title",)],style={'justify-content': 'center', 'display': 'grid'})] +
         [dbc.Row([dbc.Col(dbc.Row(
                  [html.P(className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                   'margin-left': '5px', 'font-size': '12px', 'color':'black'}),
                  dcc.RadioItems(id={'type': 'effectselectors', 'index': f'{i}'},
                               options=options_effect_size_cont if outcometype[i]=='continuous' else options_effect_size_bin,
                               inline=True, className='upload_radio',
                            #    style={'width': '60px', "height":'30px',
                            #                            'vertical-align': 'middle',
                            #                            "font-family": "sans-serif",
                            #                            'margin-bottom': '2px',
                            #                            'display': 'inline-block',
                            #                            'color': 'black',
                            #                            'font-size': '10px'}
                                                         )]
          ),  style={'margin-left': '55px', 'margin-right': '5px'})]
        )], style={'justify-content': 'center', 'display': 'grid'}
     ),
     html.Div(
            [dbc.Row([html.P(f"Outcome direction for outcome {i+1}",  className="selcect_title")], style={'justify-content': 'center', 'display': 'grid'})] +
            [dbc.Row([dbc.Col(dbc.Row(
                [html.P(className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                 'margin-left': '-1.5px', 'font-size': '12px',
                                                                 'color': 'black'}),
                 dcc.RadioItems(id={'type': 'directionselectors', 'index': f'{i}'},
                              options=options_outcome_direction,inline=True, className='upload_radio',
                                # style={'width': '60px', "height": '30px',
                                #                       'vertical-align': 'middle',
                                #                       "font-family": "sans-serif",
                                #                       'margin-bottom': '2px',
                                #                       'display': 'inline-block',
                                #                       'color': 'black',
                                #                       'font-size': '10px'}
                                                      )]
            ), style={'margin-left': '55px', 'margin-right': '5px'})]
            )], style={'justify-content': 'center', 'display': 'grid'}
        ),
        html.Br(),
        html.Div([
        html.Div(
            [dbc.Row([html.P(f"Select variables for outcome {i+1}", className="selcect_title")], style={'justify-content': 'center', 'display': 'grid'})] +
            [dbc.Row([dbc.Col(dbc.Row(
                [html.P(f"{name}:",className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                  'margin-left': '0px', 'font-size': '12px'}),
                 dcc.Dropdown(id={'type': 'variableselectors', 'index': f'{i}'},
                              options=options_var, searchable=True, placeholder="...", className="box",
                              clearable=False, style={'width': '80px',  # 'height': '30px',
                                                      "height": '30px',
                                                      'vertical-align': 'middle',
                                                      "font-family": "sans-serif",
                                                      'margin-bottom': '2px',
                                                      'display': 'inline-block',
                                                      'color': 'black',
                                                      'font-size': '10px','margin-left':'-7px'})]),
                style={'margin-bottom': '0px'}) for name in col_vars[i]],
                style={'display': 'grid', 'grid-template-columns': '1fr 1fr', 'width': '400px', 'justify-content': 'center'})],
                style={'justify-content': 'center', 'display': 'grid'}
        )
        ]),
        html.Br(),
        dbc.Button("Next outcome", n_clicks=0, id={'type': 'outcomebutton', 'index': f'{i}'},disabled=True,
                                    style={'color': 'white',
                                            'background-color':'orange',
                                            'display': 'inline-block',
                                            'justify-self':'center',
                                            'border': 'unset',
                                            'padding': '4px'})

        ], className='upload_second_select', 
        style={'display':'grid' if i==0 else 'none'}, 
        id={'type': 'displayvariable', 'index': f'{i}'}) for i in range(number_outcomes)]


    return selectors_ef, {'display':'grid', 'justify-content': 'center'}







def __effect_modifier_options(search_value_format,contents, filename):
    
    if search_value_format is None: 
        return None
    # if search_value_outcome1 is None: 
    #     return None
    else: 
        data_user = parse_contents(contents, filename)
        options_var = [{'label': '{}'.format(col, col), 'value': col} for col in data_user.columns]   

        selectors_ef = html.Div([
            html.Div(
            dbc.Row([dbc.Col(dbc.Row(
                    [html.P("Select potential effect modifiers", className="selcect_title", style={'text-align': 'center'}),
                        dcc.Checklist(id='effect_modifier_checkbox',
                                    options=options_var, className="",
                                    style={'display': 'grid', 
                                            'grid-template-columns': '1fr 1fr 1fr', 
                                            'width': '400px', 'justify-content': 'center'}),
                    dcc.Checklist(id='no_effect_modifier',
                                    options=[{'label':'No effect modifires', 'value':'no'}], className="",
                                    style={'display': 'grid','color': 'green', 'font-weight':'bold'})
                    ],
                                            style={'justify-content': 'center'}
                                            ))],
                                            ),
                    style={'justify-content': 'center', 'display': 'grid'}
            )], className='upload_second_select')


        return selectors_ef
