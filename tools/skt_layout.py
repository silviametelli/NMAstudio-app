
import dash_bootstrap_components as dbc, dash_html_components as html
from dash import dcc
from tools.navbar import Navbar
import dash_ag_grid as dag 
import pandas as pd
from assets.storage import DEFAULT_DATA
import numpy as np
import plotly.express as px, plotly.graph_objects as go

TITLE = "/assets/logos/Title.png"

# Create a DataFrame from the provided data
data = {
    'Ref': ["PBO" ,"" ,"" ,"" ,''],
    'Treatment': ["AIL1223", "ATA", "AIL17", "SM", "CSA"],
    'Mixed effect\n95%CI': ["RR 19.5\n(15.9, 23.9)", "RR 13.4\n(11.2, 15.9)", "RR 29.4\n(24.3, 35.6)", "RR 9.1\n(7.1, 12.5)", "RR 4.6\n(2.1, 10.3)"],
    'Pairwise effect\n95%CI': ["20.2\n(12.5, 32.6)", "16.7\n(12.3, 22.6)", "33.5\n(23.2, 48.3)", "0.12\n(0.07, 0.19)", "4.83\n(1.76, 13.24)"],
    'Indirect effect': [19.6, 12.5, 28.2, 12.5, None],
    'p-value': [0.96, 0.23, 0.6, 0.06, None],
    'RoB': ["low", "low", "low", "low", "high"],
    'Comments': [None, None, None, None, None]
}

out_list = [['PASI90',"Death"]]

outcome_list = [{'label': '{}'.format(out_name), 'value': out_name} for out_name in np.unique(out_list)]


treat_list = [['PBO',"AIL1223", "ATA", "AIL17", "SM", "CSA"]]

treatment_list = [{'label': '{}'.format(treat_name), 'value': treat_name} for treat_name in np.unique(treat_list)]



df = pd.DataFrame(data)

df['Value1'] = df['Mixed effect\n95%CI'].str.extract(r'(\d+\.\d+)')[0].astype(float)
df['Value2'] = df['Mixed effect\n95%CI'].str.extract(r'\((\d+\.\d+),')[0].astype(float)
df['Value3'] = df['Mixed effect\n95%CI'].str.extract(r', (\d+\.\d+)\)')[0].astype(float)

df['CI_width_hf'] = df.Value3 - df['Value1']
df['lower_error'] = df['Value1'] - df.Value2
df['weight'] = 1/df['CI_width_hf']

up_rng, low_rng = df.Value3.max(), df.Value2.min()
# up_rng = 10**np.floor(np.log10(up_rng))
# low_rng = 10 ** np.floor(np.log10(low_rng))

df['Graph'] = ''

for i in range(df.shape[0]):
    filterDf = df.iloc[i]
    filter_df = pd.DataFrame([filterDf])
    # fig = px.histogram(filterDf, x='Source', y='Money')
    fig = px.scatter(filter_df, x='Value1', y="Treatment",
                     error_x_minus='lower_error',
                     error_x='CI_width_hf' ,
                     log_x='Value1',
                     size_max=5,
                     range_x=[low_rng, up_rng],
                     size= 'weight',height=82)

    fig.update_layout(
            barmode='group',
            bargap=0.25,
            showlegend=False,
            yaxis_visible=False,
            yaxis_showticklabels=False,
            xaxis_visible=False,
            xaxis_showticklabels=False,
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            # template="plotly_dark",
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)')

    fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=10, x1=10,
                      line=dict(color="green", width=0.5,dash="dot"), layer='below')

    fig.update_traces(marker=dict(symbol='circle',
                                  opacity=0.8,
                                  line=dict(color='DarkSlateGrey'),
                                  color='green'),
                      error_x=dict(thickness=2.1, color='#313539')  # '#ef563b' nice orange trace
                      )
     

    df.at[i, "Graph"] = fig


columnDefs =  [
    {
        "field": "Ref",
        "rowSpan": {"function": "rowSpan(params)"},
        "cellClassRules": {
        "cell-span": "params.value==='PBO'"
        },
        'cellStyle': {'border-right': 'solid 0.8px',
                      'text-align': 'center',
                      'align-items': 'center',
                      'display': 'grid',
                      'padding':0,
                      'font-weight':'bold'
                      },
        "width": '100%'
    },
    {"field": "Treatment", "sortable": False,
      "filter": True, "width": 150,
      'cellStyle': {'font-weight':'bold'}},
    {"field": "Mixed effect\n95%CI", 
     "width": 150,
     'cellStyle': {'border-left': 'solid 0.8px',
                   'backgroud-color':'white'}
       },
    {
        "field": "Graph",
        "cellRenderer": "DCC_GraphClickData",
        "headerName": "Forest plot",
        "maxWidth": 500,
        "minWidth": 200,
        'cellStyle': {'border-right': 'solid 0.8px' ,'backgroud-color':'white'}

    },
    {"field": "Pairwise effect\n95%CI", "width": 170},
    {"field": "Indirect effect", "width": 120},
    {"field": "p-value", "width": 100},
    {"field": "RoB", "width": 90},
    {"field": "Comments", "width": 140, 'cellStyle': {'border-left': 'solid 0.5px'}},
    
    ]


n_row = df.shape[0]


