import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output

from dashboard_utils.terms import terms
from dashboard_utils.common_functions import plot_table
from dashboard_utils.common_styles import checklist_style, line_plot_style, table_style, layout_style


def create_dash(df):
    app = DjangoDash('Cashflow_Dashboard')
    df.columns = [terms[col] for col in df.columns]
    df['自由現金流'] = df['營運淨現金流'] + df['資本支出']
    df['淨現金流'] = df['營運淨現金流'] + df['籌資淨現金流'] + df['投資淨現金流']
    cashflow_table = plot_table(df)
    app.layout = html.Div([
        html.H3(children='近年現金流量表', style={'text-align': 'center'}),
        dcc.Checklist(id='checkbox',
                      options=[{
                          'label': df.columns[i],
                          'value': i
                      } for i in range(len(df.columns))
                               if df.columns[i] != '季'],
                      value=[
                          i for i in range(len(df.columns))
                          if df.columns[i] not in ['季', '資本支出', '營運現金流']
                      ],
                      style=checklist_style),
        dcc.Graph(id='line_plot', style=line_plot_style),
        html.Div([cashflow_table], style=table_style),
    ],
                          style=layout_style)

    @app.callback(Output('line_plot', 'figure'), [Input('checkbox', 'value')])
    def update_line_chart(contents):
        features = [df.columns[i] for i in contents]
        fig = go.Figure()

        for col in features:
            if col in ['自由現金流', '淨現金流']:
                line_type = 'dash'
            else:
                line_type = 'solid'
            fig.add_trace(
                go.Scatter(x=df['季'],
                           y=df[col].values.reshape(-1) / 1e4,
                           line=dict(dash=line_type),
                           mode='lines+markers',
                           name=col))

        fig.update_layout(title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'text': '近年現金流量表'
        },
                          yaxis_title='$NTD 萬')

        fig.update_xaxes(tickangle=45)
        return fig
