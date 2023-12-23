# Con este script queremos hacer heatmaps que nos muestre cuales fueron las variaciones en los precios
# de los bonos del Tesoro Nacional (en pesos), y de los bonos soberanos (en pesos y dolares).
# El usuario puede elegir ver el heatmap de las variaciones del precio de uno de los instrumentos anteriores
# en los siguientes plazos:
# a) Los últimos 2 días hábiles
# b) El primer día hábil de la semana y el último día hábil
# c) En lo que va del mes
# d) En lo que va del año
# Para eso vamos a encapsular todo en una clase

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

# Nos conectamos al entorno "Sandbox" (i.e., un entorno de prueba)
# Cambiar la variable "sandbox" a False para conectarse con la cuenta verdadera
##sandbox_public_key=''
##sandbox_secret_key=''

# Keys verdaderas
sandbox_public_key=''
sandbox_secret_key=''
ppi = PPI(sandbox=False)

# Cambiar las credenciales de inicio de sesión para conectarse a la API de PPI
ppi.account.login_api(sandbox_public_key,sandbox_secret_key)


# Acá definimos la clase

class Bonos_argentinos:
    def __init__(self):
        self.bank_holidays = [datetime(2023, 1, 1), datetime(2023, 10, 13), datetime(2023, 10, 16), datetime(2023, 12, 8), datetime(2023, 12, 25)]
        self.limit_time = datetime.strptime('17:00', '%H:%M').time()
        self.current_time = datetime.now().time()
        self.end_date = self.calculate_end_date()
        self.variation_type = None
        self.variation_string = None
        self.soberanos_pesos = ["AL30", "GD30", "GD35", "AL35", "GD38", "AE38", "GD41", "AL29", "AL41", "GD46", "GD29"]
        self.soberanos_dolares = ["AL30D", "GD30D", "GD35D", "AL35D", "GD38D", "AE38D", "GD41D", "AL29D", "AL41D", "GD46D", "GD29D"]
        self.bonos_tesoro = ["T4X4", "T2X4", "TX24", "TX26", "TX28", "DICP", "PR13", "PR17", "PARP", "TO26", "TC25P"]
                   
            
    def calculate_end_date(self):
        end_date = datetime.now()

        if self.current_time > self.limit_time:
            end_date = datetime.combine(end_date.date(), self.limit_time)
        else:
            end_date = datetime.combine(end_date.date(), self.current_time)

        i = 0
        while end_date.weekday() >= 5 or end_date.date() in [d.date() for d in self.bank_holidays]:
            end_date -= timedelta(days=1)
            i += 1

        if i > 0:
            end_date = datetime.combine(end_date.date(), self.limit_time)

#        print('\nend data = ', end_date)

        return end_date
    
    
    def calculate_start_date(self, variation_type):
        if variation_type == "daily":
            start_date = self.end_date - timedelta(days=1)
        elif variation_type == "weekly":
            start_date = self.end_date - timedelta(days=self.end_date.weekday())
        elif variation_type == "monthly":
            start_date = self.end_date.replace(day=1)
        elif variation_type == "annually":
            start_date = self.end_date.replace(month=1, day=1)
        else:
            raise ValueError("Invalid variation type!")

        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
