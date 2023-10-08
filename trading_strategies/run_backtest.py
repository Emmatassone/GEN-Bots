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

# Generamos señales de compra y venta
entries,exits = StrategyBook.moving_average(ohlcv_wbuf['Close'].values)

df=pd.concat([ohlcv_wbuf, pd.DataFrame(entries,index=ohlcv_wbuf.index,columns=['entry'])], axis=1)
df=pd.concat([df, pd.DataFrame(exits,index=ohlcv_wbuf.index,columns=['exit'])], axis=1)

fig = df['Close'].vbt.plot(trace_kwargs=dict(name='Price'))
fig = df['entry'].vbt.signals.plot_as_entry_markers(ohlcv_wbuf['Close'], fig=fig)
fig = df['exit'].vbt.signals.plot_as_exit_markers(ohlcv_wbuf['Close'], fig=fig)

fig.show_svg()

# Comparamos porcentajes de retorno de las estrategias
# buy&hold
# MA rápida supera la MA lenta
hold_entries = pd.Series.vbt.signals.empty_like(df['entry'])
hold_entries.iloc[0] = True
hold_exits = pd.Series.vbt.signals.empty_like(hold_entries)
hold_exits.iloc[-1] = True
hold_pf = vbt.Portfolio.from_signals(df['Close'], hold_entries, hold_exits)

pf = vbt.Portfolio.from_signals(df['Close'], df['entry'], df['exit'])

fig = pf.value().vbt.plot(trace_kwargs=dict(name='MA 10/20'))
hold_pf.value().vbt.plot(trace_kwargs=dict(name='Hold'), fig=fig).show_svg()
