# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 12:51:40 2024

@author: Alejandro
"""


import threading
from tools.file_manager import config_read
from tools.data_flow_handlers import Transmitter, Listener
from connections.database import db_map, db_tools
from connections.helpers import query_handler



stop_all_threads = None
orders_data = None

initialized = False
initialize_lock = threading.Lock()

def initialize():
    global initialized, initialize_lock, stop_all_threads, orders_data
    
    with initialize_lock:
        if initialized: return
        
        stop_all_threads = threading.Event()
        orders_data = Transmitter(stop_event=stop_all_threads)
        orders_data.get = query_handler.Get_Orders_Status()
        
        config = config_read()
        
        if config['Data_Storage_Settings'].getboolean('USE_DATABASE'):
            orders_db_updater = Listener(handler        = db_tools.updater, 
                                         handler_kwargs = dict(table=db_map.Orders), 
                                         stop_event     = stop_all_threads)
            orders_data.subscribe(orders_db_updater)
            
        if config['Data_Storage_Settings'].getboolean('USE_DATAFRAME'):
            pass
        
        orders_data.start()
        
        initialized = True