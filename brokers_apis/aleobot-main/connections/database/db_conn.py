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

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tools import file_manager

# https://docs.sqlalchemy.org/en/20/core/connections.html
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
# https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-declarative-mapping
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#declarative-table-with-mapped-column


def return_engine(user, password, host, port, database):
    return create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(user, password, host, port, database))    


server_info_file_path = os.getcwd()+'\\connections\\database\\'
server_info = file_manager.Json(file_name='server_info', path=server_info_file_path).read()

engine = return_engine(**server_info)

Session = scoped_session(sessionmaker(bind=engine))
# Para obtener una instancia de Session hay que hacer Session()
