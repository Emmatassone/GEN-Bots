# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 21:24:00 2023

@author: Alejandro
"""
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from tools.variables_with_lock import Object_with_Lock, Dict_with_Lock, List_with_Lock

# Con las siguientes líneas importo directamente la clase en lugar del modulo para poder instanciarlo directamente.
from connections.pyRofex.pyRofex_connection import pyR
from connections.homebroker.hb_connection   import HB
from connections.cocos.cocos_connection     import appCocos
from connections.broker_connection import Broker_Connection
from connections.database import db_query, db_orders_manager
O_db_U = db_orders_manager.Orders_Updater



class Connections:
    # Para acceder a una variable externa dentro de una clase, generalmente debes proporcionar esa
    # variable como un argumento al constructor de la clase o configurarla como un atributo de clase así:
    modules = { m.__name__: m for m in [ pyR, appCocos, HB] }  # Si una alyc tiene habilitado más de un módulo el orden en que está este diccionario es el que se va a utilizar por defecto cuando el dato del modulo no es pasado como parámetro.
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
        # Ver la opción de no iniciar nuevamente una conexion que ya existe
        with ThreadPoolExecutor() as executor:
            for future in as_completed([executor.submit(self._new_conn, acct) for acct in accounts], timeout=self.timeout):
            # En lugar de .map me conviene usar .submit ya que con el primero no se podrá ejecutar codigo con el retorno obtenido (como con as_completed) a medida que que los hilos vayan terminando.
                try: 
                    c = future.result()
                    if isinstance(c, Broker_Connection):
                        self.conns[c.credentials.get('conn_id')] = Object_with_Lock(c)  # Dict_with_Lock self.conns ya está protegido contra bloqueos en este método.
                    elif c is not None: print(' Durante una conexión se produjo un error no identificado. Retorno future: {}'.format(c)) 
                except Exception as e:
                    print('\n Durante una conexión se produjo la siguiente excepción: \n {} {}'.format(type(e), str(e)))
                    self.logs += [traceback.format_exc()]  # traceback.print_exc()
                    
    def _get_conn(self, conn_id:int):  
        # Para obtener la referencia a la ubicación en memoria. No debe ser usado directamente
        # ya que retorna el objeto sin el lock tomado.
        return self.conns[conn_id].get_obj()
            
    def _new_conn(self, account:dict):
        """ La lógica en esta función hace primar el valor de module sobre el el resto de las opciones. """
        
        if not isinstance(account, dict):
            if account is not None: raise Exception(' El tipo de datos account es incorrecto: {}'.format(type(account)))
            else: account = dict(module=list(Connections.modules)[0])  # Si account is None la ejecución va a continuar y va a conectarse con la primer cuenta que obtenga con el primer modulo de Credentials.modules
        
        credentials = db_query.get_credentials(look_for=account)  # Si get_credentials no obtiene credenciales válidas lanza una excepción.
        
        if credentials.get('conn_id') in self.conns: 
            return print(' Ya hay una conexión para conn_id {} - module {}, broker_id {}, nroComitente {} '.format(
                          credentials['conn_id'], credentials['module'], credentials['broker_id'], credentials['nroComitente']))
        
        return Connections.modules[credentials.get('module')](account=credentials, orders_db_updater=self.orders_db_updater)
        """
        conn = Connections.modules[credentials.get('module')](account=credentials)
        if isinstance(conn, Broker_Connection):
            self.conns[conn.credentials.get('conn_id')] = Object_with_Lock(conn)  # Dict_with_Lock self.conns ya está protegido contra bloqueos en este método.
        else: print(' Durante una conexión se produjo un error no identificado. conn: {}'.format(conn))
        """
            
    def send_order(self, order):
        with self.conns as a:
            # validar orden antes ?
            a[order.broker_id, order.nroComitente].conn.send_order(order)
            
    def send_multiple_orders(self, accounts:list, df):  # ver de iniciar una conexión para una orden cuyos datos de cuentas no tiene una conexión iniciada.        
        """ accounts es una lista de tuplas que contienen los datos (broker_id, nroComitente, module_str)
        """
        
        # con as_completed NO ir guardando el retorno de la función en la base de datos de las ordenes enviadas sino hacerlo en la propia funcion de la clase especifica de conexión.
        i=0
        print(accounts, df)
        with self.conns as conns:
            connected_accounts = conns.keys()
            # set(accounts).difference(connected_accounts)
        accounts_to_connect = []
        for broker_id, nroComitente, module_str in set(accounts).difference(connected_accounts):
            accounts_to_connect.append({'broker_id': broker_id, 'nroComitente': nroComitente, 'module': module_str})               
        self.add_connections(accounts_to_connect)
        with self.conns as conns:
            for acct in accounts:
                print(acct)
                for index, row in df.iterrows():
                    i+=1
                    print('\n\n ejecucion nro: {} \n\n'.format(i))
                    print(row)
                    #print(order_class.get(acct[-1]))
                    order=None #order = order_class.get(acct[-1])(*iter(row))
                    
                    # self.TPE_for_sending_orders.submit(conns.get(acct).send_order, order)
                    if acct[-1] == 'pyR': print('\n',order.ticker,'\n')
                    print(conns.get(acct).send_order, order)

