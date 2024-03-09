# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:51:31 2023

@author: Alejandro
"""

from pyRofex.components.enums import TimeInForce, Market, Side, OrderType   #, MarketSegment, MarketDataEntry

from connections.helpers.orders_helpers import status_map


##################################################
###    Referencias para el envio de órdenes    ###
##################################################
settlements = { 0: 'CI',
                1: '24hs',
                2: '48hs', }
settlements_inverted = {v: k for k, v in settlements.items()}

side        = { 1: Side.BUY,
               -1: Side.SELL, }
side_inverted = {v.value.upper(): k for k, v in side.items()}

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


##################################################
####    Referencias del reporte de órdenes    ####
##################################################
status_ref = { 'PENDING_NEW':      status_map.get('SENT'),         #  0
               'NEW':              status_map.get('IN_MARKET'),    #  1
               'PARTIALLY_FILLED': status_map.get('PART_FILLED'),  #  2
               'FILLED':           status_map.get('FILLED'),       #  3
               'REJECTED':         status_map.get('REJECTED'),     # -1
               'PENDING_CANCEL':   status_map.get('PEND_CANCEL'),  # -2
               'CANCELLED':        status_map.get('CANCELLED'),    # -3
               'EXPIRED':          status_map.get('EXPIRED'),  }   # -4


def order_data_update(data):
    global status_ref
    return dict(
        remaining   = data.get('leavesQty'),
        status      = status_ref.get(data.get('status')), )

def order_data_map_to_db(data):  # def order_data_map_to_db(data, conn_id):
    global status_ref, settlements_inverted
    return dict(
    #   conn_id     = conn_id,
        id_ext      = data.get('clOrdId'),
    #   symbol      = data.get('instrumentId').get('symbol').split(' - ')[2],
    #   settlement  = settlements_inverted.get( data.get('instrumentId').get('symbol').split(' - ')[3] ),
    #   op_type     = side_inverted.get(data.get('side')),
    #   size        = data.get('orderQty'),
    #   price       = data.get('price'),
        
      # remaining   = data.get('leavesQty'),
        status      = status_ref.get(data.get('status')),
      # currency    = data.get(),
      # amount      = data.get(),
        
    #   order_type  = data.get('ordType'),
      # cancel_prev = data.get(),
        
      # display_qty = data.get('display_qty'),
      # iceberg     = data.get(),
      # all_or_none = data.get(),
    
      # timeInForce = data.get(),
      # expire_date = data.get(),  
      )


def order_data_update_db(data):
    global status_ref
    return dict(
        remaining   = data.get('leavesQty'),
        status      = status_ref.get(data.get('status')), )

securities = []
        
def validations(order):
    if order.get('symbol') not in securities: raise Exception(' Símbolo inválido!')
    if order.get('price') <= 0: raise Exception(' Precio inválido!')
    if order.get('size')  <= 0: raise Exception(' Cantidad inválida!')
    # ....
    
       
        