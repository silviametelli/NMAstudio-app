import pandas as pd


def __netsplit(edges, outcome, net_split_data, net_split_data_out2, consistency_data):
    df = (pd.read_json(net_split_data, orient='split') if not outcome
          else  pd.read_json(net_split_data_out2, orient='split') if net_split_data_out2 else None)
    consistency_data = pd.read_json(consistency_data, orient='split')
    if df is not None:
        comparisons = df.comparison.str.split(':', expand=True)
        df['Comparison'] = comparisons[0] + ' vs ' + comparisons[1]
        df = df.loc[:, ~df.columns.str.contains("comparison")]
        df = df.sort_values(by='Comparison').reset_index()
        df = df[['Comparison', "direct", "indirect", "p-value"]].round(decimals=4)

    slctd_comps = []
    for edge in edges or []:
        src, trgt = edge['source'], edge['target']
        slctd_comps += [f'{src} vs {trgt}']
    if edges and df is not None:
        df = df[df.Comparison.isin(slctd_comps)]

    data_cols = [{"name": c, "id": c} for c in df.columns]
    data_output = df.to_dict('records') if df is not None else dict()
    _out_net_split_table = [data_output, data_cols]

    data_consistency = consistency_data.round(decimals=4).to_dict('records')
    consistency_tbl_cols = [{"name": i, "id": i} for i in consistency_data.columns]
    _out_consistency_table = [data_consistency, consistency_tbl_cols]


    return _out_net_split_table + _out_consistency_table