# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro
"""

import pandas as pd
from . import db_map, db_tools
from connections.helpers.orders_helpers import status_filters


def get_credentials(session=None, look_for:dict=None, exclude:dict=None, return_db_obj=False):
    """  Solo se admite un valor por key.  """
    
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


def save_order(order:db_map.Orders, session=None):
    return db_tools.query(session=session, method=db_tools.set_update, obj=order)

def get_orders(session=None, look_for:dict=None, look_for_any:dict=None, exclude:dict=None, 
               contains:dict=None, not_contains:dict=None, return_db_obj=False):
    
    tables  = [db_map.Orders]
    filters = dict(equal_to=look_for, equal_to_any=look_for_any, not_equal_to=exclude, 
                   contains=contains, not_contains=not_contains)
    
    rsp = db_tools.query(session=session, method=db_tools.get, tables=tables, filters=filters)
    if return_db_obj: return rsp
    
    return DataBase_Orders_Query.rsp_to_df(rsp)


class DataBase_Orders_Query:
    tables = [db_map.Orders]
    pending_filter = dict(equal_to_any={ 'status': status_filters.get('pending') })
    filled_filter  = dict(equal_to_any={ 'status': status_filters.get('filled')  })
    filled_and_partially = dict(equal_to_any={ 'status': status_filters.get('filled_and_partially') })
    
    def __init__(self):
        self.session = db_tools.db_conn.Session() # La session es unica en un mismo hilo (es la misma para todo)
        self.qry = db_tools.Query.partial_build(session=self.session, tables=self.tables, order_by=None)
        
    @classmethod
    def rsp_to_df(cls, rsp):
        if rsp == []: return db_map.Orders.empty_df() 
        return pd.DataFrame([order.data() for order in rsp]).set_index('id')
    
    def _get(self, qry):
        self.session.commit()
        return self.rsp_to_df(qry.all())
    
    def get_all(self):
        return self._get(self.qry())
    
    def get_pending(self):
        return self._get(self.qry(filters=self.pending_filter))
    
    def get_filled(self, include_partially=False):
        filters = self.filled_and_partially if include_partially else self.filled_filter
        return self._get(self.qry(filters=filters))
        
    def get_by(self, **filters):
        return get_orders(self.session, **filters)



def table_to_df(table_name:str, index_col:[str,list[str]]=None, session=None):
    # return pd.read_sql_table(table_name=table_name, con=session.bind)
    return db_tools.query(session=session, method=db_tools.table_to_df, table_name=table_name)
    """ timeit db_query.table_to_df('orders', index_col='id')
        45.8 ms ± 2.37 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
        es lo mismo que: 
        timeit db_query.get_orders()
        2.51 ms ± 54.1 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)  """
        

