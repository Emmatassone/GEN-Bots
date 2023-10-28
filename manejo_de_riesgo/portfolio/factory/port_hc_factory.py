import riskfolio as rp
import warnings
import pandas as pd

warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:.4%}'.format


# Building the portfolio object
class PortfolioOptimizer:
    """
    This class is used to optimize the portfolio using the risk-folio library and the HRP model
    """

    def __init__(self):
        self.weights_initial_sum = None
        self.assets = None
        self.cvar_value = None

    # Parameters
    model = 'HRP'  # Could be HRP or HERC
    codependency = 'pearson'  # Correlation matrix used to group assets in clusters
    rm = 'MV'  # Risk measure used, this time will be variance
    rf = 0  # Risk-free rate
    linkage = 'single'  # Linkage method used to build clusters
    max_k = 10  # Max number of clusters used in two different gap statistics, only for the HERC model
    leaf_order = True  # Consider the optimal order of leafs in the dendrogram

    def set_initial_cvar(self, cvar: int):
        cvar_value = cvar / 252 ** 0.5
        self.cvar_value = cvar_value
        return f'Cvar set in :{cvar}'

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

    def port_optimize(self, returns_train) -> pd.DataFrame:
        """
        :rtype: Pd.DataFrame(weights)
        """
        port = rp.HCPortfolio(returns=returns_train)
        w = port.optimization(
            model=self.model,
            codependence=self.codependency,
            rm=self.rm,
            rf=self.rf,
            linkage=self.linkage,
            max_k=self.max_k,
            leaf_order=self.leaf_order
        )
        if self.weights_initial_sum is not None:
            w['weights'] = w['weights'] * (1 - self.weights_initial_sum)
            self.assets.set_index('assets', inplace=True)
            w = pd.concat([self.assets, w], axis=0)
        return w
