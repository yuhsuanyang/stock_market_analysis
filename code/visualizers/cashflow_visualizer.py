import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from jupyter_dash import JupyterDash

from visualizers import BaseVisualizer


class CashflowVisualizer(BaseVisualizer):
    def __init__(self, stock_id):
        super(CashflowVisualizer, self).__init__()
        self.load_stock_info()
        self.stock_id = stock_id
        self.company_name = self.stock_info[self.stock_info.code ==
                                            stock_id].name.values[0]
        self.col_dict = {'營運產生之現金流入（流出）': 'cash_from_operation',
                         '營業活動之淨現金流入（流出）': 'cash_from_opertation_acitivities',
                         '取得不動產、廠房及設備': 'real_estate',
                         '投資活動之淨現金流入（流出）': 'cash_from_investment',
                         '籌資活動之淨現金流入（流出）': 'cash_from_fundraise'}
        self.data = self.create_df(stock_id)
        self.features = self.data.columns[1:]

    def create_df(self, stock_id):
        data_all = []
        col_names = ['季', '營運現金流', '營業淨現金流', '資本支出', '投資淨現金流', '籌資淨現金流']
        for i, col in enumerate(self.col_dict):
            df = pd.read_csv(
                f'{self.root}/{self.col_dict[col]}.csv')
            data = self.transform_by_season(df, col)
            data_all.append(data)

        data_all = pd.concat(data_all, axis=1)
        adjust_col = ['季'] + data_all.columns.tolist()
        data_all['季'] = data_all.index
        data_all = data_all[adjust_col]
        data_all.columns = col_names
        data_all['自由現金流'] = data_all['營業淨現金流'] + data_all['資本支出']
        data_all['淨現金流'] = data_all['營業淨現金流'] + \
            data_all['籌資淨現金流'] + data_all['投資淨現金流']
        return data_all

    def plot_table(self):
        fig = go.Figure()
        column_size = [80] + [100]*7
        fig.add_trace(go.Table(columnorder=[i for i in range(8)],
                               columnwidth=column_size,
                               header=dict(values=self.data.columns,
                                           align="left"),
                               cells=dict(values=[self.data[col].tolist() for col in self.data.columns],
                                          align="left", font=dict(size=10))))
        fig.update_layout(title={
                          'y': 0.9, 'x': 0.45, 'xanchor': 'center', 'yanchor': 'top', 'text': '近年現金流量表'})
        return fig

    def run_dash(self):
        table = self.plot_table()
        app = JupyterDash(__name__)
        app.layout = html.Div([
            dcc.Graph(id='line_plot',
                      style={'width': '900px', 'height': '80%', 'text-align': 'center'}),
            dcc.Checklist(id='checkbox',
                          options=[{'label': self.features[i], 'value': i}
                                   for i in range(len(self.features))],
                          value=[i for i in range(len(self.features))],
                          style={'width': '900px', 'text-align': 'center'}),
            dcc.Graph(figure=table, style={'width': '900px', 'text-align': 'center'})],
            style={'marginLeft': '25%'})

        @app.callback(Output('line_plot', 'figure'), [Input('checkbox', 'value')])
        def update_line_chart(contents):
            features = [self.features[i] for i in contents]
            fig = go.Figure()

            for col in features:
                if col in ['自由現金流', '淨現金流']:
                    line_type = 'dash'
                else:
                    line_type = 'solid'
                fig.add_trace(go.Scatter(x=self.data['季'],
                                         y=self.data[col].values.reshape(
                                             -1)/1e4,
                                         line=dict(dash=line_type),
                                         mode='lines+markers', name=col))

            fig.update_layout(title={'y': 0.9, 'x': 0.45, 'xanchor': 'center',
                                     'yanchor': 'top', 'text': f'{self.stock_id} {self.company_name}'}, yaxis_title='$NTD 萬')
            return fig

        app.run_server(mode='external')
