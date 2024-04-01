from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd

from sources.option_strategies import OptionStrategyBuilder


class OptionStrategyRequest(BaseModel):
    expiration_month: str
    underlying_asset: str


class OptionStrategyResponse(BaseModel):
    strike_compra: float = Field(alias="Strike Compra")
    precio_compra: float = Field(alias="Precio de Compra")
    strike_venta: float = Field(alias="Strike Venta")
    precio_venta: float = Field(alias="Precio de Venta")
    costo:  Optional[float] = Field(alias="Costo")
    credito_neto: Optional[float] = Field(alias="Credito Neto")
    ganancia_maxima: float = Field(alias="Ganancia Maxima")
    riesgo_maximo: float = Field(alias="Riesgo Maximo")


df = pd.read_csv('opciones.csv')
cleaned_df = df.dropna(subset=['volume'])

print(df)

# Aquí establecemos los valores de expiration_month y underlying_asset
expiration_month = 'AB'
underlying_asset = 'GGAL'

app = FastAPI()


@app.get("/option-strategy/bull_call_spread", response_model=List[OptionStrategyResponse])
def create_option_strategy(expiration_month: str = expiration_month, underlying_asset: str = underlying_asset):
    ggal_options = cleaned_df[cleaned_df['underlying_asset'] == underlying_asset]
    ggal_options_april = ggal_options[ggal_options['symbol'].str.contains(expiration_month)]

    strategy_builder = OptionStrategyBuilder(ggal_options_april)
    strategy_data_df = strategy_builder.bull_call_spread()

    strategy_data_list = strategy_data_df.to_dict(orient='records')

    strategies = [OptionStrategyResponse(**data) for data in strategy_data_list]

    return strategies


@app.get("/option-strategy/bull_put_spread", response_model=List[OptionStrategyResponse])
def create_option_strategy_bullput(expiration_month: str = expiration_month, underlying_asset: str = underlying_asset):
    ggal_options = cleaned_df[cleaned_df['underlying_asset'] == underlying_asset]
    ggal_options_april = ggal_options[ggal_options['symbol'].str.contains(expiration_month)]

    strategy_builder = OptionStrategyBuilder(ggal_options_april)
    strategy_data_df = strategy_builder.bull_put_spread()

    strategy_data_list = strategy_data_df.to_dict(orient='records')
    print(strategy_data_list)
    strategies = [OptionStrategyResponse(**data) for data in strategy_data_list]

    return strategies


