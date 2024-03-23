import pandas as pd
import itertools

class OptionStrategyBuilder:
    # La clase aún no contempla las comisiones
    def __init__(self, options_df):
        self.options_df = options_df
        self.call_options = options_df[options_df['kind']=='CALL']
        self.put_options = options_df[options_df['kind']=='PUT']
    
    def search_call(self, strike, orderbook_side='ask' ):
        index = self.call_options[self.call_options['strike'] == strike].index[0]
        price = self.call_options.loc[index, orderbook_side]
        
        return price
    
    def search_put(self, strike, orderbook_side='ask'):
        index = self.put_options[self.put_options['strike'] == strike].index[0]
        price = self.put_options.loc[index, orderbook_side]
        
        return price
    
    def bull_call_spread(self, order_by='Ganancia Maxima', rows=10):
        """
        Build all possible bull CALL spreads with the options in the dataframe.
        Calls must have the same underlying stock and the same expiration date.
        
        Parameters:
            order_by (string): Column in the DataFrame to be used in the ordering.
            rows (int): Number of rows to show in the final DataFrame.

       Returns:
           A DataFrame containing the current bull call spread strategies.
        """
        
        bull_call_spreads = []
        strikes = self.call_options['strike'].unique()
      
        for strike1, strike2 in list(itertools.product(strikes, repeat=2)):
            
            if strike2<=strike1: continue
        
            ask1 = self.search_call(strike1)
            ask2 = self.search_call(strike2)
            cost = ask2-ask1
            spread = {
                'Strike Compra': strike1,
                'Precio de Compra': ask1,
                'Strike Venta': strike2,
                'Precio de Venta': ask2,
                'Costo': cost,
                'Credito Neto': None,
                'Ganancia Maxima': strike2 - strike1 - cost,
                'Riesgo Maximo': - cost 
            }
            bull_call_spreads.append(spread)

        return pd.DataFrame(bull_call_spreads).sort_values(by=order_by, ascending=False).head(rows).reset_index(drop=True)
    
    def bear_call_spread(self, order_by='Ganancia Maxima', rows=10):
        """
        Build all possible bear CALL spreads with the options in the dataframe.
        """
        bear_call_spreads = []
        strikes = self.call_options['strike'].unique()
        
        for strike1, strike2 in list(itertools.product(strikes, repeat=2)):
        
            if strike2<=strike1: continue
        
            bid = self.search_call(strike1, orderbook_side = 'bid')
            ask = self.search_call(strike2)
            net_credit = bid - ask 
            spread = {
                'Strike Venta': strike1,
                'Precio de Venta': bid,
                'Strike Compra': strike2,
                'Precio de Compra': ask,
                'Costo': None,
                'Credito Neto': net_credit,
                'Ganancia Maxima': net_credit,
                'Riesgo Maximo': - (strike2 - strike1 - net_credit)
            }
            
            bear_call_spreads.append(spread)
            
        return pd.DataFrame(bear_call_spreads).sort_values(by=order_by, ascending=False).head(rows).reset_index(drop=True)
    
    def bull_put_spread(self, order_by='Ganancia Maxima', rows=10):
        """
        Build all possible bull PUT spreads with the options in the dataframe.
        """
        bull_put_spreads = []
        strikes=self.put_options['strike'].unique()

        for strike1, strike2 in list(itertools.product(strikes, repeat=2)):
            
            if strike2<=strike1: continue 
        
            ask = self.search_put(strike1)
            bid = self.search_put(strike2, orderbook_side = 'bid')
            net_credit = bid - ask 
            
            spread = {
                'Strike Compra': strike1,
                'Precio de Compra': ask,
                'Strike Venta': strike2,
                'Precio de Venta': bid,
                'Costo': None,
                'Credito Neto': net_credit,
                'Ganancia Maxima': net_credit ,
                'Riesgo Maximo': - (strike2 - strike1 - net_credit ) 
            }
            bull_put_spreads.append(spread)
        return pd.DataFrame(bull_put_spreads).sort_values(by=order_by, ascending=False).head(rows).reset_index(drop=True)
    
    def bear_put_spread(self, order_by='Ganancia Maxima', rows=10):
        """
        Build all possible bear PUT spreads with the options in the dataframe.
        """
        bear_put_spreads = []
        strikes=self.put_options['strike'].unique()

        for strike1, strike2 in list(itertools.product(strikes, repeat=2)):
            
            if strike2>=strike1: continue 
        
            ask = self.search_put(strike1)
            bid = self.search_put(strike2, orderbook_side = 'bid')
            cost = bid - ask 
            
            spread = {
                'Strike Compra': strike1,
                'Precio de Compra': ask,
                'Strike Venta': strike2,
                'Precio de Venta': bid,
                'Costo': cost,
                'Credito Neto': None,
                'Ganancia Maxima': (strike1 - strike2 - cost) ,
                'Riesgo Maximo': - cost 
            }
            bear_put_spreads.append(spread)
        return pd.DataFrame(bear_put_spreads).sort_values(by=order_by, ascending=False).head(rows).reset_index(drop=True)
    
    def butterfly(self, order_by='Ganancia Maxima', rows=10):
        """
        Build butterflies using bull CALL spreads and bear PUT spreads.
        """
        butterflies = []
        bull_call_spreads = self.bull_call_spread()
        bear_put_spreads = self.bear_put_spread()
        for bull_call in bull_call_spreads:
            for bear_put in bear_put_spreads:
                butterfly = {
                    'LongCall': bull_call['LongCall'],
                    'ShortCall': bull_call['ShortCall'],
                    'ShortPut': bear_put['ShortPut'],
                    'LongPut': bear_put['LongPut'],
                    'Cost': bull_call['Cost'] + bear_put['Cost'],
                    'MaxProfit': min(bull_call['MaxProfit'], bear_put['MaxProfit'])
                }
                butterflies.append(butterfly)
        return butterflies
