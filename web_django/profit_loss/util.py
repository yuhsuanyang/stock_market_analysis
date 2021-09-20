import dash
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output

from dashboard_utils.terms import terms
from dashboard_utils.common_functions import plot_table
from dashboard_utils.common_styles import layout_style, checklist_style, line_plot_style, table_style


def create_percentage_df(df):
    df_pr = pd.DataFrame(df['季'])
    df_pr['毛利率'] = (100 * df['毛利'] / df['營業收入']).round(2)

    df_pr['營業利益率'] = (100 * df['營業利益'] / df['營業收入']).round(2)
    df_pr['淨利率'] = (100 * df['稅後淨利'] / df['營業收入']).round(2)
    return df_pr


def create_dash(df):
    clicked_bttn_style = {
        'border-radius': 0,
        'border-color': 'white',
        'background-color': 'lightgray',
        'padding': '10px',
        'shadow': 0,
    }
    unclicked_bttn_style = {
        'border-radius': 0,
        'border-color': 'white',
        'background-color': 'white',
        'padding': '10px',
        'shadow': 0,
    }
    eps_plot_title = {
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'text': '每股盈餘'
    }

    app = DjangoDash('Profit_Loss_Dashboard')
    features = [col for col in df.columns if col != 'season']
    df1 = df.drop(columns='EPS')
    df1.columns = [terms[col] for col in df1.columns]
    df_eps = pd.DataFrame()
    df_eps[['year',
            'season']] = pd.DataFrame([s.split('_') for s in df['season']])
    df_eps['EPS'] = df['EPS']

    profit_loss_table = plot_table(df1)
    eps_one_line_plot = go.Figure()
    eps_one_line_plot.add_trace(
        go.Scatter(x=df['season'],
                   y=df['EPS'].values.reshape(-1),
                   mode='lines+markers'))
    eps_one_line_plot.update_layout(title=eps_plot_title, yaxis_title='$NTD')
    eps_one_line_plot.update_xaxes(tickangle=45)
    eps_four_line_plot = go.Figure()
    print(df_eps)
    for i in [4, 3, 2, 1]:
        eps_data = df_eps[df_eps.season == str(i)]
        print(eps_data)
        eps_four_line_plot.add_trace(
            go.Scatter(x=eps_data['year'],
                       y=eps_data['EPS'].values.reshape(-1),
                       mode='lines+markers',
                       name=f'第{i}季'))

    eps_four_line_plot.update_layout(title=eps_plot_title, yaxis_title='$NTD')

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
                      style=checklist_style),
        dcc.Graph(id='profit_loss_line_plot', style=line_plot_style),
        html.Div([profit_loss_table], style=table_style),
        html.Div([
            dcc.Graph(id='eps_figure',
                      figure=eps_one_line_plot,
                      style={
                          'width': '90%',
                          'left': '10%',
                          'height': '10%',
                          'text-align': 'center',
                      }),
            html.Div([
                html.Button(
                    '不分季', id='bttn1', n_clicks=0, style=clicked_bttn_style),
                html.Button(
                    '分季', id='bttn2', n_clicks=0, style=unclicked_bttn_style)
            ],
                     style={
                         'marginLeft': '10%',
                         'text-align': 'left',
                     })
        ])
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
        percentage_line_plot.update_xaxes(tickangle=45)
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

    app.layout = html.Div(div_children, style=layout_style)

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

        fig.update_xaxes(tickangle=45)
        return fig

    @app.callback(Output('bttn1', 'style'),
                  [Input('bttn1', 'n_clicks'),
                   Input('bttn2', 'n_clicks')])
    def change_bttn1_style(n_clicks1, n_clicks2):
        change = [p['prop_id'] for p in dash.callback_context.triggered]
        if 'bttn1.n_clicks' in change or n_clicks2 == 0:
            return clicked_bttn_style
        else:
            return unclicked_bttn_style

    @app.callback(Output('bttn2', 'style'),
                  [Input('bttn1', 'n_clicks'),
                   Input('bttn2', 'n_clicks')])
    def change_bttn2_style(n_clicks1, n_clicks2):
        change = [p['prop_id'] for p in dash.callback_context.triggered]
        if 'bttn2.n_clicks' in change:
            return clicked_bttn_style
        else:
            return unclicked_bttn_style

    @app.callback(Output('eps_figure', 'figure'),
                  [Input('bttn1', 'n_clicks'),
                   Input('bttn2', 'n_clicks')])
    def change_bttn1_style(n_clicks1, n_clicks2):
        change = [p['prop_id'] for p in dash.callback_context.triggered]
        if 'bttn1.n_clicks' in change or n_clicks2 == 0:
            return eps_one_line_plot
        else:
            return eps_four_line_plot
