# Autor: Nicolas Baseggio
class YFinanceDataFetchError(Exception):
    """
    Raised when there is an error fetching financial data using Yahoo Finance.

    Attributes:
        message (str): Descriptive error message.
    """

    def __init__(self, message="Error fetching financial data from Yahoo Finance"):
        self.message = message
        super().__init__(self.message)


class PortfolioOptimizationError(Exception):
    """
    Raised when there is an error in the portfolio optimization process.

    Attributes:
        message (str): Descriptive error message.
    """

    def __init__(self, message="Error in portfolio optimization"):
        self.message = message
        super().__init__(self.message)


class TestingDataFetchError(Exception):
    """
    Raised when there is an error fetching testing data.

    Attributes:
        message (str): Descriptive error message.
    """

    def __init__(self, message="Error fetching testing data"):
        self.message = message
        super().__init__(self.message)


class PortfolioReturnsCalculationError(Exception):
    """
    Raised when there is an error in the calculation of portfolio returns.

    Attributes:
        message (str): Descriptive error message.
    """

    def __init__(self, message="Error calculating portfolio returns"):
        self.message = message
        super().__init__(self.message)
