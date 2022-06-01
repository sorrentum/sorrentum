import logging

import numpy as np
import pandas as pd

import core.artificial_signal_generators as carsigen
import core.finance.volatility as cfinvola
import helpers.hpandas as hpandas
import helpers.hunit_test as hunitest

_LOG = logging.getLogger(__name__)


class Test_compute_close_var1(hunitest.TestCase):
    def test1(self) -> None:
        data = get_data()
        close_col = "close"
        variance = cfinvola.compute_close_var(data, close_col)
        actual = get_square_root_as_str(variance)
        expected = r"""
                           volatility
2022-01-10 09:45:00-05:00         NaN
2022-01-10 10:00:00-05:00     0.00444
2022-01-10 10:15:00-05:00     0.00028
2022-01-10 10:30:00-05:00     0.00481
2022-01-10 10:45:00-05:00     0.00596
2022-01-10 11:00:00-05:00     0.00313
2022-01-10 11:15:00-05:00     0.00211
2022-01-10 11:30:00-05:00     0.00345
2022-01-10 11:45:00-05:00     0.00874
2022-01-10 12:00:00-05:00     0.00131
2022-01-10 12:15:00-05:00     0.00701
2022-01-10 12:30:00-05:00     0.01230
2022-01-10 12:45:00-05:00     0.00430
2022-01-10 13:00:00-05:00     0.00048
2022-01-10 13:15:00-05:00     0.00247
2022-01-10 13:30:00-05:00     0.00175
2022-01-10 13:45:00-05:00     0.00406
2022-01-10 14:00:00-05:00     0.00212
2022-01-10 14:15:00-05:00     0.00743
2022-01-10 14:30:00-05:00     0.00342
2022-01-10 14:45:00-05:00     0.00500
2022-01-10 15:00:00-05:00     0.00132
2022-01-10 15:15:00-05:00     0.00342
2022-01-10 15:30:00-05:00     0.00362
2022-01-10 15:45:00-05:00     0.00220
2022-01-10 16:00:00-05:00     0.00319"""
        self.assert_equal(actual, expected, fuzzy_match=True)


class Test_compute_parkinson_var1(hunitest.TestCase):
    def test1(self) -> None:
        data = get_data()
        high_col = "high"
        low_col = "low"
        variance = cfinvola.compute_parkinson_var(data, high_col, low_col)
        actual = get_square_root_as_str(variance)
        expected = r"""
                           volatility
2022-01-10 09:45:00-05:00     0.00203
2022-01-10 10:00:00-05:00     0.00375
2022-01-10 10:15:00-05:00     0.00161
2022-01-10 10:30:00-05:00     0.00369
2022-01-10 10:45:00-05:00     0.00337
2022-01-10 11:00:00-05:00     0.00170
2022-01-10 11:15:00-05:00     0.00258
2022-01-10 11:30:00-05:00     0.00226
2022-01-10 11:45:00-05:00     0.00623
2022-01-10 12:00:00-05:00     0.00183
2022-01-10 12:15:00-05:00     0.00268
2022-01-10 12:30:00-05:00     0.00742
2022-01-10 12:45:00-05:00     0.00515
2022-01-10 13:00:00-05:00     0.00121
2022-01-10 13:15:00-05:00     0.00244
2022-01-10 13:30:00-05:00     0.00171
2022-01-10 13:45:00-05:00     0.00326
2022-01-10 14:00:00-05:00     0.00151
2022-01-10 14:15:00-05:00     0.00492
2022-01-10 14:30:00-05:00     0.00277
2022-01-10 14:45:00-05:00     0.00367
2022-01-10 15:00:00-05:00     0.00193
2022-01-10 15:15:00-05:00     0.00285
2022-01-10 15:30:00-05:00     0.00285
2022-01-10 15:45:00-05:00     0.00176
2022-01-10 16:00:00-05:00     0.00176"""
        self.assert_equal(actual, expected, fuzzy_match=True)


class Test_compute_garman_klass_var1(hunitest.TestCase):
    def test1(self) -> None:
        data = get_data()
        open_col = "open"
        high_col = "high"
        low_col = "low"
        close_col = "close"
        variance = cfinvola.compute_garman_klass_var(
            data, open_col, high_col, low_col, close_col
        )
        actual = get_square_root_as_str(variance)
        expected = r"""
                           volatility
2022-01-10 09:45:00-05:00     0.00178
2022-01-10 10:00:00-05:00     0.00390
2022-01-10 10:15:00-05:00     0.00190
2022-01-10 10:30:00-05:00     0.00228
2022-01-10 10:45:00-05:00     0.00250
2022-01-10 11:00:00-05:00     0.00169
2022-01-10 11:15:00-05:00     0.00252
2022-01-10 11:30:00-05:00     0.00218
2022-01-10 11:45:00-05:00     0.00350
2022-01-10 12:00:00-05:00     0.00216
2022-01-10 12:15:00-05:00     0.00151
2022-01-10 12:30:00-05:00     0.00502
2022-01-10 12:45:00-05:00     0.00432
2022-01-10 13:00:00-05:00     0.00142
2022-01-10 13:15:00-05:00     0.00222
2022-01-10 13:30:00-05:00     0.00197
2022-01-10 13:45:00-05:00     0.00268
2022-01-10 14:00:00-05:00     0.00099
2022-01-10 14:15:00-05:00     0.00375
2022-01-10 14:30:00-05:00     0.00218
2022-01-10 14:45:00-05:00     0.00277
2022-01-10 15:00:00-05:00     0.00224
2022-01-10 15:15:00-05:00     0.00160
2022-01-10 15:30:00-05:00     0.00296
2022-01-10 15:45:00-05:00     0.00202
2022-01-10 16:00:00-05:00     0.00189"""
        self.assert_equal(actual, expected, fuzzy_match=True)


def get_square_root_as_str(df: pd.DataFrame) -> pd.DataFrame:
    precision = 5
    srs = df.squeeze()
    srs.name = "volatility"
    square_root = np.sqrt(srs)
    str_df = hpandas.df_to_str(
        square_root.round(precision),
        num_rows=None,
        precision=precision,
    )
    return str_df


def get_data() -> pd.DataFrame:
    price_process = carsigen.PriceProcess(seed=10)
    prices = price_process.generate_price_series_from_normal_log_returns(
        start_datetime=pd.Timestamp("2022-01-10 09:31:00", tz="America/New_York"),
        end_datetime=pd.Timestamp("2022-01-10 15:59:00", tz="America/New_York"),
        asset_id=100,
        bar_volatility_in_bps=10,
    )
    ohlc = prices.resample("15T", label="right", closed="right").ohlc().round(2)
    _LOG.debug("ohlc=\n%s", hpandas.df_to_str(ohlc, num_rows=None))
    return ohlc
