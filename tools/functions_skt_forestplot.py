import pandas as pd
import plotly.express as px, plotly.graph_objects as go
import numpy as np

def update_indirect_direct(row):
    if pd.isna(row['direct']):
        row['indirect'] = pd.NA
    elif pd.isna(row['indirect']):
        row['direct'] = pd.NA
    return row


def __skt_all_forstplot(df, lower, upper):
    
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
        new_rows.loc[idx/19, 'Reference'] = df.loc[idx, 'Reference']

    new_rows['Treatment'] = 'Scale'
    new_rows['risk'] = 'Enter a number'
    new_rows['Scale_lower'] = 'Enter a number for lower'
    new_rows['Scale_upper'] = 'Enter a number for upper'
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat([df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):

        data_ex = df[j+1:j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))
     
        range_scale=[min(low_rng_min, -1, low_mix_min), 
                              max(up_rng_max, 2.25, up_mix_max+1)]  
        
        fig = go.Figure(go.Scatter( y = [],x = []))
        fig.update_layout(
        xaxis=dict(range=range_scale,
                    tickvals=[i for i in range(int(min(low_rng_min, -1, low_mix_min)+1),
                                        int(max(up_rng_max, 2.25, up_mix_max+1)-1))],
                        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        margin=dict(l=0, r=0)
        )
        fig.update_xaxes(ticks="outside",
                        showgrid=False,
                        autorange=True, showline=True,
                        # tickcolor='rgba(0,0,0,0)',
                        linecolor='black'
                        )

        df.at[j, "Graph"] = fig
        
        for i in range(j+1, j + 20):
                filterDf = df.iloc[i]
                filter_df = pd.DataFrame([filterDf])
                filter_df = filter_df.apply(update_indirect_direct, axis=1)
    
                # data_ex = df[j+1, j + 20]     
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

                hovert_template=['indirect estimate with CI'+'<extra></extra>',
                        'direct estimate with CI'+'<extra></extra>',
                        'mixed estimate with CI & PI'+'<extra></extra>',
                        'mixed estimate with CI & PI'+'<extra></extra>'
                        ]

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
                                    showlegend=False,
                                    hovertemplate= hovert_template[idx] 
                                ))
                
                fig.update_layout(
                    barmode='group',
                    bargap=0.25,
                    xaxis=dict(range=range_scale),
                    # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
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
                            x0=f"{lower}",
                            y0="0",
                            x1=f"{upper}",
                            y1='1',
                            fillcolor="orange",
                            opacity=0.4,
                            line_width=0,
                            layer="below"
                        ),]
                    # template="plotly_dark",
                )
            
                fig.add_trace(go.Scatter(
                    x=[0.8, 1.25],  # x-coordinate in the middle of the shape
                    y=[0, 0],    # y-coordinate (doesn't matter, since it's vertical shape)
                    mode='markers',
                    marker=dict(color='rgba(0, 0, 0, 0)', size=5),
                    hovertemplate = '<b>Range of equivalence</b>: %{x} <extra></extra>',
                    hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)")
                ))
                    
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                                plot_bgcolor='rgba(0,0,0,0)')

                fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                                line=dict(color="green", width=2,dash="dot"), layer='below')
            
                df.at[i, "Graph"] = fig
                
    return df

