# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 21:00:55 2024

@author: Alejandro
"""
import copy
import threading
from contextlib import nullcontext

import pyRofex


class _Environment_Config(dict):
    def __init__(self):
        self.lock = threading.Lock()
        self.conn_id = 0  # Los valores por defecto de environment_config se guardan en este key.
        self.data = {self.conn_id: copy.deepcopy(pyRofex.components.globals.environment_config)}
        self.env_key = pyRofex.Environment.LIVE
        
    def __getitem__(self, key):
        # print(f"Leyendo el valor para la clave '{key}'")
        with self.lock if not self.lock.locked() else nullcontext():  # nullcontext es necesario si se están llamando a los metodos dentro de un bloque de contexto 'with self.lock'.
            return self.data[self.conn_id].get(key)

    def __setitem__(self, key, value):
        # print(f"Estableciendo el valor '{value}' para la clave '{key}'")
        with self.lock if not self.lock.locked() else nullcontext():
            self.conns[self.conn_id][key] = value
        
    def new_conn(self, conn_id):
        with self.lock if not self.lock.locked() else nullcontext():
            self.data[conn_id] = copy.deepcopy({self.env_key: self.data[0].get(self.env_key)})
            
    def get_conn(self, conn_id):
        with self.lock if not self.lock.locked() else nullcontext():
            return self.data[conn_id][self.env_key]
    
    def set_active_conn(self, conn_id):
        with self.lock if not self.lock.locked() else nullcontext():
            self.conn_id = conn_id
    
    def __len__(self):
        with self.lock if not self.lock.locked() else nullcontext():
            return len(self.data)
    
    def __repr__(self):
        with self.lock if not self.lock.locked() else nullcontext():
            return repr(self.data)
   
    def __iter__(self):
        with self.lock if not self.lock.locked() else nullcontext():
            yield self.data
        
    def items(self, conn_id=None):
        with self.lock if not self.lock.locked() else nullcontext():
            return self._getattr('items', conn_id)
   
    def keys(self, conn_id=None):
        with self.lock if not self.lock.locked() else nullcontext():
            return self._getattr('keys', conn_id)
   
    def values(self, conn_id=None):
        with self.lock if not self.lock.locked() else nullcontext():
            return self._getattr('values', conn_id)
    
    def _getattr(self, attr, conn_id=None):
        if conn_id is None: conn_id = self.conn_id
        elif conn_id == 0: return getattr(self.data, attr)()
        return getattr(self.data.get(conn_id), attr)()
    
    def __enter__(self):
        self.lock.acquire()  # No va a continuar la ejecución del código sino hasta que pueda obtener el acceso al lock
        return self
    
    def __exit__(self, *args):
        if self.lock.locked(): self.lock.release()
    

class PyRofexWrapper:
    env_config = pyRofex.components.globals.environment_config = _Environment_Config()
    def __init__(self, conn_id):
        self.conn_id = conn_id
        self.env_config.new_conn(self.conn_id)
        
    def get_ws_conn(self):
        return self.env_config.get_conn(self.conn_id)['ws_client']
    
    def get_rest_conn(self):
        return self.env_config.get_conn(self.conn_id)['rest_client']
    
    def __getattr__(self, attr):
        with self.env_config.lock:
            self.env_config.conn_id = self.conn_id
            return getattr(pyRofex, attr)

"""
w=PyRofexWrapper(1)

api_url = "https://api.veta.xoms.com.ar/" 
ws_url = "wss://api.veta.xoms.com.ar/"
w._set_environment_parameter("url", api_url, pyRofex.Environment.LIVE) 
w._set_environment_parameter("ws", ws_url, pyRofex.Environment.LIVE)

w.initialize(user="",
                   password="",
                   account=44444,
                   environment=pyRofex.Environment.LIVE)
"""