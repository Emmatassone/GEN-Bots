#  -*- coding: utf-8 -*-
"""
@author: Alejandro Ben
"""
import threading
import random
from datetime import datetime


class Pipeline:
    def __init__(self):
        self.message = True # Se asigna este valor por beneficio del script al ahorrar 1 linea de codigo pero debería ser None
        self.lock = threading.Lock()

    def get_message(self):
        with self.lock:
            message = self.message
            # self.message = None <= agregar esta linea si quiero que el mensaje sea leido 1 sola vez
            # Al no agregar la línea anterior siempre se va a enviar el último mensaje producido por set_message
        return message

    def set_message(self, message):
        with self.lock:
            self.message = message


class Data:  # clase idéntica a Pipeline
    def __init__(self):
        self.value = True # Se asigna este valor por beneficio del script al ahorrar 1 linea de codigo pero debería ser None
        self.lock = threading.Lock()

    def get_value(self):
        with self.lock:
            return self.value

    def set_value(self, value):
        with self.lock:
            self.value = value
            raise Exception()
            
            
class List_with_Lock:
    def __init__(self, lst:list=None, lock=threading.Lock(), msg=True):
        if not isinstance(lst, (list, type(None))): raise Exception(' Tipo de dato erróneo.')
        self.msg = msg
        self.timestamp = datetime.now()
        self.lock = lock
        with lock: self.lst = lst.copy() if lst is not None else []
        self.lst_len = len(self.lst)  # Con este atributo evito tomar control del lock para calcular el tamaño de la lista
                
    def _update(self):
        self.lst_len = len(self.lst)
        self.timestamp = datetime.now()
    
    def __len__(self):
        return self.lst_len
    
    def __call__(self,n=0):
        with self.lock: return self.lst.copy() # retorna copia de la lista (copia porque retornando dicha lista original podría modificarse sin usar el lock) haciendo: List_with_Lock_object()
            
    def __getitem__(self, index=-1):  # retorna un elemento de la lista en base al indice haciendo: List_with_Lock_object[index]
        with self.lock:
            if len(self.lst) > 0:  # Primero controlo que la lista no esté vacia
                if index == -1: return random.choice(self.lst)
                try: return self.lst[index]
                except IndexError: print(' Índice erróneo.') if self.msg else None
                # Si la lista está vacia o el índice es incorrecto devuelve None
    
    def __setitem__(self, index, value):
        with self.lock:
            try: self.lst[index] = value; self._update()
            except IndexError: print(' Índice erróneo.') if self.msg else None

    def set_value(self, lst):
        with self.lock:
            self.lst = lst.copy(); self._update()
            
    def __iadd__(self, value):
        with self.lock:
            self.lst += value; self._update()
            return self
            
    def __delitem__(self, index):  # elimina el elemento de la lista según el índice haciendo: del List_with_Lock_object[index]
        with self.lock:
            try: del self.lst[index]; self._update()
            except IndexError: print(' Índice erróneo.') if self.msg else None
            
    def del_value(self, value):   # elimina el elemento de la lista por su valor 
        with self.lock:
            try: self.lst.remove(value); self._update()
            except ValueError: print(' Valor erróneo.') if self.msg else None
            
    def pop(self, index=-1): # -1 devuelve un valor random
        value = self[index]
        if value is not None: self.del_value(value)
        return value
    
    def __contains__(self, value): # consigo evaluar si un elemento está en el listado haciendo value in List_with_Lock_object
        with self.lock: 
            return value in self.lst

    def __iter__(self):  # consigo iterar los elementos haciendo for i in List_with_Lock_object
        with self.lock: lst = self.lst.copy()
        return iter(lst)
        
    
