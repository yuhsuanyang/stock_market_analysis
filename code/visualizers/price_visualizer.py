import time
import pickle
import requests
import pandas as pd
from io import StringIO
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from jupyter_dash import JupyterDash
from datetime import datetime, timedelta
from dash.dependencies import Input, Output

from visualizers import BaseVisualizer


class PriceVisualizer(BaseVisualizer):
    def __init__(self, stock_id):
        super(PriceVisualizer, self).__init__()
        self.load_stock_info()
        self.stock_id = stock_id
        self.company_name = self.stock_info[self.stock_info.code ==
                                            stock_id].name.values[0]
        self.whole_data = pickle.load(open(f"{self.root}/price.pkl", 'rb'))

        self.data = self.whole_data[self.stock_id]
        self.update_data()
        self.technical = self.create_df()
        self.features = ['5MA', '20MA', '60MA']
        self.start_date = self.data.Date[0]
        self.end_date = self.data.Date.iloc[-1]
        self.default_date = self.data.Date.iloc[-90]

    def create_df(self):
        technical = self.data[['Date', 'Close']]
        technical.columns = ['date', 'daily']
        technical['5MA'] = self.data.Close.rolling(5).mean()
        technical['20MA'] = self.data.Close.rolling(20).mean()
        technical['60MA'] = self.data.Close.rolling(60).mean()
        return technical

    def update_data(self):
        start_date = datetime.strptime(self.data.iloc[-1].Date,
                                       '%Y-%m-%d') + timedelta(days=1)
        today_date = datetime.today()

        if today_date.isoweekday() > 5:  # weekend
            today_date = today_date - timedelta(days=today_date.isoweekday() -
                                                6)

        if (today_date - timedelta(days=1)) <= start_date:
            print('data is already up-to-date')
            return
        else:
            print('updating data...')

        start_date = datetime.strftime(start_date, '%Y-%m-%d')
        today_date = datetime.strftime(today_date, '%Y-%m-%d')
        print('start date', start_date)
        print('today', today_date)

        start = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
        end = int(time.mktime(time.strptime(today_date, '%Y-%m-%d')))

        url = f"https://query1.finance.yahoo.com/v7/finance/download/{self.stock_id}.TW?period1={start}&period2={end}&interval=1d&events=history&crumb=DCkS0u002FOZyL"
        res = requests.get(url)
        self.data = pd.concat([self.data,
                               pd.read_csv(StringIO(res.text))
                               ]).reset_index(drop=True)

        self.whole_data[self.stock_id] = self.data
        with open(f"{self.root}/price.pkl", 'wb') as f:
            pickle.dump(self.whole_data, f)

    def transform_date_style(self, date):
        return date.replace('-', '/')

    def run_dash(self):
        app = JupyterDash(__name__)
        app.layout = html.Div([
            html.H1(f'{self.stock_id} {self.company_name}',
                    style=self.title_style),
            dcc.Graph(id='line_plot',
                      style={
                          'width': '900px',
                          'height': '80%',
                          'text-align': 'center'
                      }),
            dcc.Checklist(id='checkbox',
                          options=[{
                              'label': self.features[i],
                              'value': i
                          } for i in range(len(self.features))],
                          value=[i for i in range(len(self.features))],
                          style={
                              'width': '900px',
                              'height': '20px',
                              'text-align': 'center'
                          }),
            dcc.Graph(id='bar_chart',
                      style={
                          'width': '900px',
                          'height': '300px',
                          'text-align': 'center'
                      }),
            dcc.RangeSlider(id='slider',
                            min=0,
                            max=len(self.data) - 1,
                            value=[len(self.data) - 90,
                                   len(self.data) - 1],
                            step=1,
                            marks={
                                0:
                                self.transform_date_style(self.start_date),
                                len(self.data) - 90:
                                self.transform_date_style(self.default_date),
                                len(self.data) - 1:
                                self.transform_date_style(self.end_date)
                            })
        ],
            style=self.main_div_style)

        @app.callback(Output('line_plot', 'figure'),
                      [Input('checkbox', 'value'),
                       Input('slider', 'value')])
        def update_line_chart(contents, date_range):
            features = ['daily'] + [self.features[i] for i in contents]
            fig = go.Figure()
            x = self.technical.date.iloc[date_range[0]:date_range[1] + 1]
            for col in features:
                fig.add_trace(
                    go.Scatter(x=x,
                               y=self.technical[col].
                               iloc[date_range[0]:date_range[1] +
                                    1].values.reshape(-1),
                               mode='lines',
                               name=col))
            fig.update_layout(title={
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'text': '股價走勢'
            },
                yaxis_title='$NTD')
            return fig

        @app.callback(Output('slider', 'marks'), [Input('slider', 'value')])
        def update_slider_mark(date_range):
            start = self.data.Date.iloc[date_range[0]]
            end = self.data.Date.iloc[date_range[1]]
            return {
                0: self.transform_date_style(self.start_date),
                date_range[0]: self.transform_date_style(start),
                date_range[1]: self.transform_date_style(end)
            }

        @app.callback(Output('bar_chart', 'figure'),
                      [Input('slider', 'value')])
        def update_bar_chart(date_range):
            selected_data = self.data.iloc[date_range[0]:date_range[1] + 1]
            bull = selected_data[selected_data.Close > selected_data.Open]
            bear = selected_data[selected_data.Close < selected_data.Open]
            tie = selected_data[selected_data.Close == selected_data.Open]
            fig = go.Figure()
            fig.add_trace(
                go.Bar(x=bull.Date,
                       y=bull.Volume.values.reshape(-1) / 1e3,
                       marker_color='red',
                       name='漲'))
            fig.add_trace(
                go.Bar(x=bear.Date,
                       y=bull.Volume.values.reshape(-1) / 1e3,
                       marker_color='green',
                       name='跌'))
            fig.add_trace(
                go.Bar(x=tie.Date,
                       y=bull.Volume.values.reshape(-1) / 1e3,
                       marker_color='gray',
                       name='平'))
            fig.update_layout(title={
                'y': 0.9,
                'x': 0.45,
                'xanchor': 'center',
                'yanchor': 'top',
            },
                yaxis_title='成交量(千股)')
            return fig

        app.run_server(mode='external')
