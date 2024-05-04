from datetime import date

from fastapi import FastAPI, HTTPException

from exception import (YFinanceDataFetchError)
from models import PortfolioUpdate, PortfolioResponse
from portfolio.analizer.port_analizer_own import calculate_portfolio_returns
from portfolio.analizer.port_analizer_qs import generate_report
from portfolio.data_procesing.f_yfinance import YFinanceDataFetcher
from portfolio.factory.port_factory import PortfolioOptimizerTest
from portfolio.factory.port_hc_factory import PortfolioOptimizer

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
        portfolio = Portfolio(assets, train_start, train_end, test_start, test_end)
        #
        portfolio.update_portfolio()
        #
        report = generate_report(portfolio.portfolio_daily_returns)
        return report

    except YFinanceDataFetchError as e:
        raise HTTPException(status_code=500, detail=f'Error fetching data: {str(e)}')


risk_level_global = None


@app.put("/portfolio/update/risk")
def update_portfolio_set_risk(risk_user: str):

    global risk_level_global
    # risk_level = 'Very Aggressive'
    risk_level = risk_user
    risk_level_global = risk_level
    print(risk_level_global)
    return {"risk_level_global": risk_level_global}


class Portfolio:

    def __init__(self, assets, train_start, train_end, test_start, test_end):
        self.assets = assets
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end
        self.portfolio_daily_returns = None
        self.portfolio_w = PortfolioOptimizerTest()

    def update_portfolio(self):
        try:
            training_data = YFinanceDataFetcher().get_training_data(self.assets, self.train_start, self.train_end)
            portfolio_w = PortfolioOptimizer().port_optimize(training_data)
            testing_data = YFinanceDataFetcher().get_testing_data(self.assets, self.test_start, self.test_end)
            portfolio_returns = calculate_portfolio_returns(testing_data, portfolio_w.T)
            self.portfolio_daily_returns = portfolio_returns['Daily Return']
        except Exception as e:
            raise e
        return {'Portfolio Updated': 'Successfully'}

    #test no implementado
    def update_portfolio_test(self):
        global risk_level_global
        risk_level = risk_level_global
        if risk_level is not None:
            try:
                training_data = YFinanceDataFetcher().get_training_data(self.assets, self.train_start, self.train_end)
                ##
                portfolio_w = self.portfolio_w
                print({'risk_level': risk_level})
                portfolio_w.risk_level = risk_level

                # portfolio_w.cvar_value = 0.8
                portfolio_w = portfolio_w.port_optimize(training_data)

                ##
                testing_data = YFinanceDataFetcher().get_testing_data(self.assets, self.test_start, self.test_end)
                portfolio_returns = calculate_portfolio_returns(testing_data, portfolio_w.T)
                self.portfolio_daily_returns = portfolio_returns['Daily Return']
            except Exception as e:
                raise e
        return {'Portfolio Updated': 'Successfully'}
