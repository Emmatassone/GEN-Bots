"""
NET_INCOME (np.float64), equivalent to the XBRL US GAAP taxonomy concept us-gaap:NetIncomeLoss, defined as the
"portion of profit or loss for the period, net of income taxes, which is attributable to the parent."
"""
NET_INCOME = 'net_income'

"""
PERIOD_END (np.datetime64) specifies the end date for a given period.
"""
PERIOD_END = 'period_end'

"""
PERIOD_START (np.datetime64) specifies the start date for a given period.
"""
PERIOD_START = 'period_start'

"""
RETURN_ON_EQUITY (np.float64) is net income divided by shareholder's equity. In terms of XBRL US GAAP taxonomy 
elements, it can be defined as the ratio us-gaap:NetIncomeLoss / us-gaap:StockholdersEquity.
"""
RETURN_ON_EQUITY = 'return_on_equity'

"""
STOCKHOLDER_EQUITY (np.float64), equivalent to the XBRL US GAAP taxonomy concept us-gaap:StockholdersEquity, defined
as the "amount of equity (deficit) attributable to parent. Excludes temporary equity and equity attributable  to
noncontrolling interest."
"""
STOCKHOLDER_EQUITY = 'stockholder_equity'

"""
TICKER_SYMBOL (string).
"""
TICKER_SYMBOL = 'ticker_symbol'
