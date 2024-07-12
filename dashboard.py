from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from flask_caching import Cache
from flask import session

# Initialize the Dash app with Flask server
dash_app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Cache initialization
cache = Cache(dash_app.server, config={'CACHE_TYPE': 'simple'})


# Default layout
def serve_layout():
    data = session.get('data', None)
    if data is None:
        return html.Div([html.H1("No data available")])

    df = pd.DataFrame(data)
    return html.Div([
        dbc.Row([dbc.Col([html.H2("Data Overview", style={'text-align': 'center'})], width=12)]),
        dbc.Row([
            dbc.Col([html.H6("Number of Rows to Display:")], width=3,
                    style={'text-align': 'right', 'margin-top': '20px', 'padding-right': '10px'}),
            dbc.Col([dcc.Dropdown(id='num-rows-dropdown', options=[{'label': i, 'value': i} for i in list(range(20))],
                                  value=4, style={'width': '200px'})], width=3,
                    style={'margin-top': '20px', 'padding-left': '10px'}),
        ]),
        dbc.Row([dbc.Col([html.Div(id='data-overview')], width=12)]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Correlation Graph"),
                    dcc.Graph(id='correlation-graph'),
                    dbc.Row([
                        dbc.Col([html.Label("X-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='correlation-x-axis',
                                              options=[{'label': col, 'value': col} for col in df.columns],
                                              value=df.columns[0], style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                    dbc.Row([
                        dbc.Col([html.Label("Y-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='correlation-y-axis',
                                              options=[{'label': col, 'value': col} for col in df.columns],
                                              value=df.columns[1], style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Bar Chart"),
                    dcc.Dropdown(id='bar-chart-dropdown',
                                 options=[{'label': col, 'value': col} for col in df.columns], value=df.columns[0],
                                 multi=True),
                    dcc.Graph(id='bar-chart'),
                ], className='chart-container'),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Histogram"),
                    dcc.Dropdown(id='histogram-dropdown',
                                 options=[{'label': col, 'value': col} for col in df.columns], value=df.columns[0]),
                    html.Div(id='histogram-container'),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Box Plot"),
                    dcc.Dropdown(id='box-plot-x-dropdown',
                                 options=[{'label': col, 'value': col} for col in df.columns], value=df.columns[0]),
                    dcc.Dropdown(id='box-plot-y-dropdown',
                                 options=[{'label': col, 'value': col} for col in df.columns], value=df.columns[1]),
                    html.Div(id='box-plot-container'),
                ], className='chart-container'),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Line Chart"),
                    dcc.Dropdown(id='line-chart-x-dropdown',
                                 options=[{'label': col, 'value': col} for col in df.columns], value=df.columns[0]),
                    dcc.Dropdown(id='line-chart-y-dropdown',
                                 options=[{'label': col, 'value': col} for col in df.columns], value=df.columns[1]),
                    html.Div(id='line-chart-container'),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Pie Chart"),
                    dcc.Dropdown(id='pie-chart-dropdown',
                                 options=[{'label': col, 'value': col} for col in df.columns], value=df.columns[0]),
                    html.Div(id='pie-chart-container'),
                ], className='chart-container'),
            ], width=6),
        ]),
        dcc.Store(id='cleaned_data', data=df.to_dict('records')),
        dcc.Store(id='filtered_data')
    ])


dash_app.layout = serve_layout


def create_data_overview_table(data, num_rows, null_values, duplicate_rows):
    if data.empty:
        return dbc.Row([dbc.Col(html.Div("No data available"), width=12)])

    summary_stats = data.describe().reset_index().round(4)
    first_observations = data.head(num_rows).round(4)

    def create_table(data, style_table, style_cell):
        return dash_table.DataTable(
            id='data-table',
            columns=[{"name": i, "id": i} for i in data.columns],
            data=data.to_dict('records'),
            style_table=style_table,
            style_cell=style_cell,
            sort_action="native",
            page_action="native",
            page_current=0,
            page_size=10,
            export_format='csv',
            export_headers='display',
            merge_duplicate_headers=True
        )

    summary_stats_table = create_table(summary_stats, {'overflowX': 'auto', 'margin-bottom': '20px'}, {
        'height': 'auto', 'minWidth': '100px', 'width': '100px', 'maxWidth': '180px', 'whiteSpace': 'normal'
    })

    first_observations_table = create_table(first_observations, {'overflowX': 'auto', 'margin-top': '20px'}, {
        'height': 'auto', 'minWidth': '100px', 'width': '100px', 'maxWidth': '180px', 'whiteSpace': 'normal'
    })

    null_values_table = dbc.Table.from_dataframe(pd.DataFrame.from_dict(null_values, orient='index'), striped=True,
                                                 bordered=True, hover=True)

    return dbc.Row([
        dbc.Row([
            dbc.Col([html.H4("Summary Statistics"), summary_stats_table], width=4),
            dbc.Col([html.H4("Data observations"), first_observations_table], width=4),
            dbc.Col([html.H4("Null Values"), null_values_table], width=4)
        ]),
        dbc.Row([
            dbc.Col([html.H6(f"Number of Duplicate Rows: {duplicate_rows}")], width=12,
                    style={'text-align': 'left', 'margin-top': '20px'})
        ])
    ])


def create_histogram(data, x_col, title):
    fig = px.histogram(data, x=x_col, title=title)
    fig.update_layout(bargap=0.1)
    return dcc.Graph(figure=fig)


def create_box_plot(data, x_col, y_col, title):
    fig = px.box(data, x=x_col, y=y_col, title=title)
    return dcc.Graph(figure=fig)


def create_bar_chart(data, columns, title):
    data_melt = data.melt(id_vars=columns[0], value_vars=columns[1:])
    fig = px.bar(data_melt, x=columns[0], y='value', color='variable', barmode='group', title=title)
    return dcc.Graph(figure=fig)


def create_correlation_plot(data, x_col, y_col, title):
    fig = px.scatter(data, x=x_col, y=y_col, trendline="ols", title=title)
    return dcc.Graph(figure=fig)


def create_line_chart(data, x_col, y_col, title):
    fig = px.line(data, x=x_col, y=y_col, title=title)
    return dcc.Graph(figure=fig)


def create_pie_chart(data, feature_col, title):
    fig = px.pie(data, names=feature_col, title=title)
    return dcc.Graph(figure=fig)


@dash_app.callback(
    Output('data-overview', 'children'),
    [Input('num-rows-dropdown', 'value')],
    [State('cleaned_data', 'data')]
)
@cache.memoize()
def update_data_overview(num_rows, data):
    df = pd.DataFrame(data)
    null_values = df.isnull().sum().to_dict()
    duplicate_rows = df.duplicated().sum()
    return create_data_overview_table(df, num_rows, null_values, duplicate_rows)


@dash_app.callback(
    Output('correlation-graph', 'figure'),
    [Input('correlation-x-axis', 'value'), Input('correlation-y-axis', 'value')],
    [State('cleaned_data', 'data')]
)
def update_correlation_graph(x_col, y_col, data):
    df = pd.DataFrame(data)
    if x_col is None or y_col is None:
        return {}
    return create_correlation_plot(df, x_col, y_col, f"Correlation between {x_col} and {y_col}")


@dash_app.callback(
    Output('bar-chart', 'figure'),
    [Input('bar-chart-dropdown', 'value')],
    [State('cleaned_data', 'data')]
)
def update_bar_chart(selected_columns, data):
    df = pd.DataFrame(data)
    if not selected_columns or len(selected_columns) < 2:
        return {}
    return create_bar_chart(df, selected_columns, f"Bar Chart for {selected_columns}")


@dash_app.callback(
    Output('histogram-container', 'children'),
    [Input('histogram-dropdown', 'value')],
    [State('cleaned_data', 'data')]
)
def update_histogram(selected_column, data):
    df = pd.DataFrame(data)
    if selected_column is None:
        return {}
    return create_histogram(df, selected_column, f"Histogram of {selected_column}")


@dash_app.callback(
    Output('box-plot-container', 'children'),
    [Input('box-plot-x-dropdown', 'value'), Input('box-plot-y-dropdown', 'value')],
    [State('cleaned_data', 'data')]
)
def update_box_plot(x_col, y_col, data):
    df = pd.DataFrame(data)
    if x_col is None or y_col is None:
        return {}
    return create_box_plot(df, x_col, y_col, f"Box Plot of {y_col} by {x_col}")


@dash_app.callback(
    Output('line-chart-container', 'children'),
    [Input('line-chart-x-dropdown', 'value'), Input('line-chart-y-dropdown', 'value')],
    [State('cleaned_data', 'data')]
)
def update_line_chart(x_col, y_col, data):
    df = pd.DataFrame(data)
    if x_col is None or y_col is None:
        return {}
    return create_line_chart(df, x_col, y_col, f"Line Chart of {y_col} over {x_col}")


@dash_app.callback(
    Output('pie-chart-container', 'children'),
    [Input('pie-chart-dropdown', 'value')],
    [State('cleaned_data', 'data')]
)
def update_pie_chart(feature_col, data):
    df = pd.DataFrame(data)
    if feature_col is None:
        return {}
    return create_pie_chart(df, feature_col, f"Pie Chart of {feature_col}")


if __name__ == '__main__':
    dash_app.run_server()
