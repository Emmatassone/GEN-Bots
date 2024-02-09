# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 21:24:00 2023

@author: Alejandro
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

import pandas as pd

from connections.database import db_query, db_orders_manager
O_db_U = db_orders_manager.Orders_Updater

class Broker_Connection:
    
    #urls = db_query.
            
        ##################################################
        ### Proteger los objetos del bloqueo con locks ###
        ##################################################
    
    def __init__(self, account:dict=None, orders_db_updater=O_db_U()):  #, db_session=None
        """  Recibe un diccionario llamado account cuyas claves pueden ser broker_id, nroComitente, dni, module, email, user.  """
        self.credentials = db_query.get_credentials(look_for=account)  # Si get_credentials no obtiene credenciales válidas lanza una excepción.
        self.nroComitente = self.credentials['nroComitente']
        self.token = self.credentials['conn_token']
        
        self.ordersTPE = ThreadPoolExecutor(max_workers=32)
        self.orders_db_updater = orders_db_updater.start()  # Si en el constructor se crea la instancia con start=True, se va a crear el thread aun recibiendo un valor para este parámetro del constructor, hilo que va a quedar en memoria corriendo en memoria sin uso.
        # self.session = db_query.new_scoped_session()
        
        
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
        
    def __enter__(self):   # Con esto puedo utilizar la clase con la declaración with. Ejemplo: with HB() as hb: ...
        return self
        
    def __exit__(self, *args):   # Con esto puedo utilizar la clase con la declaración with. Ejemplo: with HB() as hb: ...
        # El método __exit__ siempre recibe cuatro argumentos: el tipo de excepción (si hay una excepción), el valor de excepción 
        # (si hay una excepción), y la traza de la pila (si hay una excepción), así como el objeto de contexto original.
        # La forma de tomar esos argumentos sería reemplazar *args por exception_type, exception_value y traceback
        self.logout()  ## ??????? falta implementar

    def send_orders(self, orders:[list[dict], pd.DataFrame], timeout=None):
                
        if isinstance(orders, pd.DataFrame):
            orders = [order._asdict() for order in orders.itertuples(index=False)]
        if not isinstance(orders, list):  # and all(isinstance(i, dict) for i in orders)
            raise Exception(' El tipo de dato es incorrecto.')
        return self.ordersTPE.map(self.send_order, orders, timeout=timeout, chunksize=10)
        # in map method the iterables are collected immediately rather than lazily.
        """
        if   isinstance(orders, list):  # and all(isinstance(i, dict) for i in orders)
            futures = [self.ordersTPE.submit(self._send_order, order) for order in orders]
        elif isinstance(orders, pd.DataFrame): 
            futures = [self.ordersTPE.submit(self._send_order, order._asdict()) for order in orders.itertuples(index=False)]
        else: raise Exception(' El tipo de dato es incorrecto.')
        for future in as_completed(futures, timeout=timeout):  
            yield future.result()
        """
            
        """        
        print(' Enviando órden: {} {} {} {} nominales a $ {}'.format(
               order.op_type, order.settlement, order.symbol, order.size, order.price))
        return self._send_order(order)
        """


    
    """
    def stop_connection(self):
        if self.module == HB: self.conn.__exit__
        
    def data_market_subscribe(self, symbols=[], settlements=[]):
        if self.module == HB:
            self.conn.subscribe_order_book(symbols=symbols, settlements=settlements)
            return True
        if self.module == pyR:
            return False
        return False
        
    def subscribed(self):
        if self.module == HB:
            return self.conn.connected()
        if self.module == pyR:
            return False
        return False
    
    def set_data_destination(destination):
        pass
    """
    