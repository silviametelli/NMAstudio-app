import dash_bootstrap_components as dbc
import dash_html_components as html
from assets.COLORS import *

NMASTUDIO_LOGO = "/assets/logos/NMAstudio_bold.png"
CRESS_LOGO = "/assets/logos/CRESS_logo.png"
UP_LOGO = "/assets/logos/logo_universite_paris.jpg"


def Navbar():
    home_button = dbc.NavItem(dbc.NavLink('HOME', href="/home", external_link=True,
                                          style = {'color':'white','font-family': "sans-serif ",
                                                   'font-size': '13px'}))
    doc_button = dbc.NavItem(dbc.NavLink('DOCUMENTATION', href="/doc", external_link=True,
                                         style = {'color':'white','font-family': "sans-serif ",
                                                  'font-size': '13px' }))
    news_button = dbc.NavItem(dbc.NavLink('NEWS', href="/news", external_link=True,
                                         style = {'color':'white','font-family': "sans-serif ",
                                                  'font-size': '13px' }))
    navbar = dbc.Navbar([
            html.Div(dbc.Col(html.Img(src=NMASTUDIO_LOGO, height="53px", style={'filter': 'invert()',
                                                                       #'filter': 'invert(44%) sepia(57%) saturate(3117%) hue-rotate(147deg) brightness(99%) contrast(94%)',
                                                                       'padding-left': '2%','padding-right': '2%',
                                                                       'padding-bottom':'0.4%','padding-top':'0.4%'}),
                             className="child", sm=3, md=2),
                     style={
                            "border": "0.01px white solid",
                            'padding-bottom':'0.2%','padding-left':'0.2%',
                            'padding-right':'0.2%', 'padding-top':'0.2%',
                            'background-color':'#304569'
                            }),

            html.Div([dbc.Col(dbc.Nav([home_button, doc_button, news_button], navbar=True, style={'margin-left':'-30%','text-align':'center',
                                                                                     'padding-right':'5%','padding-top':'2.5%'})),

            dbc.Col(html.Img(src=UP_LOGO, height="57px"), style={'padding-right':'1%','padding-top':'0.3%','padding-bottom':'0.3%'},
                    width="auto")], className="child child-right" ),
        ],
        color="dark",
        dark=True,
    )

    return navbar