# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:51:31 2023

@author: Alejandro
"""

from pyRofex.components.enums import TimeInForce, Market, MarketSegment, Side, OrderType, MarketDataEntry

from ..broker_connection import db_query


settlements = { 0: 'CI',
                1: '24hs',
                2: '48hs', }

side        = { 1: Side.BUY,
               -1: Side.SELL, }

orderType   = { 0: OrderType.LIMIT, 
                1: OrderType.MARKET, 
                2: OrderType.MARKET_TO_LIMIT, }

timeInForce = { 0: TimeInForce.DAY,
                1: TimeInForce.ImmediateOrCancel,
                2: TimeInForce.FillOrKill,
                3: TimeInForce.GoodTillDate, }

market      = { 0: Market.ROFEX, }

currency    = { 0: 'ARS', 
                1: 'USD', }



securities = []
        
def validations(order):
    if order.get('symbol') not in securities: raise Exception(' Símbolo inválido!')
    if order.get('price') <= 0: raise Exception(' Precio inválido!')
    if order.get('size')  <= 0: raise Exception(' Cantidad inválida!')
    # ....
    
       
        