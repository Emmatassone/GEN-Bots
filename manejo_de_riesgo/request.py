import requests
from datetime import date


def test_request():
    # Datos
    response = None
    request_data = {
        "assets": ["JPM", "MSFT", "BA", "KO", "AAPL", "TSLA", "AMZN", "NVDA"],
        "train_start": "2019-01-01",
        "train_end": "2022-12-30",
        "test_start": "2022-12-30",
        "test_end": "2023-12-08"
    }

    # URL del endpoint
    url = "http://127.0.0.1:8000/portfolio/update"

    try:
        response = requests.put(url, json=request_data)

        if response.status_code == 200:
            print(response.json())
        else:
            print(f'Error en la petición. Código de estado: {response.status_code}')

        response = response.json()
    except Exception as e:
        print(f'Error en la petición: {str(e)}')

    return response


def test_request_risk(risk):
    # risk = 'Moderate'
    url = f'http://127.0.0.1:8000/portfolio/update/risk?risk_user={risk}'
    response = None

    try:
        response = requests.put(url)

        if response.status_code == 200:
            print(response.json())
        else:
            print(f'Error en la petición. Código de estado: {response.status_code}')

        response = response.json()

    except Exception as e:
        print(f'Error en la petición: {str(e)}')

    return response


