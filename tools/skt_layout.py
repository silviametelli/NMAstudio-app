
import dash_bootstrap_components as dbc, dash_html_components as html
from dash import dcc
from tools.navbar import Navbar
import dash_ag_grid as dag 
import pandas as pd
from assets.storage import DEFAULT_DATA
import numpy as np
import plotly.express as px, plotly.graph_objects as go
import dash_daq as daq




data = pd.read_csv('db/skt/final_all.csv')

pw_data = pd.read_csv('db/skt/forest_data_pairwise.csv')


df = pd.DataFrame(data)

out_list = [['PASI90',"Death"]]

outcome_list = [{'label': '{}'.format(out_name), 'value': out_name} for out_name in np.unique(out_list)]


# treat_list = [['PBO',"AIL1223", "ATA", "AIL17", "SM", "CSA"]]

treat_list = [np.unique(df.Treatment)]


treatment_list = [{'label': '{}'.format(treat_name), 'value': treat_name} for treat_name in np.unique(treat_list)]


# df['p-value'] = 0.05
certainty_values = ['High', 'Low', 'Moderate']
df['Certainty'] = np.random.choice(certainty_values, size=df.shape[0])

df['Comments'] = ['' for _ in range(df.shape[0])]
# df['Value1'] = df['Mixed effect\n95%CI'].str.extract(r'(\d+\.\d+)')[0].astype(float)
# df['Value2'] = df['Mixed effect\n95%CI'].str.extract(r'\((\d+\.\d+),')[0].astype(float)
# df['Value3'] = df['Mixed effect\n95%CI'].str.extract(r', (\d+\.\d+)\)')[0].astype(float)

df['CI_width_hf'] = df.CI_upper - df['RR']
df['lower_error'] = df['RR'] - df.CI_lower
df['weight'] = 1/df['CI_width_hf']


df = df.round(2)

# up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
# up_rng = 10**np.floor(np.log10(up_rng))
# low_rng = 10 ** np.floor(np.log10(low_rng))
def update_indirect_direct(row):
    if pd.isna(row['direct']):
        row['indirect'] = pd.NA
    elif pd.isna(row['indirect']):
        row['direct'] = pd.NA
    return row

df['Graph'] = ''


for j in range(0, 380, 19):
    data_ex = df[j:j + 19]
    up_rng, low_rng = data_ex.CI_upper.max(), data_ex.CI_lower.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))

    for i in range(j, j + 19):
        filterDf = df.iloc[i]
        filter_df = pd.DataFrame([filterDf])
        filter_df = filter_df.apply(update_indirect_direct, axis=1)

        filter_df = pd.concat([filter_df] * 4, ignore_index=True)


        filter_df['CI_width_hf'][3] = (filter_df.CI_upper[3] - filter_df['RR'][2]*1.2)
        filter_df['lower_error'][3] = (filter_df['RR'][3] - filter_df.CI_lower[2]*1.2)


        filter_df['Treatment'][1] = 'Direct'
        filter_df['RR'][1] = filter_df['direct'][1]
        filter_df['CI_width_hf'][1] = (filter_df.direct_up[1] - filter_df['direct'][1])
        filter_df['lower_error'][1] = (filter_df['direct'][1] - filter_df.direct_low[1])

        filter_df['Treatment'][0] = 'Indirect'
        filter_df['RR'][0] = filter_df['indirect'][0]
        filter_df['CI_width_hf'][0] = (filter_df.indirect_up[0] - filter_df['indirect'][0])
        filter_df['lower_error'][0] = (filter_df['indirect'][0] - filter_df.indirect_low[0])

        up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
        up_rng = 10**np.floor(np.log10(up_rng))

        colors = ['#ABB2B9', '#707B7C', 'red','black']
        fig = go.Figure()
        for idx in range(filter_df.shape[0]):
            data_point = filter_df.iloc[idx]
            if np.isnan(data_point['RR']):
                continue
            fig.add_trace(go.Scatter(
                            x=[data_point['RR']],
                            y=[data_point['Treatment']],
                            # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                            error_x=dict(type='data',color = colors[idx],array=[data_point['lower_error'],data_point['CI_width_hf']],visible=True),
                            marker=dict(color=colors[idx], size=12),
                            showlegend=False
                        ))
        
        fig.update_layout(
            barmode='group',
            bargap=0.25,
            # xaxis=dict(range=[min(low_rng, 0.1), max(up_rng, 10)]),
            showlegend=False,
            yaxis_visible=False,
            yaxis_showticklabels=False,
            xaxis_visible=False,
            xaxis_showticklabels=False,
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            height=95,  # Set the height to 82 pixels
            # width=200,  # Set the width to 200 pixels
            shapes=[
                dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0="0.8",
                    y0="0",
                    x1="1.25",
                    y1='1',
                    fillcolor="orange",
                    opacity=0.4,
                    line_width=0,
                    layer="below"
                ),]
            # template="plotly_dark",
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                        plot_bgcolor='rgba(0,0,0,0)')

        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                        line=dict(color="green", width=2,dash="dot"), layer='below')
    
            

        df.at[i, "Graph"] = fig

