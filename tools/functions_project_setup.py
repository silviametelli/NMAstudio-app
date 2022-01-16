import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.COLORS import *
from tools.utils import parse_contents
import dash_core_components as dcc


options_effect_size_cont = [{'label':'MD', 'value':'MD'},  {'label':'SMD', 'value':'SMD'}]
options_effect_size_bin  = [{'label':'OR',  'value':'OR'}, {'label':'RR',  'value':'RR'}]

def __update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):

    if search_value_format is None: return None
    if search_value_outcome1 is None: return None

    data_user = parse_contents(contents, filename)

    name_outcomes = ['1st outcome*', '2nd outcome'] if search_value_outcome2 is not None else ['1st outcome']
    search_values = [search_value_outcome1, search_value_outcome2] if search_value_outcome2 is not None else [search_value_outcome1]
    options_var = [{'label': '{}'.format(col, col), 'value': col} for col in data_user.columns]

    if search_value_format is None: return None
    col_vars = [[]] * 3
    if search_value_format == 'long':
        col_vars[0] = ['study id', 'treat', 'rob']
        if search_value_outcome1 == 'continuous':
            col_vars[1] = ['y', 'sd', 'n']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2', 'sd2', 'n2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n.z']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['r', 'n']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2', 'sd2', 'n2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n.z']

        else:
            return None
    elif search_value_format == 'contrast':
        col_vars[0] = ['studlab', 'treat 1', 'treat 2', 'rob']
        if search_value_outcome1 == 'continuous':
            col_vars[0] += ['n1', 'n2']
            col_vars[1] = ['y1', 'sd1', 'y2', 'sd2']
            if search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2.1', 'sd1.2', 'y2.2', 'sd2.2']
            elif search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n1.z', 'z2.z', 'n2.z']
        elif search_value_outcome1 == 'binary':
            col_vars[1] = ['r1', 'n1', 'r2', 'n2']
            if search_value_outcome2 == 'binary':
                col_vars[2] = ['z1', 'n1.z', 'z2', 'n2.z']
            elif search_value_outcome2 == 'continuous':
                col_vars[2] = ['y2.1', 'sd1.2', 'y2.2', 'sd2.2']

        else:
            return None


    vars_names = [[f'{search_value_format}.{c}' for c in col_vars[0]],
                  [f'{search_value_outcome1}.{c}' for c in col_vars[1]],
                  [f'{search_value_outcome2}.{c}' for c in col_vars[2]]]


    selectors_ef = html.Div([html.Div(
        [dbc.Row([html.P("Select effect size", style={'color': 'white', 'vertical-align': 'middle'})])] +
         [dbc.Row([dbc.Col(dbc.Row(
                  [html.P(f"{name}", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                   'margin-left': '0px', 'font-size': '12px'}),
                  dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-{name_outcomes}'},
                               options=options_effect_size_cont if val=='continuous' else options_effect_size_bin,
                               searchable=True, placeholder="...",
                               clearable=False, style={'width': '60px', "height":'20px',
                                                       'vertical-align': 'middle',
                                                       "font-size": "1em",
                                                       "font-family": "sans-serif",
                                                       'margin-bottom': '10px',
                                                       'display': 'inline-block',
                                                       'color': CLR_BCKGRND_old, 'font-size': '10px',
                                                       'background-color': CLR_BCKGRND_old} )]
          ),  style={'margin-left': '55px', 'margin-right': '5px'}) for name, val in zip(name_outcomes, search_values)]
        )],
     ),

    html.Div([html.Div(
        [dbc.Row([html.P("Select effect size", style={'color': 'white', 'vertical-align': 'middle'})])]
    ),
        html.Div(
            [dbc.Row([html.P("Select your variables", style={'color': 'white', 'vertical-align': 'middle'})])] +
            [dbc.Row([dbc.Col(dbc.Row(
                [html.P(f"{name}:", className="selectbox", style={'display': 'inline-block', "text-align": 'right',
                                                                  'margin-left': '0px', 'font-size': '12px'}),
                 dcc.Dropdown(id={'type': 'dataselectors', 'index': f'dropdown-{var_name}'},
                              options=options_var, searchable=True, placeholder="...", className="box",
                              clearable=False, style={'width': '80px',  # 'height': '30px',
                                                      'vertical-align': 'middle',
                                                      'margin-bottom': '10px',
                                                      # 'padding-bottom':'10px',
                                                      'display': 'inline-block',
                                                      'color': CLR_BCKGRND_old, 'font-size': '10px',
                                                      'background-color': CLR_BCKGRND_old})]),
                style={'margin-bottom': '0px'})
                for var_name, name in zip(var_names, col_var)],
                style={'display': 'inline-block'})
                for var_names, col_var in zip(vars_names, col_vars)],

        )
    ])
        ])


    return selectors_ef