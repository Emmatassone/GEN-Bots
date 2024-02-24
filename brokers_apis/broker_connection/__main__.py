from connections import pyRofexConnection
from connections import homeBrokerConnection
import configparser


class Connection:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        connection_type = config.get('Connection', 'CONNECTION_PACKAGE')
        
        if connection_type == 'pyrofex':
            self.Connector = pyRofexConnection(config)
        elif connection_type == 'homebroker':
            self.Connector = homeBrokerConnection(config)
        else:
            raise ValueError("Connetion type must be 'pyrofex' or 'homebroker'. Other types of connections are not currently available ")
        
        
    def get_stocks(self):
        return self.Connector.get_stocks()
    
    def get_bonds(self):
        return self.Connector.get_stocks()
    
    def get_options(self):
        return self.Connector.get_options()