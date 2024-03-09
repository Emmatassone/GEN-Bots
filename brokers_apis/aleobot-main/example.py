# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 12:51:40 2024

@author: Alejandro
"""

from connections.connections_manager import Connections

##################################################
###                Referencias                 ###
##################################################

settlements  = { 0: 'spot',
                 1: '24hs',
                 2: '48hs', }

op_type_dict = { 1: 'buy',
                -1: 'sell', }

boards = {'options', 'accionesLideres', 'panelGeneral', 'cedears', 'rentaFija', 'letes', 'obligaciones'}





##################################################
###                Connections                 ###
##################################################

conns = Connections()  # permite manejar multiples conexiones en simultáneo de todos los modulos e inclusive varias del mismo modulo.

opt_df = conns.get_market_snapshot(board='options')
acc_df = conns.get_market_snapshot(board='accionesLideres', settlement=2)
print(opt_df, acc_df)
1/0
orders = []
orders+= [dict(conn_id=1, symbol='AL30', op_type=1, price=45000, size=1, settlement=2)]
orders+= [dict(conn_id=2, symbol='AL30', op_type=1, price=45000, size=1, settlement=2)]

conns.send_orders(orders)
