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


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import global_config

def return_engine(user, password, host, port, database):
    return create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(user, password, host, port, database))

db_url_mask = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(db_url_mask.format(**global_config.server_info))

Session = scoped_session(sessionmaker(bind=engine))



