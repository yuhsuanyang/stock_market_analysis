import time
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output


def query_historical_price(stock_code, end_date):
    end = datetime.strptime(end_date, '%Y-%m-%d')
    end = int(time.mktime(time.strptime(end_date, '%Y-%m-%d'))) + 86400
    start = end - 86400 * 365 * 5
    print('stock_code:', stock_code)
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_code}.TW?period1={start}&period2={end}&interval=1d&events=history&crumb=DCkS0u002FOZyL"
    # print(url)
    res = requests.get(url)
    data = pd.read_csv(StringIO(res.text))[['Date', 'Open', 'Close', 'Volume']]
    data.columns = ['date', 'open', 'daily', 'volume']
    data['5MA'] = data.daily.rolling(5).mean()
    data['20MA'] = data.daily.rolling(20).mean()
    data['60MA'] = data.daily.rolling(60).mean()
    return data


def create_dash(stock_code, company_name, df):
    features = ['daily', '5MA', '20MA', '60MA']
    app = DjangoDash('Price_Dashboard')
    app.layout = html.Div(
        [
            html.H3(id='title',
                    children="近90天股價走勢",
                    style={'text-align': 'center'}),
            dcc.Checklist(id='checkbox',
                          options=[{
                              'label': features[i],
                              'value': i
                          } for i in range(len(features))],
                          value=[i for i in range(len(features))],
                          style={
                              'width': '100%',
                              'height': '20px',
                              'text-align': 'center'
                          }),
            dcc.Graph(id='line_plot',
                      style={
                          'width': '100%',
                          'height': '80%',
                          'left': '10%',
                          'text-align': 'center'
                      }),
            dcc.Graph(id='bar_chart',
                      style={
                          'width': '100%',
                          'height': '300px',
                          'text-align': 'center'
                      }),
            dcc.RangeSlider(id='slider',
                            min=0,
                            max=len(df) - 1,
                            value=[len(df) - 90, len(df) - 1],
                            step=1,
                            marks={
                                0: df.date[0],
                                len(df) - 90: df.date.iloc[-90],
                                len(df) - 1: df.date.iloc[-1]
                            })
        ],
        style={
            'position': 'absolute',
            'left': '10%',
            'width': '80%',
            'text-align': 'center'
        })

    @app.callback(Output('title', 'children'), [Input('slider', 'value')])
    def update_title(date_range):
        text = f"近{date_range[1] - date_range[0] +1}天股價走勢"
        return text

    @app.callback(Output('line_plot', 'figure'),
                  [Input('checkbox', 'value'),
                   Input('slider', 'value')])
    def update_line_chart(contents, date_range):
        #        features = ['daily'] + [self.features[i] for i in contents]
        selected_features = [features[i] for i in contents]
        fig = go.Figure()
        x = df.date.iloc[date_range[0]:date_range[1] + 1]
        for col in selected_features:
            fig.add_trace(
                go.Scatter(x=x,
                           y=df[col].iloc[date_range[0]:date_range[1] +
                                          1].values.reshape(-1),
                           mode='lines',
                           name=col))
        fig.update_layout(title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
                          yaxis_title='$NTD')
        return fig

    @app.callback(Output('slider', 'marks'), [Input('slider', 'value')])
    def update_slider_mark(date_range):
        start = df.date.iloc[date_range[0]]
        end = df.date.iloc[date_range[1]]
        return {0: df.date[0], date_range[0]: start, date_range[1]: end}

    @app.callback(Output('bar_chart', 'figure'), [Input('slider', 'value')])
    def update_bar_chart(date_range):
        selected_data = df.iloc[date_range[0]:date_range[1] + 1]
        bull = selected_data[selected_data.daily > selected_data.open]
        bear = selected_data[selected_data.daily < selected_data.open]
        tie = selected_data[selected_data.daily == selected_data.open]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=bull.date,
                   y=bull.volume.values.reshape(-1) / 1e3,
                   marker_color='red',
                   name='漲'))
        fig.add_trace(
            go.Bar(x=bear.date,
                   y=bear.volume.values.reshape(-1) / 1e3,
                   marker_color='green',
                   name='跌'))
        fig.add_trace(
            go.Bar(x=tie.date,
                   y=tie.volume.values.reshape(-1) / 1e3,
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

    return app
