Key = str

"""
DEBT_AND_LEASE_CURRENT (np.float64), equivalent to the XBRL US GAAP 2023 taxonomy concept us-gaap:DebtCurrent,
defined as the "amount of debt and lease obligation, classified as current." In Yahoo Finance it is specified as
"Current Debt And Capital Lease Obligation"
"""
DEBT_AND_LEASE_CURRENT = 'debt_and_lease_current'

"""
DEBT_AND_LEASE_NON_CURRENT (np.float64). Specified in Yahoo Finance as "Long Term Debt And Capital Lease Obligation"
Includes DEBT_NON_CURRENT in addition to capital lease obligations.
"""
DEBT_AND_LEASE_NON_CURRENT = 'debt_and_lease_non_current'

"""
DEBT_NON_CURRENT (np.float64), equivalent to the XBRL US GAAP 2023 taxonomy concept us-gaap:LongTermDebtNoncurrent,
defined as the "amount, after deduction of unamortized premium (discount) and debt issuance cost, of long-term debt 
classified as noncurrent. Excludes lease obligation." The standard label is "Long-Term Debt, Excluding Current 
Maturities." In Yahoo Finance it is given as "Long Term Debt," below "Long Term Debt and Capital Lease Obligations."
"""
DEBT_NON_CURRENT = 'debt_non_current'

"""
NET_INCOME (np.float64), equivalent to the XBRL US GAAP 2023 taxonomy concept us-gaap:NetIncomeLoss, defined as the
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
noncontrolling interest." In Yahoo Finance it is specified as "Common Stock Equity."
"""
STOCKHOLDER_EQUITY = 'stockholder_equity'

"""
TICKER_SYMBOL (string).
"""
TICKER_SYMBOL = 'ticker_symbol'

"""
TOTAL_ASSETS (np.float64), equivalent to the XBRL US GAAP taxonomy concept us-gaap:Assets, defined as the "sum of the
carrying amounts as of the balance sheet date of all assets that are recognized. Assets are probable future economic
benefits obtained or controlled by an entity as a result of past transactions or events."
"""
TOTAL_ASSETS = 'total_assets'
