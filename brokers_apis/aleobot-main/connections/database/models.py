# coding: utf-8
from sqlalchemy import Column, Float, ForeignKey, ForeignKeyConstraint, String, Table, text
from sqlalchemy.dialects.mysql import BIGINT, CHAR, INTEGER, MEDIUMINT, SMALLINT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


t_accounts_view = Table(
    'accounts_view', metadata,
    Column('nroComitente', INTEGER),
    Column('broker_id', INTEGER),
    Column('broker', String(255)),
    Column('dni', INTEGER),
    Column('nombreCompleto', String(255))
)


class Broker(Base):
    __tablename__ = 'brokers'

    id = Column(INTEGER(3), primary_key=True)
    nombre = Column(VARCHAR(255), nullable=False)
    short_str = Column(CHAR(50), nullable=False)


t_credentials_view = Table(
    'credentials_view', metadata,
    Column('nroComitente', INTEGER),
    Column('nombreCompleto', String(255)),
    Column('broker_id', INTEGER),
    Column('broker', String(255)),
    Column('module', String(16)),
    Column('user', String(30)),
    Column('password', String(255)),
    Column('conn_id', SMALLINT, server_default=text("'0'")),
    Column('conn_token', String(999))
)


class Module(Base):
    __tablename__ = 'modules'

    name = Column(VARCHAR(16), primary_key=True)


class Person(Base):
    __tablename__ = 'persons'

    dni = Column(INTEGER, primary_key=True)
    nombreCompleto = Column(VARCHAR(255), nullable=False)
    CUIT = Column(BIGINT, nullable=False)


class Settlement(Base):
    __tablename__ = 'settlements'

    t = Column(TINYINT, primary_key=True)
    str1 = Column(CHAR(50), nullable=False)
    str2 = Column(CHAR(50), nullable=False)


class Account(Base):
    __tablename__ = 'accounts'

    broker_id = Column(ForeignKey('brokers.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    nroComitente = Column(INTEGER, primary_key=True, nullable=False)
    dni = Column(ForeignKey('persons.dni', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    broker = relationship('Broker')
    person = relationship('Person')


class Credential(Base):
    __tablename__ = 'credentials'
    __table_args__ = (
        ForeignKeyConstraint(['broker_id', 'nroComitente'], ['accounts.broker_id', 'accounts.nroComitente'], ondelete='CASCADE', onupdate='CASCADE'),
    )

    broker_id = Column(INTEGER, primary_key=True, nullable=False)
    nroComitente = Column(INTEGER, primary_key=True, nullable=False)
    module = Column(ForeignKey('modules.name', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False, index=True)
    user = Column(VARCHAR(30), nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    conn_id = Column(SMALLINT, nullable=False, index=True)
    conn_token = Column(VARCHAR(999))

    broker = relationship('Account')
    module1 = relationship('Module')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(INTEGER, primary_key=True)
    conn_id = Column(ForeignKey('credentials.conn_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    id_ext = Column(CHAR(50), index=True)
    instrument = Column(CHAR(50), nullable=False, comment='(str_id)')
    settlement = Column(TINYINT, nullable=False, server_default=text("(0)"), comment='(int_id)')
    op_type = Column(TINYINT, nullable=False, comment='(int_id)')
    size = Column(MEDIUMINT, nullable=False)
    price = Column(Float, nullable=False)
    remaining = Column(MEDIUMINT, nullable=False)
    status = Column(TINYINT, nullable=False, server_default=text("'0'"), comment='(int_id)')
    currency = Column(TINYINT, nullable=False, server_default=text("(0)"), comment='(int_id)')
    amount = Column(Float, nullable=False)

    conn = relationship('Credential')
