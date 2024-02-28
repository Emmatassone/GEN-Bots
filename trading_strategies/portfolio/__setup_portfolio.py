import importlib
import plotly.graph_objects as go
import plotly.io as pio
import vectorbt as vbt
import pandas as pd 
import numpy as np

class SetUpPortfolio():
    
    def __init__(self,strategy_name,ohlcv_dataframe):
        self.__strategy_name=strategy_name
        self.__ohlcv_dataframe=ohlcv_dataframe
        
        self.set_initial_portfolio()
        strategy_class = self.import_strategy(strategy_name)
        self.strategy_instance = strategy_class()
        
    def strategy_params(self):
        return self.strategy_instance.get_strategy_params()
        
    
    def set_initial_portfolio(self):
        vbt.settings.portfolio['init_cash'] = 100.  # 100$
        vbt.settings.portfolio['fees'] = 0.0025  # 0.25%
        
    def import_strategy(self, strategy_name):
        try:
            module = importlib.import_module('trading.strategy')
            strategy_class = getattr(module, strategy_name)
            return strategy_class
        except ImportError:
            print(f"Could not import strategy '{strategy_name}'. Make sure the file and class exist.")
            return None
        except AttributeError:
            print(f"Could not find class '{strategy_name}' in the strategy module.")
            return None
    
    def get_entries_and_exits(self,params):
        ohlcv=self.__ohlcv_dataframe
        
        self.strategy_instance.change_params(*params)
        
        entries, exits = self.strategy_instance.entries_and_exits(ohlcv['Close'].values)
        
        df = pd.concat([ohlcv, pd.DataFrame(entries,index=ohlcv.index,columns=['entry'])], axis=1)
        self.__df = pd.concat([df, pd.DataFrame(exits, index=ohlcv.index,columns=['exit'])], axis=1)
        
    def plot_backtest(self):
        df=self.__df
        ohlcv=self.__ohlcv_dataframe
        
        fig = df['Close'].vbt.plot(trace_kwargs=dict(name='Price'))
        fig = df['entry'].vbt.signals.plot_as_entry_markers(ohlcv['Close'], fig=fig)
        fig = df['exit'].vbt.signals.plot_as_exit_markers(ohlcv['Close'], fig=fig)
        pio.write_image(fig, 'chart_signals.png', format='png')
        
        strategy_signals= vbt.Portfolio.from_signals(df['Close'], df['entry'], df['exit'])
        hold_signals=self.build_hold_signals(df)
        
        fig = strategy_signals.value().vbt.plot(trace_kwargs=dict(name=self.__strategy_name))
        hold_signals.value().vbt.plot(trace_kwargs=dict(name='Hold'), fig=fig)
        
        pio.write_image(fig, 'porfolio_evolution.png', format='png')
        
    def build_hold_signals(self,df):
        
        hold_entries = pd.Series.vbt.signals.empty_like(df['entry'])
        hold_entries.iloc[0] = True
        hold_exits = pd.Series.vbt.signals.empty_like(hold_entries)
        hold_exits.iloc[-1] = True
        hold_pf = vbt.Portfolio.from_signals(df['Close'], hold_entries, hold_exits)
        return hold_pf
    
    def build_short_signals(self, df):
        # Initialize entries.
        entries = df['Close'] > 100
        exits = df['Close'] < 50
        short_pf = vbt.Portfolio.from_signals(df['Close'], entries, exits, direction="short")

        return short_pf