import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as ff

from core.database import *
from core.forecast import *

import dash_table_experiments as dt

# Define database
db = Database(name='bdf')

# Define www app
app = dash.Dash()


def generate_table(df, max_rows=20):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )


def generate_html_table(df):
    table = go.Table(
        header=dict(
            values=list(df.columns),
            font=dict(size=10),
            line=dict(color='rgb(50, 50, 50)'),
            align='left',
            fill=dict(color='#d562be'),
        ),
        cells=dict(
            values=[df[k].tolist() for k in df.columns],
            line=dict(color='rgb(50, 50, 50)'),
            align='left',
            fill=dict(color='#f5f5fa')
        )
    )

    return table


def generate_pd_table(df):
    table = ff.create_table(df)

    return table


def generate_dt_table(df):
    return df.to_dict('records')


app.layout = html.Div([
    html.Div([
        html.H1('Commodity Chart'),
        dcc.Dropdown(
            id='commodity-dropdown',
            options=[
                {'label': 'Gold', 'value': 'gold'},
                {'label': 'Silver', 'value': 'silver'}
            ], value='gold'
        ),
        dcc.Graph(id='commodity-graph'),
    ], style={'width': '48%', 'float': 'left', 'display': 'inline-block'}),

    html.Div([
        html.H1('Data Table'),
        dt.DataTable(
            rows=[{}],
            sortable=True,
            selected_row_indices=[],
            id='commodity-table'
        )
    ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

    html.Div([
        html.H2('Method'),
        dcc.Dropdown(
            id='forecast-method',
            options=[
                {'label': 'Recurrent Neural Network (RNN)', 'value': 'rnn'}
            ],
            value='rnn'
        ),

        html.H2('Number of periods'),
        dcc.Slider(
            id='forecast-periods',
            min=1,
            max=30,
            step=1,
            marks={i: '{}'.format(i) for i in range(1, 31)},
            value=24,
        ),

        html.H2('Forecasting horizon'),
        dcc.Slider(
            id='forecast-horizon',
            min=1,
            max=7,
            step=1,
            marks={i: '{}'.format(i) for i in range(1, 31)},
            value=1,
        ),

        html.H2('Hidden layers'),
        dcc.Input(
            id='forecast-layers',
            placeholder='Enter number of layers...',
            type='number',
            value=100
        ),

        html.H2('Epochs'),
        dcc.Input(
            id='forecast-epochs',
            placeholder='Enter number of epochs...',
            type='number',
            value=1000
        ),

        html.H2('Learning rate'),
        dcc.Input(
            id='forecast-rate',
            placeholder='Toggle learning rate...',
            type='number',
            min=0,
            max=1,
            step=0.001,
            value=0.001
        )

    ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

    html.Div([
        html.H1('Forecast'),
        dcc.Graph(id='forecast-graph')
    ], style={'width': '48%', 'float': 'left', 'display': 'inline-block'})

])


@app.callback(
    Output('commodity-graph', 'figure'),
    [Input('commodity-dropdown', 'value')])
def update_graph(commodity_dropdown_value):
    data = db.get_commodity(commodity_dropdown_value)
    data.set_index('date', inplace=True)
    return {
        'data': [{
            'x': data.index,
            'y': data.price
        }]}


@app.callback(
    Output('commodity-table', 'rows'),
    [Input('commodity-dropdown', 'value')])
def update_table(commodity_dropdown_value):
    data = db.get_commodity(commodity_dropdown_value)
    data = data[[c for c in data.columns if c not in ['commodity']]]
    data.drop_duplicates(inplace=True)
    return generate_dt_table(data)


@app.callback(
    Output('forecast-graph', 'figure'),
    [
        Input('commodity-dropdown', 'value'),
        Input('forecast-method', 'value'),
        Input('forecast-periods', 'value'),
        Input('forecast-horizon', 'value'),
        Input('forecast-layers', 'value'),
        Input('forecast-epochs', 'value'),
        Input('forecast-rate', 'value')
    ])
def update_graph(
        commodity_dropdown_value,
        forecast_method_value,
        forecast_periods_value,
        forecast_horizon_value,
        forecast_layers_value,
        forecast_epochs_value,
        forecast_rate_value
):
    data = db.get_commodity(commodity_dropdown_value)
    data.set_index('date', inplace=True)

    # instantiate an object of Forecast class choosing Recurring Neural Network model
    forecast = Forecast(data['price'], method=forecast_method_value)

    # set parameters
    forecast.rnn(
        learning_rate=forecast_rate_value,
        hidden=forecast_layers_value,
        horizon=forecast_horizon_value,
        num_periods=forecast_periods_value,
        epochs=forecast_epochs_value
    )

    # fit model
    forecast.fit()

    # predict
    index = data.index[:forecast.num_periods]
    observed = forecast.Y_test
    predicted = forecast.predict()

    df_raw = pd.DataFrame(np.array([observed, predicted]).T, index=index, columns=['observed', 'predicted'])
    df_raw.reset_index(inplace=True)
    df = pd.melt(df_raw, id_vars=['date'], value_vars=['observed', 'predicted'])

    traces = []
    for var in df.variable.unique():
        df_by_variable = df[df['variable'] == var]
        traces.append(go.Scatter(
            x=df_by_variable['date'],
            y=df_by_variable['value'],
            # text=df_by_variable['variable'],
            mode='markers',
            opacity=0.8,
            marker={
                'size': 7,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=var
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'date', 'title': 'Date'},
            yaxis={'title': 'Commodity Price', 'range': [np.min(df_raw.predicted)-50, np.max(df_raw.predicted)+50]},
            # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 1, 'y': 1},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server()
