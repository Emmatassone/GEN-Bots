from typing import List
from pydantic import BaseModel


class PortfolioUpdate(BaseModel):
    assets: list
    train_start: str
    train_end: str
    test_start: str
    test_end: str


class PortfolioItem(BaseModel):
    StartPeriod: str
    EndPeriod: str
    RiskFreeRate: str
    TimeInMarket: str
    CumulativeReturn: str
    CAGRPercentage: str
    Sharpe: str
    ProbSharpeRatio: str
    Sortino: str
    SortinoSquareRoot2: str
    Omega: str
    MaxDrawdown: str
    LongestDDDays: str
    GainPainRatio: str
    GainPain1M: str
    PayoffRatio: str
    ProfitFactor: str
    CommonSenseRatio: str
    CPCIndex: str
    TailRatio: str
    OutlierWinRatio: str
    OutlierLossRatio: str
    MTD: str
    r3M: str
    r6M: str
    YTD: str
    r1Y: str
    r3Yann: str
    r5Yann: str
    r10Yann: str
    Alltimeann: str
    AvgDrawdown: str
    AvgDrawdownDays: str
    RecoveryFactor: str
    Ulcer_Index: str
    Serenity_Index: str


class PortfolioResponse(BaseModel):
    SPY: PortfolioItem
    Portfolio: PortfolioItem
