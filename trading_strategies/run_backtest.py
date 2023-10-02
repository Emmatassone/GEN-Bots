# import pandas as pd
import vectorbt as vbt
import numpy as np
from strategies import StrategyBook
from data_processing import load_data
import pandas as pd 

ohlcv_wbuf = load_data()
ohlcv_wbuf = ohlcv_wbuf.astype(np.float64)


vbt.settings.portfolio['init_cash'] = 100.  # 100$
vbt.settings.portfolio['fees'] = 0.0025  # 0.25%

# Apply the strategy to generate signals
entries,exits = StrategyBook.moving_average(ohlcv_wbuf['Close'].values)

df=pd.concat([ohlcv_wbuf, pd.DataFrame(entries,index=ohlcv_wbuf.index,columns=['entry'])], axis=1)
df=pd.concat([df, pd.DataFrame(exits,index=ohlcv_wbuf.index,columns=['exit'])], axis=1)

fig = df['Close'].vbt.plot(trace_kwargs=dict(name='Price'))
fig = df['entry'].vbt.signals.plot_as_entry_markers(ohlcv_wbuf['Close'], fig=fig)
fig = df['exit'].vbt.signals.plot_as_exit_markers(ohlcv_wbuf['Close'], fig=fig)

fig.show_svg()
