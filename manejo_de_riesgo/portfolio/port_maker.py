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
#    risk_level_user = {'Conservative': 1, 'Moderate': 2, 'Aggressive': 3, 'Very Aggressive': 4}

portfolio_w = PortfolioOptimizerTest()
risk_user = input('Enter your risk profile: ')
print(portfolio_w.set_risk_level(risk_user))
portfolio_w = portfolio_w.port_optimize(YFinanceDataFetcher().get_training_data(assets, train_start, train_end))



print(portfolio_w.T)
portfolio = calculate_portfolio_returns(YFinanceDataFetcher()
                                        .get_testing_data(assets, test_start, test_end), portfolio_w.T)

stock = portfolio['Daily Return']
report = generate_report(stock)
print(report)
#%%
