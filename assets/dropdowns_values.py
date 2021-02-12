####### contains all lists of values (except for data variables) for the app dropdowns #######

options_format = [{'label':'long',      'value':'long'},
                  {'label':'contrast',  'value':'contrast'}
                  ]

options_outcomes = [{'label':'continuous',      'value':'continuous'},
                   {'label':'binary',  'value':'binary'}
                   ]

options_outcomes_direction = [{'label':'beneficial',  'value':'beneficial'},
                             {'label':'harmful',     'value':'harmful'}
                             ]

import dash_core_components as dcc
import dash_bootstrap_components as dbc, dash_html_components as html

Input_color = dcc.Input(id="node_color",
                type="text",
                style={'background-color':'#40515e','margin-left':'-px', 'font-size':'10.5px', 'padding-left':'-2px'},
                placeholder="Type color name / Hex")


Dropdown_nodesize = dbc.DropdownMenu(
    label="Node size",
    children=[
        dbc.DropdownMenuItem("Default", id='dd_nds_default'),
        dbc.DropdownMenuItem("Tot randomized", id='dd_nds_tot_rnd'),
        dbc.DropdownMenuItem("Other", id='dd_nds_other'),
        html.Div(id='dd_nds', style={'display': 'none'}),
    ], style={'display': 'inline-block',}
)

modal = html.Div(
    [dbc.Button("Choose your color", id="open"),
     dbc.Modal([
                dbc.ModalBody(Input_color),
                dbc.ModalFooter(dbc.Button("Close", id="close", className="ml-auto"))
                ],
            id="modal",style={'background-color':'#40515e','margin-left':'-px', 'font-size':'10.5px', 'padding-left':'-2px'})])

# Dropdown_nodecolor = dbc.DropdownMenu(
#     label="Node color",
#     children=[
#         dbc.DropdownMenuItem("Default", id='dd_nclr_default'),
#         dbc.DropdownMenuItem("Risk of Bias", id='dd_nclr_rob'),
#         dbc.DropdownMenuItem("Choose your color", id='dd_nclr_input'),
#         html.Div(id='dd_nclr', style={'display': 'none'}),
#     ], style={'display': 'inline-block',}
# )

Dropdown_nodecolor = dbc.DropdownMenu(
    label="Node color",
    children=[
        dbc.DropdownMenuItem("Default", id='dd_nclr_default'),
        dbc.DropdownMenuItem("Risk of Bias", id='dd_nclr_rob'),
        dbc.DropdownMenuItem(Input_color, id='dd_nclr_input'), ### or modal
        html.Div(id='dd_nclr', style={'display': 'none'}),
        ], style={'display': 'inline-block',}
)


Dropdown_graphlayout = dbc.DropdownMenu(
    label="Graph Layout",
    children=[
        dbc.DropdownMenuItem(item, id=f'dd_ngl_{item.lower()}')
        for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                     'Cose-Bilkent', 'Dagre', 'Klay']
             ] + [html.Div(id='graph-layout-dropdown', style={'display': 'none'})
             ],
    style={'display': 'inline-block',}
)

Dropdown_edgesize = dbc.DropdownMenu(
    label="Edge size",
    children=[
        dbc.DropdownMenuItem("Default", id='dd_egs_default'),
        dbc.DropdownMenuItem("Number of studies", id='dd_egs_tot_rnd'),
        dbc.DropdownMenuItem("Other", id='dd_egs_other'),
        html.Div(id='dd_egs', style={'display': 'none'}),
    ], style={'display': 'inline-block',}
)

