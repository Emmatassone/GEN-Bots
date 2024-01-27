# -*- coding: utf-8 -*-
"""
Created on Wed May 31 19:14:55 2023

@author: Alejandro
"""
null=None
true=True
false=False

import requests, json
import time, inspect
from datetime import datetime
import threading
import pandas as pd
import numpy as np


from tools.variables_with_lock import Object_with_Lock
from tools.file_manager import File_with_Lock
from tools import file_manager
from connections.common import brokers, securities, user_agents
from connections.helpers import orders_helper
from tools.custom_thread_classes import Thread_with_Timer, data_feeder
from connections.broker_connection import Broker_Connection



module_alycs = [brokers.cocos_id]


"""
VER DE AGREGAR UNA CLASE, UNA FUNCION O UNA LISTA, DICCIONARIO O QUE DE CONSULTAS A LA WEB
Y ASI TAMBIEN PODRIA SEPÀRAR LO ESPECÍFICO DE UN FORMATO DE CONEXION (SEGUN BROKER, SISTEMA ETC.) DE LA TAREA EN SI DE PROCESAR LA INFO RECIBIDA
"""
class Order:
    pass

class appCocos(Broker_Connection):
    alycs = [brokers.cocos_id] # necesito esto acá
    # Los atributos de clase son compartidos por todas las instancias de la clase y no pertenecen a cada instancia de forma individual. 
    # Todas las instancias de la clase accederán y modificarán el mismo valor de dichos atributos de clase.
    # Los siguientes son atributos de clase:
    attempts = range(1,6)
    sleep_time = 1
    url = {'login':         'https://api.cocos.capital/auth/v1/token?grant_type=password',
           'me':            'https://api.cocos.capital/api/v1/users/me',
           'buying-power':  'https://api.cocos.capital/api/v2/orders/buying-power',
           'selling-power': 'https://api.cocos.capital/api/v2/orders/selling-power?long_ticker=',
           'portfolio':     'https://api.cocos.capital/api/v1/wallet/portfolio', 
           'orders':        'https://api.cocos.capital/api/v2/orders',
           'tickers_rules': 'https://api.cocos.capital/api/v1/markets/tickers/rules'}
    
    def __init__(self, account:dict=None, wait_time:float=12):
        
        ##################################################
        ### Proteger los objetos del bloqueo con locks ###
        ##################################################
        
        self.auth_token = ''
        self.log = {}
        
        (account:= {} if account is None else account).update(dict(module='appCocos', broker_id=265))  # Con esta línea aseguro el módulo y el broker correcto.
        super().__init__(account=account)  # Llama a login()
        
        self.headers = { 'Authorization': self.auth_token, 'x-account-id': str(self.nroComitente) }
        self.orders_df = Object_with_Lock(orders_helper.app_cocos_data['orders_empty_df'])
        self.orders_summary = Object_with_Lock(pd.DataFrame())
        self.orders = {}
        #self.orders = Object_with_Lock(orders_helper.app_cocos_data['orders_empty_df'])
        self.orders_ids = []
        
        self.ordersList = File_with_Lock('app_cocos_orders_'+str(self.nroComitente))
        self.pendingOrdersFile = File_with_Lock('app_cocos_'+str(self.nroComitente)+'_pending_orders')
        self.pendingOrdersDF = Object_with_Lock(orders_helper.app_cocos_data['orders_empty_df'])
        self.tenencias  = Object_with_Lock(pd.DataFrame())
        self.saldos     = Object_with_Lock(pd.DataFrame())
        
        
    def print_msg(self, msg:str):
        caller_function = inspect.currentframe().f_back.f_code.co_name
        if caller_function in ['logged_in', 'attain_new_token']:
            print(msg.format(self.credentials['nombreCompleto'], self.nroComitente))
        
    def login(self, token_file_read=False):
        super().login()
        if self.auth_token != '' and self.logged_in(msg=True): return True
        if not token_file_read:
            self.auth_token = file_manager.read_txt('app_cocos_token_'+str(self.nroComitente), path=brokers.token_path)
            return self.login(True)
        return self.attain_new_token()
    
    def logged_in(self, msg=False):
        if isinstance(self.auth_token, str) and len(self.auth_token) > 0:
            self.log['logged_in_response'] = response = requests.get(self.url['me'], headers={ 'Authorization': self.auth_token})
            if response.status_code < 400 and response.json()['id_accounts'][0] == self.nroComitente:
                if msg: self.print_msg(' Sesión de usuario {} \n con app Cocos cuenta Nº {} ya iniciada. Continúa')
                return True
        if msg: self.print_msg(' El usuario {} \n con app Cocos cuenta Nº {} NO está logueado.')
        return False
        
    def attain_new_token(self):
        headers = { "User-Agent": user_agents.get_random(), "Accept-Encoding": "gzip, deflate, br", }
        payload = {'email':    self.credentials['user'], 
                   'password': self.credentials['password'] } 
        self.print_msg(' Iniciando sesión con usuario {} \n app Cocos cuenta Nº {}')
        self.log['new_token_response'] = response = requests.post(self.url['login'], json=payload, headers=headers)
        if response.status_code < 400 and response.json()['user']['aud']=='authenticated':
            self.auth_token = 'Bearer {}'.format(response.json()['access_token'])
            self.headers = { 'Authorization': self.auth_token, 'x-account-id': str(self.nroComitente) }
            print(' --- Login Exitoso ---')
            if file_manager.save_to_txt(self.auth_token, 'app_cocos_token_'+str(self.nroComitente), path=brokers.token_path):
                print(' Token guardado en archivo.')
            else: print(' El token NO pudo ser guardado en archivo.')
            return True
        else: print(' --- El usuario no pudo ser autenticado ---'); return False
        
        
    def update_orders(self, sleep_time=0):
        def thread(order_id:str, url:str, headers:str, orders_df):
            response = requests.get(url+'/'+order_id, headers=headers)
            if response.status_code < 400 and response.json():
                order_data = pd.DataFrame()  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                with orders_df as df: df.update(order_data)
                
        if not self.logged_in(): self.login()
        with self.orders_df as df: orders_ids = df.index.values
        threads = []; url = self.url['orders']; headers=self.headers
        for order_id in orders_ids:  # no hace falta hacer len(orders_ids) > 0 ya que si es 0 no entra
            threads += [threading.Thread(target=thread, args=(order_id, url, headers, self.orders_df))]
            threads[-1].start()
        for t in threads: t.join()
        # y acá tengo que guardar en archivo
        time.sleep(sleep_time if sleep_time > 0 else self.sleep_time)
            
            

    
    def send_order(self, order:Order):  # symbol, price, size, op_type='buy', settlement='spot'):
        print(' Enviando órden: {} {} {} {} nominales a $ {}'.format(
               order.op_type, order.settlement, order.symbol, order.size, order.price))
        payload = {'type': 'LIMIT', 'side': order.op_type, 'quantity': order.size, 
                   'long_ticker': order.long_ticker, 'price': order.price}
        self.log['send_order_response'] = response = requests.post(self.url['orders'],
                                                                   headers=self.headers, data=payload)
        if response.status_code < 400 and response.json()['Success']:
            order.id = response.json()['Orden']; self.orders[order.id] = order
            if not self.ordersList.append(str(order.to_str())+','): print(' La orden no pudo ser guardada (intente manualmente). Continúa.')
            file_manager.append_to_txt(order.id+', ', 'app_cocos_orders__pending')
            # self.update_orders(order)
            print('\n Orden nro {} enviada exitosamente:'.format(order.id))
            print('  {} {} {} {} nominales a $ {} '.format(
                   order.op_type, order.settlement, order.symbol, order.size, order.price))
        elif response.status_code < 400 and response.json()['message'] == 'jwt expired':
            print(' La sesión ha expirado. Se reintenta.')
            if self.attain_new_token(): self.send_order(order)
        else: print(' Orden Rechazada: ', response.text)
    
    def send_multiple_orders(self, df):  # ya el dataframe podría venir cargado con un listado de objetos Order
        orders=[]
        for index, row in df.iterrows():
            try:
                orders += [Order(*iter(row))]
                threading.Thread(target=self.send_order, args=(orders[-1],), daemon=True).start()
            except Exception as exception:
                print(' DataException. {} '.format(str(exception)))
                continue
        return orders
    
    def cancel_orders(self, ordersToCancel=None):  # ordersToCancel es un DataFrame
        if ordersToCancel is None:
            print(' ============= Cancelando TODAS las Ordenes =============')
            file_name = 'app_cocos_orders__pending'        
            otc = file_manager.read_txt(file_name).split(', ')[:-1]
            file_manager.save_to_txt('', file_name)

            threads=[]
            for i in otc:
                threads += [threading.Thread(target=self.cancel_order, args=(i,))]
                threads[-1].start()
            for t in threads:
                t.join()
                
            # repito por las dudas    
            for i in otc:
                self.cancel_order(i)
            
            print(' Todavia no implementado! ')
          # thread()  # no necesito crear un nuevo hilo, solo llamo a la funcion.
          # self.cancel_orders( Data.pending_orders(self.ordersList.obj, self.ordersList.lock) )
        else: 
            print(' ================== Cancelando Ordenes ===================')
            # print(ordersToCancel)
            # print(ordersToCancel.columns)
            columns_to_drop = ['datetime', 'status'] + [None]*(None in ordersToCancel) + [True]*(True in ordersToCancel)
            ordersToCancel.drop(columns_to_drop, axis=1, inplace=True)
            print(ordersToCancel)
            for order_id, order in ordersToCancel.iterrows():
                threading.Thread(target=self.cancel_order, args=(order_id,), daemon=True).start()  
        
    def cancel_order(self, order_id:str):
        
        response = requests.delete(self.url['orders']+'/'+order_id, headers=self.headers)
        self.cancel_response = response
        print(response.text)
        
        {"message":"The order cannot be cancelled. The order has status: CANCELLED"}
        {"message":"The order cannot be cancelled. The order has status: FILLED"}
        {"Success":true,"Orden":"7c766fd2-3aaa-4584-b662-ce8d4284c1c0"}
        
        
        
    def ordersList_read(self):
        ordersList = self.ordersList.read()
        if len(ordersList) > 0: return pd.DataFrame(json.loads(f"[{ordersList[:-2]}]")) 
        return orders_helper.app_cocos_data['orders_empty_df']
        

        {'order_id': '7c766fd2-3aaa-4584-b662-ce8d4284c1c0',
          'order_type': 'BUY',
          'ticker': 'GD30',
          'instrument': '',
          'currency': 'USD',
          'settlement_days': 2,
          'date': '2023-06-01T19:37:17.65045+00:00',
          'status': 'CANCELLED',
          'set_quantity': 2,
          'set_price': 26.23,
          'result_quantity': 2,  ## ????????
          'result_price': 26.23,
          'error': None,         ## ????????
          'quantity_oms': 2}     ## ????????
    def get_orders_status(self):
        headers={ 'Authorization': self.auth_token, 'x-account-id': str(self.nroComitente), 'Cache-Control': 'no-cache' } # Agrega 'no-cache' para forzar la respuesta 
        response = requests.get(self.url['orders'], headers=headers)
        self.orders_status_response = response
        if response.status_code < 400 and response.json() is not None:
            # df = pd.DataFrame(response.json(), columns=['order_id', 'date', 'ticker', 'currency', 'settlement_days',
            #                   'order_type', 'set_quantity', 'set_price', 'result_quantity', 'status']).set_index('order_id')
            df = pd.DataFrame(response.json(), columns=['order_id', 'order_id_ext', 'date', 'ticker', 'settlement_days', 'order_type',
                              'set_quantity', 'set_price', 'result_quantity', 'status', 'currency', 'set_amount']).set_index('order_id')
            # df = sf.filtrar(df, status=o('PENDING', 'PARTIAL'))
            df['ticker'] = np.where(df['currency'].values=='USD', df['ticker']+'D', df['ticker'])  # np.where es más rápido que df.loc
            # df = df.drop(['currency'], axis=1)  # Ulteriormente no me conviene eliminar esta columna
            df['date'] = pd.to_datetime(df['date'].values)
            # df = df.rename(columns=orders_helper.app_cocos_data['orders_columns_new_names'])
            df.columns = orders_helper.orders_columns_names
            df['account'] = self.credentials['ususario']
            
            # Creo un nueva instancia del dataframe filtrado para luego guardarlo con un nuevo hilo (y así
            # evitar la espera de posesión del lock) consiguiendo agilizar toda la ejecucion de esta función:
            filtered_df = df[(df.status.values=='MARKET') | (df.status.values=='PARTIALLY_EXECUTED')]
            threading.Thread(target=self.update_orders_df, args=(df,), daemon=True).start()
            
            return filtered_df
        
    def update_orders_df(self, df):
        with self.orders_df as orders_df:  
            orders_df = df
            # Creo un df auxiliar para evitar usar el lock de orders_df cuando estoy esperando para actulizar el valor en self.orders_summary (y también porque groupby hace una copia):
            summary_df = orders_df.groupby(['symbol', 'settlement', 'op_type'])[['size', 'amount']].sum().reset_index().rename_axis(datetime.now().strftime('%H:%M.%Ss'))
        self.orders_summary.set_obj_value(summary_df)
        
    
    def get_order_status(self, order_id):
        response = requests.get(self.url['orders']+'/'+order_id, headers=self.headers)
        self.get_order_status_response = response
        # self.orders_ids += [response.json()]
        print(response.text)
        
        
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
                                 args=(self.ordersList, stop_event, self.sleep_time, self.get_orders_status, message_to_print, msg), daemon=True)
                updater_thread.start()
            time.sleep(self.sleep_time)
        print(' ========== Actualización de Ordenes Terminada ==========')

 
    def account_info(self, process_list=[], msg=False): # antes incluia: process_list=[1, 62]
        def _procesar(self, proceso:dict, cookie, msg=False):  # !!!!!!!!!!!!!!!!!!!! borrar process
            start_time = time.monotonic()
            payload = { 'comitente': str(self.auth.nroComitente), 'proceso': str(proceso) }  
            url = '{}/Consultas/GetConsulta'.format(self.auth.broker_url)
            for i in self.attempts:
                if i > self.attempts[0]: time.sleep(self.sleep_time)  # se ejecuta una pausa si es que no es el primer intento
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
        start_time = time.monotonic()
        for i in self.attempts:
            if i > self.attempts[0]: time.sleep(self.sleep_time)  # se ejecuta una pausa si es que no es el primer intento
            response = requests.get(self.url['buying-power'], headers=self.headers)
            if response.status_code < 400:
                data = pd.DataFrame(response.json())
                data.index.name = datetime.now().strftime('%H:%M.%Ss')
                self.saldos.set_obj_value(data)
                break
        return time.monotonic() - start_time
    
        
    def procesar_tenencias(self):  # , msg=False):
        start_time = time.monotonic()
        for i in self.attempts:
            if i > self.attempts[0]: time.sleep(self.sleep_time)  # se ejecuta una pausa si es que no es el primer intento
            response = requests.get(self.url['portfolio'], headers=self.headers)
            if response.status_code < 400:
                tickers = response.json()['tickers']
                data = []
                for i in tickers:
                    if i['instrument_code'] is not None:
                        response = requests.get(self.url['selling-power']+i['instrument_code']+'-0003-C-CT-ARS', headers=self.headers)
                        if response.status_code < 400:
                            dicc = response.json()
                            del dicc['id_account']
                            dicc['id_instrument'] = i['instrument_code']
                            data+=[dicc]
                
                if len(data)>0: self.tenencias.set_obj_value(pd.DataFrame(data).set_index('id_instrument').rename_axis(index={'id_instrument':datetime.now().strftime('%H:%M.%Ss')}))
                break
        return time.monotonic() - start_time
            
            
    def _process(self):
        self.procesar_poder_compra()
        self.procesar_tenencias()
        print(self.saldos.obj)
        print(self.tenencias.obj)
        
        
        
        """
            data = pd.DataFrame.from_dict(aux, orient='index', columns=['Total'])
            data['Disponible'] = data['Total']
            data.index.name = datetime.now().strftime('%H:%M.%Ss')
            self.tenencias.set_obj_value(data)
            return time.monotonic()
        """
    
        


    
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
    """
    case Vo.PENDING:
                return "En mercado";
            case Vo.CANCELLED:
                return "Cancelada";
            case Vo.COMPLETED:
                return "Concretada";
            case Vo.PARTIAL:
                return "Parcial";
            default:
                return "En proceso"
            }


            e.PENDING = "PENDING",
            e.COMPLETED = "COMPLETED",
            e.CANCELLED = "CANCELLED",
            e.PARTIAL = "PARTIAL",
            e.ERROR = "ERROR",
            e.EXECUTED = "EXECUTED",
            e.CONFIRMED = "CONFIRMED"
    """
    settlement_map = {k: v for k, v in zip(securities.settlements, ['1', '2', '3'])}
    id=''

    def __init__(self, symbol, price, size, op_type='buy', settlement='spot'): # hb, avg_purch_price=0
        
        self.symbol = symbol
        
        "GD30D-0001-C-CT-USD"
        
        """
        if symbol in Data.symbols: self.symbol = symbol
        else: raise Exception(' Símbolo inválido!')
        """
        if float(price) > 0: self.price = float(price)
        else: raise Exception(' Precio inválido!')
        
        if int(size) > 0: self.size = int(size)
        else: raise Exception(' Cantidad inválida!')
        
        if op_type.lower() in ['buy', 'sell']: self.op_type = op_type.upper()
        else: raise Exception(' Operación inválida!')
        
        if settlement in securities.settlements: self.settlement = settlement
        else: raise Exception(' Plazo inválido!')
        
        self.status = self.status_map['CREATED']
        self.number = 0
        self.original_size = 0
        self.cancellable = True
        self.remaining_size = self.size
        self.datetime = pd.to_datetime(datetime.now())
        
        self.long_ticker = self.symbol+'-000'+self.settlement_map[self.settlement]+'-C-CT-'+('USD' if self.symbol.endswith('D') else 'ARS')
        # if self.symbol == 'GD30D': self.long_ticker = 'sdsd'
        
    def to_str(self):
        return str({'id': self.id, 'symbol': self.symbol, 'price': self.price, 'size': self.size, 
                    'op_type': self.op_type, 'settlement': self.settlement, 'datetime': str(self.datetime), 
                    'long_ticker': self.long_ticker}).replace("'", "\"")+', '
    
    def to_lst(self):
        return [{'id': self.id, 'symbol': self.symbol, 'price': self.price, 'size': self.size, 
                    'op_tyoe': self.op_type, 'settlement': self.settlement, 'datetime': str(self.datetime), 
                    'long_ticker': self.long_ticker},]
        
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
        
# connection_class = App_Cocos