

urls = {key: 'https://api.cocos.capital'+value for key, value in {
        
       'login':         '/auth/v1/token?grant_type=password',
       'me':            '/api/v1/users/me',
       'buying-power':  '/api/v2/orders/buying-power',
       'selling-power': '/api/v2/orders/selling-power?long_ticker=',
       'portfolio':     '/api/v1/wallet/portfolio', 
       'orders':        '/api/v2/orders',
       'tickers_rules': '/api/v1/markets/tickers/rules',
       
        }.items() }