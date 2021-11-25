import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
from plotly.subplots import make_subplots


def create_dash(chip_data, institutional_df, price_df):
    pie_chart_color = [
        'cornflowerblue', 'lightcoral', 'mediumaquamarine', 'mediumpurple',
        'gold', 'lightsteelblue', 'sandybrown'
    ]
    fig_pie = go.Figure(data=[
        go.Pie(labels=['董監', '外資', '投信', '自營商', '融資', '融券', '其他'],
               values=chip_data['amount'],
               marker_colors=pie_chart_color)
        #textinfo='label+percent')
    ])
    fig_pie.update_layout(margin=dict(t=10, b=0, l=0, r=0), font=dict(size=14))
    institutional_investors = {
        'foreign': '外資',
        'invest': '投信',
        'dealer': '自營商'
    }
    fig_bar_with_line = make_subplots(specs=[[{'secondary_y': True}]])
    for col in institutional_investors:
        fig_bar_with_line.add_trace(
            go.Bar(x=institutional_df['date'],
                   y=institutional_df[col],
                   name=institutional_investors[col]))
    fig_bar_with_line.update_layout(barmode='stack', yaxis={'title': "成交量"})
    #   fig_bar_with_line.add_trace(fig_bar)
    fig_bar_with_line.add_trace(go.Scatter(x=institutional_df['date'],
                                           y=price_df['close'],
                                           name='收盤價',
                                           mode='lines+markers',
                                           marker_color='gray'),
                                secondary_y=True)

    app = DjangoDash('Chip_Dashboard')
    app.layout = html.Div([
        html.H3(children="籌碼分布", style={'text-align': 'center'}),
        dcc.Graph(id='pie_chart',
                  figure=fig_pie,
                  style={
                      'width': '90%',
                      'text-align': 'center',
                      'marginTop': '5%',
                      'marginBottom': '15%',
                      'marginLeft': '5%'
                  },
                  config={'displayModeBar': False}),
        html.H3(children="近90天三大法人買賣超", style={'text-align': 'center'}),
        dcc.Graph(id='fig_bar',
                  figure=fig_bar_with_line,
                  style={
                      'width': '90%',
                      'marginLeft': '5%'
                  })
    ])
