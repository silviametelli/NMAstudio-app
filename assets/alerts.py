import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

alert_outcome_type = dcc.ConfirmDialog(id='data-type-danger',
                                    message='Choose a correct outcome type')


alert_data_type = dcc.ConfirmDialog(id='data-missing-n-danger',
                                    message='sample size for each outcome missing')


R_errors_nma =  dcc.ConfirmDialog(
            message = "R function failed: see error below and check your data",
            id="R-alert-nma")

R_errors_pair =  dcc.ConfirmDialog(
            message = "R function failed: see error below and check your data",
            id="R-alert-pair")

R_errors_league =  dcc.ConfirmDialog(
            message = "R function failed: see error below and check your data",
            id="R-alert-league")

R_errors_funnel =  dcc.ConfirmDialog(
            message = "R function failed: see error below and check your data",
            id="R-alert-funnel")
