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
    _3M: str
    _6M: str
    YTD: str
    _1Y: str
    _3Yann: str
    _5Yann: str
    _10Yann: str
    Alltimeann: str
    AvgDrawdown: str
    AvgDrawdownDays: str
    RecoveryFactor: str
    UlcerIndex: str
    SerenityIndex: str


class PortfolioResponse(BaseModel):
    SPY: PortfolioItem
    Portfolio: PortfolioItem
