# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 21:24:00 2023

@author: Alejandro
"""
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from tools.variables_with_lock import Object_with_Lock, Dict_with_Lock, List_with_Lock

from connections.pyRofex.pyRofex_connection import pyR
from connections.homebroker.hb_connection   import HB
from connections.cocos.cocos_connection     import appCocos
from connections.broker_connection import Broker_Connection
from connections.database import db_query, db_orders_manager
O_db_U = db_orders_manager.Orders_Updater



class Connections:
    modules = { m.__name__: m for m in [ pyR, appCocos, HB] }
    timeout = 10
    
    def __init__(self, accounts:list=[]):  
        """  El parámetro accounts es una lista con diccionarios en los que cada uno puede contener: module(str), 
        broker_id, nroComitente, dni o credentials (todos opcionales porque puede ser que reciba uno u otro dato).  """
        self.conns = Dict_with_Lock() # conns va a ser un objeto del tipo Dict_with_Lock que va a contener como clave el conn_id y
                                      # como valor un objeto del tipo Object_with_Lock con la instancia de conexión como objeto.
        self.logs = List_with_Lock()
        
        self.TPE_for_sending_orders = ThreadPoolExecutor(max_workers=32)
        self.orders_db_updater = O_db_U(start=True)
        
        self.add_connections(accounts)
        
                
    def add_connections(self, accounts:list=[]):
        with ThreadPoolExecutor() as executor:
            for future in as_completed([executor.submit(self._new_conn, acct) for acct in accounts], timeout=self.timeout):
                try: 
                    c = future.result()
                    if isinstance(c, Broker_Connection):
                        self.conns[c.credentials.get('conn_id')] = Object_with_Lock(c) 
                    elif c is not None: print(' Durante una conexión se produjo un error no identificado. Retorno future: {}'.format(c)) 
                except Exception as e:
                    print('\n Durante una conexión se produjo la siguiente excepción: \n {} {}'.format(type(e), str(e)))
                    self.logs += [traceback.format_exc()]
                    
    def _get_conn(self, conn_id:int):  
        return self.conns[conn_id].get_obj()
            
    def _new_conn(self, account:dict):
        """ La lógica en esta función hace primar el valor de module sobre el el resto de las opciones. """
        
        if not isinstance(account, dict):
            if account is not None: raise Exception(' El tipo de datos account es incorrecto: {}'.format(type(account)))
            else: account = dict(module=list(Connections.modules)[0]) 
        
        credentials = db_query.get_credentials(look_for=account) 
        
        if credentials.get('conn_id') in self.conns: 
            return print(' Ya hay una conexión para conn_id {} - module {}, broker_id {}, nroComitente {} '.format(
                          credentials['conn_id'], credentials['module'], credentials['broker_id'], credentials['nroComitente']))
        
        return Connections.modules[credentials.get('module')](account=credentials, orders_db_updater=self.orders_db_updater)

            
    def send_orders(self, orders:[list[dict], pd.DataFrame], timeout=None):
        
        if isinstance(orders, list):
            orders = pd.DataFrame(orders)
            
        if not isinstance(orders, pd.DataFrame):
            raise Exception(' El tipo de dato es incorrecto.')
            
        orders.sort_values(by='conn_id', inplace=True)
            
        with self.conns as conns:
            for conn_id in orders['conn_id'].unique():
                conns[conn_id].send_orders(orders[orders.conn_id==conn_id])
