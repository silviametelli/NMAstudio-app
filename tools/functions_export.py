import pandas as pd
import dash
from assets.COLORS import *



def __generate_xlsx_league(n_clicks, leaguedata):
    df = pd.DataFrame(leaguedata['props']['data'])
    style_data_conditional = leaguedata['props']['style_data_conditional']

    conditional_df = {r: {c: None for c in df.columns} for r in  df.columns}
    for d in style_data_conditional:
        col_k = d['if']['column_id']
        if 'filter_query' in d['if']:
            row_string = d['if']['filter_query'].split('=')[-1]
            row_k = row_string[row_string.find("{") + 1: row_string.find("}")]
            conditional_df[row_k][col_k] = d['backgroundColor']

    df = df.set_index('Treatment')[df.Treatment]

    def to_xlsx(bytes_io):
        writer = pd.ExcelWriter(bytes_io, engine='xlsxwriter')  # Create a Pandas Excel writer using XlsxWriter as the engine.
        df.to_excel(writer, sheet_name='League_Table')  # Convert the dataframe to an XlsxWriter Excel object.
        workbook, worksheet = writer.book, writer.sheets['League_Table']  # Get the xlsxwriter workbook and worksheet objects.
        wrap_format = workbook.add_format({'text_wrap': True,
                                           'border':1})
        wrap_format.set_align('center')
        wrap_format.set_align('vcenter')

        for r, rl in enumerate(df.columns):
            for c, cl in enumerate(df.columns):
                worksheet.write(r+1, c+1, df.loc[rl, cl], wrap_format) # Overwrite both the value and the format of each header cell
                worksheet.conditional_format(first_row=r+1, first_col=c+1,
                                             last_row=r+1, last_col=c+1,
                                             options={'type': 'cell',
                                                      'format': workbook.add_format({
                                                          'bg_color': (conditional_df[rl][cl]
                                                                       if conditional_df[rl][cl]!=CLR_BCKGRND2
                                                                       else 'white'),
                                                          'text_wrap': True
                                                           }),
                                                      'criteria': '>',
                                                      'value': -int(1e8)
                                                      })
        worksheet.set_default_row(30)  # Set the default height of Rows to 20.
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col].astype(str).str.split('\n').str[-1]
            max_len = max((
                series.map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 0  # adding a little extra space
            worksheet.set_column(idx+1, idx+1, max_len)  # set column width
        writer.save()  # Close the Pandas Excel writer and output the Excel file.

    return dash.dcc.send_bytes(to_xlsx, filename="League_Table.xlsx")

    ######### return dash.dcc.send_data_frame(writer.save(), filename="league_table.xlsx")



def __generate_csv_consistency(n_nlicks, outcome_idx, consistencydata_all):

    button_trigger  = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'btn-netsplit-all.n_clicks' in triggered: button_trigger = True

    df = pd.read_json(consistencydata_all[outcome_idx], orient='split')

    if button_trigger:
        if df is not None:
            comparisons = df.comparison.str.split(':', expand=True)
            df['Comparison'] = comparisons[0] + ' vs ' + comparisons[1]
            df = df.loc[:, ~df.columns.str.contains("comparison")]
            df = df.sort_values(by='Comparison').reset_index()
            df = df[['Comparison', 'k', "direct", 'nma', "indirect", "p-value"]].round(decimals=4)
            df = df.set_index('Comparison')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
            return dash.dcc.send_data_frame(df.to_csv, filename="consistency_table_full.csv")

    else: return None



def __generate_xlsx_netsplit(n_nlicks, consistencydata):
    df = pd.DataFrame(consistencydata)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    def to_xlsx(bytes_io):
        writer = pd.ExcelWriter(bytes_io, engine='xlsxwriter')  # Create a Pandas Excel writer using XlsxWriter as the engine.
        df.to_excel(writer, sheet_name='Netsplit_Table', index=False)  # Convert the dataframe to an XlsxWriter Excel object.
        workbook, worksheet = writer.book, writer.sheets['Netsplit_Table']  # Get the xlsxwriter workbook and worksheet objects.
        wrap_format = workbook.add_format({'text_wrap': True,
                                           'border':1})
        wrap_format.set_align('center')
        wrap_format.set_align('vcenter')

        col_pval=3
        start_row, end_row =0, df.shape[0]
        #worksheet.write(r+1, col_pval, df.loc[rl, cl], wrap_format) # Overwrite both the value and the format of each header cell
        worksheet.conditional_format(first_row=0, first_col=col_pval,
                                             last_row=end_row, last_col=col_pval,
                                             options={'type': 'cell',
                                                      'format': workbook.add_format({
                                                          'bg_color': 'white',
                                                          'font_color': 'blue',
                                                          'text_wrap': True
                                                           }),
                                                      'criteria': 'between',
                                                      'minimum': 0.10001,
                                                      'maximum': 0.15,
                                                      })
        worksheet.conditional_format(first_row=0, first_col=col_pval,
                                             last_row=end_row, last_col=col_pval,
                                             options={'type': 'cell',
                                                      'format': workbook.add_format({
                                                          'bg_color': 'white',
                                                          'font_color': 'orange',
                                                          'text_wrap': True
                                                           }),
                                                      'criteria': 'between',
                                                      'minimum': 0.05001,
                                                      'maximum': 0.10,
                                                      })
        worksheet.conditional_format(first_row=0, first_col=col_pval,
                                             last_row=end_row, last_col=col_pval,
                                             options={'type': 'cell',
                                                      'format': workbook.add_format({
                                                          'bg_color': 'white',
                                                          'font_color': 'red',
                                                          'text_wrap': True
                                                           }),
                                                      'criteria': '<=',
                                                      'value': 0.05
                                                      })
        worksheet.set_default_row(30)  # Set the default height of Rows to 20.
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col].astype(str).str.split('\n').str[-1]
            max_len = max((
                series.map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 0  # adding a little extra space
            worksheet.set_column(idx+1, idx+1, max_len)  # set column width
        writer.save()  # Close the Pandas Excel writer and output the Excel file.

    return dash.dcc.send_bytes(to_xlsx, filename="Netsplit_Table.xlsx")
    ###########return dash.dcc.send_data_frame(writer.save(), filename="Netsplit_Table_table.xlsx")

