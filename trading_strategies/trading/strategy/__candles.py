import numpy as np
import vectorbt as vbt

from trading.indicators.__candles_count import CountCandlesIndicator

class Candles:

    def __init__(self, green_candles_entry: int = 3, red_candles_exit: int = 2):
        self.strategy_name = 'Candles'
        
        self.__green_candles_entry = green_candles_entry
        self.__red_candles_exit = red_candles_exit

    def entries_and_exits(self, data: np.ndarray):        
        """
        Generate entry and exit signals based on consecutive green and red candles.

        :param data: DataFrame with price data.
        :return: Tuple of entry and exit signals as numpy arrays.
        """
        res_green_count = CountCandlesIndicator.run(
            data,
            consecutive_moves_threshold=self.__green_candles_entry,
            direction=1) # direction for green candles
        
        res_red_count = CountCandlesIndicator.run(
            data,
            consecutive_moves_threshold=self.__red_candles_exit,
            direction=-1) # direction for red candles    
                
        entry_signals = res_green_count.value == 1.0
        exit_signals = res_red_count.value == 1.0      
        
        return entry_signals.to_numpy(), exit_signals.to_numpy()
    
    def get_strategy_params(self):
        params = {
            'green_candles_entry': self.__green_candles_entry,
            'red_candles_exit': self.__red_candles_exit
        }
        return params

    def change_params(self, green_candles_entry, red_candles_exit):
        self.__green_candles_entry = green_candles_entry
        self.__red_candles_exit = red_candles_exit
