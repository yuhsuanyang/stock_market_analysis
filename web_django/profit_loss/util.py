import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output

from dashboard_utils.terms import terms
from dashboard_utils.common_functions import plot_table


def create_percentage_df(df):
    df_pr = pd.DataFrame(df['季'])
    df_pr['毛利率'] = (100 * df['毛利'] / df['營業收入']).round(2)

    df_pr['營業利益率'] = (100 * df['營業利益'] / df['營業收入']).round(2)
    df_pr['淨利率'] = (100 * df['稅後淨利'] / df['營業收入']).round(2)
    return df_pr


def create_dash(df):
    app = DjangoDash('Profit_Loss_Dashboard')
    features = [col for col in df.columns if col != 'season']
    df1 = df.drop(columns='EPS')
    df1.columns = [terms[col] for col in df1.columns]
    profit_loss_table = plot_table(df1)
    eps_line_plot = go.Figure()
    eps_line_plot.add_trace(
        go.Scatter(x=df['season'],
                   y=df['EPS'].values.reshape(-1),
                   mode='lines+markers'))
    eps_line_plot.update_layout(title={
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'text': '每股盈餘'
    },
                                yaxis_title='$NTD')
    div_children = [
        html.H3(children='近年損益表', style={'text-align': 'center'}),
        dcc.Checklist(id='checkbox',
                      options=[{
                          'label': df1.columns[i],
                          'value': i
                      } for i in range(len(df1.columns))
                               if df1.columns[i] != '季'],
                      value=[
                          i for i in range(len(df1.columns))
                          if df1.columns[i] != '季'
                      ],
                      style={
                          'width': '100%',
                          'height': '20px',
                          'text-align': 'center'
                      }),
        dcc.Graph(id='profit_loss_line_plot',
                  style={
                      'width': '100%',
                      'height': '80%',
                      'left': '10%',
                      'text-align': 'center'
                  }),
        html.Div(
            [profit_loss_table],
            style={
                'width': '100%',
                'text-align': 'center',
                'marginTop': '50px',
                'marginBottom': '50px'
            }),
        dcc.Graph(figure=eps_line_plot,
                  style={
                      'width': '90%',
                      'left': '10%',
                      'height': '10%',
                      'text-align': 'center'
                  })
    ]

    if 'gross' in features:
        df_pr = create_percentage_df(df1)
        percentage_table = plot_table(df_pr)
        percentage_line_plot = go.Figure()
        for col in df_pr.columns:
            if col != '季':
                percentage_line_plot.add_trace(
                    go.Scatter(x=df_pr['季'],
                               y=df_pr[col].values.reshape(-1),
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
                          'width': '100%',
                          'height': '10%',
                          'left': '10%',
                          'text-align': 'center'
                      }),
            html.Div(
                [percentage_table],
                style={
                    'position': 'absolute',
                    'width': '60%',
                    'left': '10%',
                    'text-align': 'center',
                    'marginTop': '50px',
                    'marginBottom': '50px',
                })
        ]
    else:
        div_children.append(
            html.H3('此類股沒有毛利', style={
                'text-align': 'center',
            }))

    app.layout = html.Div(div_children,
                          style={
                              'position': 'absolute',
                              'left': '5%',
                              'width': '90%',
                              'text-align': 'center'
                          })

    @app.callback(Output('profit_loss_line_plot', 'figure'),
                  [Input('checkbox', 'value')])
    def update_line_chart(contents):
        features = [df1.columns[i] for i in contents]
        fig = go.Figure()

        for col in features:
            fig.add_trace(
                go.Scatter(x=df1['季'],
                           y=df1[col].values.reshape(-1) / 1e4,
                           mode='lines+markers',
                           name=col))

        fig.update_layout(title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
                          yaxis_title='$NTD 萬')
        return fig
