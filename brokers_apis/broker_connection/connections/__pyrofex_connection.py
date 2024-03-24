
class PyRofexConnection:
    def __init__(self, config):
        cred={}
        cred['alyc'] = config.get('Credentials', 'ALYC')
        cred['user'] = config.get('Credentials', 'USERNAME')
        cred['pass'] = config.get('Credentials', 'PASSWORD')
        
    
    def get_stocks(self):
        return 
    
    def get_bonds(self):
        return 
    
    def get_options(self):
        return
        