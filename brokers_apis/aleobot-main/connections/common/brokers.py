# -*- coding: utf-8 -*-
"""
@author: Alejandro Ben 
"""

import os
import pandas as pd
from types import SimpleNamespace
from pyhomebroker.common import brokers as hb_brokers


id_dict = {'cocos': 265, 'veta': 284, 'ieb': 203}
id_num = SimpleNamespace(**id_dict)

cocos_id = id_num.cocos
veta_id  = id_num.veta
ieb_id   = id_num.ieb


alycs = { id_num.cocos: 'Cocos Capital S.A.', 
          id_num.veta : 'Veta Capital S.A.',
          id_num.ieb  : 'Invertir en Bolsa S.A.', }

token_path = os.getcwd()+'\\data\\tokens\\'