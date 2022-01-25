import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


alert_outcome_type = dcc.ConfirmDialog(id='data-type-danger',
                                    message='Choose a correct outcome type')


alert_data_type = dcc.ConfirmDialog(id='data-missing-n-danger',
                                    message='sample size for each outcome missing')



R_errors_nma = dbc.Modal([
        dbc.ModalHeader("Error"),
        dbc.ModalBody([html.P("R function failed: see error below and check your data"),
                       html.P(id="R_errors_nma_console", style={"color":"white"})])],
        id="R-alert-nma",
        size="lg",
        is_open=False)

R_errors_pair = dbc.Modal([
        dbc.ModalHeader("Error"),
        dbc.ModalBody([html.P("R function failed: see error below and check your data"),
                       html.P(id="R_errors_nma_console", style={"color":"white"})])],
        id="R-alert-pair",
        size="lg",
        is_open=False)

R_errors_league = dbc.Modal([
    dbc.ModalHeader("Error"),
    dbc.ModalBody([html.P("R function failed: see error below and check your data"),
                   html.P(id="R_errors_nma_console", style={"color": "white"})])],
    id="R-alert-league",
    size="lg",
    is_open=False)


R_errors_funnel= dbc.Modal([
    dbc.ModalHeader("Error"),
    dbc.ModalBody([html.P("R function failed: see error below and check your data"),
                   html.P(id="R_errors_nma_console", style={"color": "white"})])],
    id="R-alert-funnel",
    size="lg",
    is_open=False)

