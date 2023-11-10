import numpy as np
import vectorbt as vbt

class RSI:
    
    def __init__(self, rsi_window: int = 14, overbought_threshold: float = 70, oversold_threshold: float = 30):
        self.strategy_name = 'RSI'
        
        self.__rsi_window = rsi_window
        self.__overbought_threshold = overbought_threshold
        self.__oversold_threshold = oversold_threshold

    def entries_and_exits(self, signal: np.ndarray):
        """
        Generate entry and exit signals based on RSI indicator.

        :param signal: Numpy array with price data.
        :return: Tuple of entry and exit signals as numpy arrays.
        """
    
        rsi = vbt.RSI.run(signal, self.__rsi_window)
        
        entries = rsi.rsi_crossed_above(self.__overbought_threshold)
        exits = rsi.rsi_crossed_below(self.__oversold_threshold)
                        
        return entries.values, exits.values

    def get_strategy_params(self):
        params = {
            'rsi_window': self.__rsi_window,
            'overbought_threshold': self.__overbought_threshold,
            'oversold_threshold': self.__oversold_threshold
        }
        return params

    def change_params(self, rsi_window, overbought_threshold, oversold_threshold):
        self.__rsi_window = rsi_window
        self.__overbought_threshold = overbought_threshold
        self.__oversold_threshold = oversold_threshold
        return
