# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro
"""

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import object_session, DeclarativeBase
from sqlalchemy import not_  # , and_, select
from connections.database import db_conn


class Query:
    
    @staticmethod
    def build(session:db_conn.Session, tables:list[DeclarativeBase], filters:dict[[str, callable], dict]):
        """ Recibe como parametros:
            - session: es la sesion que se va a usar para consultar (tipo: Session).
            - tables:  es un lista de las tablas (ya mapeadas en db_map) sobre las que se van a hacer
              las consultas a la base de datos. La primer tabla en la lista es sobre la que se va a
              traer toda la información.
            - filters: es un diccionario que tiene como key el tipo de consulta (ej: equal_to, etc)
              que puede ser un string o un callable que llama directo a la función, como value otro 
              diccionario (con el key como atributo de la tabla y como value el valor buscado para
              ese atributo, y solo 1 valor, no una lista a menos que es lo que se busque).
        """
        querys = {}
        for fk, fv in filters.items():
            if fv is not None:
                querys.update( {fk: [{} for table in range(len(tables))] } )
                for k, v in fv.items():
                    for idx in range(len(tables)):
                        if k in tables[idx].__annotations__.keys():
                            querys[fk][idx].update({k:v})
                            break      
        query = None
        for qk, qv in querys.items():
            if qv != {}:
                for idx in range(len(tables)):  # la cantidad va a coincidir con la cantidad de items de querys
                    method = getattr(Query, qk) if isinstance(qk, str) else qk  # En la ultima opción se tiene que cumplir callable(qk)==True
                    qry = session.query(tables[idx])
                    if query is None: 
                        query = method(qry=qry, table=tables[idx], values=qv[idx])
                    else:
                        query = query.join( method(qry=qry, table=tables[idx], values=qv[idx]).subquery() )
        return query

    @staticmethod
    def equal_to(qry, table, values):
        return qry.filter_by(**values)
        
    @staticmethod
    def not_equal_to(qry, table, values):
        for k, v in values.items():
            qry = qry.filter(not_(getattr(table, k) == v))
        return qry
            
    @staticmethod
    def contains(qry, table, values):    
        for k, v in values.items():
            qry = qry.filter(getattr(table, k).like('%{}%'.format(v)))
        return qry
        
    @staticmethod
    def not_contains(qry, table, values):
        for k, v in values.items():
            qry = qry.filter(not_(getattr(table, k).like('%{}%'.format(v))))
        return qry


def get(session, results=0, *args, **kwargs):  # SELECT
    qry = Query.build(session, *args, **kwargs)
    if results is None: return qry
    results_map = {0: 'all', 1: 'first'}
    return getattr(qry, results_map.get(results))()


def put(session, obj, key, value):
    if   object_session(obj) is None: session.add(obj)
    elif object_session(obj) is not session: session = object_session(obj)
    setattr(obj, key, value)    
    session.commit()
    return obj  #.primary_key   ## ???


def query(session=None, method=None, *args, **kwargs):  # Nombre alternativo para la función: frame.
    if isinstance(method, str): method = {'get': get, 'put': put}.get(method)
    try: 
        if session is not None: return method(session, *args, **kwargs)  # No cierra la sesion
        with db_conn.Session() as sess:  # Cierra la sesion
            return method(sess, *args, **kwargs)
    except OperationalError as e:
        print(str(e))
        print(' Falló la operación con la base de datos. No se reintenta.')
