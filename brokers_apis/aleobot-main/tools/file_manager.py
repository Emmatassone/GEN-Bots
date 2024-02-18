#  -*- coding: utf-8 -*-
"""
@author: Alejandro Ben
"""
import os
import threading
import pickle
import json
import numpy as np
import pandas as pd
import xlwings as xw
from datetime import datetime, timedelta
from cryptography.fernet import Fernet


#########################
####### TXT FILES #######
#########################
def df_to_txt(df:pd.DataFrame, file_name:str, path:str=''):
    try: 
        df.to_csv(f"{path}{file_name}.txt", sep='\t')
        return True
    except Exception as e:
        print(f"Hubo un problema al guardar el archivo: {e}")
        return False
    
def df_from_txt(file_name:str, path:str=''):
    try: 
        return pd.read_csv(f"{path}{file_name}.txt", sep='\t')
    except Exception as e:
        print(f"Hubo un problema al leer el archivo: {e}")
        return False

def save_to_txt(var, file_name:str, path:str=''):
    with open(f"{path}{file_name}.txt", "w") as file:
        return True if file.write(str(var)) > 0 else False
    
def read_txt(file_name:str, path:str=''):
    with open(f"{path}{file_name}.txt", "r") as file:
        return file.read()
    
def append_to_txt(var, file_name:str, path:str=''):
    with open(f"{path}{file_name}.txt", "a") as file:
        return True if file.write(str(var)) > 0 else False

def read_file_to_numpy(file_name:str, path:str=''):
    return np.array(read_txt(file_name=file_name,path=path).split('\n'))


class File:
    def __init__(self, file_name:str, path:str=''):
        self.file_name = file_name
        self.path = path if path != '' else os.getcwd()+'\\'

#########################
####### JSON FILES ######
#########################
class Json(File):
    
    def save(self, data:dict):
        with open(f"{self.path}{self.file_name}.json", "w") as file:
            json.dump(data, file)
    
    def read(self) -> dict:
        with open(f"{self.path}{self.file_name}.json", "r") as file:
            return json.load(file)


def raiseException(msg=None):
    raise Exception(msg)
            
class File_with_Lock:  # clase idéntica a Pipeline
    def __init__(self, file_name:str, file_type:str='txt', path:str=''):
        self.file_name = file_name
        self.path = path
        self.file_type = file_type if file_type in ['txt', 'pkl'] else raiseException(' Formato de archivo no soportado')
        self.lock = threading.Lock()

    def read(self):
        with self.lock:
            if   self.file_type == 'txt': return read_txt(file_name=self.file_name, path=self.path)
            elif self.file_type == 'pkl':
                with open('{}.pkl'.format(self.path+self.file_name), "rb") as file:
                    return pickle.load(file)
        
    def write(self, value):
        with self.lock:
            if   self.file_type == 'txt': return save_to_txt(value, file_name=self.file_name, path=self.path)
            elif self.file_type == 'pkl': 
                with open('{}.pkl'.format(self.path+self.file_name), "wb") as file:
                    pickle.dump(value, file); return True  # pickle.dump no retorna nada. Si no hay excecpcion es porque se guardó correctamente
        return False
            
    def append(self, value):  # and update en el caso del dataframe
        if self.file_type == 'txt': 
            with self.lock: return append_to_txt(value, file_name=self.file_name, path=self.path)
        elif self.file_type == 'pkl': 
            data = self.read()
            if   isinstance(value, pd.DataFrame) and isinstance(data, pd.DataFrame):
                data = value.combine_first(data) # el orden value-data es correcto así
            elif isinstance(value, list) and isinstance(data, list):
                data += value
            elif isinstance(value, dict) and isinstance(data, dict):
                data.update(value)
            return self.write(data)
        

#########################
####### PASSWORD ########
#########################
class Password:
    # Tengo que encontrar la manera de usar esto:
    _salt = str(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=16581))

    def __init__(self, nroComitente, file_name_mask='clave_{}.txt', path:str=''):
        self._file_name = file_name_mask.format(nroComitente)
        self._path = path
        with open(self._path+'clave_key.txt', 'rb') as f:
            self._key=f.read()
        self._crypt = Fernet(self._key)
        
    def save(self, clave):  # Uso: Password('{Nro.Comitente}').save('{Clave}')
        with open(self._path+self._file_name, 'wb') as f:
            f.write(self._crypt.encrypt( str(clave).encode()))
        print('\nClave guardada correctamente.')

    def read(self):   # Uso: Password('{Nro.Comitente}').read()
        # Se lee la clave cifrada desde el archivo
        with open(self._path+self._file_name, 'rb') as f:
            return self._crypt.decrypt(f.read()).decode()


#########################
####### XLS FILES #######
#########################
def open_in_new_instance_if_not_opened(file_abspath:str):  # Debe pasarse con el siguiente formato r'C:\ruta\a\archivo\nombre.extension'
    for app in xw.apps:
        for book in app.books:
            if book.fullname == os.path.abspath(file_abspath):
                return book  # Si el archivo está abierto lo retorna
    # Si no está abierto, crea una nueva instancia de Excel y lo abre y retorna el libro
    return xw.App(add_book=False).books.open(file_abspath)


#########################
######### MAIN ##########
#########################
if __name__ == '__main__':
    _path = os.getcwd()[:os.getcwd().find('tools')] +'data\\accounts\\keys\\'
    if input(' Desea guardar una nueva clave? (ingresar S ó s): ').lower() == 's':
        while True: 
            _module = {1: 'appCocos', 2: 'HB', 3: 'pyRofex' }.get(int( input('\n 1- appCocos\n 2- HB \n 3- pyRofex \n\n Elija una opción: ') ) )
            if _module is None: print('\n Ha ingresado una opción inválida.')
            else: break
        Password(input('\n Ingrese Comitente Nro: '), file_name_mask=_module+'_clave_cta_{}.txt', path=_path).save(input('\n Ingrese Comitente Clave: '))
