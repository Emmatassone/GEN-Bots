import riskfolio as rp
import warnings
import pandas as pd

warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:.4%}'.format


def rm():
    return self._rm


class PortfolioOptimizerTest:
    """
    This class is used to TEST optimize the portfolio using the risk-folio library
    """
    method_mu = 'hist'
    method_cov = 'hist'
    hist = True
    rf = 0
    lib = 0
    MODEL_OPTIONS = {'Classic', 'BL', 'FM', 'BLFM'}
    OBJ_OPTIONS = {'MinRisk', 'Utility', 'Sharpe', 'MaxRet'}
    RISK_LEVEL_USER = {'Conservative': 1, 'Moderate': 2, 'Aggressive': 3, 'Very Aggressive': 4}
    RISK_LEVEL_MAPPING = {
        1: 'MinRisk',
        2: 'Utility',
        3: 'Sharpe',
        4: 'MaxRet'
    }
    RISK_LEVEL_DEFAULT = 'Moderate'

    def __init__(self):
        self.weights_initial_sum = None
        self._assets = None
        self._cvar_value = None
        self._risk_level = None
        self._obj = 'Sharpe'
        self._model = 'Classic'
        self._rm = 'MV'

    @property
    def model(self):
        return self._model

    @property
    def obj(self):
        return self._obj

    @property
    def cvar_value(self):
        return self._cvar_value

    @property
    def risk_level(self):
        return self._risk_level

    @property
    def assets(self):
        return self._assets

    @property
    def weights_initial_sum(self):
        return self._weights_initial_sum

    @cvar_value.setter
    def cvar_value(self, cvar_value):
        self._cvar_value = cvar_value / 252 ** 0.5

    @risk_level.setter
    def risk_level(self, risk_profile):
        self._risk_level = self.RISK_LEVEL_USER.get(risk_profile, self.RISK_LEVEL_DEFAULT)
        self.set_objective_function(self.RISK_LEVEL_MAPPING.get(self._risk_level, self.RISK_LEVEL_DEFAULT))

    @weights_initial_sum.setter
    def weights_initial_sum(self, value):
        self._weights_initial_sum = value

    def set_initial_asset(self, assets, weights=None):
        if not isinstance(assets, (list, tuple)):
            raise TypeError("The 'assets' parameter must be a list or tuple.")

        if weights is not None and not isinstance(weights, (list, tuple)):
            raise TypeError("The 'weights' parameter must be a list or tuple.")

        if weights is not None and len(assets) != len(weights):
            raise ValueError("The lengths of 'assets' and 'weights' must be the same.")

        self._assets = pd.DataFrame({'assets': assets, 'weights': weights})

        weights_initial_sum = self._assets['weights'].sum()
        self.weights_initial_sum = weights_initial_sum
        print('Initial weights sum:', weights_initial_sum)

    def set_objective_function(self, objective: str):
        """
        Set the objective function for portfolio optimization.
        :param objective: str
            The name of the objective function (e.g., 'MinRisk', 'Utility', 'Sharpe', 'MaxRet').
        """
        if objective in self.OBJ_OPTIONS:
            self._obj = objective
        else:
            raise ValueError(f'Invalid objective function: {objective}')

    def port_optimize(self, returns_train):
        portfolio = rp.Portfolio(returns=returns_train)
        portfolio.assets_stats(method_mu=self.method_mu, method_cov=self.method_cov, d=0.94)
        if self.cvar_value is not None:
            try:
                portfolio.upperCVaR = self.cvar_value
            except Exception as e:
                print(e)
        weights_optimized = portfolio.optimization(
            model=self.model,
            rm=rm,
            obj=self.obj,
            rf=self.rf,
            l=self.lib,
            hist=True)
        if self.weights_initial_sum is not None:
            try:
                weights_optimized['weights'] = weights_optimized['weights'] * (1 - self.weights_initial_sum)
                self.assets.set_index('assets', inplace=True)
                weights_optimized = pd.concat([self.assets, weights_optimized], axis=0)
            except Exception as e:
                print(e)

        return weights_optimized
