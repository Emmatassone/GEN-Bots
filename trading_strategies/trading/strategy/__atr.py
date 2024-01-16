import pandas as pd
import numpy as np
import vectorbt as vbt

class ATR:
    def __init__(self, window: int = 14):
        """
        Initialize the ATR strategy.

        Args:
        - window (int): The window size for calculating ATR. Default is 14.
        """
        if not isinstance(window, int) or window <= 0:
            raise ValueError("Window must be a positive integer")
        self.strategy_name = 'ATR'
        self.__window = window

    def entries_and_exits(self, signal: np.ndarray):
        """
        Generate entries and exits based on the ATR strategy.

        Args:
        - signal (np.ndarray): The input signal as a numpy array.

        Returns:
        - entries (np.ndarray): Boolean array indicating the entry points.
        - exits (np.ndarray): Boolean array indicating the exit points.
        """
        if not isinstance(signal, np.ndarray):
            raise TypeError("Input signal must be a numpy array")
        try:
            atr = vbt.ATR.run(signal, self.__window)
        except Exception as e:
            raise Exception("Error calculating ATR: " + str(e))
        entries = signal > atr.atr 
        exits =  signal < atr.atr              
        return entries, exits

    def get_strategy_params(self):
        """
        Get the strategy parameters.

        Returns:
        - params (dict): Dictionary containing the strategy parameters.
        """
        params = {
            'window': self.__window
        }
        return params.copy()

    def change_params(self, window):
        """
        Change the strategy parameters.

        Args:
        - window (int): The new window size for calculating ATR.
        """
        if not isinstance(window, int) or window <= 0:
            raise ValueError("Window must be a positive integer")
        self.__window = window
        return
    
