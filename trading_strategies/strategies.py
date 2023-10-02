import vectorbt as vbt

class StrategyBook:
    def __init__(self, params):
        pass

    @classmethod
    def threshold(cls,price_data):
        buy_threshold= 7000
        sell_threshold= 16000
        entry_signals = []
        exit_signals = []

        for price in price_data:
            if price < buy_threshold:
                entry_signals.append(True)
                exit_signals.append(False)
            elif price > sell_threshold:
                entry_signals.append(False)
                exit_signals.append(True)
            else:
                entry_signals.append(False)
                exit_signals.append(False)

        return entry_signals, exit_signals
    
    @classmethod
    def moving_average(cls,price_data,ma1=10,ma2=20):
        fast_ma = vbt.MA.run(price_data, ma1, short_name='fast')
        slow_ma = vbt.MA.run(price_data, ma2, short_name='slow')
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        return entries.values, exits.values
    