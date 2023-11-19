import numpy as np
import vectorbt as vbt

class MACD:
    
    def __init__(self, fast_window: int = 12, slow_window: int = 26, signal_window: int = 9):
        self.strategy_name='MACD'
        
        self.__fast_window = fast_window
        self.__slow_window = slow_window
        self.__signal_window = signal_window

    
    def entries_and_exits(self, signal: np.ndarray):
        """
        Generate entry and exit signals based on MACD indicator.

        :param signal: Numpy array with price data.
        :return: Tuple of entry and exit signals as numpy arrays.
        """
            
        macd = vbt.MACD.run(signal, fast_window=self.__fast_window, slow_window=self.__slow_window, signal_window=self.__signal_window)
        
        entries = macd.macd_crossed_above (macd.signal) 
        exits =  macd.macd_crossed_below (macd.signal)                
        return entries.values, exits.values
    
    def get_strategy_params(self):
        params = {
            'fast_window': self.__fast_window,
            'slow_window': self.__slow_window,
            'signal_window': self.__signal_window
        }
        return params

    def change_params(self, fast_window, slow_window, signal_window):
        self.__fast_window = fast_window
        self.__slow_window = slow_window
        self.__signal_window = signal_window
        return