import numpy as np, pandas as pd
import plotly.express as px, plotly.graph_objects as go


def __TapNodeData_fig(data, outcome_idx, forest_data,style,net_storage):


    if data:
        treatment = data[0]['label']
        if outcome_idx:
             i = int(outcome_idx)
            #  forest_data = forest_data[i]
             forest_data = pd.read_json(forest_data[i], orient='split')
        else:          
            i = 0
            forest_data = pd.read_json(forest_data[i], orient='split')
                
        df = forest_data[forest_data.Reference == treatment]
        net_data = pd.read_json(net_storage[0], orient='split')
        outcome_direction_data = net_data[f'outcome{i+1}_direction'].iloc[1]
        outcome_direction = False if outcome_direction_data == 'beneficial' else True
        effect_size = df.columns[1]
        tau2 = round(df['tau2'].iloc[1], 2)
        df['Treatment'] += ' ' * 23
        df['CI_width'] = (df.CI_upper - df.CI_lower)/2
        df['lower_error'] = df[effect_size] - df.CI_lower
        df['CI_width_hf'] = df.CI_upper - df[effect_size] 
        # df['CI_width_hf'] = df['CI_width'] / 2
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        CI_lower, CI_upper = df["CI_lower"].map('{:,.2f}'.format), df["CI_upper"].map('{:,.2f}'.format),
        df['CI'] = '(' + CI_lower.astype(str) + ', ' + CI_upper.astype(str) + ')'
        df = df.sort_values(by=effect_size, ascending=False)
        n = len(df)
        FOREST_ANNOTATION = ('<b>RE model:</b>'
                             + u"\u03C4" + '<sup>2</sup>='
                             + f"{'NA' if np.isnan(tau2) else tau2}")
        LEN_FOREST_ANNOT = 25 + len(str(tau2))
        style.update({'height': 200+16*(n-2)})
    else:
        effect_size = ''
        outcome_direction = False
        df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf'])
        FOREST_ANNOTATION = ''
        LEN_FOREST_ANNOT = 0
        style.update({'height': '100%'})


    xlog = effect_size in ('RR', 'OR')
    up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
    up_rng = 10**np.floor(np.log10(up_rng)) if xlog else None
    low_rng = 10 ** np.floor(np.log10(low_rng)) if xlog else None
    fig = px.scatter(df, x=effect_size, y="Treatment",
                     error_x_minus='lower_error' if xlog else None,
                     error_x='CI_width_hf' if xlog else 'CI_width' if data else None,
                     log_x=xlog,
                     size_max=5,
                     range_x=[min(low_rng, 0.1), max([up_rng, 10])] if xlog else None,
                     range_y=[-1, len(df.Treatment)],
                     size=df.WEIGHT if data else None)

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)')
    if xlog:
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                      line=dict(color="black", width=1), layer='below')

    fig.update_traces(marker=dict(symbol='circle',
                                  opacity=0.8 if data else 0,
                                  line=dict(color='DarkSlateGrey'),
                                  color='green'),
                      error_x=dict(thickness=2.1, color='#313539')  # '#ef563b' nice orange trace
                      )
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black',
                     ticklen=5,
                     categoryorder='category descending' if outcome_direction else 'category ascending',
                     # dtick=1,
                     autorange=False,
                     showline=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinecolor='black')

    if data:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          modebar= dict(orientation = 'v', bgcolor = 'rgba(0,0,0,0.5)'),
                          autosize=True,
                          #width=500,
                          margin=dict(l=5, r=10, t=12, b=80),
                          xaxis=dict(showgrid=False, autorange=True,
                                     #tick0=0, # TODO: JUST EXPLAIN IT!!!
                                     title=''),
                          yaxis=dict(showgrid=False, title=''),
                          annotations=[dict(x=0, ax=0, y=0, ay=-0.1, xref='x', axref='x', yref='paper',yanchor='bottom',yshift=-40,
                                             showarrow=False, text=effect_size),
                                       dict(x=np.floor(np.log10(min(low_rng, 0.1))) if xlog else df.CI_lower.min(),
                                            ax=0, y=0, ay=-0.1,
                                            xref='x', axref='x', yref='paper',yanchor='bottom',yshift=-45,
                                            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                            arrowcolor='green' if outcome_direction else 'black'),
                                       dict(x= np.floor(np.log10(max([up_rng, 10]))) if xlog else abs(df.CI_upper).max(),
                                            ax=0, y=0, ay=-0.1,
                                            xref='x', axref='x', yref='paper',yanchor='bottom',yshift=-45,
                                            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                            arrowcolor='black' if outcome_direction else 'green'),  #'#751225'
                                       dict(x=np.floor(np.log10(min(low_rng, 0.1)))/2 if xlog else df.CI_lower.min()/2,
                                            y=0,  xref='x', yref='paper',yanchor='bottom',yshift=-65,
                                            text='Favours treatment' if outcome_direction else f'Favours {treatment}',
                                            showarrow=False),
                                       dict(x=np.floor(np.log10(max([up_rng, 10])))/2 if xlog else abs(df.CI_upper).max()/2,
                                            y=0,
                                            xref='x', yref='paper',yanchor='bottom',yshift=-65,
                                            text=f'Favours {treatment}'if outcome_direction else 'Favours treatment',
                                            showarrow=False),
                                       dict(x=-0.47, y=1, align='center',
                                            xref='paper', yref='paper',
                                            text='<b>Treatment</b>',
                                            showarrow=False),
                                       dict(x=-0.52, y=0, align='center',
                                            xref='paper', yref='paper',
                                            text=FOREST_ANNOTATION, #'<b>RE model:</b> ' u"\u03C4" '<sup>2</sup>=' f'{tau2}',
                                            showarrow=False),
                                 ]
                          )


        fig.add_trace(go.Scatter(x=[], y=[],
                                 marker=dict(opacity=0),
                                 showlegend=False, mode='markers',
                                 yaxis="y2"))

        fig.update_layout(
            autosize=True,
            yaxis2=dict(tickvals = [*range(df.shape[0])],
                        ticktext=[' '*8 + '{:.2f}   {:<17}'.format(x,y)
                                  for x, y in zip(df[effect_size].values, df['CI'].values)],
                        showgrid=False,  zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        type='category',
                        range=[-1.4, df.shape[0]+1],
                        anchor="x", overlaying="y",
                        side="right"),
        ),

        fig.update_layout(yaxis_range=[-1.4, len(df["Treatment"])+1])

        fig.add_annotation(x=1.19, y=1, align='center',
             xref='paper', yref='y domain',
             text=f'<b>{effect_size}</b>',
             showarrow=False)


        fig.add_annotation(x=1.44, y=1, align='center',
                           xref='paper', yref='y2 domain',
                           text='<b>95% CI</b>',
                           showarrow=False)

    else:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          margin=dict(l=5, r=10, t=12, b=80),
                          xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, title=''),
                          title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                          annotations=[]
                          )

    if not data:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          modebar= dict(orientation = 'v', bgcolor = 'rgba(0,0,0,0.5)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig, style





###### BIDIMENSIONAL PLOT

def __TapNodeData_fig_bidim(data, forest_data_store,out_idx1, out_idx2):
    """If click on node uses node as reference to produce both forest plots."""
    ##  ranking data used to check if second outcome is present (easier to check than using dataselectors)
    # df_ranking = pd.read_json(ranking_data, orient='split')
    # df_ranking = df_ranking.loc[:, ~df_ranking.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    if not out_idx1:
         out_idx1 =0
    if not out_idx2:
         out_idx2 = 0


    if data:
        # if "pscore2" in df_ranking.columns:

        forest_data  = pd.read_json(forest_data_store[out_idx1], orient='split')
        forest_data_out2 = pd.read_json(forest_data_store[out_idx2], orient='split')
        treatment = data[0]['label']
        df = forest_data[forest_data.Reference == treatment]
        
        effect_size = df.columns[1]
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['lower_error_1'] = df[effect_size] - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] / 2
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        df = df.sort_values(by=effect_size, ascending=False)
        #second outcome
        df_second = forest_data_out2[forest_data_out2.Reference == treatment]
        
        effect_size_2 = df_second.columns[1]
        df_second['CI_width'] = df_second.CI_upper - df_second.CI_lower
        df_second['lower_error_2'] = df_second[effect_size] - df_second.CI_lower
        df_second['CI_width_hf'] = df_second['CI_width'] / 2
        # else:
        #     effect_size = effect_size_2 = ''
        #     df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
        #                                           'CI_width', 'CI_width_hf'])
        #     df_second = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
        #                                                  'CI_width', 'CI_width_hf'])
    else:
            effect_size = effect_size_2 = ''
            df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                                  'CI_width', 'CI_width_hf'])
            df_second = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                                         'CI_width', 'CI_width_hf'])

    xlog = effect_size in ('RR', 'OR')
    up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
    up_rng = 10**np.floor(np.log10(up_rng)) if xlog else None
    low_rng = 10 ** np.floor(np.log10(low_rng)) if xlog else None
    if len(df_second.Treatment) > len(df.Treatment):
        trts_rmd = set(df_second.Treatment).difference(df.Treatment)
        df_second[df_second['Treatment'].isin(trts_rmd) == False]
    else:
        trts_rmd = set(df.Treatment).difference(df_second.Treatment)
        df[df['Treatment'].isin(trts_rmd) == False]
    df['size'] = df.Treatment.astype("category").cat.codes
    fig = px.scatter(df, x=df[effect_size], y=df_second[effect_size_2],
                 color=df.Treatment,
                 error_x_minus=df['lower_error_1'] if xlog else None,
                 error_x='CI_width_hf' if xlog else 'CI_width' if data else None,
                 error_y_minus=df_second['lower_error_2'] if xlog else None,
                 error_y=df_second.CI_width_hf if data else df_second.CI_width if xlog else None,
                 log_x=xlog,
                 log_y=xlog,
                 size_max = 10,
                 color_discrete_sequence = px.colors.qualitative.Light24,
                 range_x = [min(low_rng, 0.1), max([up_rng, 10])] if xlog else None
                 )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  autosize=True,
                  modebar=dict(orientation='v', bgcolor='rgba(0,0,0,0.5)'),
                  legend=dict(itemsizing='trace', itemclick="toggle",
                              itemdoubleclick="toggleothers", # orientation='v', xanchor='auto',
                              traceorder='normal',
                              orientation='h', y=1.25, xanchor='auto',
                              font=dict(size=10)) if df['Treatment'].unique().size > 10 else
                                        dict(itemsizing='trace', itemclick="toggle", itemdoubleclick="toggleothers", orientation='v',
                      font=dict(size=10))
                  )
    if xlog:
            fig.add_hline(y=1,line=dict(color="black", width=1, dash='dashdot'))
            fig.add_vline(x=1,line=dict(color="black", width=1, dash='dashdot'))
    fig.update_traces(marker=dict(symbol='circle',
                              size=9,
                              opacity=1 if data else 0,
                              line=dict(color='black'),
                              ),
                  error_y=dict(thickness=1.3),
                  error_x=dict(thickness=1.3), ),
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5, dtick=1,
                 autorange=True, showline=True, linewidth=1, linecolor='black',
                 zeroline=True, zerolinecolor='gray', zerolinewidth=1),
    fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5, dtick=1,
                 autorange=True, showline=True, linewidth=1, linecolor='black',
                 zeroline=True, zerolinecolor='gray', zerolinewidth=1),
    fig.update_layout(clickmode='event+select',
                  font_color="black",
                  margin=dict(l=10, r=10, t=12, b=80),
                  xaxis=dict(showgrid=False, tick0=0, title=f'Click to enter x label ({effect_size})'),
                  yaxis=dict(showgrid=False, title=f'Click to enter y label ({effect_size_2})'),
                  title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                  )
    if not data:
            fig.update_shapes(dict(xref='x', yref='y'))
            fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
            fig.update_yaxes(tickvals=[], ticktext=[], title='', visible=False)
            fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                             coloraxis_showscale=False)  ## remove visible=False to show initial axes
            fig.update_traces(hoverinfo='skip', hovertemplate=None)
    # if data and  "pscore2" not in df_ranking.columns:
    #         fig = px.scatter(df, x=df[effect_size], y=df_second[effect_size_2])
    #         fig.update_shapes(dict(xref='x', yref='y'))
    #         fig.update_xaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
    #         fig.update_yaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
    #         fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
    #                            xaxis=dict(showgrid=False, title=''),
    #                            modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0.5)'),
    #                            yaxis=dict(showgrid=False, title=''),
    #                            showlegend=False,
    #                            coloraxis_showscale=False,
    #                            paper_bgcolor='rgba(0,0,0,0)',
    #                            plot_bgcolor='rgba(0,0,0,0)',
    #                            autosize=True,
    #                            annotations=[
    #                                {"text": "Please provide a second outcome in data upload to display bi-dimensional plot",
    #                                 "font": {"size": 15, "color": "black", 'family': 'sans-serif'},
    #                                 "xref": "paper", "yref": "paper",
    #                                 "showarrow": False},
    #                                ]
    #                            ),
    #         fig.update_annotations(align="center")
    #         fig.update_traces(hoverinfo='skip', hovertemplate=None)
    return fig
