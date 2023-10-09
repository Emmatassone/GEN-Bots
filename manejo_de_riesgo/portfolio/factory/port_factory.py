import pandas as pd
import riskfolio as rp
import warnings

warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:.4%}'.format


# Building the portfolio object
class PortfolioOptimizer:
    def __init__(self):
        pass

    # Parameters
    model = 'HRP'  # Could be HRP or HERC
    codependency = 'pearson'  # Correlation matrix used to group assets in clusters
    rm = 'MV'  # Risk measure used, this time will be variance
    rf = 0  # Risk-free rate
    linkage = 'single'  # Linkage method used to build clusters
    max_k = 10  # Max number of clusters used in two different gap statistics, only for the HERC model
    leaf_order = True  # Consider the optimal order of leafs in the dendrogram

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
        return w



# %%
