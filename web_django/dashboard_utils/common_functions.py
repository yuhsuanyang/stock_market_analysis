import dash_table
import pandas as pd


def create_price_sequence(model_table):
    df = []
    for row in model_table:
        df.append([row.date, row.Close])
    return pd.DataFrame(df, columns=['date', 'close'])


def create_df(model_table):
    # create dataframe from django model table (QuerySet)
    df = {'year': [], 'season': []}
    for col in model_table[0].get_values():  # initialize columns
        df[col] = []

    for row in model_table:
        df['year'].append(row.season[0:3])  # season=yyy_q
        df['season'].append(row.season[-1])
        row_values = row.get_values()
        for col in row_values:
            df[col].append(row_values[col])
    df = pd.DataFrame.from_dict(df).sort_values(
        by=['year', 'season']).reset_index(drop=True)
    return df


def transform_by_season(df):
    # transfrom accumulated data (raw) to data per season
    years = df['year'].unique()
    df_each_year = []
    cols = [col for col in df.columns if col != 'year' and col != 'season']
    for year in years:
        one_year_data = df[df.year == year]
        if len(df[df.year == year]) > 1:
            one_year_diff = one_year_data[cols].diff(periods=1)
            one_year_data.iloc[1:4][cols] = one_year_diff.iloc[1:4][cols]
        df_each_year.append(one_year_data)
    processed_df = pd.concat(df_each_year, ignore_index=True)
    processed_df['season'] = processed_df['year'].astype(int).astype(
        str) + '_' + processed_df['season'].astype(int).astype(str)
    del processed_df['year']
    return processed_df


def plot_table(df):
    df1 = df.copy()
    df1 = df1.iloc[::-1].reset_index(drop=True)
    table = dash_table.DataTable(columns=[{
        'id': col,
        'name': col
    } for col in df1.columns],
                                 data=df1.to_dict('records'),
                                 style_cell={
                                     'whiteSpace': 'normal',
                                     'height': 'auto',
                                     'text-align': 'left',
                                     'color': 'darkslategrey',
                                     'minWidth': '50px'
                                 },
                                 style_header={
                                     'fontWeight': 'bold',
                                     'text-align': 'center'
                                 },
                                 style_table={
                                     'overflowX': 'auto',
                                     'overflowY': 'auto',
                                     'height': '300px'
                                 },
                                 fixed_rows={'headers': True})
    return table
