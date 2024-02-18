# -*- coding: utf-8 -*-
"""
@author: Alejandro Ben 
"""

import numpy as np
import pandas as pd
import functools, operator
import threading

from tools import simple_filter as sf
from connections.common.securities import symbols, settlements   # Solución a 'ImportError' al ejecutar este archivo directamente como un script en Solucion_ImportError.txt

# nombre de las columnas del dataframe de ordene (el index es order_id)
orders_columns_names = ['account', 'datetime', 'symbol', 'settlement',
       'op_type', 'size', 'price', 'remaining', 'status', 'currency', 'amount']


orders_df = pd.DataFrame(columns=['order_number', 'datetime', 'symbol', 'settlement', 'operation_type', 'op_type',
                                  'size', 'price', 'remaining_size', ])  # , index=['order_number']) si le agrego order_number como index no será un df.empty a la hora de evaluarse en la funcion pending_orders

# nombre de las columnas del dataframe de ordene (el index es order_id)
orders_columns_names = ['account', 'datetime', 'symbol', 'settlement',
       'op_type', 'size', 'price', 'remaining', 'status', 'currency', 'amount']


def orderBookDict (symbols=symbols, settlements=settlements, firstRowOfBoxData = 2, boxdepth = 5):
    row = np.arange(firstRowOfBoxData, boxdepth*len(settlements)*len(symbols)+firstRowOfBoxData , boxdepth*len(settlements))
    # En lugar de retorna una tupla con 2 diccionarios retorno un unico diccionario ya que settlements y symbols nunca van a tener claves repetidas
    return { **dict(zip(symbols,row)), **dict(zip(settlements, range(0,len(settlements)*boxdepth,boxdepth) )) }


def orderBookDF (symbols=symbols, settlements=settlements, boxdepth = 5):
    multi_index = pd.MultiIndex.from_arrays([
        functools.reduce(operator.iconcat, [ [i]*boxdepth*len(settlements) for i in symbols ], []),
        functools.reduce(operator.iconcat, [ [i]*boxdepth for i in settlements ], [])*len(symbols),
        list(range(1,boxdepth+1))*(len(settlements)*len(symbols)),
        ], names=('symbol',	'settlement', 'position'))
    return pd.DataFrame(index=multi_index,columns=['bid_size',	'bid',	'bid_offers_count',	'ask_size',	'ask',	'ask_offers_count'])


def pending_orders(ordersList, lock=threading.Lock()):
    with lock:
        if not isinstance(ordersList, pd.DataFrame) or ordersList.empty: return orders_df
        df = sf.filtrar(ordersList, cancellable=True)  # devuelve una copia del df y no uno modificado. Sino para mantener la info original deberia hacer ordersList.copy()
    df = df.drop(['status','cancellable', 'total'], axis=1)  # devuelve una copia del df y no uno modificado. Sino para mantener la info original deberia hacer ordersList.copy()
    df['remaining_size'] = np.where(df['operation_type'].values=='BUY', df['remaining_size'].values, -1*df['remaining_size'].values )
    df.rename(columns={"operation_type": "op_type", "remaining_size": "remaining"}, inplace=True)
    # df.sort_values(by=['symbol','datetime','price'], inplace=True)
    df.sort_values(['symbol', 'op_type', 'price', 'datetime'], ascending=[True, False, False, True], inplace=True)
    df = df.reindex(columns=['datetime','symbol', 'settlement', 'op_type', 'size', 'price', 'remaining'])
    df['cancela'] = None
    return df


# Datos auxiliares App_Cocos :
    
app_cocos_data = {
    'orders_columns_new_names': { 
        'order_id_ext':     'account',
        'date':             'datetime',
        'ticker':           'symbol',
        'settlement_days':  'settlement',
        'order_type':       'op_type',
        'set_quantity':     'size',
        'set_price':        'price',
        'result_quantity':  'remaining',
        'set_amount':       'amount',    }, }

app_cocos_data['orders_empty_df'] = pd.DataFrame(columns=app_cocos_data['orders_columns_new_names'].values()).rename_axis('order_id')
     
    
    
