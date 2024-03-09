# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:51:31 2023

@author: Alejandro
"""

import pandas as pd
import simplejson

import global_variables
from .pyRofex_orders_helpers import order_data_map_to_db


def order_report_handler(msg):
    #if msg['type']=='co':
    print( '\n', 'tipo:',msg['type'], '\n', msg, '\n', '\n')
    data = msg['orderReport']
    status = data['status']
    if status == 'PENDING_NEW':
        print(data['wsClOrdId'])
        global_variables.orders_data.queue.put( ({'id_int': data['wsClOrdId']}, order_data_map_to_db(data=data)) )
        # agregar tercer elemento en la tupla con los datos a chequear
    elif status == 'NEW':
        global_variables.orders_data.queue.put( ({'id_ext': data['ClOrdId']}, order_data_map_to_db(data=data)) )
    elif status == 'PARTIALLY_FILLED':
        pass
    elif status == 'FILLED':
        pass
    elif status == 'REJECTED':
        pass
    elif status == 'PENDING_CANCEL':
        pass
    elif status == 'CANCELLED':
        pass
    elif status == 'EXPIRED':
        pass
    
    else:
        pass #
    
def market_data_handler(msg):
    print("Market Data msg Received: {0} \n\n".format(msg))
    
    {'type': 'Md', 'timestamp': 1708713883555, 'instrumentId': 
         {'marketId': 'ROFX', 'symbol': 'MERV - XMEV - AL30 - CI'},
         'marketData': {'OF': [{'price': 47665, 'size': 18965},
                               {'price': 47670, 'size': 34063},
                               {'price': 47690, 'size': 44103},
                               {'price': 47695, 'size': 20500}, 
                               {'price': 47700, 'size': 1500}], 
                        'BI': [{'price': 47655, 'size': 20000}, 
                               {'price': 47650, 'size': 57837}, 
                               {'price': 47645, 'size': 100000},
                               {'price': 47640, 'size': 991},
                               {'price': 47635, 'size': 102585}]}}
    
    # msg['instrumentId']['symbol'][14:].split(' - ')
    
    index = pd.MultiIndex.from_product([[i if i!='CI' else 'spot'] for i in msg['instrumentId']['symbol'][14:].split(' - ')]+[range(1,6)], 
                                       names=['symbol', 'settlement', 'position'])
    ask_df = pd.DataFrame(msg['marketData']['OF'], columns=['size', 'price'], index=index).rename(columns={'price': 'ask', 'size': 'ask_size'})
    bid_df = pd.DataFrame(msg['marketData']['BI'], columns=['size', 'price'], index=index).rename(columns={'price': 'bid', 'size': 'bid_size'})
    df = pd.concat([bid_df, ask_df], axis=1)
    df.insert(2, 'bid_offers_count', 0)
    df['ask_offers_count']=0
    print(df)
    
"""
def order_report_handler(message):
    print("Order Report Message Received: {0}".format(message))
    # 6-Handler will validate if the order is in the correct state (pending_new)
    if message["orderReport"]["status"] == "NEW":
        # 6.1-We cancel the order using the websocket connection
        print("Send to Cancel Order with clOrdID: {0}".format(message["orderReport"]["clOrdId"]))
        #pyRofex.cancel_order_via_websocket(message["orderReport"]["clOrdId"])

    # 7-Handler will receive an Order Report indicating that the order is cancelled (will print it)
    if message["orderReport"]["status"] == "CANCELLED":
        print("Order with ClOrdID '{0}' is Cancelled.".format(message["orderReport"]["clOrdId"]))
"""
    
def error_handler(message):
    print("Error Message Received: {0}".format(message))
    if eval(message.get('message')).get('type') == 'co': print('Cancel Order Error Message Type')
    msg = simplejson.loads(message.get('message'))
    if msg['type'] == 'co': print('alt2: Cancel Order Error Message Type')
    

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))
