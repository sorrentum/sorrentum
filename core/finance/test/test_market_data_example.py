import logging

import pandas as pd

import core.finance.market_data_example as cfmadaex
import helpers.hobject as hobject
import helpers.hpandas as hpandas
import helpers.hunit_test as hunitest
import market_data.market_data_example as mdmadaex

_LOG = logging.getLogger(__name__)


# #############################################################################
# Test_generate_random_bars
# #############################################################################


class Test_generate_random_bars(hunitest.TestCase):
    def test1(self) -> None:
        start_datetime = pd.Timestamp(
            "2000-01-03 09:30:00", tz="America/New_York"
        )
        end_datetime = pd.Timestamp("2000-01-03 09:40:00", tz="America/New_York")
        asset_ids = [100, 200]
        seed = 10
        df = cfmadaex.generate_random_bars(
            start_datetime, end_datetime, asset_ids, seed=seed
        )
        actual = hpandas.df_to_str(df, num_rows=None)
        expected = r"""
              start_datetime              end_datetime              timestamp_db        close  volume    f1    f2     s1   s2  asset_id
0  2000-01-03 09:30:00-05:00 2000-01-03 09:31:00-05:00 2000-01-03 09:31:10-05:00   998.897270    1034  1968  1994   1.96   98       100
1  2000-01-03 09:30:00-05:00 2000-01-03 09:31:00-05:00 2000-01-03 09:31:10-05:00  1000.034193     988  1925  2052   1.92   96       200
2  2000-01-03 09:31:00-05:00 2000-01-03 09:32:00-05:00 2000-01-03 09:32:10-05:00   998.173307    1007  1944  2010   3.06  110       100
3  2000-01-03 09:31:00-05:00 2000-01-03 09:32:00-05:00 2000-01-03 09:32:10-05:00  1001.394912    1015  1991  1975   2.84   92       200
4  2000-01-03 09:32:00-05:00 2000-01-03 09:33:00-05:00 2000-01-03 09:33:10-05:00   997.393235     962  1985  1969   4.98   96       100
5  2000-01-03 09:32:00-05:00 2000-01-03 09:33:00-05:00 2000-01-03 09:33:10-05:00  1002.622093     960  2023  1928   7.00  104       200
6  2000-01-03 09:33:00-05:00 2000-01-03 09:34:00-05:00 2000-01-03 09:34:10-05:00   997.659551     961  2050  1916   7.20  111       100
7  2000-01-03 09:33:00-05:00 2000-01-03 09:34:00-05:00 2000-01-03 09:34:10-05:00  1002.110578    1016  2068  1996   8.00  100       200
8  2000-01-03 09:34:00-05:00 2000-01-03 09:35:00-05:00 2000-01-03 09:35:10-05:00   997.411583     973  1979  2061   9.04   92       100
9  2000-01-03 09:34:00-05:00 2000-01-03 09:35:00-05:00 2000-01-03 09:35:10-05:00  1001.812025    1032  1868  2032   8.00  103       200
10 2000-01-03 09:35:00-05:00 2000-01-03 09:36:00-05:00 2000-01-03 09:36:10-05:00   997.537746    1002  1995  2049  10.88   92       100
11 2000-01-03 09:35:00-05:00 2000-01-03 09:36:00-05:00 2000-01-03 09:36:10-05:00  1001.283824    1005  1980  1911   8.74   74       200
12 2000-01-03 09:36:00-05:00 2000-01-03 09:37:00-05:00 2000-01-03 09:37:10-05:00   998.379068     979  2009  2002  13.42  127       100
13 2000-01-03 09:36:00-05:00 2000-01-03 09:37:00-05:00 2000-01-03 09:37:10-05:00  1001.854444     986  2070  2066  13.84  102       200
14 2000-01-03 09:37:00-05:00 2000-01-03 09:38:00-05:00 2000-01-03 09:38:10-05:00   999.235981     985  2017  1956  15.40   99       100
15 2000-01-03 09:37:00-05:00 2000-01-03 09:38:00-05:00 2000-01-03 09:38:10-05:00  1001.798277     974  1979  2043  15.74   95       200
16 2000-01-03 09:38:00-05:00 2000-01-03 09:39:00-05:00 2000-01-03 09:39:10-05:00   999.710914     963  1963  1970  15.40   97       100
17 2000-01-03 09:38:00-05:00 2000-01-03 09:39:00-05:00 2000-01-03 09:39:10-05:00  1002.546786    1040  1995  1929  16.70   96       200
18 2000-01-03 09:39:00-05:00 2000-01-03 09:40:00-05:00 2000-01-03 09:40:10-05:00   999.260378    1041  2051  2023  17.36   98       100
19 2000-01-03 09:39:00-05:00 2000-01-03 09:40:00-05:00 2000-01-03 09:40:10-05:00  1000.696466     997  1904  1972  19.52   94       200
"""
        self.assert_equal(actual, expected, fuzzy_match=True)


