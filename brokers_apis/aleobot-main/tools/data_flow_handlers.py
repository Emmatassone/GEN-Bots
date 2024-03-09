# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro
"""
# Librerias como pubsub, pydispatcher y RxPY implementan soluciones parecidas.

# Nombres alternativos para el modulo data_stream, data_flux_handlers, data_flow

import threading
from queue import Queue

class Participant:
    
    def __init__(self, task:callable, task_kwargs:dict=None, stop_event=threading.Event()):
        self.task = task
        self.task_kwargs = task_kwargs if task_kwargs is not None else dict()
        self.stop_event = stop_event
        self.queue = Queue()
        
    def _new_thread(self):
        self.thread = threading.Thread(target=self.task, kwargs=self.task_kwargs, daemon=True)
        self.thread.started = False  # Necesario para no reiniciar un hilo que se cerró.
        
    def start(self):
        if not self.thread.is_alive(): 
            if not self.thread.started: 
                self.thread.start()
                self.thread.started = True
            else:
                self._new_thread()
                self.start()
        return self
        
    def stop(self, wait=False):
        self.stop_event.set()
        self.queue.put(None)  # Sin esta línea el hilo se va a quedar esperando en queue.get y no se va a detener hasta no obtener un nuevo elemento de la cola.
        if wait: self.thread.join()
        

class Listener(Participant):
    
    def __init__(self, handler:callable, handler_kwargs:dict=None, stop_event=threading.Event(), frequency=0):
        super().__init__(task=handler, task_kwargs=handler_kwargs, stop_event=stop_event)
        self.task_kwargs['listener'] = self
        self.frequency = frequency
        self._new_thread()


class Transmitter(Participant):  # Distribuiter
    
    def __init__(self, listeners:list[Listener]=[], stop_event=threading.Event(), start=False):
        super().__init__(task=self._broadcast_loop, stop_event=stop_event)
        self.listeners = listeners
        self._new_thread()
        if start: self.start()
        
    def _broadcast_loop(self):
        while not self.stop_event.is_set():
            data = self.queue.get()
            for l in self.listeners:
                l.start()
                l.queue.put(data)
                
    def start(self):
        super().start()
        for l in self.listeners: l.start()
            
    def subscribe(self, listener:Listener):
        self.listeners.append(listener)

        