def __skt_PI_forstplot(df, lower, upper):
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
        new_rows.loc[idx/19, 'Reference'] = df.loc[idx, 'Reference']

    new_rows['Treatment'] = 'Scale'
    new_rows['risk'] = 'Enter a number'
    new_rows['Scale_lower'] = 'Enter a number for lower'
    new_rows['Scale_upper'] = 'Enter a number for upper'
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat([df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):

        data_ex = df[j+1:j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))
     
        range_scale=[min(low_rng_min, -1, low_mix_min), 
                              max(up_rng_max, 2.25, up_mix_max+1)]  
        
        fig = go.Figure(go.Scatter( y = [],x = []))
        fig.update_layout(
        xaxis=dict(range=range_scale,
                    tickvals=[i for i in range(int(min(low_rng_min, -1, low_mix_min)+1),
                                        int(max(up_rng_max, 2.25, up_mix_max+1)-1))],
                        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        margin=dict(l=0, r=0)
        )
        fig.update_xaxes(ticks="outside",
                        showgrid=False,
                        autorange=True, showline=True,
                        # tickcolor='rgba(0,0,0,0)',
                        linecolor='black'
                        )

        df.at[j, "Graph"] = fig

        for i in range(j+1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)

            filter_df = pd.concat([filter_df] * 2, ignore_index=True)


            filter_df['CI_width_hf'][1] = (filter_df.CI_upper[1] - filter_df['RR'][0]*1.2)
            filter_df['lower_error'][1] = (filter_df['RR'][1] - filter_df.CI_lower[0]*1.2)


            # up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
            # up_rng = 10**np.floor(np.log10(up_rng))

            colors = ['red','black']

            hovert_template=[
                    'mixed estimate with CI & PI'+'<extra></extra>',
                    'mixed estimate with CI & PI'+'<extra></extra>'
                    ]

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
                                showlegend=False,
                                hovertemplate= hovert_template[idx] 
                            ))
            
            fig.update_layout(
                barmode='group',
                bargap=0.25,
                xaxis=dict(range=range_scale),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
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
                        x0=f"{lower}",
                        y0="0",
                        x1=f"{upper}",
                        y1='1',
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below"
                    ),]
                # template="plotly_dark",
            )
        
            fig.add_trace(go.Scatter(
                x=[0.8, 1.25],  # x-coordinate in the middle of the shape
                y=[0, 0],    # y-coordinate (doesn't matter, since it's vertical shape)
                mode='markers',
                marker=dict(color='rgba(0, 0, 0, 0)', size=5),
                hovertemplate = '<b>Range of equivalence</b>: %{x} <extra></extra>',
                hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)")
            ))
                
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=2,dash="dot"), layer='below')            

            df.at[i, "Graph"] = fig

    return df


def __skt_direct_forstplot(df, lower, upper):
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
         new_rows.loc[idx/19, 'Reference'] = df.loc[idx, 'Reference']

    new_rows['Treatment'] = 'Scale'
    new_rows['risk'] = 'Enter a number'
    new_rows['Scale_lower'] = 'Enter a number for lower'
    new_rows['Scale_upper'] = 'Enter a number for upper'
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat([df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):

        data_ex = df[j+1:j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))
     
        range_scale=[min(low_rng_min, -1, low_mix_min), 
                              max(up_rng_max, 2.25, up_mix_max+1)]  
        
        fig = go.Figure(go.Scatter( y = [],x = []))
        fig.update_layout(
        xaxis=dict(range=range_scale,
                    tickvals=[i for i in range(int(min(low_rng_min, -1, low_mix_min)+1),
                                        int(max(up_rng_max, 2.25, up_mix_max+1)-1))],
                        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        margin=dict(l=0, r=0)
        )
        fig.update_xaxes(ticks="outside",
                        showgrid=False,
                        autorange=True, showline=True,
                        # tickcolor='rgba(0,0,0,0)',
                        linecolor='black'
                        )

        df.at[j, "Graph"] = fig

        for i in range(j+1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)

            filter_df = pd.concat([filter_df] * 2, ignore_index=True)


            filter_df['Treatment'][0] = 'Direct'
            filter_df['RR'][0] = filter_df['direct'][0]
            filter_df['CI_width_hf'][0] = (filter_df.direct_up[0] - filter_df['direct'][0])
            filter_df['lower_error'][0] = (filter_df['direct'][0] - filter_df.direct_low[0])

            colors = ['#707B7C', 'black']

            hovert_template=[
                    'direct estimate with CI'+'<extra></extra>',
                    'mixed estimate with CI'+'<extra></extra>'
                    ]

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
                                showlegend=False,
                                hovertemplate= hovert_template[idx] 
                            ))
            
            fig.update_layout(
                barmode='group',
                bargap=0.25,
                xaxis=dict(range=range_scale),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
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
                        x0=f"{lower}",
                        y0="0",
                        x1=f"{upper}",
                        y1='1',
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below"
                    ),]
                # template="plotly_dark",
            )
        
            fig.add_trace(go.Scatter(
                x=[0.8, 1.25],  # x-coordinate in the middle of the shape
                y=[0, 0],    # y-coordinate (doesn't matter, since it's vertical shape)
                mode='markers',
                marker=dict(color='rgba(0, 0, 0, 0)', size=5),
                hovertemplate = '<b>Range of equivalence</b>: %{x} <extra></extra>',
                hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)")
            ))
                
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=2,dash="dot"), layer='below')
        
                

            df.at[i, "Graph"] = fig
    
    return df


