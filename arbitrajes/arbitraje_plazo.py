# Este script busca desarbitrajes en el mercado argentino en distintos instrumentos (acciones argentinas, CEDEARs, bonos soberanos, ONs, etc).
# Compara el precio de compra en contado inmediato (CI) con el precio de venta a 48 horas.

#------------------------------------------------------------------------------

import configparser
import requests

cred={}
config = configparser.ConfigParser()
config.read('PPI.ini')
cred['AuthorizedClient'] = config.get('Client', 'AuthorizedClient')
cred['ClientKey'] = config.get('Client', 'ClientKey')
cred['key_pública'] = config.get('Keys', 'key_publica')
cred['key_privada'] = config.get('Keys', 'key_privada')

base_url = 'https://clientapi.portfoliopersonal.com/api'
api_version = '1.0'

# Definimos los endpoints
endpoint1 = 'Account/LoginApi'   # Para obtener el token
endpoint2 = 'MarketData/Book'    # Para poder leer la caja de puntas
#endpoint = 'MarketData/SearchInstrument'

url = base_url+'/'+api_version+'/'+endpoint1
#url = f"{base_url}/{api_version}/{endpoint1}"  # esta es otra opcion

headers={
    'AuthorizedClient': cred['AuthorizedClient'],
    'ClientKey': cred['ClientKey'],
    'ApiKey': cred['key_pública'],
    'ApiSecret': cred['key_privada'],
}

response = requests.post(url, headers=headers)

if response.status_code == 200:
    print("")
    print("POST Request successful!\n")
    # Obtener el token de la respuesta JSON
    token = response.json()['accessToken']
    print("So far, so good... \n")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
    # Salir del script si la solicitud POST no fue exitosa
    exit()

#------------------------------------------------------------------------------

# Tickers de ACCIONES argentinas
#tickers = ["AGRO", "ALUA", "AUSO", "BBAR", "BHIP", "BMA", "BOLT", "BPAT", "BYMA", "CADO", "CAPX", "CECO2",
#           "CELU", "CEPU", "CGPA2", "COME", "CRE3W", "CRES", "CTIO", "CVH", "DGCU2", "DOME", "DYCA", "EDN", 
#           "FERR", "FIPL", "GAMI", "GARO", "GBAN", "GCDI", "GCLA", "GGAL", "GRIM", "HARG", "HAVA", "INTR", "INVJ",
#           "IRS2W", "IRSA", "LEDE", "LOMA", "LONG", "METR", "MIRG", "MOLA", "MOLI", "MORI", "MTR", "OEST", 
#           "PAMP", "PATA", "RICH", "RIGO", "ROSE", "SUPV", "SAMI", "SEMI", "TECO2", "TGNO4", "TGSU2", "TRAN",
#           "TXAR", "VALO", "YPFD"]

#tipo_instrumento = "Acciones"
#comis = 0.6 + 0.126

# Tickers de CEDEARs
#tickers = [
#    "AAL", "AAPL", "ABBV", "ABEV", "ABNB", "ABT", "ADBE", "ADGO", "ADP", "AEG", "AEM", "AIG", "AKO.B", "AMAT",
#    "AMD", "AMGN", "AMX", "AMZN", "ANF", "AOCA", "ARCO", "ARKK", "AVGO", "AVY", "AXP", "AZN", "BA", "BABA",
#    "BA.C", "BAYN", "BB", "BBD", "BBV", "BCS", "BHP", "BIDU", "BIIB", "BIOX", "BITF", "BK", "BMY", "BNG", "BP",
#    "BRFS", "BRKB", "C", "CAAP", "CAH", "CAR", "CAT", "CL", "COIN", "COST", "CRM", "CSCO", "CVX", "DD", "DE",
#    "DEO", "DESP", "DIA", "DISN", "DOCU", "DOW", "EA", "EBAY", "EBR", "EEM", "EFX", "ERIC", "ERJ", "ETSY",
#    "EWZ", "F", "FCX", "FDX", "FMX", "FSLR", "GE", "GGB", "GILD", "GLOB", "GOLD", "GOOGL", "GPRK", "GRMN",
#    "GS", "GSK", "HAL", "HD", "HL", "HMY", "HOG", "HON", "HPQ", "HSBC", "HUT", "HWM", "IBM", "IFF", "INFY",
#    "INTC", "IP", "ITUB", "IWM", "JD", "JMIA", "JNJ", "JPM", "KGC", "KMB", "KO", "LLY", "LMT", "LVS",
#    "LYG", "MA", "MCD", "MDT", "MELI", "META", "MMM", "MO", "MOS", "MRK", "MSFT", "MSTR", "MU", "MUFG",
#    "NEM", "NFLX", "NG", "NIO", "NKE", "NMR", "NOKA", "NTCO", "NTES", "NVDA", "ORCL", "OXY", "PAAS", "PANW",
#    "PBR", "PCAR", "PEP", "PFE", "PG", "PKS", "PSX", "PYPL", "QCOM", "QQQ", "RBLX", "RIO", "ROST", "RTX",
#    "SAN", "SAP", "SATL", "SBS", "SBUX", "SCCO", "SE", "SHEL", "SHOP", "SI", "SID", "SLB", "SNAP",
#    "SNOW", "SONY", "SPGI", "SPOT", "SPY", "SQ", "SUZ", "SYY", "T", "TEN", "TGT", "TM", "TMO", "TRIP", "TSLA",
#    "TSM", "TTE", "TXN", "TXR", "UAL", "UBER", "UGP", "UL", "UNH", "UNP", "UPST", "URBN", "USB", "V",
#    "VALE", "VIST", "VIV", "VOD", "VRSN", "VZ", "WBA", "WBO", "WFC", "WMT", "X", "XLE", "XLF", "XOM", "XROX",
#    "YELP", "YY", "YZCA", "ZM"
#]

