from abc import abstractmethod

import dash_table
import pandas as pd


class BaseVisualizer(object):
    title_style = {
        'text-align': 'left',
        'height': '50px',
        'marginLeft': '42%',
        'marginBottom': 0,
        'marginTop': '5%'
    }
    main_div_style = {'marginLeft': '25%', 'width': '900px'}

    def __init__(self):
        pass

    def load_stock_info(self):
        self.root = '../data_sample'
        self.stock_info = pd.read_csv(f'{self.root}/stock_meta_data.csv')

    def transform_by_season(self, df):
        # transfrom accumulated data (raw) to data per season
        years = [[df.index[j] for j in range(i, i + 4)]
                 for i in range(0, len(df), 4)]
        #        company_data = df[df.company == self.stock_id]
        processed_data = []
        for year in years:
            one_year_data = df.loc[year].reset_index(drop=True)
            #            print(one_year_data)
            one_year_diff = one_year_data.diff(periods=1)
            one_year_diff.iloc[0] = one_year_data.iloc[0]
            one_year_diff.index = year
            processed_data.append(one_year_diff)

        processed_data = pd.concat(processed_data).sort_index()
        #        processed_data.columns = [column_name]
        return processed_data

    def plot_table(self, df):
        table = dash_table.DataTable(columns=[{
            'id': col,
            'name': col
        } for col in df.columns],
            data=df.to_dict('records'),
            style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'text-align': 'left',
            'color': 'darkslategrey'
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

    @abstractmethod
    def create_df(self):
        pass

    @abstractmethod
    def run_dash(self):
        pass
