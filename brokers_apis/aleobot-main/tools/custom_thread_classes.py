#  -*- coding: utf-8 -*-
"""
@author: Alejandro Ben
"""
import time
import threading
import traceback

    
""" Anterior versión de Thread_with_Return:
class Thread_with_Return(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        if self._target is not None:
            return self._target(*self._args, **self._kwargs)
El problema con esta versión es que en el método run de Thread, la función objetivo (_target) se llama internamente, pero el valor de retorno de esa función se pierde porque está diseñado para ejecutar la función objetivo en un nuevo hilo sin preocuparse por su valor de retorno
"""
class Thread_with_Return(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retorno = None # Es importante agregar esta linea para evitar que se evalue el valor de retorno antes de que se le haya asignado uno en la funcion run y asi evitar una excepción

    def run(self):
        if self._target is not None:
            try:
                self.retorno = self._target(*self._args, **self._kwargs)
            except Exception as e:
                traceback.print_exc()
                self.retorno = e  # Luego evaluar el retorno de Thread_with_Return para ver si lo retornado es lo buscado o una excepcion haciendo: isinstance(retorno, Exception)
            


class Thread_with_Timer(threading.Thread):
    def __init__(self, auto_start=False, wait_time=1, timer_event=threading.Event(), raise_exception=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._auto_start = auto_start
        self._wait_time = wait_time
        self.raise_exception = raise_exception
        self._create_timer()
        self.external_event = timer_event
        self.internal_event = threading.Event()  # tengo que agregar un internal_event ya que external event hace referencia a un
                                                 # objeto que puede ser modificado o reescrito desde afuera e impedir la correcta 
                                                 # funcionalidad del threading.Timer

    def _set_events(self):
        self.external_event.set()   # No es necesario un Lock adicional para modificar o leer el estado de un objeto threading.Event. 
        self.internal_event.set()  # El objeto Event ya proporciona mecanismos integrados para la sincronización entre hilos. 

    def _create_timer(self):
        self._timer = threading.Timer(self._wait_time, self._set_events)

    def run(self):
        if self._auto_start: self.start_timer()
        try: super().run()
        finally:                # Si el método run() finaliza antes de que se agote el temporizador, es necesario
            self.stop_timer()   # cancelar el temporizador para que self.timer_event no sea seteado a True.
    
    def start_timer(self):  # También va a resetear el timer al hacer : if self._timer.is_alive(): self._timer.cancel()
        # hasattr(self, '_timer') and
        self._timer.cancel()  # Es conveniente esta línea para no dejar hilos abiertos que puedan generar conflictos ante llamadas redundantes desde fuera
        self._create_timer()
        self._timer.start()
        self._start_time = time.monotonic()

    def stop_timer(self, print_time=True):
        self._timer.cancel()  # Si threading.Timer está vivo o no, o haya transcurrido el tiempo o no para llamar a la funcion,
                              # hacer cancel() sobre dicho hilo no levantara ninguna excepcion u error. El único efecto que tendrá 
                              # será que si el tiempo no transcurrió dicho cronómetro se detendrá y no se llamará a la funcion.
        if print_time: print(' Tiempo insumido (en segundos): {:.3f}'.format(time.monotonic()-self._start_time))
        if self.internal_event.is_set():  # la unica forma de verificar que transcurrió el tiempo es con esta sentencia ya que si
                                          # uso is_alive() el hilo timer puede estar vivo pero igual ya haber llamado a la función.
            if self.raise_exception: raise TimeoutError(" TimeoutError Exception: La ejecución excedió el tiempo del estipulado. El hilo se detendrá.")
            else: print((" La ejecución excedió el tiempo del estipulado. El hilo se detendrá."))  # va a retornar None
        return True
        
    def elapsed_time(self):
        if self._timer.is_alive(): return time.monotonic()-self._start_time
        else: return 0


"""
Función que ejecuta otra de manera continua a la que le da un tiempo determinado para ejecutarse o hasta que reciba una señal de detención:
 * data:              Object_with_Lock que guarda la información
 * stop_event:        señal de detención recibida desde fuera
 * sleep_time:        tiempo a esperar para que solicitar un nuevo resultado de function
 * function:          funcion a ser llamada cuyo resultado va a ser guardado en data
 * message_to_print:  mensaje a imprimir por consola si el resultado fue satisfactorio
 * print_time:        si es True imprime el tiempo insumido
 * args y **kwargs:   argumentos para function
"""
def data_feeder(data, stop_event, sleep_time, function, message_to_print='', print_time=True, *args, **kwargs):
    check_ok = isinstance(threading.current_thread(), Thread_with_Timer)
    while not stop_event.is_set():
        if check_ok:
          # print('\n threading.current_thread().internal_event.is_set(): ', threading.current_thread().internal_event.is_set())
            if threading.current_thread().internal_event.is_set(): break
            threading.current_thread().start_timer()
        return_of_function = function(*args, **kwargs)
     #  print('\n elapsed_time: ',time.monotonic()-threading.current_thread()._start_time)
     #  print('\n threading.current_thread().internal_event.is_set(): ', threading.current_thread().internal_event.is_set())
        if check_ok and not threading.current_thread().stop_timer(print_time): break  # Si el tiempo se agotó va lanzar un excepción terminando la ejecución del hilo
        if not stop_event.is_set():  # vuelvo a chequear si stop_event is set
            data.set_obj_value(return_of_function)
            if message_to_print != '': print(message_to_print)
        time.sleep(sleep_time)



