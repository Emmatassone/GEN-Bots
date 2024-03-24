from pyhomebroker import HomeBroker

hb = HomeBroker(81) #Broker ID, 81=TM Inversiones

# Authenticate with the homebroker platform
hb.auth.login(dni='homebroker_id', user='hombebroker_user', password='homebroker_pass', raise_exception=True)

hb.online.df = None
# Get orders status for account 14565
def f(online, msg):
    online.df = msg
    
hb.online._on_options = f

hb.online.connect()

hb.online.subscribe_options()
hb.online.unsubscribe_options()

import pandas as pd

# Assuming df is your DataFrame
hb.online.df.to_csv('opciones.csv', index=True)  # Set index=False if you don't want to save row indices
