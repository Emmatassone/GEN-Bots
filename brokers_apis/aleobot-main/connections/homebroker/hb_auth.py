# -*- coding: utf-8 -*-
"""
Created on Thu May 25 20:17:36 2023

@author: Alejandro
"""

import time, threading
import requests as rq
import urllib.parse, json
from pyquery import PyQuery as pq

from pyhomebroker import HomeBroker

from .hb_imports import hb_user_agent, hb_brokers
from connections.common import AR_ip
from tools.variables_with_lock import List_with_Lock


class Account_Auth:
    def __init__(self, broker_id, nroComitente, cookies_qty=1, msg=False, credentials=None):
        self.msg=msg
        self.nroComitente = int(nroComitente)
        self.broker_id = int(broker_id)
        self.broker_url = hb_brokers.loc[self.broker_id, 'url']
        self.credentials = credentials
        
        self.payload = { 'Dni': self.credentials['dni'], 'Usuario': self.credentials['user'], 
                         'Password': self.credentials['password'] }
        self.cookies = List_with_Lock([])
        print(' Iniciando sesión con cuenta Nº {}: \n  {} ( Broker Nº {} ) '.format(self.nroComitente, 
                self.credentials['nombreCompleto'], self.broker_id))
        start_time = time.monotonic()
        threads = []
        for i in range(cookies_qty): 
            threads += [threading.Thread(target=self._attain_cookie, daemon=True)]
            threads[i].start()  # with concurrent.futures.ThreadPoolExecutor(daemon=True) da error ya que no recibe el parametro deamon
        for t in threads: t.join()
        print(' --- Login Exitoso ---') if len(self.cookies) > 0 else print(' --- El usuario no pudo ser autenticado ---')       
        if self.msg: print(' Tiempo insumido (en segundos) para {}: {:.3f}'.format('__init__', time.monotonic()-start_time))
        
    def _attain_cookie(self):
        for m in [self.login_main, self.login_alternative, self.login_alternative_2, self.hb_login]:
            cookie = m()
            if cookie != []:
                self.cookies += cookie; break
            
    def hb_login(self):
        start_time = time.monotonic()
        hb = HomeBroker(self.broker_id)
        rta = hb.auth.login(dni=self.credentials['dni'], user=self.credentials['usuario'],
                            password=self.credentials['password']['HB'])
        if self.msg: print(' Tiempo insumido (en segundos) para {}: {:.3f}'.format('hb_login', time.monotonic()-start_time))
        self.actual_ip = hb.auth._HomeBrokerSession__ipaddress
        return [hb.auth.cookies] if rta else []
    
    def _login(self, method, url, payload, headers):
        start_time = time.monotonic()
        with rq.Session() as sess:
            response = sess.post(url, data=payload, headers=headers)
            if response.status_code >= 400: return [] # Si status_code es mayor o igual a 400 (categoría de errores 4xx o 5xx) retorna [] para intentar otro metodo.
        
            doc = pq(response.text)
            if not doc('#usuarioLogueado'):
                errormsg = doc('.callout-danger')
                if errormsg: 
                    print(errormsg.text())
                    raise Exception(' Error al loguearse. No se reintenta. ')
                else: print('Session cannot be created. Check the entered information and try again.')
                return []
            
            if self.msg: print(' Tiempo insumido (en segundos) para {}: {:.3f}'.format(method, time.monotonic()-start_time))
            return [{k: v for k, v in sess.cookies.items()}]
                
    def login_main(self):
        payload = self.payload
        payload['IpAddress'] = AR_ip.get_random()
        payload = urllib.parse.urlencode(payload)
        headers = { 'User-Agent': hb_user_agent, 'Accept-Encoding': 'gzip, deflate',
                    'Content-Type': 'application/x-www-form-urlencoded' }
        url = '{}/Login/Ingresar'.format(hb_brokers.loc[self.broker_id, 'url'])
        return self._login('login_main', url, payload, headers)
        
    def login_alternative(self):
        payload = self.payload
        payload['IpAddress'] = AR_ip.get_random()
        payload = json.dumps(payload, separators=(',', ':'))
        headers = { 'User-Agent': hb_user_agent, 'Accept-Encoding': 'gzip, deflate',
                    'Content-Type': 'application/json; charset=utf-8' }
        url = '{}/Login/IngresarModal'.format(hb_brokers.loc[self.broker_id, 'url'])
        return self._login('login_alternative', url, payload, headers)
        
    def login_alternative_2(self):
        url = '{}/Login/Ingresar'.format(hb_brokers.loc[self.broker_id, 'url'])
        return self._login('login_alternative_2', url, self.payload, headers={})
 