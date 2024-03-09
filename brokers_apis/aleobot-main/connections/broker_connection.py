# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 21:24:00 2023

@author: Alejandro
"""

from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from tools.custom_thread_classes import run_in_TPE
from connections.helpers import query_handler as query
import global_variables



class Broker_Connection:
    
    def __init__(self, account:dict=None):  #, db_session=None
        """  Recibe un diccionario llamado account cuyas claves pueden ser broker_id, nroComitente, dni, module, email, user.  """
        self.credentials = query.get_credentials(account)  # Si get_credentials no obtiene credenciales válidas lanza una excepción.
        self.nroComitente = self.credentials['nroComitente']
        self.token = self.credentials['conn_token']
        
        self.TPE = ThreadPoolExecutor(max_workers=12)
        self.ordersTPE = ThreadPoolExecutor(max_workers=32)
        
        global_variables.initialize()
        self.orders_data = global_variables.orders_data
        
        
    def login(self):
        print(' Iniciando sesión con cuenta Nº {} - {}: '.format(self.nroComitente, self.credentials['nombreCompleto']))
        print(' Modulo: {} ( Broker {} ) '.format(self.credentials['module'], self.credentials['broker_name']))
        # Extender este método en las clases hijas con la sentencia super().login()
        
    def logout(self):
        print(' Cerrando sesión con cuenta Nº {} - {}: '.format(self.nroComitente, self.credentials['nombreCompleto']))
        print(' Modulo: {} ( Broker {} ) '.format(self.credentials['module'], self.credentials['broker_name']))
        
    def connect(self):
        print(' Desconectando cuenta Nº {} - {}: '.format(self.nroComitente, self.credentials['nombreCompleto']))
        print(' Modulo: {} ( Broker {} ) '.format(self.credentials['module'], self.credentials['broker_name']))
        
    def __enter__(self):
        return self
        
    def __exit__(self, *args):   
        self.logout()  ## ??????? falta implementar
        
        
    @run_in_TPE
    def _oper_orders(self, oper:str, orders:[list[dict], pd.DataFrame], timeout=None):
        
        if isinstance(orders, pd.DataFrame):
            orders = [order._asdict() for order in orders.itertuples(index=False)]
            
        if not isinstance(orders, list):  # and all(isinstance(i, dict) for i in orders)
            raise Exception(' El tipo de dato es incorrecto.')
        
        self.ordersTPE.map(getattr(self, oper), orders, timeout=timeout, chunksize=10)  # [1]
    
    def send_orders(self, orders:[list[dict], pd.DataFrame], timeout=None):
        oper = 'send_order'
        self._oper_orders(oper, orders, timeout)
    
    def cancel_orders(self, orders:[list[dict], pd.DataFrame], timeout=None):
        oper = 'cancel_order'
        self._oper_orders(oper, orders, timeout)
        
        
        
    # def hb_get_market_data_snapshot(boards, ) # c.conns[4].hb_connection.online.get_market_snapshot()
    # c.conns[4].hb_connection.online._scrapping.get_securities('government_bonds',1)
        
    
""" Referencias:
    [1] - In map method of ThreadPoolExecutor the iterables are collected immediately rather than lazily.
          TPE._work_queue.qsize() para obtener la cantidad de tareas en cola en el ThreadPoolExecutor.
"""