#tipo_instrumento = "CEDEARS"
#comis = 0.6 + 0.126

# Tickers de Bonos Soberanos en pesos
tickers = ["AL30", "GD30", "GD35", "AL35", "GD38", "AE38", "GD41", "AL29", "AL41", "GD46", "GD29"]

tipo_instrumento = "BONOS"
comis = 0.6

# Tickers de Bonos del Tesoro Nacional (y otros) en pesos:
#tickers = ["TV24", "T3X4", "TDF24", "TDJ24", "TDN24","T4X4", "T2X4", "TX24", "TDG24", "T2X5", "TDA24", "T2V4", 
#           "BPO27", "TV25", "T6X4", "TX26", "TX28", "TX31","DICP", "TVPA", "TVPP","T5X4", "PR13", "PR17", "PARP",
#           "TO26", "TC25P", "TZX26", "TDE25", "TZX27"]

#tipo_instrumento = "BONOS"
#comis = 0.6

# Tickers de ONs en pesos
#tickers = ["TLCHO", "MRCAO", "YCA6O", "YMCJO", "TLC1O", "YMCIO", "MGCHO", "YMCHO", "YPCUO", "TLC5O", "LOC2O", 
#           "YMCQ", "MGCJO", "MGC9O", "CLSIO", "MTCGO", "SNS9O", "IRCFO", "ARC1O", "CRCEO", "MRCGO", "AEC1O", 
#           "CS38O", "NPCAO", "GN40O", "LECAO", "RCCJO", "MRCPO", "MRCRO", "IRCEO", "LOC3O", "MRCOO"]

#tipo_instrumento = "ON"
#comis = 0.6

#print("\nLeyendo tickers de...\n")
print(f"\nLeyendo tickers de {tipo_instrumento}\n")

#------------------------------------------------------------------------------

print("\nBuscando datos en el mercado...\n")

url = base_url+'/'+api_version+'/'+endpoint2

# Creamos una lista para almacenar las oportunidades de arbitraje
arbitrage_opportunities = []

for ticker in tickers:
    # Parámetros de la solicitud GET
    params_CI = {
        'ticker': ticker,
        'type': tipo_instrumento,
        'settlement': 'INMEDIATA'
    }
    
    params_48 = {
        'ticker': ticker,
        'type': tipo_instrumento,
        'settlement': 'A-48HS'
    }
    
    # Headers para la solicitud GET
    headers = {
        'AuthorizedClient': cred['AuthorizedClient'],
        'ClientKey': cred['ClientKey'],
        'Content-Type': "application/json",
        'Authorization': f"Bearer {token}",
    }
    
    # Realizar la solicitud GET para obtener la caja de puntas
    response_CI = requests.get(url, headers=headers, params=params_CI)
    response_48 = requests.get(url, headers=headers, params=params_48)
    
    # Verificar si la solicitud GET fue exitosa
    if response_CI.status_code == 200 and response_48.status_code == 200:
        # Obtener los datos de la respuesta en formato JSON
        book_data_CI = response_CI.json()
        book_data_48 = response_48.json()

        print(f"Ticker: {ticker}")
        
        print("\n")
           
        # Imprimimos solo el primer valor de bid en CI y 48hs
        first_bid_CI = book_data_CI['bids'][0]
        print(f"First Bid CI: Position: {first_bid_CI['position']}, Price: {first_bid_CI['price']}, Quantity: {first_bid_CI['quantity']}")
        first_bid_48 = book_data_48['bids'][0]
        print(f"First Bid 48hs: Position: {first_bid_48['position']}, Price: {first_bid_48['price']}, Quantity: {first_bid_48['quantity']}")

        # Imprimimos solo el primer valor de offers/asks en CI y 48hs
        first_offer_CI = book_data_CI['offers'][0]
        print(f"First Offer CI: Position: {first_offer_CI['position']}, Price: {first_offer_CI['price']}, Quantity: {first_offer_CI['quantity']}")
        first_offer_48 = book_data_48['offers'][0]
        print(f"First Offer 48hs: Position: {first_offer_48['position']}, Price: {first_offer_48['price']}, Quantity: {first_offer_48['quantity']}")
        
        print("\n")
        
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
        print(f"Ticker: {ticker}")
        print(f"Error: {response.status_code}")
        print(response.text)
        print("\n\n")

#------------------------------------------------------------------------------

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
else:
    print("\nNo hay oportunidades de arbitraje por el momento :-( ")



