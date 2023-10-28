import ge.finance.concept as concept
import pandas as pd
import yfinance

Frequency = str
FREQ_YEARLY = 'yearly'
FREQ_QUARTERLY = 'quarterly'

BALANCE_SHEET_MAPPING = {
    concept.TOTAL_ASSETS: 'Total Assets',
    concept.STOCKHOLDER_EQUITY: 'Common Stock Equity',
    concept.DEBT_AND_LEASE_CURRENT: 'Current Debt And Capital Lease Obligation',
    concept.DEBT_AND_LEASE_NON_CURRENT: 'Long Term Debt And Capital Lease Obligation',
}


def fetch_balance_sheet(ticker_symbol: str, frequency: Frequency = FREQ_YEARLY) -> pd.DataFrame:
    # Initialize client.
    source = yfinance.Ticker(ticker_symbol)
    # Get balance sheet.
    balance_sheet = source.get_balance_sheet(pretty=True, freq=frequency)
    # Translate Yahoo Finance representation into internal common representation.
    df = pd.DataFrame({key: balance_sheet.loc[value] for key, value in BALANCE_SHEET_MAPPING.items()})
    # Add ticker symbol to all rows.
    df.insert(0, concept.TICKER_SYMBOL, ticker_symbol)
    # Set time.
    df.reset_index(inplace=True)
    df.rename(columns={'index': concept.PERIOD_START}, inplace=True)
    df.sort_values(by=concept.PERIOD_START, ascending=True, inplace=True)
    #
    return df
