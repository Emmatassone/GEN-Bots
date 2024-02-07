# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 09:37:41 2024

@author: Alejandro
"""

from connections.connection import Connections

conn = Connections([{'module': 'HB', 'nroComitente': 44444}])

print(conn.credentials.keys())
"""
Out[1]:
['broker_id',
 'nroComitente',
 'module',
 'user',
 'password',
 'conn_id',
 'conn_token',
 'nombreCompleto',
 'broker_name',
 'dni',
 'checked']
"""





from connections.homebroker.hb_connection   import HB

def HB_order_book_handler(online, quotes):
    print(quotes)
    
def HB_securities_handler(online, quotes):
    print(quotes)


connHB  = HB({'nroComitente': 44444})

connHB.set_on_order_book_callback(HB_order_book_handler)
connHB.set_on_securities_callback(HB_securities_handler)

connHB.subscribe_order_book(symbols=['AL30'], settlements=['spot'], subscription='order_book')

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





from connections.pyRofex.pyRofex_connection import pyR

connPyR = pyR({'nroComitente': 44444})


# Lo siguiente falta implementar correctamente las suscripciones a funciones que reciben la data de mercado