grid = dag.AgGrid(
    id="quickstart-grid",
    className="ag-theme-alpine color-fonts ",
    rowData=df.to_dict("records"),
    columnDefs =  columnDefs,
    defaultColDef={
                    # "resizable": True, 
                #    "sortable": False, "filter": True,
                    "wrapText": True, 
                    'autoHeight': True,
                    'cellStyle': {'white-space': 'pre',
                                  'display': 'grid',
                                  'text-align': 'center',
                                  'align-items': 'center',
                                #   'border-right': 'solid 0.5px'
                                  },},
    columnSize="sizeToFit", 
    dashGridOptions = {'suppressRowTransform': True,}, 
    style={ "width": "100%",'height':f'{48 + 83 * n_row}px'}
    
)





def Sktpage():
    return html.Div([Navbar(), skt_layout()])

def skt_layout():
    return html.Div(id='skt_all',children=[dcc.Markdown('Scalable Knowledge Translation Tool',
                                                className="markdown_style_main",
                                                style={
                                                    "font-size": '30px',
                                                    'text-align': 'center',
                                                    'color':'#5c7780',
                                                       }),
                                            html.Div([dbc.Row([dbc.Col(html.Span('Title', className='title_first'),className='title_col1'), 
                                                              dbc.Col(dcc.Input(id='title_skt',
                                                                            value='Systemic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis', 
                                                                            style={'width':'800px'}
                                                                            ),className='title_col2')],
                                                                       className='row_skt'),
                                                      dbc.Row([dbc.Col([
                                                          dbc.Toast([html.Span('Study Design', className='study_design'),
                                                                     html.Span('Patients: patients with psoriasis',className='skt_span1'),
                                                                              html.Span('Primary outcome: PASI90',className='skt_span1'), 
                                                                              html.Span('Study design: randomized control study', className='skt_span1'),
                                                                              ], className='tab1',headerClassName='headtab1',bodyClassName='bodytab1'),],className='tab1_col'),

                                                                dbc.Col([
                                                                         dbc.Row([html.Span('Interventions', className='inter_label'),
                                                                                 html.Span('Please tick to select the reference treatment', className='note_tick')], style={'padding-top': 0}),
                                                                         dbc.Toast([
                                                                        #   html.Span('AIL1223',className='skt_span2'),
                                                                        #   html.Span('ATA',className='skt_span2'),
                                                                        #   html.Span('PBO',className='skt_span2'),
                                                                        #   html.Span('AIL17',className='skt_span2'),
                                                                        #   html.Span('SM' ,className='skt_span2'),
                                                                        #   html.Span('CSA',className='skt_span2'),
                                                                        dbc.RadioItems( options=treatment_list, value='PBO',inline=True, 
                                                                                       inputStyle={'width':'30px'}, 
                                                                                       style={'display': 'contents','font-size':"large"},
                                                                                       labelCheckedStyle={"color": "red"},
                                                                                       )
                                                                              ], bodyClassName= 'skt_interbody',className='skt_intervention',headerClassName='headtab1')], className='tab2_col')               
                                                                              ], className='row_skt'),

                                                      dbc.Row([dbc.Col([dbc.Toast([
                                                          html.Span('Select the outcome',className='select_outcome'),
                                                          dcc.Dropdown(id='select_dropdown',clearable=True, placeholder="",
                                                                       options=outcome_list,
                                                                       className="tapEdgeData-fig-class",
                                                                       style={'width': '150px', 'height': '30px',
                                                                              'display': 'inline-block',}
                                                                              ),],className='skt_studyinfo2', bodyClassName='slect_body',headerClassName='headtab1'),],
                                                                                style={'width':'220px'}),
                                                            dbc.Col(dbc.Toast(
                                                                              [html.Span('Data Source', className='study_design'),
                                                                              html.Span('Number of studies: 96',className='skt_span1'),
                                                                              html.Span('Number of participents: 1020',className='skt_span1'), 
                                                                              html.Span('Number of comparisions: 21', className='skt_span1'),
                                                                              html.Span('Number of comparisons with direct evidence: 13', className='skt_span1'),
                                                                              html.Span('Number of comparisons without direct evidence: 8', className='skt_span1'),
                                                                              ], className='skt_studyinfo',headerClassName='headtab1'), style={'width':'400px'}) ,
                                                            dbc.Col(html.Span('This is empty', className='empty_class'),style={'width':'580px','display' :'grid','align-items': 'center'})    
                                                                          
                                                                          ], className='row_skt'),
                                                    #   dbc.Row([dbc.Toast([html.Span('Number of studies: 96',className='skt_span1'),
                                                    #                           html.Span('Number of participents: 1020',className='skt_span1'), 
                                                    #                           html.Span('Number of comparisions: 21', className='skt_span1'),
                                                    #                           html.Span('Number of comparisons with direct evidence: 13', className='skt_span1'),
                                                    #                           html.Span('Number of comparisons without direct evidence: 8', className='skt_span1'),
                                                    #                           ], className='skt_studyinfo')], className='row_skt'),
                                                      dbc.Row([
                                                        #   dbc.Col(dbc.Toast([html.Span('Ref.',className='span_ref1'),
                                                        #                       html.Span('PBO', className='span_ref2')
                                                        #                       ],),className='skt_col1'),
                                                               dbc.Col([grid,],className='skt_col2'),
                                                                              ],className='skt_rowtable'),
                                                      html.Br(), html.Br(),
                                                      dbc.Row(),
                                                                              ]),])



