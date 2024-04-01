from fastapi import FastAPI
import pandas as pd

from opciones.sources.option_strategies import OptionStrategyBuilder

df = pd.read_csv('opciones/opciones.csv')

cleaned_df = df.dropna(subset=['volume'])

expiration_month = 'AB'
underlying_asset = 'GGAL'

GGAL_options = cleaned_df[cleaned_df['underlying_asset'] == underlying_asset]
GGAL_options_april = GGAL_options[GGAL_options['symbol'].str.contains(expiration_month)]

app = FastAPI()

strategy_builder = OptionStrategyBuilder(GGAL_options_april)
strategy_data = strategy_builder.bull_call_spread()

print(strategy_data)


@app.get("/")
def read_root():
    return 'Welcome to the portfolio API!'

#%%
