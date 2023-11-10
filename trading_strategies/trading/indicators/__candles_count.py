import pandas as pd
import numpy as np
import vectorbt as vbt

def count_consecutive_candles(data, consecutive_moves_threshold, direction=1):
    """
    Generate a boolean indicator that is True if there have been N consecutive price moves in the specified direction.

    :param data: DataFrame with price data
    :param consecutive_moves_threshold: Number of consecutive moves to count.
    :param direction: Direction of the moves (1 for up, -1 for down).
    :return: DataFrame with True values if there have been N consecutive moves in the specified direction, False otherwise.
    """
    
    df_data = pd.DataFrame(data, columns=['Close'])    

    result_np = np.full(df_data.shape, False)

    consecutive_moves = 0

    for i in range(len(df_data)):
        if i == 0:
            result_np[i] = False
        else:
            current_close = df_data['Close'].iloc[i]
            previous_close = df_data['Close'].iloc[i - 1]

            consecutive_moves = consecutive_moves + 1 if (
                (direction == 1 and current_close > previous_close) or
                (direction == -1 and current_close < previous_close)
            ) else 0

            if consecutive_moves >= consecutive_moves_threshold:
                result_np[i] = True

    return result_np

CountCandlesIndicator = vbt.IndicatorFactory(
    class_name='Candles',
    short_name='candles',
    input_names=['close'],
    param_names=['consecutive_moves_threshold', 'direction'],
    output_names=['value'],
).from_apply_func(count_consecutive_candles, consecutive_moves_threshold=3, direction=1)