def __skt_indirect_forstplot(df, lower, upper):
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
         new_rows.loc[idx/19, 'Reference'] = df.loc[idx, 'Reference']

    new_rows['Treatment'] = 'Scale'
    new_rows['risk'] = 'Enter a number'
    new_rows['Scale_lower'] = 'Enter a number for lower'
    new_rows['Scale_upper'] = 'Enter a number for upper'
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat([df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):

        data_ex = df[j+1:j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))
     
        range_scale=[min(low_rng_min, -1, low_mix_min), 
                              max(up_rng_max, 2.25, up_mix_max+1)]  
        
        fig = go.Figure(go.Scatter( y = [],x = []))
        fig.update_layout(
        xaxis=dict(range=range_scale,
                    tickvals=[i for i in range(int(min(low_rng_min, -1, low_mix_min)+1),
                                        int(max(up_rng_max, 2.25, up_mix_max+1)-1))],
                        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        margin=dict(l=0, r=0)
        )
        fig.update_xaxes(ticks="outside",
                        showgrid=False,
                        autorange=True, showline=True,
                        # tickcolor='rgba(0,0,0,0)',
                        linecolor='black'
                        )

        df.at[j, "Graph"] = fig

        for i in range(j+1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)

            filter_df = pd.concat([filter_df] * 2, ignore_index=True)


            filter_df['Treatment'][0] = 'Indirect'
            filter_df['RR'][0] = filter_df['indirect'][0]
            filter_df['CI_width_hf'][0] = (filter_df.indirect_up[0] - filter_df['indirect'][0])
            filter_df['lower_error'][0] = (filter_df['indirect'][0] - filter_df.indirect_low[0])


            colors = ['#ABB2B9','black']

            hovert_template=['indirect estimate with CI'+'<extra></extra>',
                    'mixed estimate with CI'+'<extra></extra>'
                    ]

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
                                showlegend=False,
                                hovertemplate= hovert_template[idx] 
                            ))
            
            fig.update_layout(
                barmode='group',
                bargap=0.25,
                xaxis=dict(range=range_scale),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
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
                        x0=f"{lower}",
                        y0="0",
                        x1=f"{upper}",
                        y1='1',
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below"
                    ),]
                # template="plotly_dark",
            )
        
            fig.add_trace(go.Scatter(
                x=[0.8, 1.25],  # x-coordinate in the middle of the shape
                y=[0, 0],    # y-coordinate (doesn't matter, since it's vertical shape)
                mode='markers',
                marker=dict(color='rgba(0, 0, 0, 0)', size=5),
                hovertemplate = '<b>Range of equivalence</b>: %{x} <extra></extra>',
                hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)")
            ))
                
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=2,dash="dot"), layer='below')
        
                

            df.at[i, "Graph"] = fig
    
    return df


