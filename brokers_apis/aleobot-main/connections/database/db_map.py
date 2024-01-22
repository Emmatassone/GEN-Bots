# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:49:22 2024

@author: Alejandro

Requirements:
- SQLAlchemy Version: 2.0.25
- typing_extensions Version: 4.9.0
    pip install --upgrade sqlalchemy
    pip install --upgrade sqlalchemy typing-extensions
"""
# https://docs.sqlalchemy.org/en/20/core/connections.html
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
# https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-declarative-mapping
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#declarative-table-with-mapped-column


from typing import Optional, Dict  #, List
from sqlalchemy import String, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref


# declarative base class
class Base(DeclarativeBase):
    
    def to_dict(self, keys_excluded:list=None) -> Dict:
        keys_excluded = ['_sa_instance_state'] + (keys_excluded if keys_excluded else [])
        return {k: v for k, v in self.__dict__.items() if k not in keys_excluded}
        # Con esa logica evito retornar el __dict__ sino una copia y que modificaciones inintencionales sobre el valor retornado modifique el de la instancia de esta clase.


class Brokers(Base):
    __tablename__ = 'brokers'
    id:         Mapped[int] = mapped_column(primary_key=True)
    nombre:     Mapped[str] = mapped_column(String(255))
    short_str:  Mapped[str] = mapped_column(String(50))
    
    # Relaciones:
    #accounts =  relationship('Accounts', backref='broker')
    accounts =  relationship('Accounts', backref=backref('broker', lazy='joined'))  # Ver [2]

class Persons(Base):
    __tablename__ = 'persons'
    dni:            Mapped[int] = mapped_column(primary_key=True)
    nombreCompleto: Mapped[str] = mapped_column(String(255))
    CUIT:           Mapped[int] = mapped_column()
    
    # Relaciones:
    #accounts =      relationship('Accounts', backref='person')
    accounts =      relationship('Accounts', backref=backref('person', lazy='joined'))  # Ver [2]
    
class Accounts(Base):
    __tablename__ = 'accounts'
    broker_id:    Mapped[int] = mapped_column(ForeignKey('brokers.id'))
    nroComitente: Mapped[int] = mapped_column()
    dni:          Mapped[int] = mapped_column(ForeignKey('persons.dni'))
    
    # Relaciones:
    #credentials = relationship('Credentials', backref='account')
    credentials = relationship('Credentials', backref=backref('account', lazy='joined'))  # Ver [2]
    
    # PrimaryKeyConstraint on composite keys:  (Ver [1])
    __table_args__ = (PrimaryKeyConstraint(broker_id, nroComitente), )
    
    @property
    def nombreCompleto(self):
        if self.person: return self.person.nombreCompleto
    @property
    def broker_name(self):
        if self.broker: return self.broker.nombre
    
class Credentials(Base):
    __tablename__ = 'credentials'
    broker_id:    Mapped[int] = mapped_column()  # ForeignKey('Accounts.broker_id') y primary_key=True ya están en __table_args__
    nroComitente: Mapped[int] = mapped_column()  # ForeignKey('Accounts.nroComitente') y primary_key=True ya están en __table_args__
    module:       Mapped[str] = mapped_column(String(16))  # primary_key=True ya están en __table_args__
    user:         Mapped[str] = mapped_column(String(30))
    password:     Mapped[str] = mapped_column(String(255))
    conn_id:      Mapped[int] = mapped_column()
    conn_token:   Mapped[str] = mapped_column(String(999))
    
    # Relaciones: Ya está en las demás tablas en al usar backref en relationship  (Ver [2])
    
    # ForeignKeyConstraint relations on composite keys:  (Ver [1])
    __table_args__ = (PrimaryKeyConstraint(broker_id, nroComitente, module),
                      ForeignKeyConstraint([broker_id, nroComitente],   # agregar dni ????????????????
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
        
    def data(self):
        d = self.to_dict(keys_excluded=['account'])
        d['nombreCompleto'] = self.account.person.nombreCompleto
        d['broker_name'] = self.account.broker.nombre
        d['dni'] = self.account.dni
        return d
        
        

class Orders(Base):
    __tablename__ = 'orders'
    id:    Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data:  Mapped[str] = mapped_column(String(50))
    other: Mapped[Optional[str]] = mapped_column(String(50))    
    
""" Referencias:
    [1] - https://stackoverflow.com/questions/7504753/relations-on-composite-keys-using-sqlalchemy
          https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#overlapping-foreign-keys
    [2] - The relationship.backref parameter is generally considered to be legacy; for modern applications, using explicit 
          relationship() constructs linked together using the relationship.back_populates parameter should be preferred.
          https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.backref
          https://docs.sqlalchemy.org/en/20/orm/backref.html#relationships-backref
"""
