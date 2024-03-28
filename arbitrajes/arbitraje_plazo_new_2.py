#!/usr/bin/env python
# coding: utf-8

# # Este script busca desarbitrajes en el mercado argentino en distintos instrumentos (acciones argentinas, CEDEARs, bonos soberanos, etc).

# # Compara el precio de compra en contado inmediato (CI) con el precio de venta a 48 horas.

# # SIN EMBARGO, FALTAN INCLUIR ALGUNAS COSAS. Por ejemplo:
# #
# # a) Ver si el desarbitraje le gana a la caución a 48hs (ver comisiones!)
# # b) Faltan agregar otros arbitrajes (agregado; falta tomar caucion)
# # c) Falta leer cuantos bids y asks hay en los instrumentos
# # d) Falta generalizar las credenciales para que no use solo PPI
# # e) Falta ver como leer los tickers de mejor manera (Ale)
# # f) Problemas con los días al tomar caución a 48hs

import configparser
import requests


class Credentials:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.base_url = 'https://clientapi.portfoliopersonal.com/api'
        self.api_version = '1.0'
        self.cred = {
            'AuthorizedClient': self.config.get('Client', 'AuthorizedClient'),
            'ClientKey': self.config.get('Client', 'ClientKey'),
            'key_pública': self.config.get('Keys', 'key_publica'),
            'key_privada': self.config.get('Keys', 'key_privada')
        }

    def login(self):
        endpoint = 'Account/LoginApi'
        url = f"{self.base_url}/{self.api_version}/{endpoint}"
        headers = {
            'AuthorizedClient': self.cred['AuthorizedClient'],
            'ClientKey': self.cred['ClientKey'],
            'ApiKey': self.cred['key_pública'],
            'ApiSecret': self.cred['key_privada']
        }        
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print("POST Request successful\n")
            # Obtener el token de la respuesta JSON
            return response.json()['accessToken']
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    def get_book_data(self, token, ticker, instrument_type, settlement):
        endpoint = 'MarketData/Book'
        url = f"{self.base_url}/{self.api_version}/{endpoint}"
        params = {
            'ticker': ticker,
            'type': instrument_type,
            'settlement': settlement
        }
        headers = {
            'AuthorizedClient': self.cred['AuthorizedClient'],
            'ClientKey': self.cred['ClientKey'],
            'Content-Type': "application/json",
            'Authorization': f"Bearer {token}"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None


class ArbitrageFinder:
    def __init__(self, api, comis):
        self.api = api
        self.comis = comis
        self.anual = 0.04015       # Comisión caución: 2% anual + IVA (0.04015 es por 2 días)
        self.impuestos = 0.00933   # Impuestos, gastos y derechos
        
    def set_anual(self, value):
        self.anual = value

    def set_impuestos(self, value):
        self.impuestos = value
        
    def calculate_caucion_income(self, token, buy_price, anual, impuestos):
        endpoint = 'MarketData/Book'
        url = f"{self.api.base_url}/{self.api.api_version}/{endpoint}"
        params = {
            'ticker': 'PESOS7',
            'type': 'CAUCIONES',
            'settlement': 'INMEDIATA'
        }
        headers = {
            'AuthorizedClient': self.api.cred['AuthorizedClient'],
            'ClientKey': self.api.cred['ClientKey'],
            'Content-Type': "application/json",
            'Authorization': f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            caucion_data = response.json()
            # Imprimimos los datos de bids y offers/asks
            print("\nBids:")
            for bid in caucion_data['bids']:
                print(f"Position: {bid['position']}, Price: {bid['price']}, Quantity: {bid['quantity']}")
                
            print("\nOffers:")
            for offer in caucion_data['offers']:
                print(f"Position: {offer['position']}, Price: {offer['price']}, Quantity: {offer['quantity']}")
#            print(buy_price, anual, impuestos)
            comis_1 = (self.buy_price * self.anual / 365)
            comis_2 = (self.buy_price * self.impuestos / 365)
            caucion_48hs = (self.buy_price / 100) * (caucion_rate * 2 / 365) - comis_1 - comis_2
            return caucion_48hs
        else:
            print(f"Error al obtener los datos de la caución: {response.status_code}")
            return None

    def find_arbitrage_opportunities(self, tickers, instrument_type):
        token = self.api.login()
        if token is None:
            return

        arbitrage_opportunities_1 = []
        arbitrage_opportunities_2 = []
        for ticker in tickers:
            book_data_CI = self.api.get_book_data(token, ticker, instrument_type, 'INMEDIATA')
            book_data_48 = self.api.get_book_data(token, ticker, instrument_type, 'A-48HS')

            if book_data_CI is not None and book_data_48 is not None:
                # COMPRO EN CI Y VENDO A 48hs
                first_offer_CI = book_data_CI['offers'][0]
                first_bid_48 = book_data_48['bids'][0] 

                charge_buy_1 = first_offer_CI['price'] * self.comis / 100
                buy_price_1 = first_offer_CI['price'] + charge_buy_1

                charge_sell_1 = first_bid_48['price'] * self.comis / 100
                sell_price_1 = first_bid_48['price'] - charge_sell_1
                
                net_income_1 = sell_price_1 - buy_price_1
                
                print(first_offer_CI['price'], charge_buy_1, buy_price_1)
#                print(first_bid_48['price'], charge_sell, net_income)
                
#                caucion_48hs = self.calculate_caucion_income(token,buy_price,0.00,0.00)
                caucion_48hs = self.calculate_caucion_income(token,1e5,10.00,110.00)
#                caucion_income = self.calculate_caucion_income(buy_price)
#                print(caucion_income)

                # VENDO EN CI Y COMPRO A 48hs
                first_bid_CI = book_data_CI['bids'][0]
                first_offer_48 = book_data_48['offers'][0]

                charge_sell_2 = first_bid_CI['price'] * self.comis / 100
                sell_price_2 = first_bid_CI['price'] - charge_sell_2
                
                charge_buy_2 = first_offer_48['price'] * self.comis / 100
                buy_price_2 = first_offer_48['price'] + charge_buy_2
                
                net_income_2 = sell_price_2 - buy_price_2

                # Chequeamos ambos posibles desarbitrajes
                if net_income_1 > 0.00 and first_offer_CI['price'] != 0 and first_bid_48['price'] != 0:
                    percentage_earn = net_income_1 * 100 / first_offer_CI['price']
                    arbitrage_opportunities_1.append((ticker, round(percentage_earn, 2)))
                elif net_income_2 > 0.00 and first_bid_CI['price'] != 0 and first_offer_48['price'] != 0:
                    percentage_earn = net_income_2 * 100 / first_offer_48['price']
                    arbitrage_opportunities_2.append((ticker, round(percentage_earn, 2)))

        arbitrage_opportunities_1.sort(key=lambda x: x[1], reverse=True)
        arbitrage_opportunities_2.sort(key=lambda x: x[1], reverse=True)
        return arbitrage_opportunities_1, arbitrage_opportunities_2


class ArbitragePrinter:
    @staticmethod
    def print_opportunities(opportunities):
        if len(opportunities) >= 1:
            print("\n\n\n--------------------------------------")
            print("** Hay", len(opportunities), "oportunidades de arbitraje **")
            print("** de comprar en CI y vender a 48hs **")
            print("--------------------------------------")
            print(" Ticker    Ganancia\n")
            for opportunity in opportunities:
                ticker_str = f" {opportunity[0]}"
                gain_str = f"   {opportunity[1]:.2f}%"
                max_len = max(len(ticker_str), len(gain_str))
                ticker_str = ticker_str.ljust(max_len)
                gain_str = gain_str.ljust(max_len)
                print(f"{ticker_str} {gain_str}")
        else:
            print("\nNo hay oportunidades de arbitraje por el momento :-( ")


class InstrumentSelector:
    @staticmethod
    def select_instrument():
        print("\nDesea buscar desarbitrajes en qué tipo de instrumento?")
        print("")
        print("1) BONOS SOBERANOS (en pesos) + BOPREAL")
        print("2) ACCIONES argentinas")
        print("3) CEDEARs")
        print("4) BONOS DEL TESORO (y otros)")
        print("5) OBLIGACIONES NEGOCIABLES (en pesos)")
        option = input("\nIngrese el número correspondiente: ")
        return option


def main():
    api = Credentials('PPI.ini')
    comis = 0.0
    
    option = InstrumentSelector.select_instrument()
    if option == "1":
        tickers = ["AL30", "GD30", "GD35", "AL35", "GD38", "AE38", "GD41", "AL29", "AL41", "GD46", "GD29",
                   "BPJ25", "BPOA7", "BPOB7", "BPOC7", "BPOD7"]
        instrument_type = 'BONOS'
        comis = 0.6
    elif option == "2":
        tickers = ["AGRO", "ALUA", "AUSO", "BBAR", "BHIP", "BMA", "BOLT", "BPAT", "BYMA", "CADO", "CAPX", "CECO2",
                   "CELU", "CEPU", "CGPA2", "COME", "CRE3W", "CRES", "CTIO", "CVH", "DGCU2", "DOME", "DYCA", "EDN",
                   "FERR", "FIPL", "GAMI", "GARO", "GBAN", "GCDI", "GCLA", "GGAL", "GRIM", "HARG", "HAVA", "INTR", 
                   "INVJ", "IRS2W", "IRSA", "LEDE", "LOMA", "LONG", "METR", "MIRG", "MOLA", "MOLI", "MORI", "MTR", 
                   "OEST", "PAMP", "PATA", "RICH", "RIGO", "ROSE", "SUPV", "SAMI", "SEMI", "TECO2", "TGNO4", 
                   "TGSU2", "TRAN", "TXAR", "VALO", "YPFD"]
        instrument_type = "Acciones"
        comis = 0.6 + 0.126
    elif option == "3":
        tickers = [
            "AAL", "AAPL", "ABBV", "ABEV", "ABNB", "ABT", "ADBE", "ADGO", "ADP", "AEG", "AEM", "AIG", "AKO.B", 
            "AMAT", "AMD", "AMGN", "AMX", "AMZN", "ANF", "AOCA", "ARCO", "ARKK", "AVGO", "AVY", "AXP", "AZN", 
            "BA", "BABA", "BA.C", "BAYN", "BB", "BBD", "BBV", "BCS", "BHP", "BIDU", "BIIB", "BIOX", "BITF", "BK", 
            "BMY", "BNG", "BP", "BRFS", "BRKB", "C", "CAAP", "CAH", "CAR", "CAT", "CL", "COIN", "COST", "CRM", 
            "CSCO", "CVX", "DD", "DE", "DEO", "DESP", "DIA", "DISN", "DOCU", "DOW", "EA", "EBAY", "EBR", "EEM",
            "EFX", "ERIC", "ERJ", "ETSY", "EWZ", "F", "FCX", "FDX", "FMX", "FSLR", "GE", "GGB", "GILD", "GLOB", 
            "GOLD", "GOOGL", "GPRK", "GRMN", "GS", "GSK", "HAL", "HD", "HL", "HMY", "HOG", "HON", "HPQ", "HSBC",
            "HUT", "HWM", "IBM", "IFF", "INFY", "INTC", "IP", "ITUB", "IWM", "JD", "JMIA", "JNJ", "JPM", "KGC", 
            "KMB", "KO", "LLY", "LMT", "LVS", "LYG", "MA", "MCD", "MDT", "MELI", "META", "MMM", "MO", "MOS",
            "MRK", "MSFT", "MSTR", "MU", "MUFG", "NEM", "NFLX", "NG", "NIO", "NKE", "NMR", "NOKA", "NTCO", "NTES",
            "NVDA", "ORCL", "OXY", "PAAS", "PANW", "PBR", "PCAR", "PEP", "PFE", "PG", "PKS", "PSX", "PYPL", 
            "QCOM", "QQQ", "RBLX", "RIO", "ROST", "RTX", "SAN", "SAP", "SATL", "SBS", "SBUX", "SCCO", "SE", 
            "SHEL", "SHOP", "SI", "SID", "SLB", "SNAP", "SNOW", "SONY", "SPGI", "SPOT", "SPY", "SQ", "SUZ", "SYY",
            "T", "TEN", "TGT", "TM", "TMO", "TRIP", "TSLA", "TSM", "TTE", "TXN", "TXR", "UAL", "UBER", "UGP", 
            "UL", "UNH", "UNP", "UPST", "URBN", "USB", "V", "VALE", "VIST", "VIV", "VOD", "VRSN", "VZ", "WBA",
            "WBO", "WFC", "WMT", "X", "XLE", "XLF", "XOM", "XROX", "YELP", "YY", "YZCA", "ZM"
            ]
        instrument_type = "CEDEARS"
        comis = 0.6 + 0.126
    elif option == "4":
        tickers = ["TV24", "T3X4", "TDF24", "TDJ24", "TDN24","T4X4", "T2X4", "TX24", "TDG24", "T2X5", "TDA24",
                   "T2V4", "BPO27", "TV25", "T6X4", "TX26", "TX28", "TX31","DICP", "TVPA", "TVPP","T5X4", "PR13",
                   "PR17", "PARP", "TO26", "TC25P", "TZX26", "TDE25", "TZX27"]
        instrument_type = "BONOS"
        comis = 0.6
    elif option == "5":
        tickers = ["TLCHO", "MRCAO", "YCA6O", "YMCJO", "TLC1O", "YMCIO", "MGCHO", "YMCHO", "YPCUO", "TLC5O",
                   "LOC2O", "YMCQ", "MGCJO", "MGC9O", "CLSIO", "MTCGO", "SNS9O", "IRCFO", "ARC1O", "CRCEO",
                   "MRCGO", "AEC1O", "CS38O", "NPCAO", "GN40O", "LECAO", "RCCJO", "MRCPO", "MRCRO", "IRCEO",
                   "LOC3O", "MRCOO"]
        instrument_type = "ON"
        comis = 0.6
    else:
        print("Opción inválida")
        return

    
    finder = ArbitrageFinder(api, comis)
    print("\nBuscando posibles desarbitrajes...\n")
    arbit_opportu_1, arbit_opportu_2 = finder.find_arbitrage_opportunities(tickers, instrument_type)
    
    printer = ArbitragePrinter()
    printer.print_opportunities(arbit_opportu_1)
    print("\n")
    printer.print_opportunities(arbit_opportu_2)

if __name__ == "__main__":
    main()

