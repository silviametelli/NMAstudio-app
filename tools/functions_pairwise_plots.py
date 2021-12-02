import numpy as np, pandas as pd
import plotly.express as px, plotly.graph_objects as go

def __update_forest_pairwise(edge, outcome, forest_data_prws, forest_data_prws_out_2):
    _HEIGHT_ROMB = 0.3
    slctd_comps = []
    if edge:
        src, trgt = edge[0]['source'], edge[0]['target']
        slctd_comps += [f'{src} vs {trgt}']
        df = pd.read_json(forest_data_prws_out_2, orient='split') if outcome else pd.read_json(forest_data_prws, orient='split')
        df = df.reset_index(drop=True)
        df['Comparison'] = df['treat1'] + ' vs ' + df['treat2']
        df = df[df.Comparison.isin(slctd_comps)]
        #df['studlab'] = str(df['studlab'])
        df['studlab'] += ' ' * 10
        effect_size = df.columns[0]
        tau2 = round(df['tau2'].iloc[0], 2) if len(df['tau2'])>0 and df['tau2'].iloc[0] and ~np.isnan(df['tau2'].iloc[0]) else np.nan
        I2 = round(df['I2'].iloc[0], 2) if len(df['I2'])>0 else np.nan
        FOREST_ANNOTATION = ('<b>RE model:</b>  I<sup>2</sup>='
                             + f"{'NA' if np.isnan(I2) else I2}%, "
                             + u"\u03C4" + '<sup>2</sup>='
                             + f"{'NA' if np.isnan(tau2) else tau2}")
        LEN_FOREST_ANNOT = 25 + len(str(I2))  + len(str(tau2))
        df['CI_width'] = df.CI_upper - df.CI_lower
        df['lower_error'] = df[effect_size] - df.CI_lower
        df['CI_width_hf'] = df['CI_width'] / 2
        df['CI_width_diamond'] = df.CI_upper_diamond - df.CI_lower_diamond
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        df['CI_width_hf_diamond'] = df['CI_width_diamond'] / 2
        CI_lower, CI_upper = df["CI_lower"].map('{:,.2f}'.format), df["CI_upper"].map('{:,.2f}'.format)
        df['CI'] = '(' + CI_lower.astype(str) + ', ' + CI_upper.astype(str) + ')'
        CI_lower_diamond, CI_upper_diamond = df["CI_lower_diamond"].map('{:,.2f}'.format), df["CI_upper_diamond"].map('{:,.2f}'.format)
        CI_d = '(' + CI_lower_diamond.astype(str) + ', ' + CI_upper_diamond.astype(str) + ')'
        df = df.sort_values(by=effect_size, ascending=False)
        pred_lo  = df['Predict_lo'].reset_index().Predict_lo[0]
        pred_up  = df['Predict_up'].reset_index().Predict_up[0]
        if abs(pred_lo) > np.float64(1000) or abs(pred_up) > np.float64(1000) :
            pred_lo, pred_up = np.nan, np.nan

        center = df['TE_diamond'].reset_index().TE_diamond[0]
        width = df['CI_width_diamond'].reset_index().CI_width_diamond[0]

    else:
        FOREST_ANNOTATION = ''
        LEN_FOREST_ANNOT = 0
        center = width = 0
        effect_size = ''
        df = pd.DataFrame([[0] * 11],
                          columns=[effect_size, "TE_diamond", "id", "studlab", "treat1", "treat2", "CI_lower",
                                   "CI_upper", "CI_lower_diamond", "CI_upper_diamond", "WEIGHT"])
        df.studlab = ''

    xlog = effect_size in ('RR', 'OR')
    up_rng_, low_rng_ = df.CI_upper.max(), df.CI_lower.min()

    up_rng = 10 ** np.floor(np.log10(up_rng_)) if xlog else None
    low_rng = 10 ** np.floor(np.log10(low_rng_)) if xlog else None

    fig = px.scatter(df, x= df[effect_size], y=df["studlab"].str.pad(max(LEN_FOREST_ANNOT, df["studlab"].str.len().max()), fillchar=' '),
                       error_x_minus='lower_error' if xlog else None,
                       error_x='CI_width_hf' if xlog else 'CI_width' if edge else None,
                       log_x=xlog,
                       size_max=10,
                       range_x=[min(low_rng, 0.1), max([up_rng, 10])] if xlog else [up_rng_, low_rng_],
                       range_y=[-1,len(df.studlab)+2],
                       size=df.WEIGHT if edge else None)

    if xlog:
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                      line=dict(color="black", width=1), layer='below')

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                          plot_bgcolor='rgba(0,0,0,0)',
                          showlegend=False,
                          xaxis_type="log" if xlog else 'linear',
                          modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0)'),
                          xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, title=''),
                          )

    fig.update_yaxes(ticks="outside",
                         type='category',
                         showgrid=False,
                         tickcolor='rgba(0,0,0,0)',
                         linecolor='rgba(0,0,0,0)',
                         linewidth=1,
                         zeroline=True, zerolinecolor='black', zerolinewidth=1),

    fig.update_xaxes(ticks="outside",
                         showgrid=False,
                         autorange=True, showline=True,
                         tickcolor='rgba(0,0,0,0)',
                         linecolor='rgba(0,0,0,0)'),

    fig.update_traces(marker=dict(symbol='square',
                                          opacity=0.8 if edge else 0,
                                          line=dict(color='DarkSlateGrey'),
                                          color='grey'),
                              error_x=dict(thickness=2, color='#313539'))  # '#ef563b' nice orange trace
        #
    if edge:
        fig.update_layout(clickmode='event+select',
                              font_color="black",
                              modebar=dict(orientation='v', bgcolor='rgba(0,0,0,0)'),
                              autosize=True,
                              # width=500,
                              margin=dict(l=5, r=10, t=12, b=80),
                              xaxis=dict(showgrid=False, autorange=True,
                                        showline=True, linewidth=1, linecolor='black',
                                         zeroline=True, zerolinecolor='black', zerolinewidth=1,
                                         title=''),
                              yaxis=dict(showgrid=False, title=''),
                              annotations=[dict(x=0 if xlog else 1, y=-0.12,
                                                xref='x',  yref='paper',
                                                showarrow=False, text=effect_size),
                                           dict(x=np.floor(np.log10(min(low_rng, 0.1))) if xlog else low_rng_,
                                                ax=0, y=-0.14, ay=-0.1,
                                                xref='x', axref='x', yref='paper',
                                                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                                arrowcolor='black'),
                                           dict(x=np.floor(np.log10(max([up_rng, 10]))) if xlog else up_rng_,
                                                ax=0, y=-0.14, ay=-0.1,
                                                xref='x', axref='x', yref='paper',
                                                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                                arrowcolor='black'),  # '#751225'
                                           dict(x=np.floor(
                                               np.log10(min(low_rng, 0.1))) / 2 if xlog else df.CI_lower.min() / 2,
                                                y=-0.22, xref='x', yref='paper', xanchor='auto',
                                                text=f'Favours {df.treat1.iloc[0]}',
                                                showarrow=False),
                                           dict(x=np.floor(
                                               np.log10(max([up_rng, 10]))) / 2 if xlog else df.CI_upper.max() / 2,
                                                y=-0.22,
                                                xref='x', yref='paper', xanchor='auto',
                                                text=f'Favours {df.treat2.iloc[0]}',
                                                showarrow=False),
                                           dict(x=0, y=1, xanchor='left',
                                                xref='paper', yref='paper',
                                                text='<b>Study</b>',
                                                showarrow=False),
                                           dict(x=0, y=0, xanchor='right',
                                                xref='paper', yref='paper',
                                                text=FOREST_ANNOTATION,
                                                showarrow=False),
                                           ]
                              )
        fig.add_vline(x=center, line_width=1, line_dash='dash', line_color='black')

        def romb(center, low=None, up=None, width=None, height=_HEIGHT_ROMB):
            if width:
                low, up =  center - width/2, center + width/2
            return {'x': [center, low, center, up, center],
                    'y': [-height/2, 0, height/2, 0, -height/2]}
        fig.add_trace(go.Scatter(x=romb(center, low=CI_lower_diamond.iloc[0], up=CI_upper_diamond.iloc[0])['x'],
                                 y=romb(center, low=CI_lower_diamond.iloc[0],up=CI_upper_diamond.iloc[0])['y'],
                                 fill="toself", mode="lines", line=dict(color='black'),
                                 fillcolor='#1f77b4', yaxis="y2", showlegend=False))

        fig.add_trace(
            go.Scatter(x=[pred_lo, pred_up],
                       y=[-_HEIGHT_ROMB*2] * 2, #["Prediction Interval"],
                       mode="lines",
                       line=dict( color='#8B0000', width=4), showlegend=False, yaxis="y3",
                     ))

        fig.update_yaxes(range=[-.3, 1 + df.studlab.shape[0]],
                         autorange=True,ticks="outside", tickwidth=2, tickcolor='black',
                         ticklen=5,
                         tickfont=dict(color='rgba(0,0,0,0)'),
                         linecolor='rgba(0,0,0,0)',
                         secondary_y=True,
                         zeroline=False)

        fig.add_trace(go.Scatter(x=[], y=[],
                                 marker=dict(opacity=0),
                                 showlegend=False, mode='markers',
                                 yaxis="y4"))

        fig.update_traces(overwrite=False)

        fig.update_layout(
            autosize=True,
            yaxis2=dict(tickvals=[], ticktext=[],
                        showgrid=False, zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        range=[-1, len(df.studlab)+1],
                        anchor="free", overlaying="y"
                        ),
            yaxis3=dict(tickvals=[], ticktext=[],
                        showgrid=False, zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        range=[-1, len(df.studlab) + 1],
                        scaleanchor = 'y',
                        anchor="x",  overlaying="y2"
                        ),
            yaxis4=dict(tickvals=[*range(df.shape[0])],
                        ticktext=[' ' * 5 + '{:.2f}   {:<17}'.format(x, y)
                                  # for x, y in zip(df[effect_size].values, df['CI'].values)],
                                  for x, y in zip(np.append(df[effect_size].values, center),
                                                  np.append(df['CI'].values, CI_d.iloc[0]))],
                        showgrid=False, zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        type='category',
                        range=[-2.4, df.shape[0]+1],
                        anchor="x", overlaying="y",
                        side="right"),
        ),

        fig.update_layout(yaxis_range=[-2.4, len(df.studlab)+1])

        fig.add_annotation(x=1.15, y=1, xanchor='center',  align='center',
                           xref='paper', yref='y domain',
                           text=f'<b>{effect_size}</b>',
                           showarrow=False)

        fig.add_annotation(x=1.4, y=1, align='center', ayref= 'y3 domain',
                           xref='paper', yref='y3 domain',
                           xanchor='center',
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
    if not edge:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          modebar=dict(orientation='v', bgcolor='rgba(0,0,0,0)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig
