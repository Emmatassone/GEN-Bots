# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro

Requirements:
- SQLAlchemy Version: 2.0.25
- typing_extensions Version: 4.9.0
    pip install --upgrade sqlalchemy
    pip install --upgrade sqlalchemy typing-extensions
    
Based on the new ORM Declarative Typing Model that follows PEP 484 typing practices 
https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#whatsnew-20-orm-declarative-typing
"""
# https://docs.sqlalchemy.org/en/20/core/connections.html
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
# https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-declarative-mapping
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#declarative-table-with-mapped-column

# https://docs.sqlalchemy.org/en/20/orm/declarative_config.html#constructing-mapper-arguments-dynamically

from datetime import datetime
from typing import Dict, List  # , Optional, 
from sqlalchemy import String, Text, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship  #, backref
import pandas as pd


# declarative base class
class Base(DeclarativeBase):
    
    def to_dict(self, keys_excluded:list=None) -> Dict:
        keys_excluded = ['_sa_instance_state'] + (keys_excluded if keys_excluded else [])
        return {k: v for k, v in self.__dict__.items() if k not in keys_excluded}
        # Con esa logica evito retornar el __dict__ sino una copia y que modificaciones inintencionales sobre el valor retornado modifique el de la instancia de esta clase.
        
    def key(self):  # return_key
        # return {attr.key: getattr(self, attr.key) for attr in inspect(self.__class__).columns if attr.primary_key}
        return self.data(primary_key=True)
    
    def data(self, primary_key=False):  # return_data
        return {attr.key: getattr(self, attr.key) for attr in inspect(self.__class__).columns if (attr.primary_key if primary_key else True)}
    
    def validate_kwargs(self, **kwargs):
        if not self.columns_not_none.issubset(set(kwargs.keys())): 
            raise Exception(' Missing args: {}'.format([self.columns_not_none - set(kwargs.keys())]))
        for k, v in kwargs.items():
            if not isinstance(v, self.columns_types.get(k)): 
                raise Exception(' {} value: {} TypeError: {} instead of {}'.format(k, v, type(v), self.columns_types.get(k)))
        # Falta agregar para los tipos unsigned y quizá validar el dato según un listado para el modulo específico.
    

class Modules(Base):
    __tablename__ = 'modules'
    name: Mapped[str] = mapped_column(String(16), primary_key=True)
    
    # Relaciones:
    credentials: Mapped[List['Credentials']] = relationship(back_populates='module_', lazy='joined')
    urls:        Mapped[List['Urls']]        = relationship(back_populates='module_', lazy='joined')
    
class Brokers(Base):
    __tablename__ = 'brokers'
    id:        Mapped[int] = mapped_column(primary_key=True)
    name:      Mapped[str] = mapped_column(String(255), nullable=False)
    short_str: Mapped[str] = mapped_column(String(50),  nullable=False)
    
    # Relaciones:
    accounts: Mapped[List['Accounts']] = relationship(back_populates='broker', lazy='joined')
    urls:     Mapped[List['Urls']]     = relationship(back_populates='broker', lazy='joined')

   
class Urls(Base):
    __tablename__ = 'urls'
    module:       Mapped[str] = mapped_column(ForeignKey('modules.name'))
    broker_id:    Mapped[int] = mapped_column(ForeignKey('brokers.id'), index=True)
    key:          Mapped[str] = mapped_column(String(30))
    address:      Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relaciones:    
    broker:  Mapped['Brokers'] = relationship(back_populates='urls', lazy='joined')
    module_: Mapped['Modules'] = relationship(back_populates='urls', lazy='joined')
    
    # PrimaryKeyConstraint on composite keys:  (Ver [1])
    __table_args__ = (PrimaryKeyConstraint(module, broker_id, key), )
    
    @property
    def broker_name(self):
        if self.broker: return self.broker.name
    

class Persons(Base):
    __tablename__ = 'persons'
    dni:            Mapped[int] = mapped_column(primary_key=True)
    nombreCompleto: Mapped[str] = mapped_column(String(255), nullable=False)
    CUIT:           Mapped[int|None] = mapped_column()
    
    # Relaciones:
    accounts: Mapped[List['Accounts']] = relationship(back_populates='person', lazy='joined')
    
    
class Accounts(Base):
    __tablename__ = 'accounts'
    broker_id:    Mapped[int] = mapped_column(ForeignKey('brokers.id'))
    nroComitente: Mapped[int] = mapped_column()
    dni:          Mapped[int] = mapped_column(ForeignKey('persons.dni'), nullable=False)
    
    # Relaciones:    
    broker: Mapped['Brokers'] = relationship(back_populates='accounts', lazy='joined')
    person: Mapped['Persons'] = relationship(back_populates='accounts', lazy='joined')
    credentials: Mapped[List['Credentials']] = relationship(back_populates='account', lazy='joined')
    
    # PrimaryKeyConstraint on composite keys:  (Ver [1])
    __table_args__ = (PrimaryKeyConstraint(broker_id, nroComitente), )
    
    @property
    def nombreCompleto(self):
        if self.person: return self.person.nombreCompleto
    @property
    def broker_name(self):
        if self.broker: return self.broker.name
    
    
class Credentials(Base):   ## Reviar lo de ondelete='CASCADE', onupdate='CASCADE'  !!!!!!!!!!!!!!!!!!
    __tablename__ = 'credentials'
    broker_id:    Mapped[int] = mapped_column()  # ForeignKey('Accounts.broker_id') y primary_key=True ya están en __table_args__
    nroComitente: Mapped[int] = mapped_column()  # ForeignKey('Accounts.nroComitente') y primary_key=True ya están en __table_args__
    module:       Mapped[str] = mapped_column(ForeignKey('modules.name'), index=True)  # primary_key=True ya están en __table_args__
    user:         Mapped[str] = mapped_column(String(30),  nullable=False)
    password:     Mapped[str] = mapped_column(String(255), nullable=False)
    conn_id:      Mapped[int] = mapped_column(nullable=False, index=True, autoincrement=True)
    conn_token:   Mapped[str|None] = mapped_column(String(999))
    
    # Relaciones:
    account: Mapped['Accounts']     = relationship(back_populates='credentials', lazy='joined')
    module_: Mapped['Modules']      = relationship(back_populates='credentials', lazy='joined')
    orders:  Mapped[List['Orders']] = relationship(back_populates='conn',        lazy='joined')
    
    # ForeignKeyConstraint relations on composite keys:  (Ver [1])
    __table_args__ = (PrimaryKeyConstraint( broker_id, nroComitente, module),
                      ForeignKeyConstraint([broker_id, nroComitente],
                                           [Accounts.broker_id, Accounts.nroComitente]), )
    @property
    def nombreCompleto(self): 
        if self.account: return self.account.nombreCompleto    
    @property
    def dni(self):
        if self.account: return self.account.dni
    @property
    def broker_name(self):
        if self.account: return self.account.broker
    
    # dict_keys_attributes:
    attributes_names = ['nombreCompleto', 'dni', 'broker_name']
        
    def data_ext(self):
        # d = self.to_dict(keys_excluded=['account'])
        d = self.data()
        d['nombreCompleto'] = self.account.person.nombreCompleto
        d['broker_name'] = self.account.broker.name
        d['dni'] = self.account.dni
        return d
    
Credentials.attributes_names += [c.name for c in inspect(Credentials).columns]
        

class Orders(Base):
    __tablename__ = 'orders'
    id:          Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    conn_id:     Mapped[int]      = mapped_column(ForeignKey('credentials.conn_id'), index=True)
    id_int:      Mapped[str]      = mapped_column(String(50), comment='internal id')
    id_ext:      Mapped[str|None] = mapped_column(String(50), comment='external id')
    date_time:   Mapped[datetime] = mapped_column(server_default="now()")
    symbol:      Mapped[str]      = mapped_column(String(50), nullable=False)
    settlement:  Mapped[int]      = mapped_column(nullable=False, server_default='0')
    op_type:     Mapped[int]      = mapped_column(nullable=False, server_default='1')
    size:        Mapped[int]      = mapped_column(nullable=False)
    price:       Mapped[float]    = mapped_column(nullable=False)
    
    remaining:   Mapped[int]      = mapped_column(nullable=False, server_default='size')
    status:      Mapped[int]      = mapped_column(nullable=False, server_default='0')
    currency:    Mapped[int]      = mapped_column(nullable=False, server_default='0')
    amount:      Mapped[float]    = mapped_column(nullable=False, server_default="(size*price)")
    
    order_type:  Mapped[int]      = mapped_column(server_default='0')
    cancel_prev: Mapped[int]      = mapped_column(server_default='0', comment='type boolean')
    
    display_qty: Mapped[int]      = mapped_column(nullable=True)
    iceberg:     Mapped[int]      = mapped_column(server_default='0', comment='type boolean')    
    all_or_none: Mapped[int]      = mapped_column(server_default='0', comment='type boolean')

    timeInForce: Mapped[int]      = mapped_column(server_default='0')
    expire_date: Mapped[datetime] = mapped_column(server_default="timestamp(curdate(),'18:00:00')")
    
  # market:      None
    
    ##################################################
    ####   MODIFICAR DATOS A GUARDAR DE ORDENES   ####
    ##################################################
    # timestamp
    # operated
    
    # Relaciones: 
    conn: Mapped[List['Credentials']] = relationship(back_populates='orders', lazy='joined')
    
    # Validations:
    columns_types = None     # Se completa 1 sola vez por fuera de la clase.
    columns_not_none = None  # Parámetros a completar para crear una instancia.
    #columns_not_none = set([conn_id, symbol, size, price])  # Parámetros a completar para crear una instancia.
    
    def __init__(self, *args, **kwargs):
        kwargs['price']  = float(kwargs.get('price'))
        kwargs['id_int'] = str(kwargs.get('id_int'))
        super().__init__(*args, **kwargs)
        self.validate_kwargs(**kwargs)
    
    def set_data(self, data:dict):
        self.validate_kwargs(data)
        return self
    
    def data_ext(self):  # to_dict // to_df
        # d = self.to_dict(keys_excluded=['conn'])
        d = self.data()
        d['dni']            = self.conn.account.dni
        d['nombreCompleto'] = self.conn.account.person.nombreCompleto
        d['broker_id']      = self.conn.broker_id
        d['broker_name']    = self.conn.account.broker.name
        d['nroComitente']   = self.conn.nroComitente
        d['module']         = self.conn.module
        return d
    
    def empty_df(): # le faltan columnas
        return pd.DataFrame(columns=Orders.__annotations__.keys()).set_index('id')
    
# populates columns class attributes:
Orders.columns_types = {column.name: column.type.python_type for column in inspect(Orders).columns}
Orders.columns_not_none = {column.name for column in inspect(Orders).columns if (False if column.autoincrement == True else not column.nullable and column.server_default is None)}
#Orders.columns_not_none = {c.name for c in Orders.columns_not_none}


    
    
""" Referencias:
    [1] - https://stackoverflow.com/questions/7504753/relations-on-composite-keys-using-sqlalchemy
          https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#overlapping-foreign-keys
    [2] - The relationship.backref parameter is generally considered to be legacy; for modern applications, using explicit 
          relationship() constructs linked together using the relationship.back_populates parameter should be preferred.
          https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.backref
          https://docs.sqlalchemy.org/en/20/orm/backref.html#relationships-backref
"""
