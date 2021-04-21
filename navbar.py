import dash_bootstrap_components as dbc
import dash_html_components as html
from assets.COLORS import *

NMASTUDIO_LOGO = "/assets/logos/NMAstudio_long2.png"
CRESS_LOGO = "/assets/logos/CRESS_logo.png"
UP_LOGO = "/assets/logos/logo_universite_paris.jpg"


def Navbar():
    home_button = dbc.NavItem(dbc.NavLink('HOME', href="/home", external_link=True,
                                          style = {'color':'white','font-family': "sans-serif ",
                                                   'font-size':'11px' }))
    doc_button = dbc.NavItem(dbc.NavLink('DOCUMENTATION', href="/doc", external_link=True,
                                         style = {'color':'white','font-family': "sans-serif ",
                                                  'font-size': '11px' }))
    navbar = dbc.Navbar([
            dbc.Col(html.Img(src=NMASTUDIO_LOGO, height="60px", style={'filter': 'invert()',
                                                                       'padding-left': '1.5%',
                                                                       'padding-top':'0.4%'}), sm=3, md=2),
            dbc.Col(dbc.Nav([home_button, doc_button], navbar=True)),
            dbc.Col(html.Img(src=CRESS_LOGO, height="75px"), style={'padding-right':'1.5%','padding-top':'0.4%'},
                    width="auto" ),
        ],
        color="dark",
        dark=True,
    )

    return navbar
