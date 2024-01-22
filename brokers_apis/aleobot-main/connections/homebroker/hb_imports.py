# -*- coding: utf-8 -*-
"""
@author: Alejandro Ben 
"""

import pandas as pd
from pyhomebroker.common import brokers as hb_brokers, user_agent as hb_user_agent, SessionException, ServerException

hb_brokers = pd.DataFrame(hb_brokers).rename(columns={'page': 'url', 'broker_id': 'id'}).set_index('id')
