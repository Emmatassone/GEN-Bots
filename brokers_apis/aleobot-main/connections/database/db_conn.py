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
from tools.file_manager import config_read

def get_server_info(user='', password='', host='', port=3310, database=''):
    try: return config_read()['Server_Info']
    except: return dict(user=user, password=password, host=host, port=port, database=database)

db_url_mask = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
engine = create_engine(db_url_mask.format(**get_server_info()))    
Session = scoped_session(sessionmaker(bind=engine))


sess = Session()