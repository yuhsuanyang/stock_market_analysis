import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output

from dashboard_utils.terms import terms
from dashboard_utils.common_functions import plot_table


def create_dash(df):
    app = DjangoDash('Asset_Debt_Dashboard')
    pbr = '每股參考淨值'
    share_capital = '股本'
    df1 = df.drop(columns=['PBR', 'share_capital'])
    df1.columns = [terms[col] for col in df1.columns]
    asset_debt_table = plot_table(df1)
    #    features = [col for col in df1.columns if col != '季']
    one_line_plot = make_subplots(rows=3,
                                  cols=1,
                                  subplot_titles=('負債比率', pbr, share_capital),
                                  shared_xaxes=True)
    one_line_plot.append_trace(go.Scatter(
        x=df['season'],
        y=100 * (df['total_debt'] / df['total_assets']).values.reshape(-1),
        mode='lines+markers'),
                               row=1,
                               col=1)
    one_line_plot.append_trace(go.Scatter(x=df['season'],
                                          y=df['PBR'].values.reshape(-1),
                                          mode='lines+markers'),
                               row=2,
                               col=1)
    one_line_plot.append_trace(go.Scatter(x=df['season'],
                                          y=(df['share_capital'] /
                                             1e4).values.reshape(-1),
                                          mode='lines+markers'),
                               row=3,
                               col=1)
    one_line_plot.update_yaxes(title_text='%', row=1, col=1)
    one_line_plot.update_yaxes(title_text='$NTD', row=2, col=1)
    one_line_plot.update_yaxes(title_text='$NTD 萬', row=3, col=1)
    one_line_plot.update_layout(showlegend=False)

    div_children = [
        html.H3(children='近年資產負債表', style={'text_align': 'center'}),
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
        dcc.Graph(id='asset_debt_line_plot',
                  style={
                      'width': '100%',
                      'height': '80%',
                      'left': '10%',
                      'text-align': 'center'
                  }),
        html.Div(
            [asset_debt_table],
            style={
                'width': '100%',
                'text-align': 'center',
                'marginTop': '50px',
                'marginBottom': '50px'
            }),
        dcc.Graph(figure=one_line_plot,
                  style={
                      'width': '900px',
                      'left': '10%',
                      'height': '10%',
                      'text-align': 'center'
                  })
    ]
    app.layout = html.Div(div_children,
                          style={
                              'position': 'absolute',
                              'left': '5%',
                              'width': '90%',
                              'text-align': 'center'
                          })

    @app.callback(Output('asset_debt_line_plot', 'figure'),
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
            'yanchor': 'top',
        },
                          yaxis_title='$NTD 萬')
        fig.update_xaxes(tickangle=45)
        return fig
