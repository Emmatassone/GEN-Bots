#!/usr/bin/env python
# coding: utf-8

import configparser
import pyRofex
import datetime
from icecream import ic


class MatrizCredentials:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.base_url = f"https://api.{self.config.get('pyRofex', 'ALYC')}.xoms.com.ar/"
        self.ws_url = f"wss://api.{self.config.get('pyRofex', 'ALYC')}.xoms.com.ar/"
        self.cred = {
            'user': self.config.get('pyRofex', 'user'),
            'password': self.config.get('pyRofex', 'password'),
            'account': self.config.get('pyRofex', 'account')
        }
        
    def connect(self):
        try:
            pyRofex._set_environment_parameter("url", self.base_url, pyRofex.Environment.LIVE)
            pyRofex._set_environment_parameter("ws", self.ws_url, pyRofex.Environment.LIVE)
            pyRofex.initialize(user=self.cred['user'],
                               password=self.cred['password'],
                               account=self.cred['account'],
                               environment=pyRofex.Environment.LIVE)
            print("\npyRofex environment successfully initialised\n")
        except pyRofex.components.exceptions.ApiException:
            print(f'\npyRofex environment could not be initialised. Authentication failed.'
                  '\nCheck login credentials: Incorrect User or Password. (APIException)')
            quit()


class ArbitrageFinder:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('comisiones.ini')
        self.comis_broker = float(config['Comisiones']['comis_broker']) # Comisión por compra/venta de instrumentos
        self.anual = float(config['Comisiones']['comis_caucion'])       # Comisión caución: 1.5% anual + IVA
        self.derechos = float(config['Comisiones']['derechos'])         # Impuestos y derechos x caución a 1 día
        self.duracion_dias = {
            "2D": 2,
            "3D": 3,
            "4D": 4,
            "5D": 5,
            "6D": 6
        }
        
    def find_instrument(self, instruments, cfi_code):
        instruments_found = []
        for instrument in instruments:
            if instrument['cficode'] == cfi_code:
                descripcion = instrument['instrumentId']['symbol']
                palabras = descripcion.split(' - ')
                ticker = palabras[2]
                if palabras[3] == "CI" and not ticker.endswith("C") and not (ticker.endswith("D") and 
                                                                             ticker != "YPFD"):
                    entries = [
                        pyRofex.MarketDataEntry.BIDS,
                        pyRofex.MarketDataEntry.OFFERS
                    ]
                    market_data_CI = pyRofex.get_market_data(descripcion, entries)
                    market_data_48hs = pyRofex.get_market_data(descripcion.replace("CI", "48hs"), entries)
                    instruments_found.append((market_data_CI, market_data_48hs, ticker))
        return instruments_found

    def find_arbitrage_opportunities(self, market_data_CI, market_data_48hs, instruments, ticker, impuestos, IVA):
        # Extraer y mostrar los precios y volúmenes BID y OFFER si existen
        arbitrage_opportunities = []
        if market_data_CI['status'] == 'OK' and market_data_48hs['status'] == 'OK':
            bid_CI = market_data_CI['marketData']['BI']
            offer_CI = market_data_CI['marketData']['OF']
            bid_48hs = market_data_48hs['marketData']['BI']
            offer_48hs = market_data_48hs['marketData']['OF']
            if not (bid_CI is None or offer_CI is None or bid_48hs is None or offer_48hs is None):
                # Acá nos fijamos si las listas no están vacías
                if bid_CI and offer_CI and bid_48hs and offer_48hs:
                    bid_price_CI = bid_CI[0]['price']
                    bid_vol_CI = bid_CI[0]['size']
                    offer_price_CI = offer_CI[0]['price']
                    offer_vol_CI = offer_CI[0]['size']
                    bid_price_48hs = bid_48hs[0]['price']
                    bid_vol_48hs = bid_48hs[0]['size']
                    offer_price_48hs = offer_48hs[0]['price']
                    offer_vol_48hs = offer_48hs[0]['size']

                    # COMPRAMOS EN CI Y VENDEMOS A 48hs
                    charge_buy_1 = offer_price_CI * (self.comis_broker*(1. + IVA/100) + impuestos) / 100
                    buy_price_1 = offer_price_CI + charge_buy_1

                    charge_sell_1 = bid_price_48hs * (self.comis_broker*(1. + IVA/100) + impuestos) / 100
                    sell_price_1 = bid_price_48hs - charge_sell_1
                    
                    net_income_1 = sell_price_1 - buy_price_1
                    
                    caucion_48hs = self.caucion_income(instruments, buy_price_1, self.anual, self.derechos)
                    
                    # Chequeamos posible desarbitraje
                    if net_income_1 > caucion_48hs:
                        percentage_earn = net_income_1 * 100 / offer_price_CI
                        earn_over_caucion = (net_income_1 - caucion_48hs) / caucion_48hs
                        arbitrage_opportunities.append({
                            'ticker': ticker,
                            'buy price': offer_price_CI,
                            'sell price': bid_price_48hs,
                            'percentage earn': round(percentage_earn, 2),
                            'percentage earn over caucion': round(earn_over_caucion, 2),
                            'volume': min(offer_vol_CI, bid_vol_48hs)
                        })
        
        arbitrage_opportunities.sort(key=lambda x: x['percentage_earn'], reverse=True)
        return arbitrage_opportunities

    def caucion_income(self, instruments, buy_price, anual, derechos):
        # Calculamos la ganancia por colocar el dinero en una caución a 48hs
        caucion_cficode = "RPXXXX"
        dias_a_colocar = ["MERV - XMEV - PESOS - 2D", "MERV - XMEV - PESOS - 3D", "MERV - XMEV - PESOS - 4D",
                          "MERV - XMEV - PESOS - 5D", "MERV - XMEV - PESOS - 6D"]
        
        for cauciones in dias_a_colocar:
            for instrument in instruments:
                if instrument['cficode'] == caucion_cficode and instrument['instrumentId']['symbol'] == cauciones:
                    entries = [
                        pyRofex.MarketDataEntry.BIDS,
                        pyRofex.MarketDataEntry.OFFERS
                    ]
                    market_data = pyRofex.get_market_data(cauciones, entries)
                    
                    # Obtenemos la información de BIDS y OFFERS de "PESOS - 2D" (o el que corresponda)
                    if market_data['status'] == 'OK':
                        bid = market_data['marketData']['BI']
                        offer = market_data['marketData']['OF']
                        if bid is not None and offer is not None:
                            if bid and offer:
                                bid_tasa = bid[0]['price']
                                bid_vol = bid[0]['size']
                                offer_tasa = offer[0]['price']
                                offer_vol = offer[0]['size']
                                duracion = cauciones.split(' - ')[-1]
                                dias = self.duracion_dias[duracion]
                                comis_1 = (buy_price * self.anual / (100 * 365))*(1. + 0.21) * dias
                                comis_2 = (buy_price * self.derechos / 100) * dias
                                comis_total = comis_1 + comis_2
                                caucion_48hs = (buy_price / 100) * (bid_tasa * dias / 365) - comis_total
                                return caucion_48hs
                        break


