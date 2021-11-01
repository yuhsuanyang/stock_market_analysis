import yfinance as yf
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html

from datetime import datetime
from dateutil.relativedelta import relativedelta

from plotly.subplots import make_subplots
from django_plotly_dash import DjangoDash
from dashboard_utils.common_styles import layout_style
from dashboard_utils.common_functions import plot_table


def query_month_avg_price(stock_code, start_month, end_month):
    start_date = datetime.strptime(start_month, '%Y-%m')
    end_date = datetime.strptime(end_month, '%Y-%m') + relativedelta(months=1)
    start_date = datetime.strftime(start_date, '%Y-%m-%d')
    end_date = datetime.strftime(end_date, '%Y-%m-%d')
    data = yf.download(f"{stock_code}.TW", start=start_date,
                       end=end_date)[['Close']]
    #    print(data)
    data['Month'] = [str(date)[0:7] for date in data.index]
    return data.groupby(['Month']).mean()


def create_dash(data):
    app = DjangoDash('MonthlyRevenue_Dashboard')
    stock_code = data['公司代碼'].values[0]
    df = data.drop(columns=['公司代碼'])
    data['年月'] = df['年'].astype(str) + '_' + df['月'].astype(str)
    years = sorted(data['年'].unique())
    start_month = f"{data['年'].iloc[0] + 1911}-{data['月'].iloc[0]}"
    end_month = f"{data['年'].iloc[-1] + 1911}-{data['月'].iloc[-1]}"
    month_avg_price = query_month_avg_price(stock_code, start_month, end_month)
    table = plot_table(df)

    fig_bar = make_subplots(specs=[[{"secondary_y": True}]])
    fig_bar.add_trace(
        go.Bar(x=data['年月'], y=data['當月營收'].values, name='月營收', opacity=0.5))
    fig_bar.add_trace(go.Scatter(x=data['年月'],
                                 y=month_avg_price['Close'].values,
                                 name='月均收盤價'),
                      secondary_y=True)

    fig_bar.update_layout(
        xaxis={
            'tickmode': 'array',
            'tickvals': [i * 12 for i in range(len(years))],
            'ticktext': [f"{year}_1" for year in years]
        })
    app.layout = html.Div([
        html.H3(children='月營收表', style={'text_align': 'center'}),
        dcc.Graph(id='bar_chart',
                  figure=fig_bar,
                  style={
                      'marginLeft': '5%',
                      'width': '90%',
                      'text-align': 'center'
                  }),
        html.Div(
            [html.P(children='單位: 千元', style={'marginLeft': '90%'}), table],
            style={
                'marginRight': '10%',
                'marginLeft': '10%',
                'width': '80%',
            }),
    ],
                          style=layout_style)
