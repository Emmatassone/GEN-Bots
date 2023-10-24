from datetime import date
from data_procesing.f_yfinance import YFinanceDataFetcher
from factory.port_hc_factory import PortfolioOptimizer
from analizer.port_analizer_own import calculate_portfolio_returns
from analizer.port_analizer_qs import generate_report
from factory.port_factory import PortfolioOptimizerTest

assets = ['JPM', 'MSFT', 'BA', 'KO', 'AAPL', 'TSLA', 'AMZN', 'NVDA']
train_start = '2019-01-01'
train_end = '2022-12-30'
test_start = '2022-12-30'
test_end = str(date.today())

portfolio_w = PortfolioOptimizer().port_optimize(YFinanceDataFetcher()
                                                 .get_training_data(assets, train_start, train_end))

portfolio = calculate_portfolio_returns(YFinanceDataFetcher()
                                        .get_testing_data(assets, test_start, test_end), portfolio_w.T)

stock = portfolio['Daily Return']
report = generate_report(stock)

if __name__ == "__main__":
    print(report)

#%%

#%%