def __skt_PIdirect_forstplot(df, lower, upper):
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
         new_rows.loc[idx/19, 'Reference'] = df.loc[idx, 'Reference']

    new_rows['Treatment'] = 'Scale'
    new_rows['risk'] = 'Enter a number'
    new_rows['Scale_lower'] = 'Enter a number for lower'
    new_rows['Scale_upper'] = 'Enter a number for upper'
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat([df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):

        data_ex = df[j+1:j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))
     
        range_scale=[min(low_rng_min, -1, low_mix_min), 
                              max(up_rng_max, 2.25, up_mix_max+1)]  
        
        fig = go.Figure(go.Scatter( y = [],x = []))
        fig.update_layout(
        xaxis=dict(range=range_scale,
                    tickvals=[i for i in range(int(min(low_rng_min, -1, low_mix_min)+1),
                                        int(max(up_rng_max, 2.25, up_mix_max+1)-1))],
                        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        margin=dict(l=0, r=0)
        )
        fig.update_xaxes(ticks="outside",
                        showgrid=False,
                        autorange=True, showline=True,
                        # tickcolor='rgba(0,0,0,0)',
                        linecolor='black'
                        )

        df.at[j, "Graph"] = fig

        for i in range(j+1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)

            filter_df = pd.concat([filter_df] * 3, ignore_index=True)


            filter_df['CI_width_hf'][2] = (filter_df.CI_upper[2] - filter_df['RR'][1]*1.2)
            filter_df['lower_error'][2] = (filter_df['RR'][2] - filter_df.CI_lower[1]*1.2)


            filter_df['Treatment'][0] = 'Direct'
            filter_df['RR'][0] = filter_df['direct'][0]
            filter_df['CI_width_hf'][0] = (filter_df.direct_up[0] - filter_df['direct'][0])
            filter_df['lower_error'][0] = (filter_df['direct'][0] - filter_df.direct_low[0])

            colors = ['#707B7C', 'red','black']

            hovert_template=[
                    'direct estimate with CI'+'<extra></extra>',
                    'mixed estimate with CI & PI'+'<extra></extra>',
                    'mixed estimate with CI & PI'+'<extra></extra>'
                    ]

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
                                showlegend=False,
                                hovertemplate= hovert_template[idx] 
                            ))
            
            fig.update_layout(
                barmode='group',
                bargap=0.25,
                xaxis=dict(range=range_scale),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
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
                        x0=f"{lower}",
                        y0="0",
                        x1=f"{upper}",
                        y1='1',
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below"
                    ),]
                # template="plotly_dark",
            )
        
            fig.add_trace(go.Scatter(
                x=[0.8, 1.25],  # x-coordinate in the middle of the shape
                y=[0, 0],    # y-coordinate (doesn't matter, since it's vertical shape)
                mode='markers',
                marker=dict(color='rgba(0, 0, 0, 0)', size=5),
                hovertemplate = '<b>Range of equivalence</b>: %{x} <extra></extra>',
                hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)")
            ))
                
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=2,dash="dot"), layer='below')
        
                

            df.at[i, "Graph"] = fig
    
    return df



