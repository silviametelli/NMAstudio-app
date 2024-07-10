
import dash_bootstrap_components as dbc, dash_html_components as html
from dash import dcc
from tools.navbar import Navbar
import dash_ag_grid as dag 
import pandas as pd
from assets.storage import DEFAULT_DATA
import numpy as np
import plotly.express as px, plotly.graph_objects as go
import dash_daq as daq
from tools.functions_skt_forestplot import __skt_all_forstplot, __skt_PI_forstplot, __skt_direct_forstplot, __skt_indirect_forstplot, __skt_PIdirect_forstplot, __skt_PIindirect_forstplot,__skt_directin_forstplot, __skt_mix_forstplot
import os


data = pd.read_csv('db/skt/final_all.csv')
pw_data = pd.read_csv('db/skt/forest_data_prws.csv')
df = pd.DataFrame(data)

cinima_dat = pd.read_csv('db/Cinema/cinema_report_PASI90.csv')

out_list = [['PASI90',"SAE"]]

outcome_list = [{'label': '{}'.format(out_name), 'value': out_name} for out_name in np.unique(out_list)]


# treat_list = [['PBO',"AIL1223", "ATA", "AIL17", "SM", "CSA"]]

treat_list = [np.unique(df.Treatment)]


treatment_list = [{'label': '{}'.format(treat_name), 'value': treat_name} for treat_name in np.unique(treat_list)]

df['Certainty']= ''
df['within_study'] = ''
df['reporting'] = ''
df['indirectness'] = ''
df['imprecision'] = ''
df['heterogeneity'] = ''
df['incoherence'] = ''

for i in range(df.shape[0]):
    src = df['Reference'][i]
    trgt = df['Treatment'][i]
    slctd_comps = [f'{src}:{trgt}']
    slctd_compsinv = [f'{trgt}:{src}']
    cinima_df = cinima_dat[cinima_dat['Comparison'].isin(slctd_comps) | cinima_dat['Comparison'].isin(slctd_compsinv)]
    df['Certainty'][i] = cinima_df['Confidence rating'].iloc[0]
    df['within_study'][i] = cinima_df['Within-study bias'].iloc[0]
    df['reporting'][i] = cinima_df['Reporting bias'].iloc[0]
    df['indirectness'][i] = cinima_df['Indirectness'].iloc[0]
    df['imprecision'][i] = cinima_df['Imprecision'].iloc[0]
    df['heterogeneity'][i] = cinima_df['Heterogeneity'].iloc[0]
    df['incoherence'][i] = cinima_df['Incoherence'].iloc[0]




# df['p-value'] = 0.05
# certainty_values = ['High', 'Low', 'Moderate']
# df['Certainty'] = np.random.choice(certainty_values, size=df.shape[0])

df['Comments'] = ['' for _ in range(df.shape[0])]
df['CI_width_hf'] = df.CI_upper - df['RR']
df['lower_error'] = df['RR'] - df.CI_lower
df['weight'] = 1/df['CI_width_hf']


df = df.round(2)

up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
up_rng = 10**np.floor(np.log10(up_rng))
low_rng = 10 ** np.floor(np.log10(low_rng))

def update_indirect_direct(row):
    if pd.isna(row['direct']):
        row['indirect'] = pd.NA
    elif pd.isna(row['indirect']):
        row['direct'] = pd.NA
    return row

df['Graph'] = ''
df['risk'] = 'Enter a number'
df['Scale_lower'] = 'Enter a value for lower'
df['Scale_upper'] = 'Enter a value for upper'
df['ab_effect'] = ''
df['ab_difference'] = ''



# df_mix = __skt_mix_forstplot(df,0.8,1.25)
df_all = __skt_all_forstplot(df,0.8,scale_lower=None, scale_upper=None, refer_name=None)
# df_PI = __skt_PI_forstplot(df,0.8,1.25)
# df_direct = __skt_direct_forstplot(df,0.8,1.25)
# df_indirect = __skt_indirect_forstplot(df,0.8,1.25)
# df_PIdirect = __skt_PIdirect_forstplot(df,0.8,1.25)
# df_PIindirect = __skt_PIindirect_forstplot(df,0.8,1.25)
# df_directin = __skt_directin_forstplot(df,0.8,1.25)
df = df_all

