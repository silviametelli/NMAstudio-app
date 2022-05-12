import pandas as pd
import plotly.express as px, plotly.graph_objects as go
import numpy as np

funnel_data =  pd.read_csv('db/funnel/funnel_data.csv')

treatment = "IXE"

df = funnel_data[funnel_data.treat2 == treatment].copy()

df['Comparison'] = (df['treat1'] + ' vs ' + df['treat2']).astype(str)



df1 = df[df['Comparison'].map(df['Comparison'].value_counts()) > 1]
