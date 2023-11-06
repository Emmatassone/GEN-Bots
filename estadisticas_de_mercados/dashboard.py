import dash

from dash import dcc
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("My Dash Dashboard"),
    dcc.Graph(
        figure={
            'data': [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Trace 1'}],
            'layout': {'title': 'Sample Bar Chart'}
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