style_certainty = {'white-space': 'pre','display': 'grid','text-align': 'center','align-items': 'center'}
columnDefs1 =  [
    {
        "field": "Reference",
        "headerName": "Ref",
        "width": 100,
        "rowSpan": {"function": "rowSpan(params)"},
        "cellClassRules": {
        "cell-span": "params.value !==''"
        },
        'cellStyle': {'border-right': 'solid 0.8px',
                      'text-align': 'center',
                      'align-items': 'center',
                      'display': 'grid',
                      'padding':0,
                      'white-space': 'pre',
                      'font-weight':'bold'
                      },
        "width": '100%'
    },
    {"field": "Treatment", 
     "headerName": "Treatment",
     "sortable": False,
      "filter": True, "width": 130,
      'cellStyle': {
        #   'font-weight':'bold'
          }},
    {"field": "RR", 
     "headerName": "Mixed effect\n95%CI",
     "width": 180,
     'cellStyle': {'border-left': 'solid 0.8px',
                   'backgroud-color':'white',
                   'line-height': '20px',
                   }
       },
    {
        "field": "Graph",
        "cellRenderer": "DCC_GraphClickData",
        "headerName": "Forest plot",
        "width": 300,
        # "maxWidth": 500,
        # "minWidth": 250,
        'cellStyle': {'border-left': 'solid 0.8px',
                      'border-right': 'solid 0.8px' ,'backgroud-color':'white'}

    },
    {"field": "direct",
     "headerName": "Direct effect\n(95%CI)",
      "width": 170,
      'cellStyle': {'color': '#707B7C'}},
    {"field": "indirect",
     "headerName": "Indirect effect\n(95%CI)",
      "width": 170,
      'cellStyle': {'color': '#ABB2B9'}},
    {"field": "p-value",
     "headerName": "p-value\n(Consistency)",
      "width": 140},
    {"field": "Certainty", 
     "headerName": "Certainty",
     "width": 110,
     "tooltipField": 'Certainty',
     "tooltipComponentParams": { "color": '#d8f0d3' },
     'cellStyle':{
        "styleConditions": [
        {"condition": "params.value == 'High'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},   
        {"condition": "params.value == 'Low'", "style": {"backgroundColor": "#B85042", **style_certainty}},
        {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},       
    ]}},
    {"field": "Comments", "width": 120, 
     'cellStyle': {'border-left': 'solid 0.5px' }},
    
    ]


# n_row = df.shape[0]


grid = dag.AgGrid(
    id="quickstart-grid",
    className="ag-theme-alpine color-fonts ",
    rowData=df.to_dict("records"),
    columnDefs =  columnDefs1,
    dangerously_allow_code=True,
    defaultColDef={
                    # "resizable": True, 
                #    "sortable": False, "filter": True,
                    "wrapText": True, 
                    'autoHeight': True,
                    'cellStyle': {'white-space': 'pre',
                                  'display': 'grid',
                                  'text-align': 'center',
                                  'align-items': 'center',
                                  'border-bottom': 'solid 0.5px'
                                  },
                    "tooltipComponent": "CustomTooltip"
                    },
    columnSize="sizeToFit", 
    dashGridOptions = {'suppressRowTransform': True,
                       "rowSelection": "multiple",
                       "tooltipShowDelay": 100}, 
    # style={ "width": "100%",'height':f'{48 + 83 * n_row}px'}
    
)

####################################################################################################################################################################
####################################################################################################################################################################

model_skt_stand1 = dbc.Modal(
                        [dbc.ModalHeader("Header",className='forest_head'),
                            dbc.ModalBody([dcc.Loading(
                                    html.Div([
                                        dcc.Graph(
                                            id='forest-fig-pairwise',
                                            style={'height': '99%',
                                                'max-height': 'calc(52vw)',
                                                'width': '99%',
                                                'max-width': 'calc(52vw)'},
                                            config={'editable': True,
                                            'edits': dict(annotationPosition=True,
                                                        annotationTail=True,
                                                        annotationText=True, axisTitleText=False,
                                                        colorbarPosition=False,
                                                        colorbarTitleText=False,
                                                        titleText=False,
                                                        legendPosition=True, legendText=True,
                                                        shapePosition=True),
                                                'modeBarButtonsToRemove': [
                                                    'toggleSpikelines',
                                                    "pan2d",
                                                    "select2d",
                                                    "lasso2d",
                                                    "autoScale2d",
                                                    "hoverCompareCartesian"],
                                                'toImageButtonOptions': {
                                                    'format': 'png',
                                                    # one of png, svg,
                                                    'filename': 'custom_image',
                                                    'scale': 3.5
                                                    # Multiply title/legend/axis/canvas sizes by this factor
                                                },
                                                'displaylogo': False})], 
                                                style={'height': '450px'})
                                                ),],className='forest_body'),
                            dbc.ModalFooter(dbc.Button( "Close", id="close_forest", className="ms-auto", n_clicks=0), className='forest_close'),
                    ],id="modal_forest", is_open=False, scrollable=True,contentClassName="forest_content")

model_skt_stand2 = dbc.Modal(
        [dbc.ModalHeader("Header",className='skt_info_head'),
            dbc.ModalBody(
                [
                html.Span('Treatment: FUM, Comparator: PBO',className='skt_span_info'),
                html.Span('Randomize control studies: 3',className='skt_span_info'),
                html.Span('Total participants in arm: 1929',className='skt_span_info'), 
                html.Span('Mean age: xxx)', className='skt_span_info'),
                html.Span('Mean male percentage: XXX', className='skt_span_info'),
                ],className='skt_info_body'),
            dbc.ModalFooter(dbc.Button( "Close", id="close_compare", className="ms-auto", n_clicks=0), className='skt_info_close'),
    ],id="skt_modal_copareinfo", is_open=False, scrollable=True,contentClassName="forest_content")
                                                        
radio_treattment = dbc.RadioItems(id='ref_selected', options=treatment_list, value='PBO',inline=True, 
                                                                                       inputStyle={'width':'30px'}, 
                                                                                       style={'display': 'contents','font-size':"medium"},
                                                                                       labelCheckedStyle={"color": "red"},)
model_password = dbc.Modal(
        [
            dbc.ModalBody(
                [
                html.Span('Input the password:', style={'font-size':'large'}),
                dcc.Input(id='password', className='upload_radio', style={'width':'150px'}),
                html.Br(),
                dbc.Button( "OK", id="password_ok",n_clicks=0, style={'background-color':'grey'})
                ]),
    ],id="pass_model", is_open=True, contentClassName="pass_content", style={'display':'grid'})
####################################################################################################################################################################
####################################################################################################################################################################
# instruct_plot = ('/assets/figure/instruction_skt1.png')

empty = [html.Span('Instruction',className='skt_span1', 
                   style={'color': '#B85042', 'font-weight': 'bold'}),
         html.Span([html.Strong('Ref:'), ' selected reference treatment\n',
                    html.Strong('Treatment:'), ' click the cell to see the corresponding comparison information\n',
                    html.Strong('Direct effect:'), ' click to see the forestplot for the corresponding comparsion\n',
                    html.Strong('Certainty:'), ' hover your mouse see the details about certainty of evidence\n',
                    html.Strong('Comments:'), ' editable, add comments if necessary'],
                   className='empty_class'),
        #  html.Img(src=instruct_plot, height="100px", style={'justify-self': 'center'})
                   ]

def Sktpage():
    return html.Div([Navbar(), skt_layout()])

def skt_layout():
    return html.Div([model_password,
    html.Div(id='skt_all',children=[dcc.Markdown('Scalable Knowledge Translation Tool',
                                                className="markdown_style_main",
                                                style={
                                                    "font-size": '30px',
                                                    'text-align': 'center',
                                                    'color':'#5c7780',
                                                       }),
                                            dbc.Col([
                                                html.P(
                                                "Standard skt",
                                                id='skttable_1',
                                                style={'display': 'inline-block',
                                                        'margin': 'auto',
                                                        'font-size': '10px',
                                                        'padding-left': '0px'}),
                                                daq.ToggleSwitch(
                                                    id='toggle_grid_select',
                                                    value = False,
                                                    color='green', size=30, vertical=False,
                                                    label={'label': "",
                                                            'style': dict(color='white', font='0.5em')},
                                                    labelPosition="top",
                                                    style={'display': 'inline-block',
                                                            'margin': 'auto', 'font-size': '10px',
                                                            'padding-left': '2px',
                                                            'padding-right': '2px'}),
                                                html.P('league table',
                                                        id='skttable_2',
                                                        style={'display': 'inline-block',
                                                            'margin': 'auto',
                                                            'font-size': '10px',
                                                            'padding-right': '0px'})],
                                                style={'justify-content': 'flex-end',
                                                        'margin-left': '70%',
                                                        'font-size': '0.8em', 'margin-top': '2%'},
                                                ),
                                            html.Br(),html.Br(),
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
                                                                        radio_treattment
                                                                              ], bodyClassName= 'skt_interbody',
                                                                              className='skt_intervention',
                                                                              headerClassName='headtab1',id='treatment_toast')], className='tab2_col')               
                                                                              ], className='row_skt'),

                                                      dbc.Row([dbc.Col([dbc.Toast([
                                                          html.Span('Select the outcome',className='select_outcome'),
                                                          dcc.Dropdown(id='select_dropdown',clearable=True, placeholder="",
                                                                       options=outcome_list,
                                                                       className="tapEdgeData-fig-class",
                                                                       style={'width': '150px', 'height': '30px',
                                                                              'display': 'inline-block',}
                                                                              ),
                                                          html.Span('Enter the baseline risk per 1000',className='select_outcome'),
                                                          dcc.Input(id="base_risk_input",
                                                                    type="text",
                                                                    name='risk',
                                                                    value=20,
                                                                    placeholder="e.g. 20",) 
                                                                              ],className='skt_studyinfo2', bodyClassName='slect_body',headerClassName='headtab1'),],
                                                                                style={'width':'220px'}),
                                                            dbc.Col(dbc.Toast(
                                                                              [html.Span('Data Source', className='study_design'),
                                                                              html.Span('Number of studies: 96',className='skt_span1'),
                                                                              html.Span('Number of participents: 1020',className='skt_span1'), 
                                                                              html.Span('Number of comparisions: 21', className='skt_span1'),
                                                                              html.Span('Number of comparisons with direct evidence: 13', className='skt_span1'),
                                                                              html.Span('Number of comparisons without direct evidence: 8 \n', className='skt_span1', style={'border-bottom': 'dashed 1px gray'}),
                                                                            #   html.Br(),
                                                                              html.Span('Potential effect modifires Info',className='skt_span1', style={'color': '#B85042', 'font-weight': 'bold'}),
                                                                            #   html.Br(),
                                                                              html.Span('Mean age: 45.3',className='skt_span1'),
                                                                              html.Span('Mean male percentage: 43.4%',className='skt_span1'),
                                                                              ], className='skt_studyinfo',headerClassName='headtab1'), style={'width':'400px'}) ,
                                                            dbc.Col(empty,style={'width':'560px','margin-left': '20px', 'border': '1px dashed rgb(184, 80, 66)','display':'grid'})    
                                                                          
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
                                                               dbc.Col([grid, model_skt_stand1, model_skt_stand2],className='skt_col2', id = 'grid_type'),
                                                                              ],className='skt_rowtable'),
                                                      html.Br(), html.Br(),
                                                      dbc.Row(),
                                                                              ]),], style={'display':'none'})])

