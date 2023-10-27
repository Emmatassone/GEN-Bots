"""Example on how to write a custom indicator using vbt features.

The package vectorbt provides several built-in features that let the user define their own
indicators using the IndicatorFactory class. This file shows how to define a simple indicator
using this approach. The core computational logic of the indicator is defined as a plain
Python function decorated with the @njit decoration, which tells Numba to generate fast LLVM
code, thus increasing computational speed. The indicator defined in this file simply computes
the median value of the last n data points, where n is given as a parameter called "window".

The example is based on several indicators defined in the 'indicators' package in the
vectorbt repository, and the same naming conventions were adopted.
"""

import numba
import numpy as np
import vectorbt as vbt


@numba.njit(cache=True)
def median_1d_nb(x: np.ndarray, window: int, minp=None) -> np.ndarray:
    # NOTE/TODO: This example does not show well how to handle minp (min. periods) and NaN values,
    # and should probably be extended.

    # Vector x is assumed to be a 1D array. We now proceed to compute the median
    # for the last 'window' values for each point in the sequence.
    out = np.empty_like(x, dtype=np.float_)

    for i in range(x.shape[0]):
        # Compute the numpy median given 'window' historical values including the i-th
        # array element, and set that to the i-th element of the output array.
        out[i] = np.nanmedian(x[max(i - window + 1, 0):i+1])

    return out


MedianIndicator = vbt.IndicatorFactory(
    input_names=['x'],
    param_names=['window'],
    output_names=['median']
).from_apply_func(median_1d_nb)
