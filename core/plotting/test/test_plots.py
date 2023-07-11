import logging
import unittest

import numpy as np
import pandas as pd

import core.plotting.visual_stationarity_test as cpvistte

_LOG = logging.getLogger(__name__)


class Test_plots(unittest.TestCase):
    @staticmethod
    def test_plot_histograms_and_lagged_scatterplot1() -> None:
        """
        Smoke test for `plot_histograms_and_lagged_scatterplot()`.
        """
        # Set inputs.
        rng = np.random.default_rng(seed=0)
        samples = rng.normal(size=100)
        index = pd.date_range(start="2023-01-01", periods=len(samples), freq="D")
        srs = pd.Series(samples, index=index)
        lag = 7
        # TODO(Dan): Remove after integration with `cmamp`
        figsize = (20, 20)
        # Plot.
        cpvistte.plot_histograms_and_lagged_scatterplot(srs, lag, figsize=figsize)