####################################################################################################################################################################
####################################################################################################################################################################

df_league = pd.read_csv("db/skt/league_table.csv")

n_row =df_league.shape[0]

# def add_line_break(value):
#     return str(value).replace("(", "\n(")

# # Apply the function to the entire DataFrame
# df_league = df_league.applymap(add_line_break)

column_names = df_league.columns.tolist()


for idx, column in enumerate(column_names):
    if idx < 2:
        pass   
    for row_idx in range(idx-1):
        treat1 = column
        treat2 = df_league['Treatment'][row_idx]
        df_league.iloc[row_idx,idx] = f' {treat2} VS. {treat1} \n Randomize control studies: 3\n Total participants in arm: xxx \n Mean age: xxx \nMean male percentage: XXX'

for column_idx, column in enumerate(column_names):
    if column_idx < 1 or column_idx >19:
        continue


    for row_idx in range(column_idx, n_row):

        filterdata = df_league.iloc[row_idx]
        filterdata = pd.DataFrame([filterdata])
        treat_t = filterdata['Treatment'].iloc[0]
        treat_c = column_names[column_idx]
        direct_info = df[(df['Treatment'] == treat_c) & (df['Reference'] == treat_t)]
        direct_info = direct_info.apply(update_indirect_direct, axis=1)
        filterdata = df_league.iloc[row_idx]
        filter_df = pd.DataFrame([filterdata])  
        filter_df[column_names[column_idx]] = filter_df[column_names[column_idx]].str.replace(r'\s', '', regex=True)

        filter_df['point'] = filter_df[column_names[column_idx]].str.extract(r'(\d+\.\d+)')[0].astype(float)
        filter_df['lower'] = filter_df[column_names[column_idx]].str.extract(r'\((\d+\.\d+),')[0].astype(float)
        filter_df['upper'] = filter_df[column_names[column_idx]].str.extract(r',(\d+\.\d+)\)')[0].astype(float)
        filter_df['CI_width_hf'] = (filter_df.upper - filter_df['point'])
        filter_df['lower_error'] = (filter_df['point'] - filter_df.lower)
    
        filter_df['direct'] = direct_info['direct']
        filter_df['indirect'] = direct_info['indirect']
        
        filterDf = filter_df.iloc[0]
        filter_df = pd.DataFrame([filterDf])

        filter_df = pd.concat([filter_df] * 4, ignore_index=True)

        filter_df['CI_width_hf'][3] = (direct_info.CI_upper - direct_info['RR']*1.2)
        filter_df['lower_error'][3] = (direct_info['RR'] - direct_info.CI_lower*1.2)


        filter_df['Treatment'][1] = 'Direct'
        filter_df['point'][1] = direct_info['direct']
        filter_df['CI_width_hf'][1] = (direct_info.direct_up - direct_info['direct'])
        filter_df['lower_error'][1] = (direct_info['direct'] - direct_info.direct_low)

        filter_df['Treatment'][0] = 'Indirect'
        filter_df['point'][0] = direct_info['indirect']
        filter_df['CI_width_hf'][0] = (direct_info.indirect_up - direct_info['indirect'])
        filter_df['lower_error'][0] = (direct_info['indirect'] - direct_info.indirect_low)

        # filter_df['weight'] = 1/(filter_df.upper - filter_df.lower)
        # error_x_colors = ['red', 'black']

        colors = ['#C35214', '#4D4DFF', 'red','black']
        text1 = f"<b>{treat_c} VS. {treat_t}</b> <span style='color:black'><br>{filter_df[column_names[column_idx]][0]}</span>"
        text2 = f"<span style='color:#4D4DFF'><br>{direct_info['direct'].iloc[0]}({direct_info['direct_low'].iloc[0]},{direct_info['direct_up'].iloc[0]})</span>" if pd.notna(direct_info['direct'].iloc[0]) else ""
        text3 =f"<span style='color:#C35214'><br>{direct_info['indirect'].iloc[0]}({direct_info['indirect_low'].iloc[0]},{direct_info['indirect_up'].iloc[0]})</span>" if pd.notna(direct_info['indirect'].iloc[0]) else ""
        text_leagtab = text1+text2+text3

        fig = go.Figure()
        for idx in range(filter_df.shape[0]):
            data_point = filter_df.iloc[idx]
            if not pd.notna(data_point['point']):
                continue
            fig.add_trace(go.Scatter(
                            x=[data_point['point']],
                            y=[data_point['Treatment']],
                            # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                            error_x=dict(type='data',color = colors[idx],array=[data_point['lower_error'],data_point['CI_width_hf']],visible=True),
                            marker=dict(color=colors[idx], size=8),
                            showlegend=False,
                        ))

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
                hovermode = False,
                height=150,  # Set the height to 100 pixels
                width=200,
                shapes=[
                dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0="0.8",
                    y0="0",
                    x1="1.25",
                    y1='1',
                    fillcolor="gray",
                    opacity=0.4,
                    line_width=0,
                    layer="below"
                ),]
               
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=1,dash="dot"), layer='below')


        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

        fig.add_annotation(
                            x=np.log10(2), 
                            y=1, 
                            # xanchor='center',  align='center',yanchor='top',
                            # xref='paper', yref='y domain',
                            # text= f"<b>{treat_c} VS. {treat_t}</b> <br>{filter_df[column_names[column_idx]][0]}",
                            text = text_leagtab,
                            showarrow=False, font=dict(size=12)
                            )
        # fig.add_annotation(
        #                     # x=np.log10(np.abs(filter_df['point'][0])),
        #                     x=np.log10(2),
        #                     y = 0.7,
        #                     # xanchor='center',  align='center',yanchor='top',
        #                     # xref='paper', yref='y domain',
        #                     text= f"<br>",
        #                     showarrow=False,
        #                     font=dict(size=12,color = 'gray'))

        df_league.iloc[row_idx, column_idx] = fig


