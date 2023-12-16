import requests
from datetime import date

# Datos
request_data = {
    "assets": ['JPM', 'MSFT', 'BA', 'KO', 'AAPL', 'TSLA', 'AMZN', 'NVDA'],
    "train_start": '2019-01-01',
    "train_end": '2022-12-30',
    "test_start": '2022-12-30',
    "test_end": str(date.today())
}

# URL del endpoint
url = "https://tu-servidor.com/tu-endpoint"

# Realizar la petición
try:
    response = requests.post(url, json=request_data)

    # Verificar el código de estado de la respuesta
    if response.status_code == 200:
        # La petición fue exitosa, puedes manejar la respuesta aquí
        print(response.json())
    else:
        print(f'Error en la petición. Código de estado: {response.status_code}')

except Exception as e:
    print(f'Error en la petición: {str(e)}')

{
    "assets": ["JPM", "MSFT", "BA", "KO", "AAPL", "TSLA", "AMZN", "NVDA"],
    "train_start": "2019-01-01",
    "train_end": "2022-12-30",
    "test_start": "2022-12-30",
    "test_end": "2023-12-08"
}