import numpy as np


class Threshold:

    def __init__(self, buy: float, sell: float):
        self.__buy = buy
        self.__sell = sell

    def entries_and_exits(self, signal: np.ndarray):
        # Initialize entries.
        entries = np.zeros_like(signal, dtype=np.bool_)
        entries[signal < self.__buy] = True
        # Initialize exits.
        exits = np.zeros_like(signal, dtype=np.bool_)
        exits[signal > self.__sell] = True
        # Return both.
        return entries, exits
