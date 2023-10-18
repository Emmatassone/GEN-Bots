import pandas as pd


def calculate_portfolio_returns(daily_returns, weights):
    weighted_returns = daily_returns * weights.values
    portfolio_return = weighted_returns.sum(axis=1)
    cumulative_return = (1 + portfolio_return).cumprod() - 1
    df_returns = pd.DataFrame({
        'Daily Return': portfolio_return,
        'Cumulative Return': cumulative_return
    })
    return df_returns

#%%
