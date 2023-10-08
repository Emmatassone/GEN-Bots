from datetime import datetime,timedelta
import pytz
import vectorbt as vbt

def load_data(symbol = 'BTC-USD'):
# Enter your parameters here
    start_date = datetime(2018, 1, 1, tzinfo=pytz.utc)  # time period for analysis, must be timezone-aware
    end_date = datetime(2020, 1, 1, tzinfo=pytz.utc)
    time_buffer = timedelta(days=100)  # buffer before to pre-calculate SMA/EMA, best to set to max window

    # Download data with time buffer
    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    ohlcv_wbuf = vbt.YFData.download(symbol, start=start_date-time_buffer, end=end_date).get(cols)
    return ohlcv_wbuf