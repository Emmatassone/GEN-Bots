# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro
"""

import pandas as pd

from connections.database import db_map, db_tools, db_conn

global_session = db_conn.Session()  # ??????????

    
# def _get_creds_obj(session=None, look_for:dict=None, exclude:dict=None)

def get_credentials(session=None, look_for:dict=None, exclude:dict=None, return_db_obj=False):
    # Hacer que por defecto se conecte con cualquier cuenta del modulo HB  ???
    """  Si look_for incluye el key 'checked'=True se retorna directamente, lo cual permite
         utilizar credenciales válidas pero no incluidas en la base de datos.
         Solo se admite un valor por key.  """
    
    if look_for is not None and look_for.get('checked'): return look_for  # Con esta línea puedo utilizar crendenciales que ya están validadas pero no guardadas en la base de datos.
    
    tables = [db_map.Credentials, db_map.Accounts, db_map.Persons, ]
    
    rsp = db_tools.query(session=session, method=db_tools.get, tables=tables, 
                         filters=dict(equal_to=look_for, not_equal_to=exclude), results=(0 if return_db_obj else 1))
    if rsp is None or rsp == []: raise Exception('\n No se han encontrado credenciales con los datos proporcionados: \n {}'.format(look_for))
    if return_db_obj: return rsp
    
    (credentials:= rsp.data()).update({'checked': True})
    return credentials


def save_token(account:dict, token:str, session=None):
    
    rsp = get_credentials(session=session, look_for=account, return_db_obj=True)
    if len(rsp) != 1: raise Exception('\n Con los datos proporcionados no se ha podido encontrar una cuenta única: \n {}'.format(account))
    
    rsp = db_tools.query(session=session, method=db_tools.put, obj=rsp[0], key='conn_token', value=token)
    print(' Token para cuenta {} guardado correctamente.'.format(account))
    

def new_order(order:dict, session=None):
    return save_order(db_map.Orders().set_data(dict), session=session)
    
def save_order(order:db_map.Orders, session=None):
    rsp = db_tools.query(session=session, method=db_tools.set_update, obj=order)
    print(rsp)
    return rsp

def get_orders(session=None, look_for:dict=None, exclude:dict=None, contains:dict=None, not_contains:dict=None, return_db_obj=False):
    
    tables  = [db_map.Orders]
    filters = dict(equal_to=look_for, not_equal_to=exclude, contains=contains, not_contains=not_contains)
    
    rsp = db_tools.query(session=session, method=db_tools.get, tables=tables, filters=filters)
    if return_db_obj: return rsp
    
    if rsp == []: return db_map.Orders.empty_df() 
    return pd.DataFrame([order.data() for order in rsp]).set_index('id')
    
def table_to_df(table_name:str, index_col:[str,list[str]]=None, session=None):
    # return pd.read_sql_table(table_name=table_name, con=session.bind)
    return db_tools.query(session=session, method=db_tools.table_to_df, table_name=table_name)
    """ timeit db_query.table_to_df('orders', index_col='id')
        45.8 ms ± 2.37 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
        es lo mismo que: 
        timeit db_query.get_orders()
        2.51 ms ± 54.1 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)  """
        

