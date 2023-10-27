import numpy as np
import pandas as pd
import unittest

from datetime import datetime

from .__custom_example import MedianIndicator


class TestCustomExampleIndicator(unittest.TestCase):

    def test_basic_usage(self):
        # Define a time signal as a pandas data frame.
        signal = pd.DataFrame({
            'p': [1, 2, 3, 4, 5],
        }, index=pd.Index([
            datetime(2020, 1, 1),
            datetime(2020, 1, 2),
            datetime(2020, 1, 3),
            datetime(2020, 1, 4),
            datetime(2020, 1, 5),
        ])).astype(float)
        # Evaluate the indicator for different values of the 'window' parameter.
        # Test with window=3 and window=4.
        v = MedianIndicator.run(signal, [3, 4])
        # Now v.median behaves like a pandas data frame with columns 3 and 4, one for
        # each given value of the 'window' parameter. Assert now that we have what we expect:
        self.assertTrue(np.all(np.array([1.0, 1.5, 2.0, 3.0, 4.0]) == v.median[3].values))
        self.assertTrue(np.all(np.array([1.0, 1.5, 2.0, 2.5, 3.5]) == v.median[4].values))
