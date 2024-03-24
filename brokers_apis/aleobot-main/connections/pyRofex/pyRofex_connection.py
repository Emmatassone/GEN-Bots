# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:51:31 2023

@author: Alejandro
"""

import uuid

import pyRofex

from ..broker_connection import Broker_Connection, db_query
from . import pyRofex_handlers as handlers
from .pyRofex_orders_helpers import settlements, side  #, orderType, timeInForce, market
from .pyRofex_wrapper import PyRofexWrapper
from .pyRofex_brokers_data import urls
import global_config


class pyR(Broker_Connection):
    class_name = 'pyR'
    use_wrapper = True
    
    def __init__(self, account:dict=None, **kwargs):
        
        (account:= {} if account is None else account).update(dict(module='pyR'))  # Con esta línea aseguro el módulo correcto.
        if len(account) == 1 and 'module' in account: account.update(dict(broker_id=284))  # Broker por defecto (si solo se aporta el modulo o nada).
        super().__init__(account=account, **kwargs)
        
        self.conn = (PyRofexWrapper if self.use_wrapper else pyRofex)(self.credentials['conn_id'])
        _urls = urls if not global_config.use_database else db_query.get_urls(self.class_name)
        for key, address in _urls[self.credentials['broker_id']].items():
            if key=='url': self.url = address
            self.conn._set_environment_parameter(key, address, pyRofex.Environment.LIVE)
            
        self.login()
        self.connect() # el constructor podría recibir el parámetro connect=True que define si hacer esto o no
        
    def login(self):
        super().login()  # el metodo de la clase padre podría llamar al de la clase hija haciendo self._login()
        
        self.conn.initialize( 
            user         = self.credentials['user'],
            password     = self.credentials['password'], 
            account      = self.nroComitente,
            environment  = pyRofex.Environment.LIVE,
            active_token = self.credentials['conn_token'])  # ver la conveniencia de dejar este argumento
        
        self.ws_conn   = self.conn.get_ws_conn()
        self.rest_conn = self.conn.get_rest_conn()
        print(' --- Login Exitoso ---')

        
    def logout(self):
        self.ws_conn.close()
    
    def connect(self):
        # 3-Initialize Websocket Connection with the handlers
        print(' Conectando con cuenta Nº {} ( Broker {} ) '.format(self.nroComitente, self.credentials['broker_name']))
        self.conn.init_websocket_connection(
            order_report_handler = handlers.order_report_handler,
            error_handler        = handlers.error_handler,
            exception_handler    = handlers.exception_handler, )
        print(' --- Conexión Exitosa ---')
        # 4-Subscribes to receive order report for the default account
        print(' Suscribiendo a {} {}'.format(None, None))
        self.conn.order_report_subscription()
        print(' Suscripción Exitosa.')
        
    def send_order(self, order:dict):  # symbol, price, size, op_type='buy', settlement='spot'):
        # c._get_conn(1).send_order({'symbol': 'AL30', 'settlement': 0, 'side': 1, 'price': 45000, 'size': 1})
        
        order['id_int']  = uuid.uuid4()
        order['conn_id'] = self.credentials['conn_id']
        # self.orders_db_updater.queue.put(order)
        
        ticker = 'MERV - XMEV - {} - {}'.format(order.get('symbol'), settlements.get(order.get('settlement')) )
        self.ws_conn.send_order(
            account            = self.nroComitente,
            ticker             = ticker,
            side               = side.get(order.get('op_type')),
            size               = order.get('size'),
            order_type         = order.get('order_type', pyRofex.OrderType.LIMIT),
            price              = order.get('price'),
            all_or_none        = order.get('all_or_none', False),
            market             = order.get('market', pyRofex.service.Market.ROFEX),
            time_in_force      = order.get('time_in_force', pyRofex.service.TimeInForce.DAY),
            cancel_previous    = order.get('cancel_prev', False),
            iceberg            = order.get('iceberg', False),
            expire_date        = order.get('expire_date', None),
            display_quantity   = order.get('display_qty', None),
            ws_client_order_id = order.get('id_int'), )
        
        print(' Orden nro {} enviada exitosamente:'.format(order.get('id_int')))
        print('  {} {} {} {} nominales a $ {} '.format(
               side.get(order.get('op_type')), 
               order.get('size'), 
               order.get('symbol'), 
               settlements.get(order.get('settlement')), 
               order.get('price'), ))
        return order['id_int']

    def get_all_orders_status(self):
        return self.conn.get_all_orders_status()
    
    def get_account_position(self):
        return self.conn.get_account_position()
    
    def get_detailed_position(self):
        return self.conn.get_detailed_position()
    
    def get_account_report(self):
        return self.conn.get_account_report()
    
    def get_detailed_instruments(self):
        rsp = self.conn.get_detailed_instruments()
        return rsp.instruments if rsp.get('status') == 'OK' else None
    
    def market_data_subscription(self, tickers:list=[], depth=1):
        entries=[ pyRofex.MarketDataEntry.BIDS,
                  pyRofex.MarketDataEntry.OFFERS, ]
        return self.conn.market_data_subscription(tickers=tickers, entries=entries, depth=depth)
    
    
    """
    def (self):
        return self.conn.()
    
    def (self):
        return self.conn.()
    
    def (self):
        return self.conn.()
    
    def (self):
        return self.conn.()
    """
    


# dir(pyRofex.service)
# Out[123]: 
['ApiException',
 'Environment',
 'Market',
 'MarketDataEntry',
 'RestClient',
 'TimeInForce',
 'WebSocketClient',
 '__builtins__',
 '__cached__',
 '__doc__',
 '__file__',
 '__loader__',
 '__name__',
 '__package__',
 '__spec__',
 '_set_environment_parameter',
 '_set_environment_parameters',
 '_validate_account',
 '_validate_environment',
 '_validate_handler',
 '_validate_initialization',
 '_validate_market_data_entries',
 '_validate_parameter',
 '_validate_websocket_connection',
 'add_websocket_error_handler',
 'add_websocket_market_data_handler',
 'add_websocket_order_report_handler',
 'cancel_order',
 'cancel_order_via_websocket',
 'close_websocket_connection',
 'get_account_position',
 'get_account_report',
 'get_all_instruments',
 'get_all_orders_status',
 'get_detailed_instruments',
 'get_detailed_position',
 'get_instrument_details',
 'get_instruments',
 'get_market_data',
 'get_order_status',
 'get_segments',
 'get_trade_history',
 'getfullargspec',
 'globals',
 'init_websocket_connection',
 'initialize',
 'logging',
 'market_data_subscription',
 'order_report_subscription',
 'remove_websocket_error_handler',
 'remove_websocket_market_data_handler',
 'remove_websocket_order_report_handler',
 'send_order',
 'send_order_via_websocket',
 'set_default_environment',
 'set_websocket_exception_handler']     
