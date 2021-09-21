import dash_table
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output

from dashboard_utils.common_styles import line_plot_style


def create_price_sequence(model_table):
    df = []
    for row in model_table:
        df.append([row.date, row.Close])
    return pd.DataFrame(df, columns=['date', 'close'])


def create_df(stock_code, data):
    df = []
    this_year = data[stock_code]['eps'].season.split('_')[0]
    columns = [
        '股名', '產業類別', '最新收盤價', '收盤價相關係數', f'{this_year}年累計EPS', '每股參考淨值',
        f'{int(this_year)-1}年股利', '相似度'
    ]
    for code in data:
        one_data = data[code]
        #        print(one_data['dividend'])
        one_data['dividend'] = one_data['dividend'].filter(
            year=int(this_year) - 1)
        one_data['dividend'] = [d.cash + d.stock for d in one_data['dividend']]
        df.append([
            f"{one_data['basic'].code} {one_data['basic'].name}",
            one_data['basic'].industry_type, one_data['price'][0].Close,
            round(one_data['corr'],
                  2), one_data['eps'].EPS, one_data['pbr'].PBR,
            sum(one_data['dividend']),
            round(one_data['score'] / 4, 2)
        ])
    df = pd.DataFrame(df, columns=columns)
    return df


def plot_table(df):
    table = dash_table.DataTable(columns=[{
        'id': col,
        'name': col
    } for col in df.columns],
                                 data=df.to_dict('recores'),
                                 style_cell={
                                     'whiteSpace': 'normal',
                                     'height': 'auto',
                                     'text-align': 'left',
                                     'color': 'darkslategrey'
                                 },
                                 style_header={
                                     'fontWeight': 'bold',
                                     'text-align': 'center'
                                 })
    return table


def create_dash(stock_code, data):
    df = create_df(int(stock_code), data)
    table = plot_table(df)
    features = [code for code in data if code != int(stock_code)]
    checklist_style = {
        'width': '100%',
        'height': '30px',
        'text-align': 'center'
    }

    app = DjangoDash('Similarity_Dashboard')
    for code in data:
        data[code]['price'] = create_price_sequence(data[code]['price'])

    app.layout = html.Div(
        [
            html.H3(id='title',
                    children="近90天股價走勢",
                    style={'text-align': 'center'}),
            dcc.Graph(id='line_plot', style=line_plot_style),
            dcc.Checklist(
                id='checkbox1',
                options=[{
                    'label':
                    f"{features[i]} {data[features[i]]['basic'].name}  ",
                    'value': features[i]
                } for i in range(5)],
                value=[],
                style=checklist_style),
            dcc.Checklist(
                id='checkbox2',
                options=[{
                    'label':
                    f"{features[i]} {data[features[i]]['basic'].name}  ",
                    'value': features[i]
                } for i in range(5, 10)],
                value=[],
                style=checklist_style),
            html.Div([table], style={
                'marginTop': '50px',
            })
        ],
        style={
            'position': 'absolute',
            'left': '10%',
            'width': '80%',
            'text-align': 'center'
        })

    @app.callback(Output('line_plot', 'figure'),
                  [Input('checkbox1', 'value'),
                   Input('checkbox2', 'value')])
    def update_line_chart(content1, content2):
        selected_codes = content1 + content2
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data[int(stock_code)]['price']['date'],
                y=data[int(stock_code)]['price']['close'].values.reshape(-1),
                marker_color='black',
                mode='lines+markers',
                name=f"{stock_code} {data[int(stock_code)]['basic'].name}"))
        for code in selected_codes:
            fig.add_trace(
                go.Scatter(
                    x=data[int(code)]['price']['date'],
                    y=data[int(code)]['price']['close'].values.reshape(-1),
                    mode='lines+markers',
                    name=f"{code} {data[int(code)]['basic'].name}"))

        #for col in selected_features:
        fig.update_layout(title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
                          yaxis_title='$NTD',
                          showlegend=True)
        return fig

    return app
