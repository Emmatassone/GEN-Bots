from data import instrument_loader
from printer import print_opportunities
from opportunity_finder import ArbitrageOpportunityFinder
import numpy as np

def main():
    # We call "instrument_loader" to load the values
    bid_AAPL_48, ask_AAPL_CI, volume_CI = load_prices()

    # Creamos una instancia de ArbitrageOpportunityFinder
    finder = ArbitrageOpportunityFinder(bid_AAPL_48, ask_AAPL_CI, volume_CI, commi, IVA)

    # Buscamos oportunidades de arbitraje
    opportunity = finder.find_opportunity()

    # Imprimimos las oportunidades de arbitraje, si es que hay alguna
    if opportunity:
        percentage_earn, vol = opportunity
        print("\n\n\n--------------------------------------")
        print("** Hay una oportunidad de arbitraje **")
        print("--------------------------------------")
        print(f"Ticker: AAPL, Ganancia: {percentage_earn}%, Volumen: {vol}")
    else:
        print("\nNo hay oportunidades de arbitraje por el momento :-(")


if __name__ == '__main__':
    main()
