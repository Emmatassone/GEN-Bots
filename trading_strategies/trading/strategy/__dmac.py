import numpy as np
import vectorbt as vbt


class DMAC:

    def __init__(self, fast_ma: int = 10, slow_ma: int = 20):
        self.strategy_name='DMAC'
        
        self.__fast = fast_ma
        self.__slow = slow_ma

    def entries_and_exits(self, signal: np.ndarray):
        fast_ma = vbt.MA.run(signal, self.__fast, short_name='fast')
        slow_ma = vbt.MA.run(signal, self.__slow, short_name='slow')
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        return entries.values, exits.values
    
    def get_strategy_params(self):
        params={'fast_ma':self.__fast,
                'slow_ma':self.__slow}
        return params
    
    def change_params(self,slow_ma,fast_ma):
        self.__fast = fast_ma
        self.__slow = slow_ma
        return
