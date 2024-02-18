# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 12:51:40 2024

@author: Alejandro
"""
import global_config
from connections.connection import Connections
from connections.pyRofex.pyRofex_connection import pyR
from connections.homebroker.hb_connection   import HB

from connections.pyRofex import pyRofex_brokers_data


global_config.use_database = False

##################################################
###                Server Info                 ###
##################################################
global_config.server_info = dict(user='', password='', database='', port=3310, host='')  # En caso de no usar dejar esta linea como está



##################################################
###    Referencias para el envio de órdenes    ###
##################################################

settlements  = { 0: 'spot',
                 1: '24hs',
                 2: '48hs', }

op_type_dict = { 1: 'buy',
                -1: 'sell', }

# En connections/pyRofex/pyRofex_handlers.py están las funciones que reciben los reportes de 
# las ordenes (order_report_handler) así como los de errores y excepciones. Modificarlas directamente
# para personalizarlas pero manteniendo la firma.


##################################################
###                  pyRofex                   ###
##################################################

print(pyRofex_brokers_data.urls)
# añadir nuevos brokers haciendo:
# pyRofex_brokers_data.urls[broker_id: {'url':'', 'ws':''}]


credential_pyR = {'broker_id': 284,
                  'nroComitente': 44444,
                  'module': 'pyR',
                  'user': '20123456781',
                  'password': 'XXXXXXXX',
                  'conn_id': 1,
                  'conn_token': '',
                  'nombreCompleto': 'Juan Perez',
                  'broker_name': 'Veta Capital S.A.',
                  'dni': 23123123,
                  'checked': True}
# Dejar conn_token y checked como están. Usar un conn_id único (int positivo) para cada conexión.


connPyR = pyR(credential_pyR)

order=dict(symbol='AL30', op_type=1, price=45000, size=1, settlement=2)
connPyR.send_orders([order.copy()])

print(connPyR.get_all_orders_status())


instruments = [ "MERV - XMEV - AL30 - CI",
                "MERV - XMEV - GD30 - CI",
                "MERV - XMEV - AL30D - CI",
                "MERV - XMEV - GD30D - CI", ]

connPyR.market_data_subscription(tickers=instruments, depth=5)  # depth: 1-5




##################################################
###                 HomeBroker                 ###
##################################################

credential_HB =  {'broker_id': 284,
                  'nroComitente': 44444,
                  'module': 'HB',
                  'user': '20123456781',
                  'password': 'XXXXXXXX',
                  'conn_id': 2,
                  'conn_token': '',
                  'nombreCompleto': 'Juan Perez',
                  'broker_name': 'Veta Capital S.A.',
                  'dni': 23123123,
                  'checked': True}
# Dejar conn_token y checked como están. Usar un conn_id único (int positivo) para cada conexión.


def HB_order_book_handler(online, quotes):
    print(quotes)
    
def HB_securities_handler(online, quotes):
    print(quotes)


conn = Connections([credential_HB])

connHB  = HB(credential_HB)

connHB.set_on_order_book_callback(HB_order_book_handler)
connHB.set_on_securities_callback(HB_securities_handler)

connHB.subscribe_order_book(symbols=['AL30'], settlements=['spot'], subscription='order_book')

# El o
# pyhomebroker/pyhomebroker/online/online.py
# def get_board_for_request(self, board):
boards = {
    'bluechips': 'accionesLideres',
    'general_board': 'panelGeneral',
    'cedears': 'cedears',
    'government_bonds': 'rentaFija',
    'short_term_government_bonds': 'letes',
    'corporate_bonds': 'obligaciones'}

# Lo siguiente funciona pero falta corregir para que sea mas entendible:
connHB.subscribe_order_book(symbols=['government_bonds'], settlements=['spot', '48hs'], subscription='securities')


order=dict(symbol='AL30', op_type=1, price=45000, size=1, settlement=2)
connHB.send_orders([order.copy()])

df=connHB.get_orders()
print(df)
connHB._cancel_order(order_number=df.iloc[0].name, symbol=df.iloc[0].symbol, op_type=df.iloc[0].operation_type.lower())





##################################################
###                Connections                 ###
##################################################

conns = Connections([credential_pyR, credential_HB])  # permite manejar multiples conexiones en simultáneo de todos los modulos e inclusive varias del mismo modulo.

# pyR(credential_pyR) es equivalente a:
# conns._get_conn(conn_id=credential_pyR['conn_id'])

print(conns._get_conn(conn_id=credential_pyR['conn_id']))
# Out[5]: <connections.pyRofex.pyRofex_connection.pyR at 0x1d436456c50>

print(conns._get_conn(conn_id=credential_HB['conn_id']))
# Out[6]: <connections.homebroker.hb_connection.HB at 0x1d4364c2e90>


orders = []
orders+= [dict(conn_id=credential_pyR['conn_id'], symbol='AL30', op_type=1, price=45000, size=1, settlement=2)]
orders+= [dict(conn_id=credential_HB['conn_id'],  symbol='AL30', op_type=1, price=45000, size=1, settlement=2)]

conns.send_orders(orders)
