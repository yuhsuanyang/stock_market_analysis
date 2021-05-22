from abc import abstractmethod

import pandas as pd


class BaseVisualizer(object):
    def __init__(self):
        pass

    def load_stock_info(self):
        self.root = '../data_sample'
        self.stock_info = pd.read_csv(
            f'{self.root}/stock_meta_data.csv')

    def transform_by_season(self, df, column_name):
        # transfrom accumulated data (raw) to data per season
        years = [[df.columns[j] for j in range(
            i, i+4)] for i in range(1, len(df.columns), 4)]
        company_data = df[df.company == self.stock_id]
        processed_data = []
        for year in years:
            one_year_data = company_data[year]
            one_year_diff = one_year_data.diff(periods=1, axis=1)
            one_year_diff[year[0]] = one_year_data[year[0]]
            processed_data.append(one_year_diff.T)

        processed_data = pd.concat(processed_data).sort_index()
        processed_data.columns = [column_name]
        return processed_data

    @abstractmethod
    def create_df(self):
        pass

    # @abstractmethod
    # def plot_line_chart(self):
    #    pass

    @abstractmethod
    def plot_table(self):
        pass

    @abstractmethod
    def run_dash(self):
        pass