class Dict_with_Lock:
    def __init__(self, dict_:dict=None, lock=threading.Lock(), msg=True):
        if not isinstance(dict_, (dict, type(None))): raise Exception(' Tipo de dato erróneo.')
        self.msg = msg
        self.timestamp = datetime.now()
        self.lock = lock
        with lock: self.dict = dict_ if dict_ is not None else {}
        self.dict_len = len(self.dict)  # Con este atributo evito tomar control del lock para calcular el tamaño de la lista
                
    def _update(self):
        self.dict_len = len(self.dict)
        self.timestamp = datetime.now()
        
    def __enter__(self):
        self.lock.acquire()  # No va a continuar la ejecución del código sino hasta que pueda obtener el acceso al lock
        return self.dict
    
    def __exit__(self, *args):
        if self.lock.locked(): self.lock.release()
    
    def __len__(self):
        return self.dict_len
            
    def __getitem__(self, key):  # retorna un elemento del diccionario en base al key haciendo: Dict_with_Lock_object[key] o .get(key)
        with self.lock:
            return self.dict.get(key)  # Si no encuentra el key retorna None
    
    def __setitem__(self, key, value):
        with self.lock:
            self.dict[key] = value; self._update()

    def set_dict(self, dict_):
        with self.lock:
            self.dict = dict_; self._update()
                        
    def pop(self, key):
        with self.lock:
            try: return self.dict.pop(key); self._update()
            except KeyError: print(' Clave errónea.') if self.msg else None
    
    def __contains__(self, data=None): 
        """ Consigo evaluar si un una clave o un valor, o ambos están en el diccionario del Dict_with_Lock_object.
            Puede recibir el key directamente o un dicionario con una clave 'key' para la clave y/o una clave 'value'
            para el valor.  """
        with self.lock: 
            if not isinstance(data, dict): 
                return data in self.dict
            key = data.get('key')
            value = data.get('value')
            if key is not None: 
                return (key, value) in self.dict.items()
            return value in self.dict.values()
        
    def apply_function_over_iteration(self, function, *args, **kwargs):
        with self.lock: 
            for k, v in self.dict.items():
                yield function(key=k, value=v, *args, **kwargs)
    

class Object_with_Lock:
    def __init__(self, obj, lock=threading.Lock(), locked=False):
        self.obj_Timestamp = datetime.now()
        self.obj = obj
        self.lock = lock
        
    def __enter__(self):
        self.lock.acquire()  # No va a continuar la ejecución del código sino hasta que pueda obtener el acceso al lock
        return self.obj
    
    def __exit__(self, *args):
        if self.lock.locked(): self.lock.release()
    
    def set_obj_value(self, obj):
        with self.lock:
            self.obj = obj
            self.obj_Timestamp = datetime.now()
        
    def apply_method(self, method:str, *args, **kwargs):
        with self as obj:
            return getattr(obj, method)(*args, **kwargs)
            

class Instances:
    def __init__(self, class_type, start_qty=1, max_qty=0, *class_args, **class_kwargs):  # por defecto la cantidad maxima va a ser la cantidad inicial
        self.class_type = class_type
        self.class_args = class_args
        self.class_kwargs = class_kwargs
        self.max_qty = max(start_qty, max_qty)  # con max() me aseguro que la cantidad maxima sea mayor o igual a la cantidad inicial
        self.objects = [ (self.class_type(*self.class_args, **self.class_kwargs), threading.Lock()) for i in range(start_qty)]
        self.objs_lock = threading.Lock()

    def get_first_available(self):
        with self.objs_lock:  # con esto me aseguro que solicitudes simultáneas (por diferentes hilos) no genere errores
            for obj, lock in self.objects:
                if not lock.locked():
                    lock.acquire()
                    return obj, lock
            if len(self.objects) < self.max_qty:
                self.objects+= [(self.class_type(*self.class_args, **self.class_kwargs), threading.Lock())]
                self.objects[-1][1].acquire()
                return self.objects[-1]
            return None, threading.Lock()
    
    def __iter__(self):  # consigo iterar los elementos haciendo for i in 'instance_object'
        return (obj[0] for obj in self.objects)
    

