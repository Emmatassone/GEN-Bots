# -*- coding: utf-8 -*-
"""
@author: Alejandro Ben 
"""

status_map = { 'SENT':         0, 
               'IN_MARKET':    1, 
               'PART_FILLED':  2, 
               'FILLED':       3, 
               'STUCK':        4,
               'REJECTED':    -1, 
               'PEND_CANCEL': -2,
               'CANCELLED':   -3, 
               'EXPIRED':     -4, }
status_labels = {v: k for k, v in status_map.items()}

status_filters = { 'pending': [status_map.get('IN_MARKET'), status_map.get('PART_FILLED')],  
                   'filled':  [status_map.get('FILLED')], 
                   'filled_and_partially': [status_map.get('FILLED'), status_map.get('PART_FILLED')], }


