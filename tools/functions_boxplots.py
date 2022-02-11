import pandas as pd
import plotly.graph_objects as go

def __update_boxplot(value, edges, net_data):
    active, non_active = '#1B58E2', '#313539'  # '#4C5353'
    if value:
        net_data  = pd.read_json(net_data, orient='split')
        df = net_data[['treat1', 'treat2', value]].copy()
        df = df.dropna(subset=[value])
        df['Comparison'] = df['treat1'] + ' vs ' + df['treat2']
        df = df.sort_values(by='Comparison').reset_index()
        if isinstance(df[value], str): df[value] = pd.to_numeric(df[value], errors='coerce')
        df[value] = pd.to_numeric(df[value], errors='coerce')
        margin = (float(df[value].max()) - float(df[value].min())) * .1  # 10%
        range1 = float(df[value].min()) - margin
        range2 = float(df[value].max()) + margin
        df['color'] = non_active
        df['selected'] = 'nonactive'

        slctd_comps = []
        for edge in edges or []:
            src, trgt = edge['source'], edge['target']
            slctd_comps += [f'{src} vs {trgt}']

        for ind, row in df.iterrows():
            df.loc[ind, 'color'] = active if row.Comparison in slctd_comps else non_active
            df.loc[ind, 'selected'] = 'active' if row.Comparison in slctd_comps else 'nonactive'

        unique_comparisons = df.Comparison.sort_values().unique()
        unique_comparisons = unique_comparisons[~pd.isna(unique_comparisons)]
        fig = go.Figure(data=[go.Box(y=df[df.Comparison == comp][value],
                                     visible=True,
                                     name=comp, # jitter=0.2, # width=0.6,
                                     marker_color=active if comp in slctd_comps else non_active,
                                     )
                              for comp in unique_comparisons]
                        )

    else:
        df = pd.DataFrame([[0] * 3], columns=['Comparison', 'value', 'selected'])
        value = df['value']
        range1 = range2 = 0
        fig = go.Figure(data=[go.Box(y=df['value'])])
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80), xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, tick0=0, title=''))

    fig.update_layout(clickmode='event+select',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      font_color="black",
                      modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
                      yaxis_range=[range1, range2],
                      showlegend=False,
                      autosize=True,
                      font=dict(  # family="sans serif", #size=11,
                          color='black'
                      ),
                      xaxis=dict(showgrid=False, tick0=0),
                      yaxis=dict(showgrid=False)
                      )

    fig.update_traces(boxpoints='outliers', quartilemethod="inclusive", hoverinfo="x+y",
                      selector=dict(mode='markers'), showlegend=False, opacity=1,
                      marker=dict(opacity=1, line=dict(color='black', outlierwidth=2))
                      )

    fig.update_xaxes(ticks="outside", tickwidth=1, tickcolor='black', ticklen=5, tickmode='linear',
                     autorange=True,
                     showline=True, linecolor='black', type="category")  # tickangle=30,

    fig.update_yaxes(showgrid=False, ticklen=5, tickwidth=2, tickcolor='black', autorange=True,
                     showline=True, linecolor='black', zeroline=False)

    if not any(value):
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          xaxis=dict(showgrid=False, tick0=0, title=''),
                          modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
                          yaxis=dict(showgrid=False, tick0=0, title=''),
                          annotations=[{
                              "text": "Check whether transitivity holds in the network: compare the distributions <br>"
                                      "of your potential effect modifiers across the different comparisons <br>"
                                       "by visual inspection of the effect modifiers box plots <br> <br>"
                                      "Effect modifiers should be similarly distributed across comparisons",
                              "font": {"size": 15, "color": "white", 'family': 'sans-serif'},
                              "xref": "paper",
                              "yref": "y",
                              #"xshift": -400,
                              "xanchor": "center",
                              "showarrow": False},
                                     ]
                          ),
        fig.update_annotations(align="center")
        fig.update_traces(quartilemethod="exclusive", hoverinfo='skip', hovertemplate=None)

    return fig