treatnames = df_league.columns[1:]

default_style = {'white-space': 'pre',
                'display': 'grid',
                'text-align': 'center',
                # 'align-items': 'center',
                'border': 'solid 0.5px gray',
                # 'line-height': 'initial'
                'height' : '163px',
                'line-height': 'normal'
                }

columnDefs2=[
    {"field": "Treatment", 
     "headerName": "Treatment",
     "tooltipField": 'ticker',
     "tooltipComponentParams": { "color": '#d8f0d3' },
     "sortable": False,
     "filter": True, 
     'cellStyle': {'font-weight':'bold',
                    'background-color':'#B85042','color':'white','font-size':'12px', **default_style}}  
    ]+[{"field": i,
        "cellRenderer": "DCC_GraphClickData",
        "maxWidth": 500,
        "minWidth": 300,
        'cellStyle': {"styleConditions":[{"condition": f"params.value === '{i}'", 
                                       "style": {"backgroundColor": "antiquewhite", **default_style}},
                                       {"condition": f"params.value !== '{i}'", 
                                       "style": {**default_style}}
                                       ]}}  for i in treatnames]

grid2 = dag.AgGrid(
    id="grid2",
    rowData=df_league.to_dict("records"),
    columnDefs= columnDefs2,
    defaultColDef={"resizable": False, 
                   "filter": True, "minWidth":125,
                   "wrapText": True, 
                   'autoHeight': True,
                    'cellStyle': {'white-space': 'pre',
                                  'display': 'grid2',
                                  'text-align': 'center',
                                #   'align-items': 'center',
                                  'background-color':'#E7E8D1',
                                  'border': 'solid 0.5px gray',
                                #   "styleConditions":styleConditions
                                    # "styleConditions": [
                                    #   {"condition": "params.value === 'ADA'", 
                                    #    "style": {"backgroundColor": "green"}}]
                                },
                   }, 
    columnSize="sizeToFit",
    # dashGridOptions = {'suppressRowTransform': True,
    #                    "rowSelection": "multiple",
    #                    "tooltipShowDelay": 100}, 
    style={'width': '1200px','height': f'{48 + 163 * n_row}px'},
)

checklist = dcc.Checklist(options= df_league.columns[1:], value= df_league.columns[1:3].values, 
                          id='checklist_treat', style={'display': 'contents'})
button_clear=html.Button('select all', id='clear-val', n_clicks=0)


