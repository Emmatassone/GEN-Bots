# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro
"""

import threading
import pandas as pd

from tools.file_manager import config_read
from tools import simple_filter as sf
from connections.database import db_query, db_map
from connections.helpers.orders_helpers import status_filters


def get_default_account():
    account_data = {k: (int(v) if v.isdigit() else v) for k,v in config_read()['Credentials'].items()}
    account_data['nroComitente'] = account_data.pop('nrocomitente')
    account_data['conn_id'] = 1 
    return account_data


def get_credentials(account_data:dict):
    if not isinstance(account_data, dict): raise Exception(f' DataTypeError. {account_data} no es del tipo dict.')
    
    if account_data.get('checked'): return account_data
    
    if config_read()['Data_Storage_Settings'].getboolean('use_database'):
        return db_query.get_credentials(look_for=account_data)
    
    missing_values = {'module', 'nroComitente', 'dni', 'user', 'password', 'conn_id'} - set(account_data.keys())
    if len(missing_values) > 0: raise Exception(' AttributeError. Faltan los siguientes datos: ', missing_values)
    
    for key in db_map.Credentials.attributes_names:
        account_data.setdefault(key, '')
    account_data['checked'] = True
    
    return account_data


class Get_Orders_Status:
    def __init__(self):
        dss = config_read()['Data_Storage_Settings']
        self.use_dataframe = dss.getboolean('use_dataframe')
        self.use_database  = dss.getboolean('use_database')
        if self.use_dataframe:
            self.df_lock = threading.Lock()
            self.df_orders = db_map.Orders.empty_df()
        if self.use_database: 
            self.db_orders = db_query.DataBase_Orders_Query()
            
    def df_updater(self, listener):
        while not listener.stop_event.is_set():
            data = listener.queue.get()
            
            if isinstance(data, tuple) and all(isinstance(d, dict) for d in data):
                with self.df_lock:
                    sf.filtrar(self.df_orders, status=filters)
                    pd.concat([df_orders, pd.DataFrame([nuevo_registro])], ignore_index=True) 
                
                
                obj = Query.build(session=sess, tables=[table], filters=dict(equal_to=data[0])).one()
                if obj is not None:
                    for k,v in data[1].items():
                        setattr(obj, k, v)
            elif not isinstance(data, dict):
                raise Exception(' DataTypeError. Tipo de datos para actualizar orders_dataframe es incorrecto.')
            else:
                if any(data.get(k) is None for k in table_keys):  # any es mas eficiente que all ya que retorna ante el primer True.
                    sess.add(table(**data))
                else:
                    obj = sess.get(table, (data[k] for k in table_keys))
                    if obj is None: 
                        sess.add(table(**data))
                    else:
                        for k,v in data.items():
                            setattr(obj, k, v)
            if not listener.queue.empty(): continue
            
    
    def all_(self):
        if self.use_dataframe:
            with self.df_lock:
                return self.df_orders
        return self.db_orders.get_all()
        
    def pending(self):
        if self.use_dataframe:
            with self.df_lock:
                return sf.filtrar(self.df_orders, status=status_filters.get('pending'))
        return self.db_orders.get_pending()
    
    def get_filled(self, include_partially=False):
        if self.use_dataframe:
            filters = status_filters.get('filled_and_partially') if include_partially else status_filters.get('filled')
            with self.df_lock:
                return sf.filtrar(self.df_orders, status=filters)
        return self.db_orders.get_pending(include_partially)
    
    
    
    
    