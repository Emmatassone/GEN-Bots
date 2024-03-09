# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 22:02:42 2023

@author: Alejandro
"""
import pandas as pd
import functools
import operator

settlements = [ 'spot', '24hs', '48hs', ]

symbols = sorted([ 'AL30', 'AL30D', 'GD30', 'GD30D', ])

cedearsARS = [ 'AAPL',  'AMZN',  'GOGL',  'NVDA',  'SHOP',  'AMD',  'TSLA',  'MELI',  'BABA',  'BRKB', ]
cedearsUSD = [ 'AAPLD', 'AMZND', 'GOGLD', 'NVDAD', 'SHOPD', 'AMDD', 'TSLAD', 'MELID', 'BABAD', 'BRKBD']
onsARS = ['YCA6O', 'CAC2O', 'CP32O', 'CS34O', 'CS38O', 'DNC2O', 'GNCXO', 'IRCFO', 'MGCHO', 'MRCAO', 'MTCGO', 'PNDCO', 'RUC3O', 'TLC1O', 'TLC5O', 'YMCQO',]
onsUSD = ['YCA6P', 'CAC2D', 'CP32D', 'CS34D', 'CS38D', 'DNC2D', 'GNCXD', 'IRCFD', 'MGCHD', 'MRCAD', 'MTCGD', 'PNDCD', 'RUC3D', 'TLC1D', 'TLC5D', 'YMCQD',]


def ticker_mask(symbol, settlement):
    if settlement == 'spot': settlement = 'CI'
    return 'MERV - XMEV - '+symbol+' - '+settlement

tickers = [ticker_mask(i,j) for i in symbols for j in settlements]
# tickers = ['MERV - XMEV - '+i+' - '+j for i in symbols for j in [s if s != 'spot' else 'CI' for s in settlements]]


def securitiesDF (symbols=sorted(cedearsARS+cedearsUSD+onsARS+onsUSD), settlements=['spot', '48hs']):
    multi_index = pd.MultiIndex.from_arrays([
        functools.reduce(operator.iconcat, [ [i]*len(settlements) for i in symbols ], []),
        functools.reduce(operator.iconcat, [ [i] for i in settlements ], [])*len(symbols),
        ], names=('symbol',	'settlement'))
    return pd.DataFrame(index=multi_index,columns=['bid_size', 'bid', 'ask', 'ask_size', 'last', 'datetime', 'turnover', 'volume'])

def securitiesMEPdf (symbols=sorted(cedearsARS+cedearsUSD+onsARS+onsUSD), settlements=['spot', '48hs'], variants=['Best', 'Mkt']):
    buy_sell_settlements_combinations = [('spot', 'spot'), ('spot', '48hs'), ('48hs', '48hs')]
    multi_index = pd.MultiIndex.from_arrays([
        functools.reduce(operator.iconcat, [ [i]*len(buy_sell_settlements_combinations) for i in symbols ], []),
        functools.reduce(operator.iconcat, [ [i] for i in buy_sell_settlements_combinations ], [])*len(symbols),
        ], names=('symbol',	'settlement'))
    return pd.DataFrame(index=multi_index,columns=['Buy (Best)', 'Buy (Mkt)', 'Sell (Best)', 'Sell (Mkt)'])