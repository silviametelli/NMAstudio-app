####### contains all lists of values (except for data variables) for the app dropdowns #######
from assets.modal_values import *


Dropdown_nodesize = dbc.DropdownMenu(
    label="Node size", direction="right",bs_size="sm",
    children=[dbc.DropdownMenuItem("Default", id='dd_nds_default'),
              dbc.DropdownMenuItem("Tot randomized", id='dd_nds_tot_rnd'),
              html.Div(id='dd_nds', style={'display': 'none'}),
              ],
)


Dropdown_nodecolor = dbc.DropdownMenu(
    label="Node color", direction="right",bs_size="sm",
    children=[dbc.DropdownMenuItem("Default", id='dd_nclr_default'),
              dbc.DropdownMenuItem("Risk of Bias", id='dd_nclr_rob'),
              dbc.DropdownMenuItem("By class", id='dd_nclr_class'),
              dbc.DropdownMenuItem("Custom selection", id='open_modal_dd_nclr_input'), # Calls up Modal
              html.Div(id='dd_nclr', style={'display': 'none'}),
              ], style={'display': 'inline-block',}
)


Dropdown_edgecolor = dbc.DropdownMenu(
    label="Edge color", direction="right", bs_size="sm",
    children=[dbc.DropdownMenuItem("Default", id='dd_edge_default'),
              dbc.DropdownMenuItem("Custom selection", id='open_modal_dd_eclr_input'), # Calls up Modal
              dbc.DropdownMenuItem("Add label", id='dd_edge_label'),
              html.Div(id='dd_eclr', style={'display': 'none'}),
              ], style={'display': 'inline-block',}
)


Dropdown_graphlayout_inner = dbc.DropdownMenu(
    label="Graph Layout",bs_size="sm",
    children=[
        dbc.DropdownMenuItem(item, id=f'dd_ngl_{item.lower()}')
        for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                      'Dagre', 'Klay']
             ] + [html.Div(id='graph-layout-dropdown', style={'display': 'none'})
             ],
    direction="right",
)

Dropdown_edgesize = dbc.DropdownMenu(
    label="Edge size", direction="right",bs_size="sm",
    children=[
        dbc.DropdownMenuItem("Number of studies", id='dd_egs_tot_rnd'),
        dbc.DropdownMenuItem("No size", id='dd_egs_default'),
        html.Div(id='dd_egs', style={'display': 'none'}),
    ],
)

Dropdown_export = dbc.DropdownMenu(
    label="Export options", direction="right",bs_size="sm",
    children=[
        dbc.DropdownMenuItem("as svg", id='svg-option'),
        dbc.DropdownMenuItem("as png", id='png-option'),
        dbc.DropdownMenuItem("as jpeg", id='jpeg-option'),  ##default option

        html.Div(id='exp-options', style={'display': 'none'}),
    ],
)
Dropdown_graphlayout = dbc.DropdownMenu(
    label="Graph Settings",
    children=[Dropdown_graphlayout_inner, Dropdown_export, Dropdown_edgesize, Dropdown_nodesize, Dropdown_nodecolor, Dropdown_edgecolor],
    style={'display': 'inline-block'},
)
