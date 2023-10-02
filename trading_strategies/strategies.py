class StrategyBook:
    def __init__(self, params):
        pass

    @classmethod
    def threshold_strategy(cls,price_data):
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
    