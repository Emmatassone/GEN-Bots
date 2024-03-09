# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 21:24:00 2023

@author: Alejandro
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

import pandas as pd

from tools.variables_with_lock import Dict_with_Lock, List_with_Lock
from tools.custom_thread_classes import run_in_TPE

from connections.pyRofex.pyRofex_connection import pyR
from connections.homebroker.hb_connection   import HB
from connections.cocos.cocos_connection     import appCocos
from connections.broker_connection import Broker_Connection
from connections.helpers import query_handler as query
import global_variables


class Connections:
    # Para acceder a una variable externa dentro de una clase, generalmente debes proporcionar esa
    # variable como un argumento al constructor de la clase o configurarla como un atributo de clase así:
    modules = { m.__name__: m for m in [ pyR, appCocos, HB] }  # Si una alyc tiene habilitado más de un módulo el orden en que está este diccionario es el que se va a utilizar por defecto cuando el dato del modulo no es pasado como parámetro.
    timeout = 10
    
    def __init__(self, accounts:list=[]):  
        """  El parámetro accounts es una lista con diccionarios en los que cada uno puede contener: module(str), 
        broker_id, nroComitente, dni o credentials (todos opcionales porque puede ser que reciba uno u otro dato).  """
        self.conns = Dict_with_Lock()
        self.logs = List_with_Lock()  # Ver de usar un file con pyarrow
        self.TPE = ThreadPoolExecutor(max_workers=12)
        
        if accounts == []: accounts = [query.get_default_account()]
        self.add_connections(accounts)
        
        global_variables.initialize()
        self.orders_data = global_variables.orders_data
        
                
    def add_connections(self, accounts:list=[]):
        # Ver la opción de no iniciar nuevamente una conexion que ya existe
        with ThreadPoolExecutor() as executor:
            for future in as_completed([executor.submit(self._new_conn, acct) for acct in accounts], timeout=self.timeout):
            # En lugar de .map me conviene usar .submit ya que con el primero no se podrá ejecutar codigo con el retorno obtenido (como con as_completed) a medida que que los hilos vayan terminando.
                try: 
                    conn = future.result()
                    if isinstance(conn, Broker_Connection):
                        self.conns[conn.credentials.get('conn_id')] = conn
                    elif conn is not None: print(' Durante una conexión se produjo un error no identificado. Retorno future: {}'.format(conn)) 
                except Exception as e:
                    print('\n Durante una conexión se produjo la siguiente excepción: \n {} {}'.format(type(e), str(e)))
                    self.logs += [traceback.format_exc()]  # traceback.print_exc()
            
    def _new_conn(self, account:dict):
        credentials = query.get_credentials(account)  # Si get_credentials no obtiene credenciales válidas lanza una excepción.
        if credentials.get('conn_id') in self.conns: 
            return print(' Ya hay una conexión para conn_id {} - module {}, broker_id {}, nroComitente {} '.format(
                          credentials['conn_id'], credentials['module'], credentials['broker_id'], credentials['nroComitente']))
        
        return Connections.modules[credentials.get('module')](account=credentials)
                
    def get_conn(self, conn_id:int):
        return self.conns[conn_id]
    def __getitem__(self, conn_id:int):
        return self.conns[conn_id]
    
    def logout(self, conn_id):
        self.conns[conn_id].logout()
        
    def shutdown(self):
        for conn_id in self.conns.keys():
            self.logout(conn_id)
        self.TPE.shutdown()
    
    
    # @run_in_TPE
    def _oper_orders(self, oper:str, orders:[list[dict], pd.DataFrame], timeout=None):
        # ver de ya arrancar un hilo para hacer lo que sigue, o inclusive hacer un queue put
        if isinstance(orders, list):
            orders = pd.DataFrame(orders)
            
        if not isinstance(orders, pd.DataFrame):
            raise Exception(' El tipo de dato es incorrecto.')
            
        orders.sort_values(by='conn_id', inplace=True)
        
        for conn_id in orders.conn_id.unique():
            getattr(self.conns[conn_id], oper)(orders[orders.conn_id==conn_id])
            
    def send_orders(self, orders:[list[dict], pd.DataFrame], timeout=None):
        oper = 'send_orders'
        self._oper_orders(oper, orders, timeout)
    
    def cancel_orders(self, orders:[list[dict], pd.DataFrame], timeout=None): 
        oper = 'cancel_orders'
        self._oper_orders(oper, orders, timeout)
        
    def get_order_status(self, order_id):
        pass
        
    def get_all_orders(self, conn_id:int=None):
        df = self.orders_data.get.all_()
        return df if conn_id is None else df[df.conn_id.values==conn_id]
        
    def get_pending_orders(self, conn_id:int=None):
        df = self.orders_data.get.pending()
        return df if conn_id is None else df[df.conn_id.values==conn_id]
    
    def get_filled_orders(self, conn_id:int=None):
        pass
    
    def get_market_snapshot(self, board:str, settlement:int=0):
        """ A homebroker connection is needed. Otherwise will return None.
            board valid string values: options, accionesLideres, panelGeneral, cedears, rentaFija, letes, obligaciones
            settlement valid int values: 0 (spot), 1 (24hs), 2 (48hs)  """
        for conn in self.conns.values():
            if isinstance(conn, HB):
                return conn.get_market_snapshot(board, settlement)