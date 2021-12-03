import pandas as pd
import plotly.express as px


def __Tap_funnelplot(node, outcome2, funnel_data, funnel_data_out2):
    EMPTY_DF = pd.DataFrame([[0] * 9],
                            columns=[ 'index', 'studlab', 'treat1', 'treat2', '',
                                     'TE_direct', 'TE_adj', 'seTE', 'Comparison'])
    if node:
        treatment = node[0]['label']
        funnel_data = pd.read_json(funnel_data, orient='split')
        funnel_data_out2 = pd.read_json(funnel_data_out2, orient='split') if outcome2 else None #TODO: change when include dataselectors for var names
        df = (funnel_data_out2[funnel_data_out2.treat2 == treatment].copy() if outcome2 else funnel_data[funnel_data.treat2 == treatment].copy())
        df['Comparison'] = (df['treat1'] + ' vs ' + df['treat2']).astype(str)
        effect_size = df.columns[3]
        df = df.sort_values(by='seTE', ascending=False)
    else:
        effect_size = ''
        df = EMPTY_DF

    max_y = df.seTE.max()+0.2

    fig = px.scatter(df if df is not None else EMPTY_DF,
                     x="TE_adj", y="seTE",#log_x=xlog,
                     range_x=[min(df.TE_adj)-3, max(df.TE_adj)+3],
                     range_y=[0.01, max_y+10],
                     symbol="Comparison", color="Comparison",
                     color_discrete_sequence = px.colors.qualitative.Light24)

    fig.update_traces(marker=dict(size=6, # #symbol='circle',
                      line=dict(width=1, color='black')),
                       )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)')

    if node:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          coloraxis_showscale=False,
                          showlegend=True,
                          modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0)'),
                          autosize=True,
                          margin=dict(l=10, r=5, t=20, b=60),
                          xaxis=dict(showgrid=False, autorange=False, zeroline=False,
                                     title='',showline=True, linewidth=1, linecolor='black'),
                          yaxis=dict(showgrid=False, autorange=False, title='Standard Error',
                                     showline=True, linewidth=1, linecolor='black',
                                     zeroline=False,
                                     ),
                          annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=False,
                                        text= 'Log' f'{effect_size} ' ' centered at comparison-specific pooled effect' if effect_size in ['OR','RR'] else f'{effect_size}' ' centered at comparison-specific pooled effect'
                                            )],

                          )
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=0, x1=0,
                      line=dict(color="black", width=1), layer='below')

        fig.add_shape(type='line', y0=max_y, x0= -1.96 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dashdot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= 1.96 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dashdot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= -2.58 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= 2.58 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dot', width=1.5))

        fig.update_yaxes(autorange="reversed", range=[max_y,0])


    if not node:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zeroline=False, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          coloraxis_showscale=False,
                          showlegend=False,
                          modebar = dict(orientation='h', bgcolor='rgba(0,0,0,0)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig
