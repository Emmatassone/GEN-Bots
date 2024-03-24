# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro
"""

import pandas as pd

from connections.database import db_map, db_tools



def get_credentials(session=None, look_for:dict=None, exclude:dict=None, return_db_obj=False):
    # Hacer que por defecto se conecte con cualquier cuenta del modulo HB  ???
    """  Si look_for incluye el key 'checked'=True se retorna directamente, lo cual permite
         utilizar credenciales válidas pero no incluidas en la base de datos.
         Solo se admite un valor por key.  """
    
    # El siguiente bloque habilita el uso de crendenciales que no están guardadas en la base de datos:
    if look_for is not None and look_for.get('checked'):
        diff = set(db_map.Credentials.attributes_names) - set(look_for.keys())
        if len (diff) == 0:
            return look_for  
        else: raise Exception(' AttributeError. Faltan los siguientes datos: ', diff)
    
    tables = [db_map.Credentials, db_map.Accounts, db_map.Persons, ]
    
    rsp = db_tools.query(session=session, method=db_tools.get, tables=tables, 
                         filters=dict(equal_to=look_for, not_equal_to=exclude), results=(0 if return_db_obj else 1))
    if rsp is None or rsp == []: raise Exception('\n No se han encontrado credenciales con los datos proporcionados: \n {}'.format(look_for))
    if return_db_obj: return rsp
    
    (credentials:= rsp.data_ext()).update({'checked': True})
    return credentials


def save_token(account:dict, token:str, session=None):
    
    rsp = get_credentials(session=session, look_for=account, return_db_obj=True)
    if len(rsp) != 1: raise Exception('\n Con los datos proporcionados no se ha podido encontrar una cuenta única: \n {}'.format(account))
    
    rsp = db_tools.query(session=session, method=db_tools.put, obj=rsp[0], key='conn_token', value=token)
    print(' Token para cuenta {} guardado correctamente.'.format(account))
        

def get_urls(module:str=None, return_:type[dict, pd.DataFrame]=dict, session=None):
    
    tables  = [db_map.Urls]
    filters = dict(equal_to=dict(module=module)) if module is not None else None
    order_by = [db_map.Urls.module, db_map.Urls.broker_id, db_map.Urls.key]
    
    rsp = db_tools.query(session=session, method=db_tools.get, tables=tables, 
                         filters=filters, order_by=order_by)
    
    if return_ is pd.DataFrame: return pd.DataFrame([url.data() for url in rsp])
    
    urls_dict = {}
    for url in rsp:
        (urls_dict.setdefault(url.module, {}) if module is None else
         urls_dict).setdefault(url.broker_id, {})[url.key] = url.address
    return urls_dict



def table_to_df(table_name:str, index_col:[str,list[str]]=None, session=None):
    # return pd.read_sql_table(table_name=table_name, con=session.bind)
    return db_tools.query(session=session, method=db_tools.table_to_df, table_name=table_name)
    """ timeit db_query.table_to_df('orders', index_col='id')
        45.8 ms ± 2.37 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
        es lo mismo que: 
        timeit db_query.get_orders()
        2.51 ms ± 54.1 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)  """
        

