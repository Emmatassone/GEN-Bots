import yfinance as yf

class FetchYfinance():
    def __init__(self) -> None:
        pass
    def fetch_yfinance_data(self,assets,start, end):
        assets.sort()
        data = yf.download(assets, start=start, end=end)
        data = data.loc[:, ('Adj Close', slice(None))]
        data.columns = assets
        asset_daily_change = data[assets].pct_change().dropna()
        asset_daily_returns = asset_daily_change
        return asset_daily_returns
    def train_data(self,assets,start=False, end=False):
        # Training Data
        _train_start = '2019-01-01'
        _train_end = '2022-12-30'
        if start:
            _train_start = start
        if end:
            _train_end = end
        return self.fetch_yfinance_data(assets,_train_start, _train_end)
    def test_data(self,assets,start=False, end=False):
        # Test Data
        _test_start = '2023-01-01'  # You might want to specify test dates
        _test_end = '2023-12-31'    # accordingly.
        if start:
            _test_start = start
        if end:
            _test_end = end
        return self.fetch_yfinance_data(assets,_test_start, _test_end)
