import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


alert_outcome_type = dcc.ConfirmDialog(id='data-type-danger',
                                    message='Choose a correct outcome type')


alert_data_type = dcc.ConfirmDialog(id='data-missing-n-danger',
                                    message='sample size for each outcome missing')


dataupload_error= dbc.Modal([
        dbc.ModalHeader("Error"),
        dbc.ModalBody([html.P("NMA estimation and/or network generation failed: see error below and check your data",  style={"color":"red"}),
                       html.P(id="dataupload-error", style={"color":"white"})])],
        id="Alert-data",
        size="lg",
        is_open=False)


R_errors_data = dbc.Modal([
        dbc.ModalHeader("Error"),
        dbc.ModalBody([html.P("Data conversion failed: see error below / check your data for format errors",  style={"color":"red"}),
                       html.P(id="Rconsole-error-data", style={"color":"white"})])],
        id="R-alert-data",
        size="lg",
        is_open=False)

R_errors_nma = dbc.Modal([
        dbc.ModalHeader("Error"),
        dbc.ModalBody([html.P("NMA estimation and/or network generation failed: see error below and check your data",  style={"color":"red"}),
                       html.P(id="Rconsole-error-nma", style={"color":"white"})])],
        id="R-alert-nma",
        size="lg",
        is_open=False)

R_errors_pair = dbc.Modal([
        dbc.ModalHeader("Error"),
        dbc.ModalBody([html.P("Pairwise meta-analysis failed: see error below and check your data", style={"color":"red"}),
                       html.P(id="Rconsole-error-pw", style={"color":"white"})])],
        id="R-alert-pair",
        size="lg",
        is_open=False)

R_errors_league = dbc.Modal([
    dbc.ModalHeader("Error"),
    dbc.ModalBody([html.P("League table generation failed: see error below and check your data", style={"color":"red"}),
                   html.P(id="Rconsole-error-league", style={"color": "white"})])],
    id="R-alert-league",
    size="lg",
    is_open=False)


R_errors_funnel= dbc.Modal([
    dbc.ModalHeader("Error"),
    dbc.ModalBody([html.P("Funnel plot data generation failed: see error below and check your data", style={"color":"red"}),
                   html.P(id="Rconsole-error-funnel", style={"color": "white"})])],
    id="R-alert-funnel",
    size="lg",
    is_open=False)

