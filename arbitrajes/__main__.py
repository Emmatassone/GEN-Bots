from data import instrument_loader
from printer import print_opportunities
import numpy as np

# Change the values of the commissions accordingly
# PPI's commssions
commi = 0.6
IVA = commi * 0.21

# We create a list to store the arbitrage opportunities
arbitrage_opportunities = []

def main():
    # We call "instrument_loader" to load the values
    bid_AAPL_48, ask_AAPL_CI, volume_CI = load_prices()

    charge_buy = ask_AAPL_CI * (commi + IVA) / 100
    buy_price = bid_AAPL_48 + charge_buy

    charge_sell = bid_AAPL_48 * (commi + IVA) / 100
    net_income = bid_AAPL_48 - charge_sell

    if net_income > buy_price:
        print("\nHay una nueva oportunidad de arbitraje!")
        percentage_earn = (net_income - buy_price) * 100 / net_income
#        arbitrage_opportunities.append((ticker, round(percentage_earn, 2), volume_CI))

        # Llamamos a la función para imprimir las oportunidades de arbitraje
        print_opportunities(arbitrage_opportunities)


if __name__ == '__main__':
    main()