#        print('start date = ', start_date)
        
        while start_date.weekday() >= 5 or start_date.date() in [d.date() for d in self.bank_holidays]:
            start_date -= timedelta(days=1)

        return start_date

    
    def fetch_market_data(self, ticker, variation_type):
        
        market_data = ppi.marketdata.search(ticker, "Bonos", "A-48HS", self.calculate_start_date(variation_type), self.end_date)
        
        if len(market_data) >= 2:
            return self.calculate_price_change(ticker, market_data)
        else:
            print(f"No data found for {ticker}.")
            return None
        

    def calculate_price_change(self, ticker, market_data):
        prices = [data['price'] for data in market_data]
        price_difference = prices[-1] - prices[0]
        percentage_change = (price_difference / prices[0]) * 100

        return {
            "Ticker": ticker,
            "Start Price": prices[0],
            "End Price": prices[-1],
            "Percentage Change": round(percentage_change, 2)
        }
            

    def plot_variation(self, tickers):
        data_list = []

        for ticker in tickers:
            market_data = self.fetch_market_data(ticker, self.variation_type)
            if market_data:
                print(f"{ticker}: {market_data['Percentage Change']}%")
                data_list.append(market_data)

        # Filter out None values before creating the DataFrame
        data_list = [data for data in data_list if data is not None]

        if not data_list:
            print("No data available for the specified tickers.")
            return

        data = pd.DataFrame(data_list)
        data = data.sort_values(by="Percentage Change")

        plt.figure(figsize=(12, 8))
        cmap = sns.diverging_palette(10, 150, s=90, l=50, as_cmap=True)

        num_tickers = len(tickers)
        num_cols = min(num_tickers, 6)
        num_rows = int(np.ceil(num_tickers / num_cols))

        matrix = np.zeros((num_rows, num_cols))

        for i, ticker in enumerate(tickers):
            row = i // num_cols
            col = i % num_cols
            matrix[row, col] = data.loc[data['Ticker'] == ticker, 'Percentage Change']

        ax = sns.heatmap(matrix, cmap=cmap, center=0, annot=False, fmt=".2f", linewidths=0.5, linecolor='black')

        for i, ticker in enumerate(tickers):
            row = i // num_cols
            col = i % num_cols
            ax.text(col + 0.5, row + 0.5, f"{ticker}\n{matrix[row, col]:.2f}%", ha='center', va='center', fontsize=14,
                    color='black')

        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=14)
#        cbar.ax.text(3.5, 2.0, "Variación Porcentual", ha='center', va='center', rotation=90, fontsize=16,
#                    color='black')

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set(xticklabels=[], yticklabels=[])

        plt.title(f"Variación de precios: {self.variation_string}", fontsize=18)
        plt.show()

        
    def choose_variation_type(self):
        print("\n¿Qué instrumento querés analizar?\n")
        print("1. Bonos del Tesoro Nacional")
        print("2. Bonos Soberanos en pesos")
        print("3. Bonos Soberanos en dólares")

        choice_list = input("\nIngrese 1, 2, o 3: ")
    
        if choice_list == '1':
            tickers_list = self.bonos_tesoro
        elif choice_list == '2':
            tickers_list = self.soberanos_pesos
        elif choice_list == '3':
            tickers_list = self.soberanos_dolares  
        else:
            print("La opción ingresada no es válida. Por favor, ingrese 1, 2, o 3.")
            return
        
        print("\nQué tipo de variación quiere ver de los Bonos del Tesoro?\n")
        print("Variación diaria?  ==> presione 1")
        print("Variación semanal? ==> presione 2")
        print("Variación mensual? ==> presione 3")
        print("Variación anual?   ==> presione 4")
        
        choice = input("\nIngrese 1, 2, 3 o 4: ")
        
        if choice in ['1', '2', '3', '4']:
            self.variation_type = {"1": "daily", "2": "weekly", "3": "monthly", "4": "annually"}[choice]
            self.variation_string = {"1": "últimos 2 días hábiles", "2": "en lo que va de la semana", 
                                     "3": "en lo que va del mes", "4": "en lo que va del año"}[choice]
            
            # Capturamos las fechas antes de llamar a otras funciones
            start_date = self.calculate_start_date(self.variation_type)
            end_date = self.end_date

            # Imprimimos las fechas
            print(f"\nFecha de inicio: {start_date}")
            print(f"Fecha de fin   : {end_date}")
            print("")
            
            # Llamamos a fetch_market_data con el tipo de variación (diaria, semanal, etc)
            for ticker in tickers_list:
                self.fetch_market_data(ticker, self.variation_type)

            # Llamamos a la función generalizada de plot_variation
            self.plot_variation(tickers_list)
        
        else:
            print("La opción ingresada no es válida. Por favor, ingrese 1, 2, 3 o 4.")
            return


# Llamamos a la clase
bonos = Bonos_argentinos()
bonos.choose_variation_type()