def __skt_PIindirect_forstplot(df, lower, upper):
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
         new_rows.loc[idx/19, 'Reference'] = df.loc[idx, 'Reference']

    new_rows['Treatment'] = 'Scale'
    new_rows['risk'] = 'Enter a number'
    new_rows['Scale_lower'] = 'Enter a number for lower'
    new_rows['Scale_upper'] = 'Enter a number for upper'
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat([df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):

        data_ex = df[j+1:j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))
     
        range_scale=[min(low_rng_min, -1, low_mix_min), 
                              max(up_rng_max, 2.25, up_mix_max+1)]  
        
        fig = go.Figure(go.Scatter( y = [],x = []))
        fig.update_layout(
        xaxis=dict(range=range_scale,
                    tickvals=[i for i in range(int(min(low_rng_min, -1, low_mix_min)+1),
                                        int(max(up_rng_max, 2.25, up_mix_max+1)-1))],
                        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        margin=dict(l=0, r=0)
        )
        fig.update_xaxes(ticks="outside",
                        showgrid=False,
                        autorange=True, showline=True,
                        # tickcolor='rgba(0,0,0,0)',
                        linecolor='black'
                        )

        df.at[j, "Graph"] = fig


        for i in range(j+1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)

            filter_df = pd.concat([filter_df] * 3, ignore_index=True)


            filter_df['CI_width_hf'][2] = (filter_df.CI_upper[2] - filter_df['RR'][1]*1.2)
            filter_df['lower_error'][2] = (filter_df['RR'][2] - filter_df.CI_lower[1]*1.2)

            filter_df['Treatment'][0] = 'Indirect'
            filter_df['RR'][0] = filter_df['indirect'][0]
            filter_df['CI_width_hf'][0] = (filter_df.indirect_up[0] - filter_df['indirect'][0])
            filter_df['lower_error'][0] = (filter_df['indirect'][0] - filter_df.indirect_low[0])

            colors = ['#ABB2B9', 'red','black']

            hovert_template=['indirect estimate with CI'+'<extra></extra>',
                    'mixed estimate with CI & PI'+'<extra></extra>',
                    'mixed estimate with CI & PI'+'<extra></extra>'
                    ]

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
                                showlegend=False,
                                hovertemplate= hovert_template[idx] 
                            ))
            
            fig.update_layout(
                barmode='group',
                bargap=0.25,
                xaxis=dict(range=range_scale),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
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
                        x0=f"{lower}",
                        y0="0",
                        x1=f"{upper}",
                        y1='1',
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below"
                    ),]
                # template="plotly_dark",
            )
        
            fig.add_trace(go.Scatter(
                x=[0.8, 1.25],  # x-coordinate in the middle of the shape
                y=[0, 0],    # y-coordinate (doesn't matter, since it's vertical shape)
                mode='markers',
                marker=dict(color='rgba(0, 0, 0, 0)', size=5),
                hovertemplate = '<b>Range of equivalence</b>: %{x} <extra></extra>',
                hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)")
            ))
                
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=2,dash="dot"), layer='below')
        
                

            df.at[i, "Graph"] = fig
    
    return df


def __skt_directin_forstplot(df, lower, upper):
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
         new_rows.loc[idx/19, 'Reference'] = df.loc[idx, 'Reference']

    new_rows['Treatment'] = 'Scale'
    new_rows['risk'] = 'Enter a number'
    new_rows['Scale_lower'] = 'Enter a number for lower'
    new_rows['Scale_upper'] = 'Enter a number for upper'
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat([df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):

        data_ex = df[j+1:j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))
     
        range_scale=[min(low_rng_min, -1, low_mix_min), 
                              max(up_rng_max, 2.25, up_mix_max+1)]  
        
        fig = go.Figure(go.Scatter( y = [],x = []))
        fig.update_layout(
        xaxis=dict(range=range_scale,
                    tickvals=[i for i in range(int(min(low_rng_min, -1, low_mix_min)+1),
                                        int(max(up_rng_max, 2.25, up_mix_max+1)-1))],
                        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        margin=dict(l=0, r=0)
        )
        fig.update_xaxes(ticks="outside",
                        showgrid=False,
                        autorange=True, showline=True,
                        # tickcolor='rgba(0,0,0,0)',
                        linecolor='black'
                        )

        df.at[j, "Graph"] = fig

        for i in range(j+1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)

            filter_df = pd.concat([filter_df] * 3, ignore_index=True)


            filter_df['Treatment'][1] = 'Direct'
            filter_df['RR'][1] = filter_df['direct'][1]
            filter_df['CI_width_hf'][1] = (filter_df.direct_up[1] - filter_df['direct'][1])
            filter_df['lower_error'][1] = (filter_df['direct'][1] - filter_df.direct_low[1])

            filter_df['Treatment'][0] = 'Indirect'
            filter_df['RR'][0] = filter_df['indirect'][0]
            filter_df['CI_width_hf'][0] = (filter_df.indirect_up[0] - filter_df['indirect'][0])
            filter_df['lower_error'][0] = (filter_df['indirect'][0] - filter_df.indirect_low[0])


            colors = ['#ABB2B9', '#707B7C', 'black']

            hovert_template=['indirect estimate with CI'+'<extra></extra>',
                    'direct estimate with CI'+'<extra></extra>',
                    'mixed estimate with CI'+'<extra></extra>'
                    ]

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
                                showlegend=False,
                                hovertemplate= hovert_template[idx] 
                            ))
            
            fig.update_layout(
                barmode='group',
                bargap=0.25,
                xaxis=dict(range=range_scale),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
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
                        x0=f"{lower}",
                        y0="0",
                        x1=f"{upper}",
                        y1='1',
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below"
                    ),]
                # template="plotly_dark",
            )
        
            fig.add_trace(go.Scatter(
                x=[0.8, 1.25],  # x-coordinate in the middle of the shape
                y=[0, 0],    # y-coordinate (doesn't matter, since it's vertical shape)
                mode='markers',
                marker=dict(color='rgba(0, 0, 0, 0)', size=5),
                hovertemplate = '<b>Range of equivalence</b>: %{x} <extra></extra>',
                hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)")
            ))
                
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=2,dash="dot"), layer='below')
        
                

            df.at[i, "Graph"] = fig
    
    return df