class InstrumentSelector:
    @staticmethod
    def select_instrument():
        print("Desea buscar desarbitrajes en qué tipo de instrumento?")
        print("")
        print("1) BONOS (soberanos, del tesoro, BOPREAL, etc, en pesos)")
        print("2) ACCIONES argentinas")
        print("3) CEDEARs")
        print("4) OBLIGACIONES NEGOCIABLES (en pesos)")
        option = input("\nIngrese el número correspondiente: ")
        print("")
        return option


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
                ticker_str = f" {opportunity['ticker']}"
                gain_str = f"   {opportunity['percentage_earn']:.2f}%"
                max_len = max(len(ticker_str), len(gain_str))
                ticker_str = ticker_str.ljust(max_len)
                gain_str = gain_str.ljust(max_len)
                print(f"{ticker_str} {gain_str}")
        else:
            print("\nNo se encontraron oportunidades de arbitraje :-( ")


def main():
    cred = MatrizCredentials('Credenciales_Matriz.ini')
    cred.connect()
    
    # Obtener la lista de todos los instrumentos disponibles
    instruments = pyRofex.get_all_instruments()['instruments']
    
    # Seleccionar el tipo de instrumento
    option = InstrumentSelector.select_instrument()
    
    # Definir el CFI code según la opción seleccionada
    cfi_code = ""
    if option == "1":
        cfi_code = "DBXXXX"  # BONOS
        impuestos = 0.0015   # Impuestos, gastos y derechos: 0.0015%
        IVA = 0.00
    elif option == "2":
        cfi_code = "ESXXXX"  # ACCIONES argentinas
        impuestos = 0.0968   # Impuestos, gastos y derechos: 0.0968%
        IVA = 21.0
    elif option == "3":
        cfi_code = "EMXXXX"  # CEDEARs
        impuestos = 0.0968   # Impuestos, gastos y derechos: 0.0968%
        IVA = 21.0
    elif option == "4":
        cfi_code = "DBXXXX"  # OBLIGACIONES NEGOCIABLES (en pesos)
        impuestos = 0.0015   # Impuestos, gastos y derechos: 0.0015%
        IVA = 0.00

    
    finder = ArbitrageFinder()
    instruments_found = finder.find_instrument(instruments, cfi_code)
    for market_data_CI, market_data_48hs, ticker in instruments_found:
        arbitrage = finder.find_arbitrage_opportunities(market_data_CI, market_data_48hs, instruments, ticker,
                                                        impuestos, IVA)
        
    printer = ArbitragePrinter()
    printer.print_opportunities(arbitrage)
    
if __name__ == "__main__":
    main()
