import quantstats as qs
import pandas as pd
import io
import sys


def get_last_two_values(row):
    values = row.dropna().values[-2:]
    return pd.Series(values, index=[0, 1])


indicators_list = [
    "StartPeriod",
    "EndPeriod",
    "RiskFreeRate",
    "TimeInMarket",
    "CumulativeReturn",
    "CAGRPercentage",
    "Sharpe",
    "ProbSharpeRatio",
    "Sortino",
    "SortinoSquareRoot2",
    "Omega",
    "MaxDrawdown",
    "LongestDDDays",
    "GainPainRatio",
    "GainPain1M",
    "PayoffRatio",
    "ProfitFactor",
    "CommonSenseRatio",
    "CPCIndex",
    "TailRatio",
    "OutlierWinRatio",
    "OutlierLossRatio",
    "MTD",
    "r3M",
    "r6M",
    "YTD",
    "r1Y",
    "r3Yann",
    "r5Yann",
    "r10Yann",
    "Alltimeann",
    "AvgDrawdown",
    "AvgDrawdownDays",
    "RecoveryFactor",
    "Ulcer_Index",
    "Serenity_Index"]


def generate_report(daily_returns):
    output_buffer = io.StringIO()
    sys.stdout = output_buffer

    qs.reports.metrics(daily_returns, benchmark='SPY')

    sys.stdout = sys.__stdout__
    metrics_output = output_buffer.getvalue()

    try:
        df = pd.read_csv(io.StringIO(metrics_output), delim_whitespace=True)
    except pd.errors.EmptyDataError:
        df = None
        print("Empty")
    except pd.errors.ParserError:
        print("ParserError")
        df = None

    if df is not None:
        result = df.apply(get_last_two_values, axis=1)

        list_indicators = pd.DataFrame(indicators_list)

        df_r = result.drop([0, 1])
        df_r = df_r.reset_index(drop=True)

        report_df = pd.concat([list_indicators, df_r], axis=1)
        report_df.columns = ['Indicator', 'SPY', 'Portfolio']
        report_df = report_df.reset_index(drop=True)
        report_df = report_df.set_index('Indicator')
        return report_df

# %%

# %%
