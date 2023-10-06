import ccxt
exchange_names = ['ascendex', 'bequant', 'bigone', 'bingx', 'bit2c', 'bitbank', 'bitbay', 'bitbns', 'bitcoincom', 'bitfinex', 'bitfinex2', 'bitflyer', 'bitforex', 'bitget', 'bithumb', 'bitmart', 'bitmex', 'bitopro', 'bitpanda', 'bitrue', 'bitso', 'bitstamp', 'bitstamp1', 'bittrex', 'bitvavo', 'bl3p', 'blockchaincom', 'btcalpha', 'btcbox', 'btctradeua', 'btcturk', 'cex', 'coincheck', 'coinex', 'coinmate', 'coinone', 'coinsph', 'coinspot', 'cryptocom', 'currencycom', 'delta', 'deribit', 'digifinex', 'exmo', 'fmfwio', 'gate', 'gateio', 'gemini', 'hitbtc', 'hitbtc3', 'hollaex', 'huobi', 'huobijp', 'huobipro', 'idex', 'independentreserve', 'indodax', 'kraken', 'krakenfutures', 'kucoin', 'kucoinfutures', 'latoken', 'lbank', 'lbank2', 'luno', 'lykke', 'mercado', 'mexc', 'mexc3', 'ndax', 'novadax', 'oceanex', 'okex', 'okex5', 'okx', 'paymium', 'phemex', 'poloniex', 'poloniexfutures']

exchanges = [getattr(ccxt, exchange_name)() for exchange_name in exchange_names]

for exchange in exchanges:
    exchange.load_markets()
#we import the library and obtain market data of all the exchanges.

symbol = 'BTC/USDT'

buy_prices = []
sell_prices = []

for exchange in exchanges:
    if symbol in exchange.symbols:
        ticker = exchange.fetch_ticker(symbol)
        buy_prices.append({'exchange': exchange.id, 'price': ticker['bid']})
        sell_prices.append({'exchange': exchange.id, 'price': ticker['ask']})

sorted_buy_prices = sorted([price for price in buy_prices if price['price'] is not None], key=lambda x: x['price'])

top_10_buy_exchanges = sorted_buy_prices[:10]

sorted_sell_prices = sorted([price for price in sell_prices if price['price'] is not None], key=lambda x: x['price'], reverse=True)

top_10_sell_exchanges = sorted_sell_prices[:10]

print("Mejores lugares para comprar:")
for buy_exchange in top_10_buy_exchanges:
    print(f"Exchange: {buy_exchange['exchange']}, Precio de compra: {buy_exchange['price']}")

print("\nMejores lugares para vender:")
for sell_exchange in top_10_sell_exchanges:
    print(f"Exchange: {sell_exchange['exchange']}, Precio de venta: {sell_exchange['price']}")
#we establish a pair and obtain its value in each of the exchanges to sort them in order to show us the best opportunities to buy and sell.
