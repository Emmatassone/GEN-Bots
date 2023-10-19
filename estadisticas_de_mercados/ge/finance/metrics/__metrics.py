import ge.finance.concept as concept

import pandas as pd


def return_on_equity(df: pd.DataFrame) -> pd.Series:
    """
    Computes standard RETURN_ON_EQUITY given a dataframe with standard columns NET_INCOME and STOCKHOLDER_EQUITY.
    The result is returned as a pandas series.
    """
    return df[concept.NET_INCOME] / df[concept.STOCKHOLDER_EQUITY]
