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

    # Inicializamos la lista de oportunidades de arbitraje como vacía
    arbitrage_opportunities = []

    # Imprimimos las oportunidades de arbitraje, si es que hay alguna
    if opportunity:
        percentage_earn, vol = opportunity
        arbitrage_opportunities = [("AAPL", percentage_earn, vol)]   # Creamos la lista de oportunidades

    print_opportunities(arbitrage_opportunities)

if __name__ == '__main__':
    main()
