from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from data_preprocessing import wrangle

def create_dash_app(flask_app):
    app = Dash(__name__, server=flask_app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dbc.Row([dbc.Col([html.H2("Data Overview", style={'text-align': 'center'})], width=12)]),
        dbc.Row([
            dbc.Col([html.H6(id='duplicate-rows-text')], width=6, style={'text-align': 'left', 'margin-top': '20px'}),
            dbc.Col([html.H6("Number of Rows to Display:")], width=3,
                    style={'text-align': 'right', 'margin-top': '20px', 'padding-right': '10px'}),
            dbc.Col([dcc.Dropdown(id='num-rows-dropdown', options=[{'label': i, 'value': i} for i in range(20)],
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
                        dbc.Col([dcc.Dropdown(id='correlation-x-axis', style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                    dbc.Row([
                        dbc.Col([html.Label("Y-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='correlation-y-axis', style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Bar Chart"),
                    dcc.Dropdown(id='bar-chart-dropdown', multi=True),
                    dcc.Graph(id='bar-chart'),
                ], className='chart-container'),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Histogram"),
                    dcc.Dropdown(id='histogram-dropdown'),
                    html.Div(id='histogram-container'),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Box Plot"),
                    dcc.Dropdown(id='box-plot-x-dropdown'),
                    dcc.Dropdown(id='box-plot-y-dropdown'),
                    html.Div(id='box-plot-container'),
                ], className='chart-container'),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Line Chart"),
                    dcc.Dropdown(id='line-chart-x-dropdown'),
                    dcc.Dropdown(id='line-chart-y-dropdown'),
                    html.Div(id='line-chart-container'),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Pie Chart"),
                    dcc.Dropdown(id='pie-chart-dropdown'),
                    html.Div(id='pie-chart-container'),
                ], className='chart-container'),
            ], width=6),
        ]),
        dcc.Store(id='cleaned_data'),
        dcc.Store(id='filtered_data')
    ])

    @app.callback(
        [Output('correlation-x-axis', 'options'),
         Output('correlation-x-axis', 'value'),
         Output('correlation-y-axis', 'options'),
         Output('correlation-y-axis', 'value'),
         Output('bar-chart-dropdown', 'options'),
         Output('bar-chart-dropdown', 'value'),
         Output('histogram-dropdown', 'options'),
         Output('histogram-dropdown', 'value'),
         Output('box-plot-x-dropdown', 'options'),
         Output('box-plot-x-dropdown', 'value'),
         Output('box-plot-y-dropdown', 'options'),
         Output('box-plot-y-dropdown', 'value'),
         Output('line-chart-x-dropdown', 'options'),
         Output('line-chart-x-dropdown', 'value'),
         Output('line-chart-y-dropdown', 'options'),
         Output('line-chart-y-dropdown', 'value'),
         Output('pie-chart-dropdown', 'options'),
         Output('pie-chart-dropdown', 'value'),
         Output('duplicate-rows-text', 'children')],
        [Input('url', 'search')]
    )
    def update_dropdowns(search):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data, null_values, duplicate_rows = wrangle(file_path)
            columns = [{'label': col, 'value': col} for col in data.columns]
            return (columns, columns[0]['value'], columns, columns[1]['value'], columns, [columns[0]['value']],
                    columns, columns[0]['value'], columns, columns[0]['value'], columns, columns[1]['value'],
                    columns, columns[0]['value'], columns, columns[1]['value'], columns, columns[0]['value'],
                    f"Number of Duplicate Rows: {duplicate_rows}")
        else:
            return ([], None, [], None, [], [],
                    [], None, [], None, [], None,
                    [], None, [], None, [], None,
                    "")

    @app.callback(
        Output('data-overview', 'children'),
        [Input('url', 'search'), Input('num-rows-dropdown', 'value')])
    def update_data_overview(search, num_rows):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data, null_values, duplicate_rows = wrangle(file_path)
            return create_data_overview_table(data, num_rows)
        else:
            return []  # Return an empty table or a default message

    @app.callback(
        Output('correlation-graph', 'figure'),
        [Input('url', 'search'), Input('correlation-x-axis', 'value'), Input('correlation-y-axis', 'value')])
    def update_correlation_graph(search, x_axis, y_axis):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data, null_values, duplicate_rows = wrangle(file_path)
            return px.scatter(data, x=x_axis, y=y_axis, title='Correlation Graph')
        else:
            return {}  # Return an empty figure or a default message

    @app.callback(
        Output('bar-chart', 'figure'),
        [Input('url', 'search'), Input('bar-chart-dropdown', 'value')])
    def update_bar_chart(search, selected_columns):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data, null_values, duplicate_rows = wrangle(file_path)
            return px.bar(data[selected_columns])
        else:
            return {}  # Return an empty figure or a default message

    @app.callback(
        Output('histogram-container', 'children'),
        [Input('url', 'search'), Input('histogram-dropdown', 'value')])
    def update_histogram(search, x_col):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data, null_values, duplicate_rows = wrangle(file_path)
            return create_histogram(data, x_col, f'Histogram of {x_col}')
        else:
            return []  # Return an empty chart or a default message

    @app.callback(
        Output('box-plot-container', 'children'),
        [Input('url', 'search'), Input('box-plot-x-dropdown', 'value'), Input('box-plot-y-dropdown', 'value')])
    def update_box_plot(search, x_col, y_col):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data, null_values, duplicate_rows = wrangle(file_path)
            return create_box_plot(data, x_col, y_col, f'Box Plot of {y_col} by {x_col}')
        else:
            return []  # Return an empty chart or a default message

    @app.callback(
        Output('line-chart-container', 'children'),
        [Input('url', 'search'), Input('line-chart-x-dropdown', 'value'), Input('line-chart-y-dropdown', 'value')])
    def update_line_chart(search, x_col, y_col):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data, null_values, duplicate_rows = wrangle(file_path)
            return create_line_chart(data, x_col, y_col, f'Line Chart of {y_col} over {x_col}')
        else:
            return []  # Return an empty chart or a default message

    @app.callback(
        Output('pie-chart-container', 'children'),
        [Input('url', 'search'), Input('pie-chart-dropdown', 'value')])
    def update_pie_chart(search, feature_col):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data, null_values, duplicate_rows = wrangle(file_path)
            return create_pie_chart(data, feature_col, f'Distribution of {feature_col}')
        else:
            return []  # Return an empty chart or a default message

    return app

def create_data_overview_table(data, num_rows):
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in data.columns],
        data=data.head(num_rows).to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left'},
    )

def create_histogram(data, x_col, title):
    return dcc.Graph(
        figure=px.histogram(data, x=x_col, title=title)
    )

def create_box_plot(data, x_col, y_col, title):
    return dcc.Graph(
        figure=px.box(data, x=x_col, y=y_col, title=title)
    )

def create_line_chart(data, x_col, y_col, title):
    return dcc.Graph(
        figure=px.line(data, x=x_col, y=y_col, title=title)
    )

def create_pie_chart(data, feature_col, title):
    return dcc.Graph(
        figure=px.pie(data, names=feature_col, title=title)
    )
