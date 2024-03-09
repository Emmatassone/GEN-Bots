# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:51:31 2023

@author: Alejandro
"""
import pandas as pd

# segment = {'marketSegmentId': 'MERV', 'marketId': 'ROFX'}

class instruments:  # db
    ticker: str
    symbol: str
    settlement: str
  # segment  ???
  # market   ???
    minPriceIncrement: float 
    minTradeVol: int
    tickSize: float
    contractMultiplier: float
    roundLot: float
    priceConvertionFactor: float
    maturityDate: int  # YYYYMMDD
    currency: str
    orderTypes: str  # list
    timesInForce: str  # list
    instrumentPricePrecision: int
    instrumentSizePrecision: int
    strike: float
    underlying: str
    

def detailed_instruments_normilize(df:pd.DataFrame):
    df.drop(['segment', 'lowLimitPrice', 'highLimitPrice', 'maxTradeVol', 'securityType', 'settlType',
             'securityId', 'securityIdSource', 'tickPriceRanges', 'cficode', 'instrumentId', ], axis=1, inplace=True)
    df[['symbol', 'settlement']] = df['securityDescription'].str.split(' - ', expand=True).iloc[:,2:4]
    df.rename(columns={'securityDescription': 'ticker'}, inplace=True)
    df['symbol'] = df['symbol'].fillna(df['ticker'])
    df['settlement'] = df['settlement'].fillna('CI')
    return df
    
    
    

