# Este script busca desarbitrajes en el mercado argentino en distintos instrumentos (como por ejemplo, acciones, CEDEARs, etc).
# Compara el precio de compra en contado inmediato (CI) con el precio de venta a 48 horas.

# Importamos API de PPI
from ppi_client.api.constants import ACCOUNTDATA_TYPE_ACCOUNT_NOTIFICATION, ACCOUNTDATA_TYPE_PUSH_NOTIFICATION
from ppi_client.api.constants import ACCOUNTDATA_TYPE_ORDER_NOTIFICATION
from ppi_client.models.account_movements import AccountMovements
from ppi_client.models.bank_account_request import BankAccountRequest
from ppi_client.models.foreign_bank_account_request import ForeignBankAccountRequest, ForeignBankAccountRequestDTO
from ppi_client.models.cancel_bank_account_request import CancelBankAccountRequest
from ppi_client.models.order import Order
from ppi_client.ppi import PPI
from ppi_client.models.order_budget import OrderBudget
from ppi_client.models.order_confirm import OrderConfirm
from ppi_client.models.disclaimer import Disclaimer
from ppi_client.models.investing_profile import InvestingProfile
from ppi_client.models.investing_profile_answer import InvestingProfileAnswer
from ppi_client.models.instrument import Instrument
from datetime import datetime, timedelta
from ppi_client.models.estimate_bonds import EstimateBonds
import asyncio
import json
import traceback
import os

# Importamos otros paquetes necesarios
import pandas as pd
import numpy as np
import datetime
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import requests

# Nos conectamos al entorno "Sandbox" (i.e., un entorno de prueba)
# Cambiar la variable "sandbox" a False para conectarse con la cuenta verdadera

# Keys verdaderas
#sandbox_public_key=''
#sandbox_secret_key=''
ppi = PPI(sandbox=False)

# Cambiar las credenciales de inicio de sesión para conectarse a la API
ppi.account.login_api(sandbox_public_key,sandbox_secret_key)

# Buscamos los precios de los instrumentos
print("\nBuscando datos en el mercado...\n")

#------------------------------------------------------------------------
#         TESTEO
#------------------------------------------------------------------------

# Obtenemos la hora actual
current_time = datetime.now().time()

# Estamos viendo si hay diferencia de precios en el momento, no?
end_date = current_time
start_date = current_time

# Imprimos las fechas para corroborar que estén bien
print("Fecha del último dato disponible:", end_date)
print("Fecha del día anterior (hábil):  ", start_date)

# Creamos una lista para almacenar los precios
data_list = []

# Tickers de algunas empresas argentinas que cotizan
tickers_arg_test = ["AGRO", "ALUA", "AUSO", "BBAR", "BHIP", "BMA", "CELU", "CEPU", "CRES", "CTIO", "CVH", "EDN",
           "PAMP", "SUPV", "TGSU2", "TRAN", "TXAR"]

# Tickers de algunos CEDEARs
tickers_cedears_test = [
    "AAPL", "ADBE", "AMZN", "ARKK", "BIDU", "BIOX", "BK", "DIA", "EWZ", "FSLR", "JPM", "MELI", "META", 
    "QCOM", "QQQ", "SPOT", "SPY", "TSLA", "ZM"
]

#------------------------------------------------------------------------
# ACA INTENTAMOS LEER LA CAJA DE PUNTAS SIN EXITO AUN
# Definimos la URL de la API para obtener la información de la caja de puntas
url = 'https://clientapi.portfoliopersonal.com/api/1.0/MarketData/Book?ticker=ALUA&type=ACCIONES&settlement=A-48HS'

# Hacemos la solicitud GET a la URL
response = requests.get(url)

# Imprimir la respuesta
print(response.text)

# Verificamos si la solicitud fue exitosa (código de estado 200)
if response.status_code == 200:
    # Extraemos los datos de la respuesta en formato JSON
    data = response.json()
    # Ahora puedes procesar los datos obtenidos, que generalmente incluirán la caja de puntas
    # Por ejemplo, podrías acceder a los precios de compra (bid) y venta (ask)
    bid_price = data['bid']
    ask_price = data['ask']
    # Luego puedes usar estos precios para tu lógica de arbitraje
