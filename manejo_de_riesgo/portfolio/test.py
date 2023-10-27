import unittest
from datetime import date
from data_procesing.f_yfinance import YFinanceDataFetcher
from analizer.port_analizer_own import calculate_portfolio_returns
from analizer.port_analizer_qs import generate_report
from factory.port_factory import PortfolioOptimizerTest
import pandas as pd


class TestPortfolioOptimization(unittest.TestCase):
    def setUp(self):
        self.assets = ['JPM', 'MSFT', 'BA', 'KO', 'AAPL', 'TSLA', 'AMZN', 'NVDA']
        self.train_start = '2019-01-01'
        self.train_end = '2022-12-30'
        self.test_start = '2022-12-30'
        self.test_end = str(date.today())

    def test_optimize_portfolio_risk(self):
        portfolio_w = PortfolioOptimizerTest()
        portfolio_w.risk_level = 'Moderate'
        portfolio_w.cvar_value = 0.8
        training_data = YFinanceDataFetcher().get_training_data(self.assets, self.train_start, self.train_end)
        portfolio_w = portfolio_w.port_optimize(training_data)
        self.assertIsInstance(portfolio_w, pd.DataFrame)

    def test_optimize_portfolio_hrp(self):
        portfolio_w = PortfolioOptimizerTest()
        portfolio_w.hrp = True
        training_data = YFinanceDataFetcher().get_training_data(self.assets, self.train_start, self.train_end)
        portfolio_w = portfolio_w.port_optimize(training_data)
        self.assertIsInstance(portfolio_w, pd.DataFrame)


if __name__ == '__main__':
    unittest.main()

#%%
