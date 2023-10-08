import yfinance as yf


class YFinanceDataFetcher:
    def __init__(self):
        pass

    @staticmethod
    def fetch_yfinance_data(assets, start, end):
        """
        Fetches Yahoo Finance data for a list of assets between specified start and end dates.

        Args:
            assets (list): List of asset tickers.
            start (str): Start date in 'YYYY-MM-DD' format.
            end (str): End date in 'YYYY-MM-DD' format.

        Returns:
            pd.DataFrame: DataFrame containing daily returns for the specified assets.
        """
        assets.sort()
        data = yf.download(assets, start=start, end=end)
        data = data.loc[:, ('Adj Close', slice(None))]
        data.columns = assets
        asset_daily_change = data[assets].pct_change().dropna()
        asset_daily_returns = asset_daily_change
        return asset_daily_returns

    def get_training_data(self, assets, start=None, end=None):
        """
        Fetches training data from Yahoo Finance for a list of assets.

        Args:
            assets (list): List of asset tickers.
            start (str, optional): Start date in 'YYYY-MM-DD' format.
            end (str, optional): End date in 'YYYY-MM-DD' format.

        Returns:
            pd.DataFrame: DataFrame containing daily returns for training data.
        """
        _train_start = '2019-01-01'
        _train_end = '2022-12-30'

        if start:
            _train_start = start
        if end:
            _train_end = end

        return self.fetch_yfinance_data(assets, _train_start, _train_end)

    def get_testing_data(self, assets, start=None, end=None):
        """
        Fetches testing data from Yahoo Finance for a list of assets.

        Args:
            assets (list): List of asset tickers.
            start (str, optional): Start date in 'YYYY-MM-DD' format.
            end (str, optional): End date in 'YYYY-MM-DD' format.

        Returns:
            pd.DataFrame: DataFrame containing daily returns for testing data.
        """
        _test_start = '2023-01-01'
        _test_end = '2023-12-31'

        if start:
            _test_start = start
        if end:
            _test_end = end

        return self.fetch_yfinance_data(assets, _test_start, _test_end)

#%%
