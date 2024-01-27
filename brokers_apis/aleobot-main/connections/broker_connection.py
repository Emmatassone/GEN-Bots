# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 21:24:00 2023

@author: Alejandro
"""

from connections.database import db_query


class Broker_Connection:
            
        ##################################################
        ### Proteger los objetos del bloqueo con locks ###
        ##################################################
    
    def __init__(self, account:dict=None):  #, db_session=None
        """  Recibe un diccionario llamado account cuyas claves pueden ser broker_id, nroComitente, dni, module, email, user.  """
        self.credentials = db_query.get_credentials(look_for=account)  # Si get_credentials no obtiene credenciales válidas lanza una excepción.
        self.nroComitente = self.credentials['nroComitente']
        self.token = self.credentials['conn_token']
        if self.credentials['module'] != 'HB': self.login()  # Corregir clase HB para eliminar restriccion para hacer login.
        
        # self.ordersTPE = ThreadPoolExecutor()   ver si conviene conservar el executor para reutilizar los hilos
        
    def login(self):
        print(' Iniciando sesión con cuenta Nº {} - {}: '.format(self.nroComitente, self.credentials['nombreCompleto']))
        print(' Modulo: {} ( Broker {} ) '.format(self.credentials['module'], self.credentials['broker_name']))
        # Extender este método en las clases hijas con la sentencia super().login()
        
    def __enter__(self):   # Con esto puedo utilizar la clase con la declaración with. Ejemplo: with HB() as hb: ...
        return self
        
    def __exit__(self, *args):   # Con esto puedo utilizar la clase con la declaración with. Ejemplo: with HB() as hb: ...
        # El método __exit__ siempre recibe cuatro argumentos: el tipo de excepción (si hay una excepción), el valor de excepción 
        # (si hay una excepción), y la traza de la pila (si hay una excepción), así como el objeto de contexto original.
        # La forma de tomar esos argumentos sería reemplazar *args por exception_type, exception_value y traceback
        self.logout()  ## ??????? falta implementar


    def send_order(self, order):  # symbol, price, size, op_type='buy', settlement='spot'):
        print(' Enviando órden: {} {} {} {} nominales a $ {}'.format(
               order.op_type, order.settlement, order.instrument, order.size, order.price))
        return self._send_order(order)
        


    
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
    