# Importamos todo lo necesario acá
#
# import ...
# import ...
# from ... import ...

# Leemos el precio del activo (acciones y CEDEARs, en ppio) a 48hs y en CI usando Matriz
#
# A modo de ejemplo, usamos los precios de cierre de AAPL a 48 hs y en CI
# bid_AAPL_48 = 21142.0
# ask_AAPL_CI = 20786.5

def load_prices():
    bid_AAPL_48 = 21142.0
    ask_AAPL_CI = 20786.5
    volume_CI = 70666776
    return bid_AAPL_48, ask_AAPL_CI, volume_CI


# NO OLVIDAR DE LEER EL VOLUMEN en CI TAMBIEN!
