
def print_opportunities(arbitrage_opportunities):
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
            vol_str = f"   {opportunity[2]:.2f}"
            # Calcula la longitud máxima para alinear las columnas
            max_len = max(len(ticker_str), len(gain_str), len(vol_str))
            # Añade espacios para alinear las columnas
            ticker_str = ticker_str.ljust(max_len)
            gain_str = gain_str.ljust(max_len)
            vol_str = vol_str.ljust(max_len)
            # Imprime las líneas con el mismo formato
            print(f"{ticker_str} {gain_str} {vol_str}")
    else:
        print("\nNo hay oportunidades de arbitraje por el momento :-(")

    # Imprimir las oportunidades de arbitraje en orden descendente
    if len(arbitrage_opportunities) >= 1:
        print("\nHay oportunidades de arbitraje!")
        for ticker, porcentaje_ganancia, vol in arbitrage_opportunities:
            print("-----------------------------------")
            print("Ticker:  ", ticker)
            print("Ganancia:", porcentaje_ganancia, "%")
            print("Volumen: ", vol)

