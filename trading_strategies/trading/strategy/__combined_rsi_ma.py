import numpy as np
import vectorbt as vbt

class Combined:

    def __init__(self,  rsi_window = 14, rsi_entry = 30, rsi_exit = 70, ma_slow = 50, ma_fast = 10):
        self.strategy_name='Combined'
        
        self.__rsi_window = rsi_window
        self.__rsi_entry = rsi_entry
        self.__rsi_exit = rsi_exit
        self.__ma_slow = ma_slow
        self.__ma_fast = ma_fast

    def entries_and_exits(self, data: np.ndarray):
        """
        Generate entry and exit signals based on multiple indicators.

        :param data: DataFrame with price data.
        :return: Tuple of entry and exit signals as numpy arrays.
        """
        
        # Calculate moving averages and RSI
        fast_ma = vbt.MA.run(data, self.__ma_fast)
        slow_ma = vbt.MA.run(data, self.__ma_slow )
        rsi = vbt.RSI.run(data, window=self.__rsi_window)

        # Generate entry and exit signals
        entry_signals = fast_ma.ma_crossed_above(slow_ma) & rsi.rsi_above( self.__rsi_entry)
        exit_signals = slow_ma.ma_crossed_above(fast_ma) & rsi.rsi_below(self.__rsi_exit)
    
        return entry_signals.values, exit_signals.values
    
    def get_strategy_params(self):
        params = {
            'rsi_window': self.__rsi_window,
            'rsi_entry': self.__rsi_entry,
            'rsi_exit': self.__rsi_exit,
            'ma_slow': self.__ma_slow,
            'ma_fast': self.__ma_fast
        }
        return params

    def change_params(self, rsi_window, rsi_entry, rsi_exit, ma_slow, ma_fast):
        self.__rsi_window = rsi_window
        self.__rsi_entry = rsi_entry
        self.__rsi_exit = rsi_exit
        self.__ma_slow = ma_slow
        self.__ma_fast = ma_fast
        return