def __skt_mix_forstplot(df, lower, upper):
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
        new_rows.loc[idx/19, 'Reference'] = df.loc[idx, 'Reference']
    new_rows['Treatment'] = 'Scale'
    new_rows['risk'] = 'Enter a number'
    new_rows['Scale_lower'] = 'Enter a number for lower'
    new_rows['Scale_upper'] = 'Enter a number for upper'
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat([df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):

        data_ex = df[j+1:j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
    # up_rng = 10**np.floor(np.log10(up_rng))
    # low_rng = 10 ** np.floor(np.log10(low_rng))
     
        range_scale=[min(low_rng_min, -1, low_mix_min), 
                              max(up_rng_max, 2.25, up_mix_max+1)]  
        
        fig = go.Figure(go.Scatter( y = [],x = []))
        fig.update_layout(
        xaxis=dict(range=range_scale,
                    tickvals=[i for i in range(int(min(low_rng_min, -1, low_mix_min)+1),
                                        int(max(up_rng_max, 2.25, up_mix_max+1)-1))],
                        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
        plot_bgcolor='rgba(0,0,0,0)',
        height=100,
        margin=dict(l=0, r=0)
        )
        fig.update_xaxes(ticks="outside",
                        showgrid=False,
                        autorange=True, showline=True,
                        # tickcolor='rgba(0,0,0,0)',
                        linecolor='black'
                        )

        df.at[j, "Graph"] = fig

        for i in range(j+1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)


            hovert_template=[
                    'mixed estimate with CI'+'<extra></extra>',
                    ]

            fig = go.Figure()
            for idx in range(filter_df.shape[0]):
                data_point = filter_df.iloc[idx]
                if np.isnan(data_point['RR']):
                    continue
                fig.add_trace(go.Scatter(
                                x=[data_point['RR']],
                                y=[data_point['Treatment']],
                                # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                                error_x=dict(type='data',color = 'black',array=[data_point['lower_error'],data_point['CI_width_hf']],visible=True),
                                marker=dict(color='black', size=12),
                                showlegend=False,
                                hovertemplate= hovert_template[idx] 
                            ))
            
            fig.update_layout(
                barmode='group',
                bargap=0.25,
                xaxis=dict(range=range_scale),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
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
                        x0=f"{lower}",
                        y0="0",
                        x1=f"{upper}",
                        y1='1',
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below"
                    ),]
                # template="plotly_dark",
            )
        
            fig.add_trace(go.Scatter(
                x=[0.8, 1.25],  # x-coordinate in the middle of the shape
                y=[0, 0],    # y-coordinate (doesn't matter, since it's vertical shape)
                mode='markers',
                marker=dict(color='rgba(0, 0, 0, 0)', size=5),
                hovertemplate = '<b>Range of equivalence</b>: %{x} <extra></extra>',
                hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)")
            ))
                
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=2,dash="dot"), layer='below')
        
                

            df.at[i, "Graph"] = fig

    # new_row.loc[0, 'Graph'] = df.iloc[1]['Graph']
    return df