else:
    # Si la solicitud no fue exitosa, maneja el error adecuadamente
    print('Error al obtener la información de la caja de puntas:', response.status_code)
#------------------------------------------------------------------------

# COMISIONES POR OPERACIONES (1)
# (1) Adicionalmente a estos aranceles y comisiones se le deberán sumar los derechos de Mercado aplicables 
# a las operaciones que fije el Bolsas y Mercados de Argentina S.A., Matba Rofex S.A., 
# Mercado Argentino de Valores S.A., y el Mercado Abierto Electrónico S.A. 
# vigentes al momento de la operación de acuerdo a lo publicado en [ver sitios web]

# Vigentes desde el 1ro de Noviembre de 2023
# Compra/Venta de acciones y Cedears: 0,6% + IVA

# Creamos una lista para almacenar las oportunidades de arbitraje
arbitrage_opportunities = []

# Iteramos a través de los tickers para obtener los datos de los precios en CI y a 48 horas
for ticker in tickers_arg_test:
    # Obtenemos el precio de mercado para el ticker actual a 48 horas
    current_market_data_48hs = ppi.marketdata.current(ticker, "Acciones", "A-48HS")
    print("Chequear precios de compra y venta!")
    print(current_market_data_48hs)
    # usar response = requests.get(url)
    
    # Obtenemos el precio de mercado para el mismo ticker (actual) pero en CI
    current_market_data_CI = ppi.marketdata.current(ticker, "Acciones", "INMEDIATA")
    
    charge_buy = current_market_data_CI['price'] * (0.6 + 0.126) / 100
    buy_price = current_market_data_CI['price'] + charge_buy

    charge_sell = current_market_data_48hs['price'] * (0.6 + 0.126) / 100
    net_income = current_market_data_48hs['price'] - charge_sell
    
    if net_income > buy_price:
        print("\nHay una nueva oportunidad de arbitraje!")
        percentage_earn = (net_income - buy_price) * 100 / net_income
        volume = current_market_data_48hs['volume']
        print(current_market_data_48hs['volume'])        
        arbitrage_opportunities.append((ticker, round(percentage_earn, 2), volume))
        
# Ordenamos la lista de oportunidades de arbitraje por porcentaje de ganancia en orden descendente
arbitrage_opportunities.sort(key=lambda x: x[1], reverse=True)

# Imprimimos las oportunidades de arbitraje, si es que hay alguna
if len(arbitrage_opportunities) >= 1:
    print("\n\n\n--------------------------------------")
    print("** Hay", len(arbitrage_opportunities), "oportunidades de arbitraje **")
    print("--------------------------------------")
    print(" Ticker    Ganancia\n")
    for opportunity in arbitrage_opportunities:
        ticker_str = f" {opportunity[0]}"
        gain_str = f"   {opportunity[1]:.2f}%"
        # Calcula la longitud máxima para alinear las columnas
        max_len = max(len(ticker_str), len(gain_str))
        # Añade espacios para alinear las columnas
        ticker_str = ticker_str.ljust(max_len)
        gain_str = gain_str.ljust(max_len)
        # Imprime las líneas con el mismo formato
        print(f"{ticker_str} {gain_str}")
#    for opportunity in arbitrage_opportunities:
#        print(f"Ticker: {opportunity[0]}, Ganancia: {opportunity[1]}%")
else:
    print("\nNo hay oportunidades de arbitraje por el momento :-(")


# Imprimir las oportunidades de arbitraje en orden descendente
if len(arbitrage_opportunities) >= 1:
    print("\nHay oportunidades de arbitraje!")
    for ticker, porcentaje_ganancia, vol in arbitrage_opportunities:
        print("-----------------------------------")
        print("Ticker:  ", ticker)
        print("Ganancia:", porcentaje_ganancia,"%")
        print("Volumen: ", vol)


