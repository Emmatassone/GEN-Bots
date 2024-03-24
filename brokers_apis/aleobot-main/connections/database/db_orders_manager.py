# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro
"""

import threading
from queue import Queue

import pandas as pd

from tools import data_flow_manager as data_mgr
from connections.database import db_map, db_tools
import global_config
 

def new_order(order:dict, session=None):
    return save_order(db_map.Orders().set_data(dict), session=session)
    
def save_order(order:db_map.Orders, session=None):
    rsp = db_tools.query(session=session, method=db_tools.set_update, obj=order)
    print(rsp)
    return rsp

def get_orders(session=None, look_for:dict=None, exclude:dict=None, contains:dict=None, not_contains:dict=None, return_db_obj=False):
    
    if not global_config.use_database: return
    
    tables  = [db_map.Orders]
    filters = dict(equal_to=look_for, not_equal_to=exclude, contains=contains, not_contains=not_contains)
    
    rsp = db_tools.query(session=session, method=db_tools.get, tables=tables, filters=filters)
    if return_db_obj: return rsp
    
    if rsp == []: return db_map.Orders.empty_df() 
    return pd.DataFrame([order.data() for order in rsp]).set_index('id')
    

class Orders_Updater:
    table = db_map.Orders
    
    def __init__(self, stop_event=threading.Event(), frequency=0, start=False):
        self.stop_event = stop_event
        self.queue = Queue()
        self.frequency = frequency
        self._new_thread()
        if start and global_config.use_database: self.start()
    
    def _new_thread(self):
        self.thread = threading.Thread(target = db_tools.updater_loop, 
                      kwargs = dict(queue=self.queue, table=self.table,
                                    stop_event=self.stop_event, frequency=self.frequency),
                      daemon = True)
        self.thread.started  = False
        
    def start(self):
        if not self.thread.is_alive(): 
            if not self.thread.started: 
                self.thread.start()
                self.thread.started = True
            else:
                self._new_thread()
                self.start()
        return self
        
    def stop(self):
        self.stop_event.set()
        try: self.queue.put(None)  # Sin esta línea el hilo se va a quedar esperando en queue.get y no se va a detener hasta no obtener un nuevo elemento de la cola.
        except: pass
    
    """ Puedo obviar lo siguiente haciendo directamente instancia.queue y el metodo .put o .get
    def put(self, *args, **kwargs):
        return self.queue.put(*args, **kwargs)
        
    def get(self):
        return self.queue.get()
    """
        

db_updater = data_mgr.Listener(handler=db_tools.updater, handler_kwargs=dict(table=db_map.Orders))
    #table = db_map.Orders

        