grouped = df.groupby(["Reference", "risk", 'Scale_lower', 'Scale_upper'])
rowData = []
for (ref, risk, Scale_lower, Scale_upper), group in grouped:
    treatments = []
    for _, row in group.iterrows():
        treatment_data = {"Treatment": row["Treatment"], 
                          "RR": row["RR"], "direct": row["direct"],
                          "Graph": row["Graph"], "indirect": row["indirect"],
                          "p-value": row["p-value"], "Certainty": row["Certainty"],
                          "direct_low": row["direct_low"],"direct_up": row["direct_up"],
                          "indirect_low": row["indirect_low"],"indirect_up": row["indirect_up"],
                          "CI_lower": row["CI_lower"],"CI_upper": row["CI_upper"],
                          "Comments": row["Comments"],"ab_effect": row["ab_effect"],
                          "ab_difference": row["ab_difference"],
                          "within_study": row["within_study"],"reporting": row["reporting"],
                          "indirectness": row["indirectness"],"imprecision": row["imprecision"],
                          "heterogeneity": row["heterogeneity"],"incoherence": row["incoherence"],
                          }
        treatments.append(treatment_data)
    rowData.append({"Reference": ref, "risk": risk,
                    'Scale_lower': Scale_lower ,
                    'Scale_lower': Scale_upper ,"Treatments": treatments})

row_data = pd.DataFrame(rowData)


row_data_default = []
for (ref, risk, Scale_lower, Scale_upper), group in grouped:
    treatments = []
    for _, row in group.iterrows():
        treatment_data = {"Treatment": row["Treatment"], 
                          "RR": row["RR"], "direct": row["direct"],
                          "Graph": row["Graph"], "indirect": row["indirect"],
                          "p-value": row["p-value"], "Certainty": row["Certainty"],
                          "direct_low": row["direct_low"],"direct_up": row["direct_up"],
                          "indirect_low": row["indirect_low"],"indirect_up": row["indirect_up"],
                          "CI_lower": row["CI_lower"],"CI_upper": row["CI_upper"],
                          "Comments": row["Comments"],"ab_effect": row["ab_effect"],
                          "ab_difference": row["ab_difference"],
                          "within_study": row["within_study"],"reporting": row["reporting"],
                          "indirectness": row["indirectness"],"imprecision": row["imprecision"],
                          "heterogeneity": row["heterogeneity"],"incoherence": row["incoherence"],
                          }
        treatments.append(treatment_data)
    row_data_default.append({"Reference": ref, "risk": risk,
                    'Scale_lower': Scale_lower ,
                    'Scale_upper': Scale_upper ,"Treatments": treatments})

row_data_default = pd.DataFrame(row_data_default)

for j in range(0, row_data_default.shape[0]):
    
    detail_data = row_data_default.loc[j, 'Treatments']
    detail_data = pd.DataFrame(detail_data)
    
    for i in range(1,detail_data.shape[0]):
        row_data_default.loc[j,'Treatments'][i]['RR'] = str(row_data_default.loc[j,'Treatments'][i]['RR'])+ '\n(' + str(row_data_default.loc[j,'Treatments'][i]['CI_lower']) + ', ' + str(row_data_default.loc[j,'Treatments'][i]['CI_upper']) + ')'
        row_data_default.loc[j,'Treatments'][i]['direct'] = f"{row_data_default.loc[j,'Treatments'][i]['direct']}" + f"\n({row_data_default.loc[j,'Treatments'][i]['direct_low']}, {row_data_default.loc[j,'Treatments'][i]['direct_up']})" if pd.notna(row_data_default.loc[j,'Treatments'][i]['direct']) else ""
        row_data_default.loc[j,'Treatments'][i]['indirect'] = f"{row_data_default.loc[j,'Treatments'][i]['indirect']}" + f"\n({row_data_default.loc[j,'Treatments'][i]['indirect_low']}, {row_data_default.loc[j,'Treatments'][i]['indirect_up']})" if pd.notna(row_data_default.loc[j,'Treatments'][i]['indirect']) else ""
        



style_certainty = {'white-space': 'pre','display': 'grid','text-align': 'center','align-items': 'center','border-left': 'solid 0.8px'}

