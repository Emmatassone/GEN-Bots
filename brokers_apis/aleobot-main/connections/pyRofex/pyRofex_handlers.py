# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:51:31 2023

@author: Alejandro
"""

import pandas as pd


def market_data_handler(msg):
    # print("Market Data msg Received: {0}".format(msg))
    # msg['instrumentId']['symbol'][14:].split(' - ')
    
    index = pd.MultiIndex.from_product([[i if i!='CI' else 'spot'] for i in msg['instrumentId']['symbol'][14:].split(' - ')]+[range(1,6)], 
                                       names=['symbol', 'settlement', 'position'])
    ask_df = pd.DataFrame(msg['marketData']['OF'], columns=['size', 'price'], index=index).rename(columns={'price': 'ask', 'size': 'ask_size'})
    bid_df = pd.DataFrame(msg['marketData']['BI'], columns=['size', 'price'], index=index).rename(columns={'price': 'bid', 'size': 'bid_size'})
    df = pd.concat([bid_df, ask_df], axis=1)
    df.insert(2, 'bid_offers_count', 0)
    df['ask_offers_count']=0
    print(df)
    
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
    
def error_handler(message):
    print("Error Message Received: {0}".format(message))

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))
