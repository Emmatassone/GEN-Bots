from portfolio import SetUpPortfolio
from data import load_data
import numpy as np

def main():
    ohlcv= load_data()
    ohlcv= ohlcv.astype(np.float64)
    
    strategies = ['MACD', 'DMAC', 'Threshold', 'RSI', 'Combined', 'Candles']  # List of available strategies

    print("Choose a trading strategy:")
    for i, strategy in enumerate(strategies, start=1):
        print(f"{i}. {strategy}")

    choice = int(input("Enter the number corresponding to the strategy: "))

    if 1 <= choice <= len(strategies):
        selected_strategy = strategies[choice - 1]
        print(f"You have selected the '{selected_strategy}' strategy.")
        # Initialize Portfolio and test the selected strategy
        portfolio = SetUpPortfolio(selected_strategy,ohlcv)
        
        print("The actual parameters of the strategy are")
        print(portfolio.strategy_params())
        parameters = input("Please, enter a list with the parameters of the strategy \n")
        
        portfolio.get_entries_and_exits(eval(parameters))
        portfolio.plot_backtest()
        
    else:
        print("Invalid choice. Please select a valid number.")

if __name__ == "__main__":
    main()
