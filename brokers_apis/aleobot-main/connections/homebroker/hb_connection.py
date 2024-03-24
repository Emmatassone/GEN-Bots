# -*- coding: utf-8 -*-
"""
@author: Alejandro Ben
"""


import time, random
import threading
from datetime import datetime
import pandas as pd
import requests as rq

from pyhomebroker import HomeBroker
from .hb_imports import hb_user_agent, SessionException, ServerException


from connections.homebroker import hb_auth

from connections.common import brokers, securities

from connections.helpers import orders_helper
# from .hb_orders_helpers import settlements, op_type
from tools.variables_with_lock import Object_with_Lock, Instances
from tools.custom_thread_classes import Thread_with_Return, Thread_with_Timer, data_feeder

from connections.broker_connection import Broker_Connection

module_alycs = [brokers.cocos_id]

headers = { 'User-Agent': hb_user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json; charset=UTF-8' }

procesos = {1: 'tenencias', 62: 'poder_compra', }



class Order:
    pass

class HB(Broker_Connection):
    alycs = [brokers.cocos_id, brokers.veta_id]
            
        ##################################################
        ### Proteger los objetos del bloqueo con locks ###
        ##################################################
    
    def __init__(self, account:dict=None, wait_time:float=12, instances=1, **kwargs):
        (account:= {} if account is None else account).update(dict(module='HB'))  # Con esta línea aseguro el módulo correcto.
        if len(account) == 1 and 'module' in account: account.update(dict(broker_id=265))  # Broker por defecto (si solo se aporta el modulo o nada).
        super().__init__(account=account, **kwargs)  # Llama a login()
        
        self.auth = hb_auth.Account_Auth(self.credentials['broker_id'], self.nroComitente, cookies_qty=10, credentials=self.credentials)
        self.cookies = self.auth.cookies()
        
        self.hb_connection = HomeBroker( self.credentials['broker_id'], on_securities=print,         # on_securities recibe como parámetros: online y quotes
                                         on_order_book=print, on_error=None)  # on_order_book recibe como parámetros: online y quotes
        self.hb_instances = Instances(HomeBroker, start_qty=instances, max_qty=instances*5, broker_id=self.credentials['broker_id'])
        for hb in self.hb_instances:
            threading.Thread(target=self.login, args=(hb,), daemon=True).start()
        
        
        # En lugar de guardar ordersList directamente acá (self.ordersList=value) lo guardo como atributo de la instancia Object_with_Lock
        # Y a dicha instancia sí la guardo dentro de HB
        self.ordersList = Object_with_Lock(orders_helper.orders_df)
        self.tenencias  = Object_with_Lock(pd.DataFrame())
        self.saldos     = Object_with_Lock(pd.DataFrame())
        
        self.attempts = range(1,6)
        self.wait_time = wait_time
        self.sleep_time = 1
    
        
    def __enter__(self):   # Con esto puedo utilizar la clase con la declaración with. Ejemplo: with HB() as hb: ...
        return self
        
    def __exit__(self, *args):   # Con esto puedo utilizar la clase con la declaración with. Ejemplo: with HB() as hb: ...
        # El método __exit__ siempre recibe cuatro argumentos: el tipo de excepción (si hay una excepción), el valor de excepción 
        # (si hay una excepción), y la traza de la pila (si hay una excepción), así como el objeto de contexto original.
        # La forma de tomar esos argumentos sería reemplazar *args por exception_type, exception_value y traceback
        self.logout()  # ya hace el disconnect
        for hb in self.hb_instances:
            self.logout(hb)

    def login(self, hb=None):
        return self._ex_login(hb)
        """
        if self.logged_in(hb): return True
        cookie = self.auth.cookies.pop()
        if cookie is not None:
            hb.auth.cookies = cookie
            hb.auth.is_user_logged_in = True
            print(' --- Login Exitoso ---')
            return True
        print(' --- El usuario no pudo ser autenticado ---')
        return False      """
    

    def _ex_login(self, hb=None):
        start_time = time.monotonic()
        # if hb is None: hb = self.hb_connection # Con esta instrucción no hay necesidad de hacer el resto de las veces la evaluación: (self.hb_connection if hb is None else hb)
        if self.logged_in(hb): return True
        (self.hb_connection if hb is None else hb).auth.__get_ipaddress = hb_auth.AR_ip.get_random()
        
        print(' Iniciando sesión con cuenta Nº {}: \n  {} ( Broker Nº {} ) '.format(self.auth.nroComitente, self.auth.credentials['nombreCompleto'], self.auth.broker_id))
        rta = (self.hb_connection if hb is None else hb).auth.login(dni=self.credentials['dni'], user=self.credentials['user'], password=self.credentials['password'])
        
     #  if rta: self.cookies += self._cookies(hb)
     #  if rta and len(self.cookies) < 10:
     #      self.cookies += [(self.hb_connection if hb is None else hb).auth.cookies]
        print(' --- Login Exitoso ---') if rta else print(' --- El usuario no pudo ser autenticado ---')
        print(' Tiempo insumido para login (en segundos): {:.3f}'.format(time.monotonic() - start_time))
        return rta
    
    def logged_in(self, hb=None): # Consulta si el usuario está logueado. Es la misma respuesta que brinda la funcion hb.auth.login
        return (self.hb_connection if hb is None else hb).auth.is_user_logged_in
    
    def logout(self, hb=None):
        
        print(' CERRANDO sesión con cuenta Nº {}: \n  {} ( Broker Nº {} ) '.format(self.nroComitente, self.credentials['nombreCompleto'], self.credentials['broker_id']))
        if self.logged_in(hb):
            self.disconnect(hb, msg=False)
            (self.hb_connection if hb is None else hb).auth.logout()
            print(' --- Logout Exitoso ---')
        else: print(' --- El usuario no estó logueado! ---\n Continúa...')
    
    def _cookies(self, hb=None):  # es como el id  ...¿?
        return (self.hb_connection if hb is None else hb).auth.cookies
    
    def connect(self, hb=None):
        for i in self.attempts:
            if self.connected(): break # si ya está conectado salgo
            if self.login(hb): # si no lo está verifico que esté logueado (y me logueo si no lo está) y luego me conecto.
                print(' Conectando con cuenta Nº {} ( Broker Nº {} ) '.format(self.auth.nroComitente, self.auth.broker_id))
                try:            
                    (self.hb_connection if hb is None else hb).online.connect()
                    print(' --- Conexión Exitosa ---')
                    break
                except SessionException as exception:
                    self._manage_exception(exception)
            print(' Reintento Nº ', i+1)
    
    def connected(self, hb=None):
        return (self.hb_connection if hb is None else hb).online.is_connected()
        
    def disconnect(self, hb=None, msg=True):
        if msg: print(' DESCONECTANDO cuenta Nº {} ( Broker Nº {} ) '.format(self.auth.nroComitente, self.auth.broker_id))
        if self.connected(hb):
            try:            
                (self.hb_connection if hb is None else hb).online.disconnect()
                print(' --- Desconexión Exitosa ---')
            except SessionException as exception:
                print(' HomeBrokerError (SessionException): ', exception, '\n Continúa...')
        else: 
            if msg: print(' --- El usuario no está conectado! ---\n Continúa...')
    
    def _manage_exception(self, exception, hb=None, attempt=1):  # Deberia ser _on_error ???
        #  on_error: function(exception, connection_lost)
        #  Callable object which is called when we get error.
        #  This function has 2 arguments.
        #  The 1st argument is the exception object.
        #  The 2nd argument is if the connection was lost due to the error.
        if isinstance(exception, SessionException):
            print(' HomeBrokerError ({}): '.format(exception))
            if str(exception) == 'User is not logged in':
                return self.login(hb)
            elif str(exception) == 'Connection is not open': 
                self.connect(hb)
            else: return False
        elif isinstance(exception, ServerException):
            print(' HomeBrokerError (ServerException): ', exception)
            if str(exception) == ' NoLogin':
                self.logout(hb)
                return self.login(hb)
            time.sleep(self.sleep_time)
            print(' Reintento Nº ', attempt)
        elif isinstance(exception, AttributeError):  # cuando el objeto no es del tipo HomeBroker
            return self.login(hb)
        else: 
            print(' Excepcion no manejada: {}. No se reintenta.'.format(exception))
            return False
        return True
    
    def set_on_order_book_callback(self, function, excel_range=None):
        self.hb_connection.online._on_order_book = function
        self.hb_connection.online.excel_range = excel_range
    
    def set_on_securities_callback(self, function, excel_range=None):
        self.hb_connection.online._on_securities = function
        self.hb_connection.online.excel_range = excel_range

    def subscribe_order_book(self, hb=None, symbols=[], settlements=[], subscription='order_book'):  # Si no está conectado, se conecta.
        self.symbols = securities.symbols if symbols == [] else symbols
        self.settlements = securities.settlements if settlements == [] else settlements
        print(' ================ Iniciando Suscripciones ================')
        for symbol in self.symbols:
            for settlement in self.settlements:
                try:
                    self.connect(hb)  # Si no está conectado, se conecta.
                    print(' Suscribiendo a {} {}'.format(symbol, settlement))
                    # (self.hb_connection if hb is None else hb).online.subscribe_order_book(symbol, settlement)
                    getattr((self.hb_connection if hb is None else hb).online, 'subscribe_'+subscription)(symbol, settlement)
                    print(' Suscripción Exitosa.')
                except SessionException as exception:
                    self._manage_exception(exception)
                    print(' La suscripción a {} {} falló. No se reintenta'.format(symbol, settlement))
        print(' =============== Suscripciones Completada ================')
                

                    
    def _attain_cookies(self, cookies_qty=10):    
        self.cookies = hb_auth.Account_Auth(self.auth.broker_id, self.auth.nroComitente, cookies_qty).cookies()
    
    def _get_cookie(self, cookie=None):
        if cookie is not None:
            try: self.cookies.remove(cookie)
            except ValueError: pass # Si no está en la lista de cookies lanza Excepción ValueError, por tanto no hace falta hacer nada.
        if len(self.cookies) < 1: self._attain_cookies()  # Si me quedé sin cookies que funcionen obtengo nuevas cookies
        if len(self.cookies) > 0: return random.choice(self.cookies) # Con esta linea me cercioro que efectivamente se hayan obtenido nuevas cookies antes de retornarla
        else: return False # Si no se obtuvieron retorno False
        
    
    def _rq_response_eval(self, response, cookie, atrib=None):
        self._rq_response = response
        if response.status_code >= 400: return False # status_code mayor o igual a 400 son las categoría de errores (4xx o 5xx).
        response = response.json()  # response va a ser un diccionario
        if atrib is not None: setattr(self, atrib, response)
        
        if response['Success']: return True
        else:
            print(response['Error']['Descripcion'])
            if response['Error']['Descripcion'] == 'NoLogin': return self._get_cookie(cookie)
            else: return False
        
                    
    def account_info(self, process_list=[], msg=False): # antes incluia: process_list=[1, 62]
        def _procesar(self, proceso:dict, cookie, msg=False):  # !!!!!!!!!!!!!!!!!!!! borrar process
            start_time = time.monotonic()
            global headers
            payload = { 'comitente': str(self.auth.nroComitente), 'proceso': str(proceso) }  
            url = '{}/Consultas/GetConsulta'.format(self.auth.broker_url)
            for i in self.attempts:
                if i > 0: time.sleep(self.sleep_time)
                self._rsp = rq.post(url, json=payload, headers=headers, cookies=cookie)
                success = self._rq_response_eval(rq.post(url, json=payload, headers=headers, cookies=cookie), cookie, '_'+str(*proceso.values()))
                if not isinstance(success, bool): cookie = success
                elif success:
                    if msg: print(' Tiempo insumido para proceso \'{}\' (en segundos): {:.3f}'.format(*proceso.values(), time.monotonic()-start_time))
                    return getattr(self, 'procesar_'+str(*proceso.values()))() - start_time # si fue exitoso se corta el bucle
                    # return process(self) - start_time # si fue exitoso se corta el bucle
                print('Reintento Nº ', i+1)
            print(' No pudieron actualizarse tenencias de la cuenta.')
    
        def procesar_poder_compra(self):
            data = self._poder_compra['Result']['Poder']
            data = {'ARS': {'CDO': float(data[0]['CAN0']), '24hs': float(data[1]['CAN0']), '48hs': float(data[2]['CAN0'])},
                    'USD': {'CDO': float(data[0]['CAN1']), '24hs': float(data[1]['CAN1']), '48hs': float(data[2]['CAN1'])}, }
            data = pd.DataFrame(data)
            data.index.name = datetime.now().strftime('%H:%M.%Ss')
            self.saldos.set_obj_value(data)
            return time.monotonic()
        
        def procesar_tenencias(self):
            data = self._tenencias['Result']['Activos'][1]['Subtotal']
            aux = {}
            for i in data:
                aux[i['TICK']] = int(i['CANT'] if i['CANT'] is not None else 0)
            data = pd.DataFrame.from_dict(aux, orient='index', columns=['Total'])
            data['Disponible'] = data['Total']
            data.index.name = datetime.now().strftime('%H:%M.%Ss')
            self.tenencias.set_obj_value(data)
            return time.monotonic()
        
        
        procesos = {1:'tenencias', 62:'poder_compra'}
        process_function = { k: 'procesar_'+v for k,v in procesos.items() }
        
        start_time = time.monotonic()
        if process_list != []: procesos = {k: procesos[k] for k in process_list if k in procesos}
        threads = []
        for k,v in procesos.items():
            threads += [ threading.Thread(_procesar(self, {k: v}, random.choice(self.cookies[1:]), msg=msg) ) ]
        
        if msg: print(' Tiempo total insumido para account_info (en segundos): {:.3f}'.format(time.monotonic()-start_time))
        t, h = [], []
        for i in range(len(process_list)):
            h[i] = Thread_with_Return(target=_procesar, args=(self, process_list[i], self.cookies[i%len(self.cookies)], 
                                                                    locals()['procesar_'+procesos[process_list[i]]], msg), daemon=True)
            t[i] = h[i].start()
        for i in h: i.join()
        
        
        
        """
        start_time = time.monotonic()
        procesos = {1:'tenencias', 62:'poder_compra'}
        if process_list != []: procesos = {k: procesos[k] for k in process_list if k in procesos}
        tasks = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for k,v in procesos.items():
                tasks += [ executor.submit(_procesar(self, {k: v}, random.choice(self.cookies[1:]), msg=msg) ) ]
        concurrent.futures.wait(tasks)
        if msg: print(' Tiempo total insumido para account_info (en segundos): {:.3f}'.format(time.monotonic()-start_time))
        """
        """
        async def _invoke_procesar(self, msg):
            start_time = time.monotonic()
            procesos = {1:'tenencias', 62:'poder_compra'}
            if process_list != []: procesos = {k: procesos[k] for k in process_list if k in procesos}
            tasks = []
            for p in procesos:
                tasks += [ asyncio.create_task( self._procesar(p, random.choice(self.cookies[1:]), msg=msg) ) ]
            await asyncio.gather(*tasks)
            if msg: print(' Tiempo total insumido para account_info (en segundos): {:.3f}'.format(time.monotonic()-start_time))
            
        asyncio.run(_invoke_procesar(self, msg))
        """
        
        """
        def thread(*args, msg):
            global procesos
            t = _procesar(*args, msg=msg)
            if msg: print(' Tiempo total insumido para proceso \'{}\' (en segundos): {:.3f}'.format(procesos[args[1]], t))
            
        for i in range(len(process_list)):
            threading.Thread(target=thread, args=(self, process_list[i], self.cookies[i%len(self.cookies)], 
                             locals()['procesar_'+procesos[process_list[i]]],), kwargs={'msg':msg}, daemon=True).start()            
        """
        """
        t, h = [], []
        for i in range(len(process_list)):
            h[i] = Thread_with_Return(target=_procesar, args=(self, process_list[i], self.cookies[i%len(self.cookies)], 
                                                                    locals()['procesar_'+procesos[process_list[i]]], msg), daemon=True)
            t[i] = h[i].start()
        for i in h: i.join()
        if msg: print(' Tiempo insumido para proceso \'{}\' (en segundos): {:.3f}'.format(procesos[process_list[i]], t[i]))
        """
        
        
    def account_info_updater_start(self, stop_event=threading.Event(), timer_event=threading.Event(), msg=False):
        wait_time = 12
        message_to_print = ' ============= Saldos y Tenencias Recibido ==============' if msg else ''
        updater_thread = Thread_with_Timer()
        while not stop_event.is_set():
            if timer_event.is_set() or not updater_thread.is_alive():
              # print('\n ========================================================')
                print(  ' ====== Se (re)inicia account_info_updater_thread  ======')
              # print(  ' ======================================================== \n')
              # print('\n ***** timer_event.is_set: {} updater_thread.is_alive: {} ***** \n '.format(timer_event.is_set(), updater_thread.is_alive()))
                timer_event = threading.Event()
                updater_thread = Thread_with_Timer(wait_time=wait_time, timer_event=timer_event, target=data_feeder, 
                                 args=(Object_with_Lock(None), stop_event, self.sleep_time, self.account_info, message_to_print, msg), daemon=True)
                updater_thread.start()
            time.sleep(self.sleep_time)
        print(' ========== Actualización de Cuenta Terminada  ==========')


    """  DataFrame retornado por get_orders:
             index:   'order_number'
             columns: 'symbol', 'settlement', 'operation_type', 'size', 'price',
                      'remaining_size', 'datetime', 'status', 'cancellable', 'total'
    """
    def get_orders(self, msg=False):
        hb, lock = self.hb_instances.get_first_available()
        try:
            for i in self.attempts:
                if hb is None: print('\n\n hb get_orders is None!!!!!!!!!!!!!!!!!!! \n\n ')
                try:    
                    if msg: print(' ============ Obteniendo Listado de Ordenes =============') 
                    return hb.orders.get_orders_status(self.auth.nroComitente)
                except Exception as exception:
                    if not self._manage_exception(exception, hb, attempt=i): break # Si la excepción no pudo ser manejada corto el loop
                    else:  # Si la excepción pudo ser manejada reseteo el timer
                        if isinstance(threading.current_thread(), Thread_with_Timer):
                            threading.current_thread().start_timer() 
                """
                finally:
                # Si el bloque try se pudo ejecutar, self.ordersList se habrá actualizado. Si surgió un excepcion 
                # no manejada quedará el valor de self.ordersList que estaba. De cualquier forma retorno dicho valor
                    return self.ordersList  #_pending_orders_format()  """
        except:  print(' No se pudo obtener el listado de ordenes. ')
        finally: lock.release()

    
    def orders_updater_start(self, stop_event=threading.Event(), timer_event=threading.Event(), msg=False):  #orders_feeder, get_orders_continuously
        message_to_print = ' ============= Listado de Ordenes Recibido ==============' if msg else ''
        updater_thread = Thread_with_Timer()
        while not stop_event.is_set():
            if timer_event.is_set() or not updater_thread.is_alive():
              # print('\n ========================================================')
                print(  ' ============= Se (re)inicia updater_thread =============')
              # print(  ' ======================================================== \n')
              # print('\n ***** timer_event.is_set: {} updater_thread.is_alive: {} ***** \n '.format(timer_event.is_set(), updater_thread.is_alive()))
                timer_event = threading.Event()
                updater_thread = Thread_with_Timer(wait_time=self.wait_time, timer_event=timer_event, target=data_feeder, 
                                 args=(self.ordersList, stop_event, self.sleep_time, self.get_orders, message_to_print, msg), daemon=True)
                updater_thread.start()
            time.sleep(self.sleep_time)
        print(' ========== Actualización de Ordenes Terminada ==========')

    def cancel_orders(self, ordersToCancel=None):  # ordersToCancel es un DataFrame
        def thread(order=None):
            hb, lock = self.hb_instances.get_first_available()
            try:
                if hb is None: print('\n\n hb cancel_orders is None!!!!!!!!!!!!!!!!!!! \n\n ')
                for i in self.attempts:
                    try:
                        if order == None:
                            hb.orders.cancel_all_orders(self.auth.nroComitente)
                            print(' ===== Terminó la Cancelación de TODAS las Ordenes ======')
                        else:
                            hb.orders.cancel_order(self.auth.nroComitente, int(order))
                            print(' == Terminó la Cancelación de la Orden: {} =='.format(int(order)))
                        break # si no hay una excepcion no reintenta
                    except Exception as exception:
                        if not self._manage_exception(exception, hb=hb, attempt=i): break # Si no pude manejar la excepcion corto el loop
            except:  print(' La orden no pudo ser cancelada. ')
            finally: lock.release()
        if ordersToCancel is None:
            print(' ============= Cancelando TODAS las Ordenes =============')
          # thread()  # no necesito crear un nuevo hilo, solo llamo a la funcion.
            self.cancel_orders( orders_helper.pending_orders(self.ordersList.obj, self.ordersList.lock) )
        else: 
            print(' ================== Cancelando Ordenes ===================')
            columns_to_drop = ['datetime', 'cancela'] + [None]*(None in ordersToCancel) + [True]*(True in ordersToCancel)
            ordersToCancel.drop(columns_to_drop, axis=1, inplace=True)
            print(ordersToCancel)
          # for order in ordersToCancel.index.values:
          #     threading.Thread(target=thread, args=(order,), daemon=True).start()
            i, j = ordersToCancel.index.values.size, len(self.cookies)
            for order_number, order in ordersToCancel.iterrows():
                threading.Thread(target=self._cancel_order, args=(order_number, order['symbol'], order['op_type'], self.cookies[i%j]), daemon=True).start()  
          
                
    def _cancel_order(self, order_number, symbol=None, op_type=None, cookie=None):
        if cookie is None: cookie = self._get_cookie()
        if symbol is None and op_type is None:
            with self.ordersList as ordersList:
                symbol  = ordersList.loc[order_number, 'symbol']
                op_type = ordersList.loc[order_number, 'op_type']
        if   op_type in ['buy',  'Buy',  'BUY']:  op_type = 'CPRA'
        elif op_type in ['sell', 'Sell', 'SELL']: op_type = 'VTAS'
        if op_type not in ['CPRA', 'VTAS']: raise Exception(' Operación inválida!')

        for i in self.attempts:
            global headers
            if i > 0: time.sleep(self.sleep_time)
            payload = { 'Ticker': symbol, 'OptionTipo': op_type, 'Numero': str(int(order_number)), }
            url = '{}/Order/EnviarCancelacionAsyc'.format(self.auth.broker_url)
            success = self._rq_response_eval(rq.post(url, json=payload, headers=headers, cookies=cookie), cookie, '_cancel_order_response')
            if not success: continue  # pasa a la siguiente iteracion
            url = '{}/Order/EnviarOrdenCanceladaAsyc'.format(self.auth.broker_url)
            success = self._rq_response_eval(rq.post(url, headers=headers, cookies=cookie), cookie, '_cancel_order_response')
            if success: 
                print(' == Terminó la Cancelación de la Orden: {} {} {} =='.format(int(order_number), op_type, symbol))
                return  # si fue exitoso se corta el bucle
        print(' == NO PUDO CANCELARSE LA ORDEN: {} {} {} =='.format(int(order_number), op_type, symbol))
        
        
    def send_order(self, order:dict):  # symbol, price, size, op_type='buy', settlement='spot'):
        hb, lock = self.hb_instances.get_first_available()
        try:
            if hb is None: print('\n\n hb send_order is None!!!!!!!!!!!!!!!!!!! \n\n ')
            
            order['op_type'] = { 1: 'buy', -1: 'sell', }.get(order.get('op_type'))
            order['settlement'] = { 0: 'spot', 1: '24hs', 2: '48hs', }.get(order.get('settlement'))
            print(f'\n{order}\n')
            for i in range(2): #self.attempts:
                try:  # retorno el nro. de orden 
                    print(' Enviando órden: {} {} {} {} nominales a $ {}'.format(
                           order.get('op_type'), order.get('settlement'), 
                           order.get('symbol'),  order.get('size'), order.get('price')))
                    order['number'] = getattr(hb.orders, 'send_'+order.get('op_type')+'_order')(
                        order.get('symbol'), order.get('settlement'), order.get('price'), order.get('size'))
                    print(' Orden nro {} enviada exitosamente:'.format(order.get('number')))
                    print('  {} {} {} {} nominales a $ {} '.format(
                           order.get('op_type'), order.get('settlement'), 
                           order.get('symbol'),  order.get('size'), order.get('price')))
                    break
                except Exception as exception:
                    if str(exception) == ' NoLogin':
                        if not self.login(hb): break
                    if str(exception).find('Por favor intente nuevamente más tarde',67) > 0:
                        print(' Orden Rechazada: Ocurrió un error inesperado. Por favor intente nuevamente más tarde.')
                    elif isinstance(exception, ServerException):
                        balance = self._check_for_balance(exception, order.get('op_type'))
                        if balance is not None and balance > 0:
                            order['original_size'], order['size'], i = order.get('size'), balance, i-1
                        else:
                            order['status'] = order_status_map['REJECTED']
                            break
                    elif not self._manage_exception(exception, hb=hb, attempt=i): 
                        order['status'] = order_status_map['REJECTED']
                        break # Si no pude manejar la excepcion corto el loop
                print(' Reintento Nº ', i+1)
        except:  print(' La orden no pudo ser enviada. ')
        finally: lock.release()

    def _check_for_balance(self, exception, op_type):
        saldoDisponible = 0
        pos = str(exception).find('Saldo disponible:', 100)
        if pos > 0: # Si es > 0 es porque encontró Saldo disponible en la respuesta y pos es la posición
            saldoDisponible = int(( str(exception)[pos+17:str(exception).find('.',pos+17)] ).replace(',', '') ) # en lugar de 17 podria ir len('Saldo disponible:')
            saldoDisponible = saldoDisponible *(-1 if str(exception).find('-',len(str(exception))-5) > 0 else 1)
            if saldoDisponible > 0 and op_type != 'buy':  
                print(' Se reenvia orden ajustada a saldo disponible: {}'.format(saldoDisponible))
                return saldoDisponible   # continúo el loop (reintento)
        if str(exception).find('ORDEN INVERSA',64) > 0:
            return print(' Orden Rechazada: TIENE UNA ORDEN INVERSA.')
        if str(exception).find('No tiene saldo suficiente',54) > 0:
            return print(' Orden Rechazada: Saldo insuficiente ( Saldo:', saldoDisponible,')')
        return print(' Exception: ',exception,'\n Orden Rechazada.')




order_status_map = { 'CREATED'  :  0,
                     'REJECTED' : -1,
                     'PENDING'  :  1, 
                     'OFFERED'  :  2,
                     'PARTIAL'  :  3,
                     'COMPLETED':  4,
                     'CANCELLED': -2,
                     'BLOCKED'  :  5, }


""" df = pd.DataFrame({'symbol': ['AL30', 'AL30D',], 
                      'price': [10000, 26],
                      'size': [1, 2],
                      'op_type': ['buy', 'sell'],
                     'settlement': ['spot', '24hs']})  """
class Order:    
#   status_map = [ 'CREATED', 'REJECTED', 'PENDING', 'OFFERED', 'PARTIAL', 'COMPLETED', 'CANCELLED', 'BLOCKED' ]
    status_map = { 'CREATED'  :  0,
                   'REJECTED' : -1,
                   'PENDING'  :  1, 
                   'OFFERED'  :  2,
                   'PARTIAL'  :  3,
                   'COMPLETED':  4,
                   'CANCELLED': -2,
                   'BLOCKED'  :  5, }

    def __init__(self, symbol, price, size, op_type='buy', settlement='spot'): # hb, avg_purch_price=0
        
        self.symbol = symbol
        self.settlement = settlement
        
        """
        if symbol in Data.symbols: self.symbol = symbol
        else: raise Exception(' Símbolo inválido!')
        """
        if float(price) > 0: self.price = float(price)
        else: raise Exception(' Precio inválido!')
        
        if int(size) > 0: self.size = int(size)
        else: raise Exception(' Cantidad inválida!')
        
        if op_type.lower() in ['buy', 'sell']: self.op_type = op_type.lower()
        else: raise Exception(' Operación inválida!')
        """
        if settlement in Data.settlements: self.settlement = settlement
        else: raise Exception(' Plazo inválido!')
        """
        self.status = self.status_map['CREATED']
        self.number = 0
        self.original_size = 0
        self.cancellable = True
        self.remaining_size = self.size
        self.datetime = pd.to_datetime(datetime.now())
        
    def to_df(self):
        df = pd.DataFrame([self.__dict__])
        df.set_index('number')
        return df
    
    def to_hb_df(self):
        df = self.to_df()
        df.drop(['original_size'], axis=1, inplace=True)
        df.rename(columns={ 'op_type': 'operation_type', 'number': 'order_number' }, inplace=True)
        df['operation_type'] = df['operation_type'].str.upper()
        status_map_inverted = {v: k for k, v in self.status_map.items()}
        df['status'].replace(status_map_inverted, inplace=True)
        df['total']=round(df['price']*df['size']/100,4)
        df.set_index('order_number', inplace=True)
        df = df.reindex(columns=['symbol', 'settlement', 'operation_type', 'size', 'price',
                            'remaining_size', 'datetime', 'status', 'cancellable', 'total'])
        return df   # uso: df_hb.combine_first(df) siendo df el que retorna esta funcion
    
    def p(self):
        print(' Order number {}: '.format(self.number))
        print(' {} {} {} {} nominales a $ {}'.format(self.op_type, self.settlement, self.symbol, self.size, self.price))
        
    @staticmethod
    def build_from_hb_df(df):
        return df # ver si conviene retornar df, np.array o lista con objetos Order (por el tema velocidad)
        
# connection_class = HB