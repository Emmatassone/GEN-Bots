from datetime import date
from typing import List

from portfolio.data_procesing.f_yfinance import YFinanceDataFetcher
from portfolio.factory.port_hc_factory import PortfolioOptimizer
from portfolio.analizer.port_analizer_own import calculate_portfolio_returns
from portfolio.analizer.port_analizer_qs import generate_report
from models import PortfolioUpdate, PortfolioResponse, PortfolioItem
from fastapi import FastAPI, HTTPException
from exception import (YFinanceDataFetchError, PortfolioOptimizationError, TestingDataFetchError,
                       PortfolioReturnsCalculationError)

app = FastAPI()


@app.get("/")
def read_root():
    return 'Welcome to the portfolio API!'


# hola
@app.put("/portfolio/update", response_model=PortfolioResponse)
def update_portfolio(update_data: PortfolioUpdate):
    assets = update_data.assets
    train_start = update_data.train_start
    train_end = update_data.train_end
    test_start = update_data.test_start
    test_end = str(date.today())

    try:
        stock = Portfolio(assets, train_start, train_end, test_start, test_end).update_portfolio()
        report = generate_report(stock)
        return report

    except YFinanceDataFetchError as e:
        raise HTTPException(status_code=500, detail=f'Error fetching data: {str(e)}')


class Portfolio:
    def __init__(self, assets, train_start, train_end, test_start, test_end):
        self.assets = assets
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end

    def update_portfolio(self):
        try:
            training_data = YFinanceDataFetcher().get_training_data(self.assets, self.train_start, self.train_end)
            portfolio_w = PortfolioOptimizer().port_optimize(training_data)
            testing_data = YFinanceDataFetcher().get_testing_data(self.assets, self.test_start, self.test_end)
            portfolio_returns = calculate_portfolio_returns(testing_data, portfolio_w.T)
            return portfolio_returns['Daily Return']
        except YFinanceDataFetchError as yfinance_error:
            return f'Error fetching financial data: {str(yfinance_error)}'
        except PortfolioOptimizationError as optimization_error:
            return f'Error in portfolio optimization: {str(optimization_error)}'
        except TestingDataFetchError as testing_error:
            return f'Error fetching testing data: {str(testing_error)}'
        except PortfolioReturnsCalculationError as returns_error:
            return f'Error calculating portfolio returns: {str(returns_error)}'
        except Exception as other_error:
            return f'Unexpected error: {str(other_error)}'