masterColumnDefs = [
    {
        "headerName": "Reference Treatment",
        "field": "Reference",
        "cellRenderer": "agGroupCellRenderer",
        'cellStyle': {'border-left': 'solid 0.8px',
                      'border-right': 'solid 0.8px'}
        # "cellRendererParams": {
        #     'innerRenderer': "DCC_GraphClickData",
        # },
    },
    {"headerName": "Risk per 1000", 
     "field": "risk",
     "editable": True,
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}
     },
     {"headerName": "Scale lower\n(forestplots)", 
     "field": "Scale_lower",
     "editable": True,
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}
     },
    {"headerName": "Scale upper\n(forestplots)", 
     "field": "Scale_upper",
     "editable": True,
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}}
]
detailColumnDefs = [
   
    {"field": "Treatment", 
     "headerName": 'Treatment',
    #  "checkboxSelection": {"function": "params.data.Treatment !== 'Instruction'"},
     "sortable": False,
     "filter": True,
     "width": 130,
     'headerTooltip': 'Treatment',
      "resizable": True ,
      'cellStyle': {
        'display': 'grid',
        "text-align":'center',
        'white-space': 'pre',
        'line-height': 'normal',
        'align-items': 'center'
          }},
    
    {"field": "RR", 
     "headerName": "Mixed effect\n95%CI",
     "width": 180,
     "resizable": True,
     'cellStyle': {'border-left': 'solid 0.8px',
                   'backgroud-color':'white',
                #    'line-height': '20px',
                   "text-align":'center',
                   'white-space': 'pre',
                   'display': 'grid',
                   'line-height': 'normal',
                   'align-items': 'center'
                   }
       },

    {"field": "ab_effect", 
     "headerName": "Absolute Effect",
     "width": 180,
     "resizable": True,
     'cellStyle': {'border-left': 'solid 0.8px',
                   'backgroud-color':'white',
                #    'line-height': '20px',
                   "text-align":'center',
                   'white-space': 'pre',
                   'display': 'grid',
                   'line-height': 'normal',
                   'align-items': 'center'
                   }
       },

       {"field": "ab_difference", 
     "headerName": "Absolute Difference",
     "width": 180,
     "resizable": True,
     'cellStyle': {'border-left': 'solid 0.8px',
                   'backgroud-color':'white',
                #    'line-height': '20px',
                   "text-align":'center',
                   'white-space': 'pre',
                   'display': 'grid',
                   'line-height': 'normal',
                   'align-items': 'center'
                   }
       },

    {
        "field": "Graph",
        "cellRenderer": "DCC_GraphClickData",
        "headerName": "Forest plot",
        "width": 300,
        "resizable": True,
        'cellStyle': {'border-left': 'solid 0.8px',
                      'border-right': 'solid 0.8px' ,'backgroud-color':'white'}

    },
    {"field": "direct",
     "headerName": "Direct effect\n(95%CI)",
      "width": 170,
      "resizable": True,
      'cellStyle': {'color': '#707B7C', "text-align":'center', 'display': 'grid',
                    'white-space': 'pre', 'line-height': 'normal', 'align-items': 'center'}},
    {"field": "indirect",
     "headerName": "Indirect effect\n(95%CI)",
      "width": 170,
      "resizable": True,
      'cellStyle': {'color': '#ABB2B9', "text-align":'center','display': 'grid',
                    'white-space': 'pre', 'line-height': 'normal', 'align-items': 'center'}},
    {"field": "p-value",
     "headerName": "p-value\n(Consistency)",
      "width": 140,
      "resizable": True,
      'cellStyle': {"text-align":'center', 'display': 'grid','line-height': 'normal',
                    'white-space': 'pre', 'align-items': 'center'}
      },
    {"field": "Certainty", 
     "headerName": "Certainty",
     "width": 110,
     "resizable": True,
     "tooltipField": 'Certainty',
     "tooltipComponentParams": { "color": '#d8f0d3'},
     "tooltipComponent": "CustomTooltip",
     'cellStyle':{
        "styleConditions": [
        {"condition": "params.value == 'High'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},   
        {"condition": "params.value == 'Low'", "style": {"backgroundColor": "#B85042", **style_certainty}},
        {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},       
    ]}},
    {"field": "Comments", "width": 120, "resizable": True,
     'editable': True,
     'cellStyle': {'border-left': 'solid 0.5px',"text-align":'center', 'display': 'grid','border-right': 'solid 0.8px'}},
    
    ]


getRowStyle = {
    "styleConditions": [
        {
            "condition": "params.data.RR === 'RR'",
            "style": {"backgroundColor": "#faead7",'font-weight': 'bold'},
        },
    ]
}

grid = dag.AgGrid(
    id="quickstart-grid",
    className="ag-theme-alpine color-fonts",
    enableEnterpriseModules=True,
    licenseKey=os.environ["AG_GRID_KEY"],
    columnDefs=masterColumnDefs,
    rowData = row_data_default.to_dict("records"),
    masterDetail=True,
    # getRowStyle=getRowStyle,
    detailCellRendererParams={
                "detailGridOptions": {
                "columnDefs": detailColumnDefs,
                "rowHeight": 60,
                "rowDragManaged": True,
                "rowDragMultiRow": True,
                "rowDragEntireRow": True,
                "rowSelection": "multiple",
                'getRowStyle': getRowStyle,
                },
                "detailColName": "Treatments",
                "suppressCallback": True,
            },
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
                                  'border-bottom': 'solid 0.5px',
                                #   'background-color':'#faead7'
                                  },
                    # "tooltipComponent": "CustomTooltip"
                    },
    columnSize="sizeToFit", 
    dashGridOptions = {'suppressRowTransform': True,
                    #    "domLayout":'print',
                       "rowSelection": "multiple",
                       "tooltipShowDelay": 100,
                       "rowDragManaged": True,
                       "rowDragMultiRow": True,
                       "rowDragEntireRow": True,
                    #    "detailRowHeight": 70+83*19,
                       "detailRowAutoHeight": True,
                       }, 
    getRowId='params.data.Reference',
    style={ "width": "100%",
           'height':f'{45.5 *20}px'
           }
    
)

