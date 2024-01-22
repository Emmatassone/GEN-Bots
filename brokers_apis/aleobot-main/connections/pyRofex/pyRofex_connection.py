# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:51:31 2023

@author: Alejandro
"""

from datetime import datetime
import pandas as pd
import requests

import pyRofex

# import Data, Tools

from .primaryURLs import primaryURLs
from connections.common import brokers
from connections.common import securities
from tools import file_manager

from connections.broker_connection import Broker_Connection

# module_alycs = [brokers.veta_id, ] # Data.cocos

class Order:
   pass

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
        pyRofex.cancel_order_via_websocket(message["orderReport"]["clOrdId"])

    # 7-Handler will receive an Order Report indicating that the order is cancelled (will print it)
    if message["orderReport"]["status"] == "CANCELLED":
        print("Order with ClOrdID '{0}' is Cancelled.".format(message["orderReport"]["clOrdId"]))
    
def error_handler(message):
    print("Error Message Received: {0}".format(message))

def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))

class pyR(Broker_Connection):
    Order = Order
    alycs = [brokers.veta_id, ]
    url = {'login': 'https://api.veta.xoms.com.ar/auth/getToken',
           }
    log = {}
    
    # def __init__(self, broker_id=brokers.veta_id, dni=accounts_data.aleben):
    def __init__(self, account:dict=None):
        print(' account: {} \n'.format(account))
        (account:= {} if account is None else account).update(dict(module='pyR'))  # Con esta línea aseguro el módulo correcto.
        if len(account) == 1 and 'module' in account: account.update(dict(broker_id=284))  # Broker por defecto (si solo se aporta el modulo o nada).
        super().__init__(account=account)  # Llama a login()
        
    def login(self):
        super().login()
        pyRofex._set_environment_parameter("url", primaryURLs[self.credentials['broker_id']]['api_url'], pyRofex.Environment.LIVE) 
        pyRofex._set_environment_parameter("ws",  primaryURLs[self.credentials['broker_id']]['ws_url' ], pyRofex.Environment.LIVE)
        print( 'X-Username: ', self.credentials['user'], 'X-Password:', self.credentials['password'] ) 
        pyRofex.initialize(user        = self.credentials['user'],
                           password    = self.credentials['password'], 
                           account     = self.nroComitente,
                           environment = pyRofex.Environment.LIVE)
        print(' --- Login Exitoso ---')
        # 3-Initialize Websocket Connection with the handlers
        print(' Conectando con cuenta Nº {} ( Broker {} ) '.format(self.nroComitente, self.credentials['broker']))
        pyRofex.init_websocket_connection(order_report_handler=order_report_handler,
                                          error_handler=error_handler,
                                          exception_handler=exception_handler)
        print(' --- Conexión Exitosa ---')
        # 4-Subscribes to receive order report for the default account
        print(' Suscribiendo a {} {}'.format(None, None))
        pyRofex.order_report_subscription()
        print(' Suscripción Exitosa.')
        
    def attain_new_token(self):
         headers = {'X-Username': self.credentials['user'], 
                    'X-Password': self.credentials['password'] } 
         print( 'X-Username: ', self.credentials['user'], 'X-Password:', self.credentials['password'] ) 
         
         
         
         self.log['new_token_response'] = response = requests.post(self.url['login'], headers=headers)
         if response.status_code < 400 :
             self.auth_token = 'Bearer {}'.format(response.headers['X-Auth-Token'])
           # self.headers = { 'Authorization': self.auth_token, 'x-account-id': str(self.nroComitente) }
             print(' --- Login Exitoso ---')
             if file_manager.save_to_txt(self.auth_token, 'veta_token_'+str(self.nroComitente), path=brokers.token_path):
                 print(' Token guardado en archivo.')
             else: print(' El token NO pudo ser guardado en archivo.')
             return True
         else: print(' --- El usuario no pudo ser autenticado ---'); return False

    def all_orders_status(self):
        url='https://api.veta.xoms.com.ar/rest/order/all?accountId={}'.format(self.nroComitente)
        return requests.get(url, headers = {'X-Auth-Token': self.auth_token}).json()

    
        
    def send_order(self, order:Order):  # symbol, price, size, op_type='buy', settlement='spot'):
        print(' Enviando órden: {} {} {} {} nominales a $ {}'.format(
               order.op_type, order.settlement, order.symbol, order.size, order.price))
        pyRofex.send_order_via_websocket(ticker=order.ticker, side=order.op_type, size=order.size,
                                         order_type=pyRofex.OrderType.LIMIT, price=order.price)
        print(' Orden nro {} enviada exitosamente:'.format(order.number))
        print('  {} {} {} {} nominales a $ {} '.format(
               order.op_type, order.settlement, order.symbol, order.size, order.price))
        
        
    def send_multiple_orders(self, df):  # ya el dataframe podría venir cargado con un listado de objetos Order
        orders=[]
        for index, row in df.iterrows():
            try:
                orders += [Order(*iter(row))]
                self.send_order(orders[-1])
            except Exception as exception:
                print(' DataException. {} '.format(str(exception)))
                continue
        return orders
        

        
        
        

class Order:    
#   status_map = [ 'CREATED', 'REJECTED', 'PENDING', 'OFFERED', 'PARTIAL', 'COMPLETED', 'CANCELLED', 'BLOCKED' ]
    status_map = { 'CREATED'  :  0,
                   'REJECTED' : -1,
                   'PENDING'  :  1, 
                   'OFFERED'  :  2,
                   'PARTIAL'  :  3,
                   'COMPLETED':  4,
                   'CANCELLED': -2,
                   'BLOCKED'  :  5, }

    def __init__(self, symbol, price, size, op_type='buy', settlement='spot'):
    
        if symbol in securities.symbols:
            self.symbol = symbol
            if settlement in securities.settlements:
                self.settlement = settlement
                ticker = securities.ticker_mask(symbol, settlement)
                if ticker in securities.tickers: self.ticker = ticker
            else: raise Exception(' Plazo inválido!')
        else: raise Exception(' Símbolo inválido!')
        
        if float(price) > 0: self.price = float(price)
        else: raise Exception(' Precio inválido!')
        
        if int(size) > 0: self.size = int(size)
        else: raise Exception(' Cantidad inválida!')
        
        if op_type.lower() in ['buy', 'sell']: self.op_type = pyRofex.Side.BUY if op_type.lower()=='buy' else pyRofex.Side.SELL
        else: raise Exception(' Operación inválida!')        

        
        self.status = self.status_map['CREATED']
        self.number = 0
        self.original_size = 0
        self.cancellable = True
        self.remaining_size = self.size
        self.datetime = pd.to_datetime(datetime.now())
        
    def to_df(self):
        df = pd.DataFrame([self.__dict__])
        df.set_index('number')
        return df
    
    def to_hb_df(self):
        df = self.to_df()
        df.drop(['original_size'], axis=1, inplace=True)
        df.rename(columns={ 'op_type': 'operation_type', 'number': 'order_number' }, inplace=True)
        df['operation_type'] = df['operation_type'].str.upper()
        status_map_inverted = {v: k for k, v in self.status_map.items()}
        df['status'].replace(status_map_inverted, inplace=True)
        df['total']=round(df['price']*df['size']/100,4)
        df.set_index('order_number', inplace=True)
        df = df.reindex(columns=['symbol', 'settlement', 'operation_type', 'size', 'price',
                            'remaining_size', 'datetime', 'status', 'cancellable', 'total'])
        return df   # uso: df_hb.combine_first(df) siendo df el que retorna esta funcion
    
    def p(self):
        print(' Order number {}: '.format(self.number))
        print(' {} {} {} {} nominales a $ {}'.format(self.op_type, self.settlement, self.symbol, self.size, self.price))
        
    @staticmethod
    def build_from_hb_df(df):
        return df # ver si conviene retornar df, np.array o lista con objetos Order (por el tema velocidad)

# connection_class = pyR