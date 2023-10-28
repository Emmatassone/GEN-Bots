import riskfolio as rp
import warnings
import pandas as pd

warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:.4%}'.format


class PortfolioOptimizerTest:
    """
    This class is used to TEST optimize the portfolio using the risk-folio library
    """

    def __init__(self):
        self.weights_initial_sum = None
        self.assets = None
        self.cvar_value = None
        self.risk_level = None

    risk_level_user = {'Conservative': 1, 'Moderate': 2, 'Aggressive': 3}
    risk_level_default = 'Moderate'
    method_mu = 'hist'
    method_cov = 'hist'
    model = 'Classic'
    rm = 'CVaR'
    obj = 'Sharpe'
    hist = True
    rf = 0
    lib = 0

    def set_objective_function(self, objective: str):
        """
        sets the objective function
        :param objective: str
        :options: MinRisk, MaxRet, Utility, Sharpe
        :return: None
        """
        self.obj = objective
        return f'Objective function set in {self.obj }'

    def set_risk_level(self, risk_profile: str):
        """
        sets the risk level
        :param risk_profile: str
        :options: Conservative, Moderate, Aggressive
        :return: None
        """
        self.risk_level = self.risk_level_user[risk_profile]
        if self.risk_level is not None:
            if self.risk_level == 1:
                self.set_objective_function('MinRisk')
        return f'Risk level set in {risk_profile} and objective function set in {self.obj}'

    def set_initial_asset(self, assets, weights=None):
        """
        sets the initial assets and weights
        :param assets: list of assets
        :param weights: list of weights
        :return: None
        """

        if not isinstance(assets, (list, tuple)):
            raise TypeError("assets must be a list or tuple")

        if weights is not None and not isinstance(weights, (list, tuple)):
            raise TypeError('tuple or list expected for weights')

        if len(assets) != len(weights) if weights is not None else False:
            raise ValueError("length of assets and weights must be the same")

        self.assets = pd.DataFrame({'assets': assets, 'weights': weights})
        weights_initial_sum = self.assets['weights'].sum()
        self.weights_initial_sum = weights_initial_sum
        print('Initial weights sum: ', weights_initial_sum)

    def set_initial_cvar(self, cvar: int):
        cvar_value = cvar / 252 ** 0.5
        self.cvar_value = cvar_value
        return f'Cvar set in :{cvar}'

    # port.assets_stats(method_mu=self.method_mu, method_cov=self.method_cov, d=0.94)
    def port_optimize(self, returns_train):
        port = rp.Portfolio(returns=returns_train)
        if self.cvar_value is not None:
            try:
                port.upperCVaR = self.cvar_value
            except Exception as e:
                print(e)
        w = port.optimization(
            model=self.model,
            rm=self.rm,
            obj=self.obj,
            rf=self.rf,
            l=self.lib,
            hist=True)
        if self.weights_initial_sum is not None:
            try:
                w['weights'] = w['weights'] * (1 - self.weights_initial_sum)
                self.assets.set_index('assets', inplace=True)
                w = pd.concat([self.assets, w], axis=0)
            except Exception as e:
                print(e)
        return w
    # %%