# #############################################################################
# Test_generate_random_ohlcv_bars
# #############################################################################


class Test_generate_random_ohlcv_bars(hunitest.TestCase):
    def test1(self) -> None:
        start_datetime = pd.Timestamp(
            "2000-01-03 09:30:00", tz="America/New_York"
        )
        end_datetime = pd.Timestamp("2000-01-03 12:00", tz="America/New_York")
        asset_ids = [100, 200]
        bar_duration = "15T"
        seed = 10
        df = cfmadaex.generate_random_ohlcv_bars(
            start_datetime,
            end_datetime,
            asset_ids,
            bar_duration=bar_duration,
            seed=seed,
        )
        actual = hpandas.df_to_str(df, num_rows=None)
        expected = r"""
              start_datetime              end_datetime              timestamp_db     open     high      low    close  volume  asset_id
0  2000-01-03 09:30:00-05:00 2000-01-03 09:45:00-05:00 2000-01-03 09:45:10-05:00   999.78   999.94   999.26   999.26     983       100
1  2000-01-03 09:30:00-05:00 2000-01-03 09:45:00-05:00 2000-01-03 09:45:10-05:00  1000.01  1000.57  1000.01  1000.47    1029       200
2  2000-01-03 09:45:00-05:00 2000-01-03 10:00:00-05:00 2000-01-03 10:00:10-05:00   999.04   999.10   997.85   998.38    1004       100
3  2000-01-03 09:45:00-05:00 2000-01-03 10:00:00-05:00 2000-01-03 10:00:10-05:00  1000.56  1000.79   999.08   999.09    1010       200
4  2000-01-03 10:00:00-05:00 2000-01-03 10:15:00-05:00 2000-01-03 10:15:10-05:00   998.33   998.50   997.96   998.32     992       100
5  2000-01-03 10:00:00-05:00 2000-01-03 10:15:00-05:00 2000-01-03 10:15:10-05:00   999.27   999.68   999.07   999.30     949       200
6  2000-01-03 10:15:00-05:00 2000-01-03 10:30:00-05:00 2000-01-03 10:30:10-05:00   998.55   998.59   997.36   997.36     965       100
7  2000-01-03 10:15:00-05:00 2000-01-03 10:30:00-05:00 2000-01-03 10:30:10-05:00   999.13   999.60   998.76   999.30    1024       200
8  2000-01-03 10:30:00-05:00 2000-01-03 10:45:00-05:00 2000-01-03 10:45:10-05:00   997.16   997.16   996.05   996.17    1007       100
9  2000-01-03 10:30:00-05:00 2000-01-03 10:45:00-05:00 2000-01-03 10:45:10-05:00   999.25   999.98   999.20   999.98     984       200
10 2000-01-03 10:45:00-05:00 2000-01-03 11:00:00-05:00 2000-01-03 11:00:10-05:00   995.89   995.94   995.38   995.55    1072       100
11 2000-01-03 10:45:00-05:00 2000-01-03 11:00:00-05:00 2000-01-03 11:00:10-05:00  1000.34  1000.44   999.80  1000.15     939       200
12 2000-01-03 11:00:00-05:00 2000-01-03 11:15:00-05:00 2000-01-03 11:15:10-05:00   995.43   996.29   995.43   995.97     975       100
13 2000-01-03 11:00:00-05:00 2000-01-03 11:15:00-05:00 2000-01-03 11:15:10-05:00  1000.56  1000.63  1000.09  1000.42     982       200
14 2000-01-03 11:15:00-05:00 2000-01-03 11:30:00-05:00 2000-01-03 11:30:10-05:00   996.17   996.69   995.94   996.66     969       100
15 2000-01-03 11:15:00-05:00 2000-01-03 11:30:00-05:00 2000-01-03 11:30:10-05:00  1000.17  1001.19   999.98  1000.89    1041       200
16 2000-01-03 11:30:00-05:00 2000-01-03 11:45:00-05:00 2000-01-03 11:45:10-05:00   996.98   996.98   994.92   994.92     987       100
17 2000-01-03 11:30:00-05:00 2000-01-03 11:45:00-05:00 2000-01-03 11:45:10-05:00  1001.01  1001.17  1000.43  1000.59     986       200
18 2000-01-03 11:45:00-05:00 2000-01-03 12:00:00-05:00 2000-01-03 12:00:10-05:00   994.68   994.82   994.21   994.66    1009       100
19 2000-01-03 11:45:00-05:00 2000-01-03 12:00:00-05:00 2000-01-03 12:00:10-05:00  1000.70  1001.33  1000.15  1000.15    1044       200
"""
        self.assert_equal(actual, expected, fuzzy_match=True)


# #############################################################################
# Test_MarketData_builders1
# #############################################################################


class Test_MarketData_builders1(hunitest.TestCase):
    def test1(self) -> None:
        event_loop = None
        market_data, _ = mdmadaex.get_ReplayedTimeMarketData_example3(event_loop)
        #
        hobject.test_object_signature(self, market_data)
