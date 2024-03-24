# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro
"""

import threading
from queue import Queue

class Stream:
    
    def __init__(self, task:callable, task_kwargs:dict=None, stop_event=threading.Event()):
        self.task = task
        self.task_kwargs = task_kwargs if task_kwargs is not None else dict()
        self.stop_event = stop_event
        self.queue = Queue()
        
    def _new_thread(self):
        self.thread = threading.Thread(target=self.task, kwargs=self.task_kwargs, daemon=True)
        self.thread.started = False
        
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
        self.queue.put(None)  # Sin esta línea el hilo se va a quedar esperando en queue.get y no se va a detener hasta no obtener un nuevo elemento de la cola.
        
    



class Listener(Stream):
    
    def __int__(self, handler:callable, handler_kwargs:dict=None, stop_event=threading.Event(), frequency=0):
        super.__init__(task=handler, task_kwargs=handler_kwargs, stop_event=stop_event)
        self.handler_kwargs['listener'] = self
        self.frequency = frequency
        self._new_thread()


class Transmitter(Stream):  # Distribuiter
    
    def __init__(self, listeners:list[Listener]=[], stop_event=threading.Event(), start=False):
        super.__init__(task=self._broadcast_loop, stop_event=stop_event)
        self.listeners = listeners
        self._new_thread()
        if start: self.start()
        
    def _broadcast_loop(self):
        while not self.stop_event.is_set():
            data = self.queue.get()
            for r in self.receivers:
                r.start()
                r.queue.put(data)
            
    
    def _new_broadcast_thread(self):
        self.broadcast_thread = threading.Thread(target = self._broadcast_loop, daemon = True)
        self.broadcast_thread.started = False
        
    def start(self):
        if not self.broadcast_thread.is_alive(): 
            if not self.broadcast_thread.started: 
                self.broadcast_thread.start()
                self.broadcast_thread.started = True
            else:
                self._new_broadcast_thread()
                self.start()
        return self
        
    def stop(self):
        self.stop_event.set()
        self.queue.put(None)  # Sin esta línea el hilo se va a quedar esperando en queue.get y no se va a detener hasta no obtener un nuevo elemento de la cola.
        
    
    """ Puedo obviar lo siguiente haciendo directamente instancia.queue y el metodo .put o .get  
    def put(self, *args, **kwargs):
        return self.queue.put(*args, **kwargs)
        
    def get(self):
        return self.queue.get()
    """
        

