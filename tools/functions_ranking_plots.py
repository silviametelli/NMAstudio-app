import numpy as np, pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from sklearn.cluster import KMeans
from collections import Counter
from functools import lru_cache


@lru_cache(maxsize=None)
def __ranking_plot(outcome_direction_1, outcome_direction_2,
                   outcome_direction_11, outcome_direction_22,
                   net_data, ranking_data):
    df = pd.read_json(ranking_data, orient='split')

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    outcomes = ("Outcome 1", "Outcome 2")

    # True=harmful
    df1 = df.copy(deep=True)

    if "pscore2" in df1.columns:

        if outcome_direction_1: df1.pscore1 = 1 - df1.pscore1.values
        if outcome_direction_2: df1.pscore2 = 1 - df1.pscore2.values
        df1 = df1.sort_values(by=["pscore1", "pscore2"], ascending=[False, False])
        z_text = (tuple(df1.pscore1.round(2).astype(str).values),
                  tuple(df1.pscore2.round(2).astype(str).values))
        pscores = (tuple(df1.pscore1), tuple(df1.pscore2))
        treatments = tuple(df1.treatment)
    else:
        outcomes = ("Outcome",)
        pscore = 1 - df1.pscore if outcome_direction_1 else df1.pscore
        pscore = pscore.sort_values(ascending=False)
        elements = pd.DataFrame({"pscore":pscore,"treat":df1.treatment})
        sorted_elements = elements.sort_values(by="pscore", ascending=False)
        strd_pscore = sorted_elements['pscore']
        strd_trt = sorted_elements['treat']
        z_text = (tuple(strd_pscore.round(2).astype(str).values),)
        pscores = (tuple(strd_pscore),)
        treatments = tuple(strd_trt)


    #################### heatmap ####################
    fig = __ranking_heatmap(treatments, pscores, outcomes, z_text)

    ######################### scatter plot #########################
    fig2 = __ranking_scatter(df, net_data, outcome_direction_11, outcome_direction_22)

    return fig, fig2

@lru_cache(maxsize=None)
def __ranking_heatmap(treatments, pscores, outcomes, z_text):
    if len(pscores)+len(outcomes)+len(z_text)==3: pscores, outcomes, z_text = list(pscores), list(outcomes), list(z_text)

    fig = ff.create_annotated_heatmap(pscores, x=treatments, y=outcomes,
                                      reversescale=True,
                                      annotation_text=z_text, colorscale= 'Viridis',
                                      hoverongaps=False)
    for annotation in fig.layout.annotations: annotation.font.size = 9
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)',
                      modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0)'),
                      xaxis=dict(showgrid=False, autorange=True, title='',
                                 tickmode='linear', type="category"),
                      yaxis=dict(showgrid=False, autorange=True, title='', range=[0,len(outcomes)]),
                      )

    fig['layout']['xaxis']['side'] = 'bottom'
    fig['data'][0]['showscale'] = True
    fig['layout']['yaxis']['autorange'] = "reversed"
    #fig['layout']['xaxis']['autorange'] = "reversed"
    fig.layout.margin = dict(l=0, r=0, t=70, b=180)

    return fig



def __ranking_scatter(df, net_data, outcome_direction_11, outcome_direction_22):
    net_data = pd.read_json(net_data, orient='split')

    if 'pscore2' in df.columns:
        if not outcome_direction_11: df.pscore1 = 1 - df.pscore1
        if not outcome_direction_22: df.pscore2 = 1 - df.pscore2

        kmeans = KMeans(n_clusters=int(round(len(df.treatment) / float(5.0), 0)),
                        init='k-means++', max_iter=300, n_init=10, random_state=0)
        labels = kmeans.fit(df[['pscore1', 'pscore2']])
        df['Trt groups'] = labels.labels_.astype(str)
        df_full = net_data.groupby(['treat1', 'treat2']).TE.count().reset_index()
        df_full_2 = net_data.groupby(['treat1', 'treat2']).TE2.count().reset_index()
        node_weight, node_weight_2 = {}, {}
        for treat in df.treatment:
            n1 = df_full[df_full.treat1 == treat].TE.sum()
            n2 = df_full[df_full.treat2 == treat].TE.sum()
            node_weight[treat] = (n1 + n2) / float(np.shape(df)[0])

            n1 = df_full_2[df_full_2.treat1 == treat].TE2.sum()
            n2 = df_full_2[df_full_2.treat2 == treat].TE2.sum()
            node_weight_2[treat] = (n1 + n2) / float(np.shape(df)[0])

        sum_weight = dict((Counter(node_weight) + Counter(node_weight_2)))
        mean_weight = {k: v / 2.0 for k, v in
                       sum_weight.items()}  # Node size prop to mean count of node size in outcome 1 and outcome 2
        df["node weight"] = df["treatment"].map(mean_weight)

        fig2 = px.scatter(df, x="pscore1", y="pscore2",
                          color="Trt groups", size='node weight',
                          hover_data=["treatment"],
                          text='treatment')

        fig2.update_layout(coloraxis_showscale=True,
                           showlegend=False,
                           paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                           plot_bgcolor='rgba(0,0,0,0)',
                           modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
                           xaxis=dict(showgrid=False, autorange=True, dtick=0.1,
                                      tickcolor='black', ticks="outside", tickwidth=1,
                                      showline=True, linewidth=1, linecolor='black',
                                      zeroline=False, zerolinecolor='black', zerolinewidth=1,
                                      range=[0, 1]),
                           yaxis=dict(showgrid=False, autorange=True, dtick=0.1,
                                      showline=True, linewidth=1, linecolor='black',
                                      tickcolor='black', ticks="outside", tickwidth=1,
                                      zeroline=False, zerolinecolor='black', zerolinewidth=1,
                                      range=[0, 1]
                                      ))
        fig2.update_traces(textposition='top center', textfont_size=10,
                           marker=dict(line=dict(width=1, color='black'))
                           )
        fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        fig2.layout.margin = dict(l=30, r=30, t=10, b=80)

    else:  # Empty scatter
        df = pd.DataFrame([[0] * 2], columns=['pscore1', 'pscore2'])
        fig2 = px.scatter(df, x="pscore1", y="pscore2")
        fig2.update_shapes(dict(xref='x', yref='y'))
        fig2.update_xaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
        fig2.update_yaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
        fig2.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          xaxis=dict(showgrid=False, title=''),
                          modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
                          yaxis=dict(showgrid=False, title=''),
                          showlegend=False,
                          coloraxis_showscale=False,
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          autosize=True,
                          annotations=[{"text": "Please provide a second outcome from data upload to display p-scores scatter plot",
                                         "font": {"size": 15, "color": "white", 'family': 'sans-serif'},
                                         "xref":"paper", "yref":"paper",
                                         "showarrow":False},
                                       ]
                           ),
        fig2.update_annotations(align="center")
    return fig2