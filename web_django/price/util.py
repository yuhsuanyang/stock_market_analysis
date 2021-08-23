import time
import yfinance as yf
from datetime import datetime

import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output


def query_historical_price(stock_code, end_date):
    end = datetime.strptime(end_date, '%Y-%m-%d')
    end = int(time.mktime(time.strptime(end_date, '%Y-%m-%d'))) + 86400
    start = end - 86400 * 365 * 5
    print('stock_code:', stock_code)
    start_date = time.strftime('%Y-%m-%d', time.localtime(start))
    data = yf.download(f"{stock_code}.TW", start=start_date, end=end_date)[[
        'Open', 'High', 'Low', 'Close', 'Volume'
    ]]
    data['Date'] = data.index.astype(str)
    data = data.reset_index(drop=True)
    data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    data.columns = ['date', 'open', 'high', 'low', 'daily', 'volume']
    data['5MA'] = data.daily.rolling(5).mean()
    data['20MA'] = data.daily.rolling(20).mean()
    data['60MA'] = data.daily.rolling(60).mean()
    return data


def create_dash(stock_code, company_name, price_df, institutional_df):
    features = ['daily', '5MA', '20MA', '60MA', 'k線']
    slider_style = {'margin-right': '-100px'}
    app = DjangoDash('Price_Dashboard')
    bar_chart2 = make_subplots(rows=4,
                               cols=1,
                               subplot_titles=('', '外資', '投信', '自營商'),
                               shared_xaxes=True)
    bar_chart2.append_trace(go.Scatter(
        x=institutional_df['date'],
        y=(institutional_df['foreign'] + institutional_df['invest'] +
           institutional_df['dealer']).values / 1000,
        mode='lines+markers'),
                            row=1,
                            col=1)
    bar_chart2.append_trace(go.Bar(x=institutional_df['date'],
                                   y=(institutional_df['foreign'] /
                                      1000).values),
                            row=2,
                            col=1)
    bar_chart2.append_trace(go.Bar(x=institutional_df['date'],
                                   y=(institutional_df['invest'] /
                                      1000).values),
                            row=3,
                            col=1)
    bar_chart2.append_trace(go.Bar(x=institutional_df['date'],
                                   y=(institutional_df['dealer'] /
                                      1000).values),
                            row=4,
                            col=1)
    bar_chart2.update_yaxes(title='成交量（千股）')
    bar_chart2.update_layout(showlegend=False)
    app.layout = html.Div(
        [
            html.H3(id='title',
                    children="近90天股價走勢",
                    style={'text-align': 'center'}),
            dcc.Checklist(
                id='checkbox',
                options=[{
                    'label': features[i],
                    'value': i
                } for i in range(len(features))],
                value=[i for i in range(len(features) - 1)],  # 預設沒有k線
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
                            max=len(price_df) - 1,
                            value=[len(price_df) - 90,
                                   len(price_df) - 1],
                            step=1,
                            marks={
                                0: {
                                    'label': price_df.date[0],
                                    'style': slider_style
                                },
                                len(price_df) - 90: {
                                    'label': price_df.date.iloc[-90],
                                    'style': {
                                        'margin-top': '-40px',
                                        'margin-right': '-100px'
                                    }
                                },
                                len(price_df) - 1: {
                                    'label': price_df.date.iloc[-1],
                                    'style': slider_style
                                }
                            }),
            html.H3(children="近90天三大法人買賣超",
                    style={
                        'text-align': 'center',
                        'margin-top': '20%'
                    }),
            dcc.Graph(figure=bar_chart2,
                      style={
                          'width': '110%',
                          'height': '800px',
                          'text-align': 'center'
                      }),
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
        selected_features = [features[i] for i in contents]
        line_colors = ['dimgray', 'dodgerblue', 'violet', 'orange']
        fig = go.Figure()
        selected_data = price_df.iloc[date_range[0]:date_range[1] + 1]
        x = selected_data.date
        #for col in selected_features:
        for i in contents:
            col = features[i]
            if col == "k線":
                fig.add_trace(
                    go.Candlestick(x=x,
                                   open=selected_data['open'],
                                   high=selected_data['high'],
                                   low=selected_data['low'],
                                   close=selected_data['daily'],
                                   name="k線",
                                   increasing_line_color='red',
                                   decreasing_line_color='green'))

            else:
                fig.add_trace(
                    go.Scatter(x=x,
                               y=selected_data[col],
                               mode='lines',
                               name=col,
                               marker_color=line_colors[i]))
        fig.update_layout(title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
                          yaxis_title='$NTD',
                          xaxis_rangeslider_visible=False)
        return fig

    @app.callback(Output('slider', 'marks'), [Input('slider', 'value')])
    def update_slider_mark(date_range):
        start = price_df.date.iloc[date_range[0]]
        end = price_df.date.iloc[date_range[1]]
        return {
            0: {
                'label': price_df.date[0],
                'style': slider_style
            },
            date_range[0]: {
                'label': start,
                'style': {
                    'margin-top': '-40px',
                    'margin-right': '-100px'
                }
            },
            date_range[1]: {
                'label': end,
                'style': slider_style
            }
        }

    @app.callback(Output('bar_chart', 'figure'), [Input('slider', 'value')])
    def update_bar_chart(date_range):
        selected_data = price_df.iloc[date_range[0]:date_range[1] + 1]
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
