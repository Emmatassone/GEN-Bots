# Este script busca desarbitrajes en el mercado argentino en distintos instrumentos (acciones argentinas, CEDEARs, bonos soberanos, ONs, etc).
# Compara el precio de compra en contado inmediato (CI) con el precio de venta a 48 horas.

#------------------------------------------------------------------------------

import configparser
import requests

class MarketArbitrage:
    def __init__(self, config_file='PPI.ini'):
        self.config_file = config_file
        self.credentials = self.read_credentials()
        self.base_url = 'https://clientapi.portfoliopersonal.com/api'
        self.api_version = '1.0'
        self.headers = {
            'AuthorizedClient': self.credentials['AuthorizedClient'],
            'ClientKey': self.credentials['ClientKey'],
            'ApiKey': self.credentials['key_pública'],
            'ApiSecret': self.credentials['key_privada'],
        }
        self.token = self.get_token()

    def read_credentials(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        return {
            'AuthorizedClient': config.get('Client', 'AuthorizedClient'),
            'ClientKey': config.get('Client', 'ClientKey'),
            'key_pública': config.get('Keys', 'key_publica'),
            'key_privada': config.get('Keys', 'key_privada'),
        }

    def get_token(self):
        endpoint = 'Account/LoginApi'
        url = f"{self.base_url}/{self.api_version}/{endpoint}"
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            print("")
            print("POST Request successful!\n")
            # Obtener el token de la respuesta JSON
            return response.json()['accessToken']
        else:
            raise Exception(f"Error: {response.status_code}\n{response.text}")
        
    def search_arbitrage_opportunities(self, tickers, instrument_type, comis):
        endpoint = 'MarketData/Book'     # Para poder leer la caja de puntas
        url = f"{self.base_url}/{self.api_version}/{endpoint}"

        arbitrage_opportunities = []     # Lista para almacenar las oportunidades de arbitraje

        for ticker in tickers:
            params_CI = {
                'ticker': ticker,
                'type': instrument_type,
                'settlement': 'INMEDIATA'
            }

            params_48 = {
                'ticker': ticker,
                'type': instrument_type,
                'settlement': 'A-48HS'
            }

            # Realizar la solicitud GET para obtener la caja de puntas
            response_CI = requests.get(url, headers=self.headers, params=params_CI)
            response_48 = requests.get(url, headers=self.headers, params=params_48)

            # Verificar si la solicitud GET fue exitosa
            if response_CI.status_code == 200 and response_48.status_code == 200:
                book_data_CI = response_CI.json()
                book_data_48 = response_48.json()

                first_bid_CI = book_data_CI['bids'][0]
                first_offer_CI = book_data_CI['offers'][0]
                first_bid_48 = book_data_48['bids'][0]
                first_offer_48 = book_data_48['offers'][0]

                charge_buy = first_offer_CI['price'] * comis / 100
                buy_price = first_offer_CI['price'] + charge_buy

                charge_sell = first_bid_48['price'] * comis / 100
                net_income = first_bid_48['price'] - charge_sell

                if net_income > buy_price and first_offer_CI['price'] != 0:
                    print("\nHay una nueva oportunidad de arbitraje!")
                    percentage_earn = (net_income - buy_price) * 100 / first_offer_CI['price']
                    arbitrage_opportunities.append((ticker, round(percentage_earn, 2)))
            else:
                # Mostrar un mensaje de error si la solicitud GET no fue exitosa
                print(f"Error: {response_CI.status_code}\n{response_CI.text}")
                print(f"Error: {response_48.status_code}\n{response_48.text}")

        # Ordenamos la lista de oportunidades de arbitraje por % de ganancia en orden descendente
        arbitrage_opportunities.sort(key=lambda x: x[1], reverse=True)
        return arbitrage_opportunities

    def print_arbitrage_opportunities(opportunities):
        if len(opportunities) >= 1:
            print("\n\n\n--------------------------------------")
            print("** Hay", len(opportunities), "oportunidades de arbitraje **")
            print("--------------------------------------")
            print(" Ticker    Ganancia\n")
            for opportunity in opportunities:
                ticker_str = f" {opportunity[0]}"
                gain_str = f"   {opportunity[1]:.2f}%"
                # Calcula la longitud máxima para alinear las columnas
                max_len = max(len(ticker_str), len(gain_str))
                # Añade espacios para alinear las columnas
                ticker_str = ticker_str.ljust(max_len)
                gain_str = gain_str.ljust(max_len)
                # Imprime las líneas con el mismo formato
                print(f"{ticker_str} {gain_str}")
        else:
            print("\nNo hay oportunidades de arbitraje por el momento :-( ")


# Ejemplo de uso
if __name__ == "__main__":
    tickers = ["AL30", "GD30", "GD35", "AL35", "GD38", "AE38", "GD41", "AL29",
               "AL41", "GD46", "GD29"]
    instrument_type = "BONOS"
    comis = 0.6

    market_arbitrage = MarketArbitrage()
    opportunities = market_arbitrage.search_arbitrage_opportunities(tickers, instrument_type, comis)
    print_arbitrage_opportunities(opportunities)

