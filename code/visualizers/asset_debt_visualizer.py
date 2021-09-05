import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from jupyter_dash import JupyterDash
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

from visualizers import BaseVisualizer


class AssetDebtVisualizer(BaseVisualizer):
    def __init__(self, stock_id):
        super(AssetDebtVisualizer, self).__init__()
        self.load_stock_info()
        self.stock_id = stock_id

        self.company_name = self.stock_info[self.stock_info.code ==
                                            stock_id].name.values[0]

        self.company_type = self.stock_info[self.stock_info.code ==
                                            stock_id].company_type.values[0]
        self.data = self.create_df(stock_id)
        self.features = self.data.columns[1:]

    def create_df(self, stock_id):
        df = pd.read_csv(
            f"{self.root}/asset_debt/{self.company_type}_asset_debt.csv",
            header=[0, 1])
        df = df[df[('year', 'code')] == stock_id]
        del df[('year', 'code')]
        data_all = []
        seasons = np.unique([col[0] for col in df.columns])
        features = [col[1] for col in df.columns if col[0] == seasons[0]]
        col_names = ['季'] + [col for col in features]

        for feature in features:
            selected_columns = [(season, feature) for season in seasons]
            df1 = df[selected_columns]
            df1.columns = df1.columns.droplevel(1)
            data_all.append(df1.T)
        data_all = pd.concat(data_all, axis=1).astype(float).reset_index()
        data_all.columns = col_names
        return data_all

    def run_dash(self):
        pbr = '每股參考淨值'
        share_capital = '股本'
        asset_debt_table = self.plot_table(self.data.drop(columns=[pbr, share_capital]))
        one_line_plot = make_subplots(rows=3,
                                      cols=1,
                                      subplot_titles=('負債比率', pbr, share_capital),
                                      shared_xaxes=True)
        one_line_plot.append_trace(go.Scatter(
            x=self.data['季'],
            y=100 * (self.data['負債總額'] / self.data['資產總額']).values.reshape(-1),
            mode='lines+markers'),
            row=1,
            col=1)
        one_line_plot.append_trace(go.Scatter(
            x=self.data['季'],
            y=self.data[pbr].values.reshape(-1),
            mode='lines+markers'),
            row=2,
            col=1)
        one_line_plot.append_trace(go.Scatter(
            x=self.data['季'],
            y=(self.data[share_capital]/10000).values.reshape(-1),
            mode='lines+markers'),
            row=3,
            col=1)
        one_line_plot.update_yaxes(title_text='%', row=1, col=1)
        one_line_plot.update_yaxes(title_text='$NTD', row=2, col=1)
        one_line_plot.update_yaxes(title_text='$NTD 萬', row=3, col=1)
        one_line_plot.update_layout(showlegend=False)

        app = JupyterDash(__name__)
        app.layout = html.Div([
            html.H1(f'{self.stock_id} {self.company_name}',
                    style=self.title_style),
            dcc.Graph(id='asset_debt_line_plot',
                      style={
                          'width': '900px',
                          'height': '80%',
                          'text-align': 'center'
                      }),
            dcc.Checklist(id='checkbox',
                          options=[{
                              'label': self.features[i],
                              'value': i
                          } for i in range(len(self.features))
                              if self.features[i] != pbr and self.features[i] != share_capital],
                          value=[
                              i for i in range(len(self.features))
                              if self.features[i] != pbr and self.features[i] != share_capital
                          ],
                          style={
                              'width': '900px',
                              'text-align': 'center'
                          }),
            dcc.Graph(figure=one_line_plot,
                      style={
                          'width': '900px',
                          'height': '10%',
                          'text-align': 'center'
                      }),
            html.Div(
                [asset_debt_table],
                style={
                    'width': '900px',
                    'text-align': 'center',
                    'marginTop': '50px',
                    'marginBottom': '50px'
                })
        ],
            style=self.main_div_style)

        @app.callback(Output('asset_debt_line_plot', 'figure'),
                      [Input('checkbox', 'value')])
        def update_line_chart(contents):
            features = [self.features[i] for i in contents]
            fig = go.Figure()

            for col in features:
                fig.add_trace(
                    go.Scatter(x=self.data['季'],
                               y=self.data[col].values.reshape(-1) / 1e4,
                               mode='lines+markers',
                               name=col))

            fig.update_layout(title={
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'text': '近年資產負債表'
            },
                yaxis_title='$NTD 萬')
            return fig

        app.run_server(mode='external')
