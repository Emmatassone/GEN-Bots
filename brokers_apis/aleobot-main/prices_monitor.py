    
import os

from ui import excel_bot as eb
from connections.common import orders_helper


eb.settlements = [ 'spot', '48hs' ]

eb.symbols = sorted([ 'AL30', 'AL30D', 'GD30', 'GD30D' ])

eb.orderBookDF = orders_helper.orderBookDF(symbols=eb.symbols, settlements=eb.settlements)



eb.start([os.path.basename(__file__)])