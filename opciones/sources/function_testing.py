import pandas as pd

# Opciones del 22/02/24 a las 12:02pm
df = pd.read_csv('opciones.csv')

# Limpiamos el df de las opciones sin volumen
cleaned_df = df.dropna(subset=['volume'])

# Nos quedamos con las opciones de un GGAL que vencen en Abril
expiration_month = 'AB'
underlying_asset = 'GGAL'

GGAL_options = cleaned_df[cleaned_df['underlying_asset'] == underlying_asset]
GGAL_options_april = GGAL_options[GGAL_options['symbol'].str.contains(expiration_month)].reset_index()

from option_strategies import OptionStrategyBuilder

strategy_builder = OptionStrategyBuilder(GGAL_options_april)

print(strategy_builder.bull_call_spread())
# print(strategy_builder.bull_call_spreads)