####################################################################################################################################################################
####################################################################################################################################################################

model_skt_stand1 = dbc.Modal(
                        [dbc.ModalHeader("Pairwise Forest Plot",className='forest_head'),
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
        [dbc.ModalHeader("Detail information",className='skt_info_head'),
            dbc.ModalBody(
                [
                html.Span('Treatment: FUM, Comparator: PBO',className='skt_span_info'),
                html.Span('Randomize control studies: 3',className='skt_span_info'),
                html.Span('Total participants: 1929',className='skt_span_info'), 
                html.Span('Mean age: xxx', className='skt_span_info'),
                html.Span('Mean male percentage: XXX', className='skt_span_info'),
                ],className='skt_info_body'),
            dbc.ModalFooter(dbc.Button( "Close", id="close_compare", className="ms-auto", n_clicks=0), className='skt_info_close'),
    ],id="skt_modal_copareinfo", is_open=False, scrollable=True,contentClassName="forest_content")
                                                        
radio_treattment = dbc.RadioItems(id='ref_selected', options=treatment_list, value='PBO',inline=True, 
                                                                                       inputStyle={'width':'30px'}, 
                                                                                style={'display': 'contents','font-size':"medium"},
                                                                                      labelCheckedStyle={"color": "red"},)

display_treatment = [html.Span(treat, className='span_treat') for treat in treat_list[0]]




model_password = dbc.Modal(
        [
            dbc.ModalBody(
                [
                html.Span('Input the password:', style={'font-size':'large'}),
                dcc.Input(id='password', className='upload_radio', style={'width':'150px'}),
                html.Br(),
                dbc.Button( "OK", id="password_ok",n_clicks=0, style={'background-color':'grey'})
                ]),
    ],id="pass_model", is_open=True, contentClassName="pass_content", style={'display':'block'})
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
options_effects = [
       {'label': 'Add prediction interval to forestplots', 'value': 'PI'},
       {'label': 'Add direct effects to forestplots', 'value': 'direct'},
       {'label': 'Add indirect effects to forestplots', 'value': 'indirect'},
   ]

def Sktpage():
    return html.Div([Navbar(), model_password], id='skt_page_content')



def skt_layout():
    return html.Div([
        # model_password,
    html.Div(id='skt_all',children=[dcc.Markdown('Scalable Knowledge Translation Tool',
                                                className="markdown_style_main",
                                                style={
                                                    "font-size": '30px',
                                                    'text-align': 'center',
                                                    'color':'#5c7780',
                                                       }),
                                    # html.Button("Export to Excel", id="btn-excel-export"),
                                    # html.Button("print", id="grid-printer-layout-btn"),
                                    # html.Button("regular", id="grid-regular-layout-btn"),
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
                                            html.Div([dbc.Row([dbc.Col(html.Span('Project Title', className='title_first'),className='title_col1'), 
                                                              dbc.Col(dcc.Input(id='title_skt',
                                                                            value='Systematic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis', 
                                                                            style={'width':'800px'}
                                                                            ),className='title_col2')],
                                                                       className='row_skt'),
                                                      dbc.Row([dbc.Col([
                                                          dbc.Toast([html.Span('PICOS', className='study_design'),
                                                                     dcc.Textarea(value ='Patients: patients with psoriasis\n'+
                                                                                'Primary outcome: PASI90\n'+
                                                                                'Study design: randomized control study'
                                                                                ,className='skt_span1'),
                                                                            #   html.Span('Primary outcome: PASI90',className='skt_span1'), 
                                                                            #   html.Span('Study design: randomized control study', className='skt_span1'),
                                                                              ], className='tab1',headerClassName='headtab1',bodyClassName='bodytab1')
                                                                              ],className='tab1_col'),

                                                                dbc.Col([
                                                                         dbc.Row([html.Span('Interventions', className='inter_label'),
                                                                                #  html.Span('Please tick to select the reference treatment', className='note_tick')
                                                                                 ], style={'padding-top': 0}),
                                                                         dbc.Toast(
                                                                                display_treatment, 
                                                                                bodyClassName='skt_interbody',
                                                                                className='skt_intervention',
                                                                                headerClassName='headtab1',
                                                                                id='treatment_toast'
                                                                              )
                                                                              ], className='tab2_col')               
                                                                              ], className='row_skt'),

                                                      dbc.Row([
                                                            dbc.Col(dbc.Toast(
                                                                              [html.Span('Overall Info', className='study_design'),
                                                                              html.Span('Number of studies: 96',className='skt_span1'),
                                                                              html.Span('Number of participents: 1020',className='skt_span1'), 
                                                                              html.Span('Number of comparisions: 21', className='skt_span1'),
                                                                              html.Span('Number of comparisons with direct evidence: 13', className='skt_span1'),
                                                                              html.Span('Number of comparisons without direct evidence: 8 \n', className='skt_span1',
                                                                                        #  style={'border-bottom': 'dashed 1px gray'}
                                                                                         )
                                                                              ], className='skt_studyinfo',headerClassName='headtab1'), style={'width':'35%'}),
                                                            dbc.Col(dbc.Toast(
                                                                              [
                                                                              html.Span('Potential effect modifires Info',className='skt_span1', style={'color': '#B85042', 'font-weight': 'bold'}),
                                                                              html.Span('Mean age: 45.3',className='skt_span1'),
                                                                              html.Span('Mean male percentage: 43.4%',className='skt_span1'),
                                                                              ], className='skt_studyinfo',headerClassName='headtab1'), style={'width':'15%','margin-left': '1%'}),
                                                                                              
                                                            dbc.Col(
                                                                    [dbc.Row(html.Span('Options', className='option_select'), style={'display':'grid', 'padding-top':'unset'}),
                                                                     dbc.Col([dbc.Toast([
                                                                            html.Span('Enter the minimum clinical difference value:',className='select_outcome'),
                                                                            dcc.Input(id="range_lower",
                                                                                        type="text",
                                                                                        name='risk',
                                                                                        value=0.2,
                                                                                        placeholder="e.g. 0.2", style={'width':'80px'}),
                                                                            # html.Span('Enter the range of equvalence upper:',className='select_outcome'),
                                                                            # dcc.Input(id="range_upper",
                                                                            #             type="text",
                                                                            #             name='risk',
                                                                            #             value=1.25,
                                                                            #             placeholder="e.g. 1.25",style={'width':'80px'}) 
                                                                                                ],className='skt_studyinfo2', bodyClassName='slect_body',headerClassName='headtab1'),
                                                                            dcc.Checklist(options= options_effects, value= ['PI', 'direct', 'indirect'], 
                                                                                          id='checklist_effects', style={'display': 'grid', 'align-items': 'end'})],
                                                                                            style={'display': 'grid', 'grid-template-columns': '1fr 1fr'})
                                                                                                ],
                                                                    style={'width':'38%','margin-left': '1%', 'border': '1px dashed rgb(184, 80, 66)','display':'grid'})    
                                                                          
                                                                          ], className='row_skt'),
                                                      dbc.Row([
                                                               dbc.Col([grid, model_skt_stand1, model_skt_stand2],className='skt_col2', id = 'grid_type'),
                                                                              ],className='skt_rowtable'),
                                                      html.Br(), html.Br(),
                                                      dbc.Row()
                                                        ]),
                                                      dbc.Col([
                                                dcc.Markdown('Expert Committee Members',
                                                className="markdown_style_main",
                                                style={
                                                        "font-size": '20px',
                                                        'text-align': 'center',
                                                        'color':'orange',
                                                        'border-bottom': '2px solid',
                                                        'font-weight': 'bold',
                                                        'height': 'fit-content',
                                                        # 'margin-left': '20px',
                                                        'width': '100%',
                                                        'margin-top': '0'
                                                        }),
                                                dcc.Markdown('Isabelle Boutron, Toshi Furukawa, Emily Karahalios, Tianjing li, Michael Mccaul, Adriani Nikolakopoulou, Haliton Oliveira, Thodoris Papakonstantiou, Georgia Salanti, Guido Schwarzer, Ian Saldanha, Nicky Welton, Sally Yaacoub',
                                                                className="markdown_style", style={"color": "black", 'font-size': 'large'}),
                                                html.Br(),html.Br(),html.Br(),],style={ 'width': '95%', 'padding-left': '5%'}) 
                                                        ], style={'display':'block'}), 
                                                                              ])

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


