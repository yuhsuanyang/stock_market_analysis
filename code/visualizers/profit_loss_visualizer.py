import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from jupyter_dash import JupyterDash

from visualizers import BaseVisualizer


class ProfitLossVisualizer(BaseVisualizer):
    def __init__(self, stock_id):
        super(ProfitLossVisualizer, self).__init__()
        self.load_stock_info()
        self.stock_id = stock_id

        self.company_name = self.stock_info[self.stock_info.code ==
                                            stock_id].name.values[0]

        self.company_type = self.stock_info[self.stock_info.code ==
                                            stock_id].company_type.values[0]
        self.data = self.create_df(stock_id)
        self.features = self.data.columns[1:]
        if '營業毛利' in self.features:
            self.df_pr = self.create_percentage_df()

    def create_df(self, stock_id):
        df = pd.read_csv(
            f"{self.root}/profit_loss/{self.company_type}_profit_loss.csv",
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
        data_all = pd.concat(data_all, axis=1)
        data_all = self.transform_by_season(
            data_all.astype(float)).reset_index()
        data_all.columns = col_names
        return data_all

    def create_percentage_df(self):
        df_pr = pd.DataFrame(self.data['季'])
        df_pr['毛利率'] = (100 * self.data['營業毛利'] / self.data['營業收入']).round(2)

        df_pr['營業利益率'] = (100 * self.data['營業利益'] / self.data['營業收入']).round(2)
        df_pr['淨利率'] = (100 * self.data['稅後淨利'] / self.data['營業收入']).round(2)
        return df_pr

    def run_dash(self):
        eps = '基本每股盈餘'
        profit_loss_table = self.plot_table(self.data.drop(columns=eps))
        eps_line_plot = go.Figure()
        eps_line_plot.add_trace(
            go.Scatter(x=self.data['季'],
                       y=self.data[eps].values.reshape(-1),
                       mode='lines+markers'))
        eps_line_plot.update_layout(title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'text': eps
        },
            yaxis_title='$NTD')

        div_children = [
            html.H1(f'{self.stock_id} {self.company_name}',
                    style=self.title_style),
            dcc.Graph(id='profit_loss_line_plot',
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
                              if self.features[i] != eps],
                          value=[
                              i for i in range(len(self.features))
                              if self.features[i] != eps
                          ],
                          style={
                              'width': '900px',
                              'text-align': 'center'
                          }),
            html.Div(
                [profit_loss_table],
                style={
                    'width': '900px',
                    'text-align': 'center',
                    'marginTop': '50px',
                    'marginBottom': '50px'
                }),
            dcc.Graph(figure=eps_line_plot,
                      style={
                          'width': '900px',
                          'height': '10%',
                          'text-align': 'center'
                      })
        ]

        if '營業毛利' in self.features:
            percentage_table = self.plot_table(self.df_pr)
            percentage_line_plot = go.Figure()
            for col in self.df_pr.columns:
                if col != '季':
                    percentage_line_plot.add_trace(
                        go.Scatter(x=self.df_pr['季'],
                                   y=self.df_pr[col].values.reshape(-1),
                                   mode='lines+markers',
                                   name=col))
            percentage_line_plot.update_layout(title={
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'text': '利潤比率'
            },
                yaxis_title='%')
            div_children += [
                dcc.Graph(figure=percentage_line_plot,
                          style={
                              'width': '900px',
                              'height': '10%',
                              'text-align': 'center'
                          }),
                html.Div(
                    [percentage_table],
                    style={
                        'width': '500px',
                        'text-align': 'center',
                        'marginTop': '50px',
                        'marginBottom': '50px',
                        'marginLeft': '20%'
                    })
            ]
        else:
            div_children.append(
                html.H3('此類股沒有毛利', style={'text-align': 'center'}))

        app = JupyterDash(__name__)
        app.layout = html.Div(div_children, style=self.main_div_style)

        @app.callback(Output('profit_loss_line_plot', 'figure'),
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
                'text': '近年損益表'
            },
                yaxis_title='$NTD 萬')
            return fig

        app.run_server(mode='external')
