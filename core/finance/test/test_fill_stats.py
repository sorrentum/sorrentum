import logging

import pandas as pd
import pytz

import core.finance.target_position_df_processing.fill_stats as cftpdpfst
import helpers.hunit_test as hunitest

_LOG = logging.getLogger(__name__)


class Test_compute_fill_stats(hunitest.TestCase):
    def helper(self) -> pd.DataFrame:
        """
        Create artificial target positions data for unit tests.
        """
        data = {
            ("holdings_notional", 1): [1000, 1200, 1100, 1300, 1400],
            ("holdings_notional", 2): [800, 850, 870, 900, 950],
            ("holdings_shares", 1): [10, 12, 11, 13, 14],
            ("holdings_shares", 2): [8, 9, 8.5, 9.5, 10],
            ("price", 1): [100, 105, 102, 108, 110],
            ("price", 2): [50, 52, 51, 53, 54],
            ("target_holdings_notional", 1): [950, 1150, 1050, 1250, 1350],
            ("target_holdings_notional", 2): [780, 830, 850, 880, 930],
            ("target_holdings_shares", 1): [9, 11, 10, 12, 13],
            ("target_holdings_shares", 2): [7.5, 8.5, 8.2, 9.2, 9.5],
            ("target_trades_shares", 1): [1, 2, -1, 2, 1],
            ("target_trades_shares", 2): [0.5, 1, -0.3, 0.7, 0.5],
        }
        index = pd.date_range(
            start="2023-01-01", periods=5, freq="T", tz=pytz.UTC
        )
        columns = pd.MultiIndex.from_tuples(data.keys())
        df = pd.DataFrame(data, index=index, columns=columns)
        return df

    def test_compute_fill_stats1(self) -> None:
        """
        Check that fills are computed correctly.
        """
        # Get target positions data sample.
        target_position_df = self.helper()
        fills_df = cftpdpfst.compute_fill_stats(target_position_df)
        # Define expected values.
        expected_length = 5
        expected_column_names = [
            ("executed_trades_shares", 1),
            ("executed_trades_shares", 2),
            ("fill_rate", 1),
            ("fill_rate", 2),
            ("underfill_share_count", 1),
            ("underfill_share_count", 2),
            ("underfill_notional", 1),
            ("underfill_notional", 2),
            ("underfill_opportunity_cost_realized_notional", 1),
            ("underfill_opportunity_cost_realized_notional", 2),
            ("underfill_opportunity_cost_notional", 1),
            ("underfill_opportunity_cost_notional", 2),
            ("tracking_error_shares", 1),
            ("tracking_error_shares", 2),
            ("tracking_error_notional", 1),
            ("tracking_error_notional", 2),
            ("tracking_error_bps", 1),
            ("tracking_error_bps", 2),
            ("is_buy", 1),
            ("is_buy", 2),
            ("is_sell", 1),
            ("is_sell", 2),
            ("is_benchmark_profitable", 1),
            ("is_benchmark_profitable", 2),
        ]
        expected_column_unique_values = None
        expected_signature = r"""
        # df=
        index=[2023-01-01 00:00:00+00:00, 2023-01-01 00:04:00+00:00]
        columns=('executed_trades_shares', 1),('executed_trades_shares', 2),('fill_rate', 1),('fill_rate', 2),('underfill_share_count', 1),('underfill_share_count', 2),('underfill_notional', 1),('underfill_notional', 2),('underfill_opportunity_cost_realized_notional', 1),('underfill_opportunity_cost_realized_notional', 2),('underfill_opportunity_cost_notional', 1),('underfill_opportunity_cost_notional', 2),('tracking_error_shares', 1),('tracking_error_shares', 2),('tracking_error_notional', 1),('tracking_error_notional', 2),('tracking_error_bps', 1),('tracking_error_bps', 2),('is_buy', 1),('is_buy', 2),('is_sell', 1),('is_sell', 2),('is_benchmark_profitable', 1),('is_benchmark_profitable', 2)
        shape=(5, 24)
                                executed_trades_shares      fill_rate           underfill_share_count      underfill_notional       underfill_opportunity_cost_realized_notional      underfill_opportunity_cost_notional      tracking_error_shares      tracking_error_notional       tracking_error_bps             is_buy        is_sell        is_benchmark_profitable
                                                    1    2         1         2                     1    2                  1     2                                            1    2                                   1    2                     1    2                       1     2                  1           2      1      2       1      2                       1    2
        2023-01-01 00:00:00+00:00                   10.0  8.0       NaN       NaN                   NaN  NaN                NaN   NaN                                          NaN  NaN                                 NaN  NaN                   NaN  NaN                     NaN   NaN                NaN         NaN   True   True   False  False                     1.0  1.0
        2023-01-01 00:01:00+00:00                    2.0  1.0       2.0  2.000000                  -1.0 -0.5             -100.0 -25.0                                          NaN  NaN                                 3.0  0.5                   3.0  1.5                   250.0  70.0        2631.578947  897.435897   True   True   False  False                    -1.0 -1.0
        2023-01-01 00:02:00+00:00                   -1.0 -0.5       0.5  0.500000                   1.0  0.5              105.0  26.0                                          3.0  0.5                                 6.0  1.0                   0.0  0.0                   -50.0  40.0        -434.782609  481.927711  False  False    True   True                    -1.0 -1.0
        2023-01-01 00:03:00+00:00                    2.0  1.0       2.0  3.333333                  -1.0 -0.7             -102.0 -35.7                                          6.0  1.0                                 2.0  0.7                   3.0  1.3                   250.0  50.0        2380.952381  588.235294   True   True   False  False                     1.0  1.0
        2023-01-01 00:04:00+00:00                    1.0  0.5       0.5  0.714286                   1.0  0.2              108.0  10.6                                          2.0  0.7                                 NaN  NaN                   2.0  0.8                   150.0  70.0        1200.000000  795.454545   True   True   False  False                     NaN  NaN
        """
        self.check_df_output(
            fills_df,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )
