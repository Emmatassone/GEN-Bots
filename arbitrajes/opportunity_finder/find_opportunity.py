
class ArbitrageOpportunityFinder:
    def __init__(self, bid_AAPL_48, ask_AAPL_CI, volume_CI, commi, IVA):
        self.bid_AAPL_48 = bid_AAPL_48
        self.ask_AAPL_CI = ask_AAPL_CI
        self.volume_CI = volume_CI
        self.commi = commi
        self.IVA = IVA

    def find_opportunity(self):
        charge_buy = self.ask_AAPL_CI * (self.commi + self.IVA) / 100
        buy_price = self.bid_AAPL_48 + charge_buy

        charge_sell = self.bid_AAPL_48 * (self.commi + self.IVA) / 100
        net_income = self.bid_AAPL_48 - charge_sell

        if net_income > buy_price:
            print("\nHay una nueva oportunidad de arbitraje!")
            percentage_earn = (net_income - buy_price) * 100 / net_income
            return round(percentage_earn, 2), self.volume_CI
        else:
            return None