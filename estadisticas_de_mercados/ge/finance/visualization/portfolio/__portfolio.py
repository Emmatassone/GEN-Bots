import ge.finance.concept as concept
import pandas as pd
import plotly.graph_objects as go


def assets_to_equity(
        data: pd.DataFrame,
        ticker_symbol: concept.Key,
        datetime_format: str = '%b %Y',
) -> go.Figure:
    # Filter for the rows for the specific symbol.
    company_rows = data[data[concept.TICKER_SYMBOL] == ticker_symbol]
    company_rows = company_rows.sort_values(by=concept.PERIOD_START, ascending=True)
    # Extract the data that we need.
    t = company_rows[concept.PERIOD_START].dt.strftime(datetime_format)
    a = company_rows[concept.TOTAL_ASSETS]
    e = company_rows[concept.STOCKHOLDER_EQUITY]
    # Generate bar graph.
    fig = go.Figure(data=[
        go.Bar(x=t, y=a, name='Assets', hoverinfo='name+y'),
        go.Bar(x=t, y=e, name='Equity', hoverinfo='name+y'),
    ])
    fig.update_xaxes(type='category')
    fig.update_layout(
        title='{}: Assets to Equity'.format(ticker_symbol),
        xaxis_title='Period Start',
        yaxis_title='Balance',
        barmode='group',
    )
    return fig
