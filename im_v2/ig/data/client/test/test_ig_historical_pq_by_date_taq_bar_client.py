import logging
from typing import Any, Dict

import pandas as pd
import pytest

import helpers.hpandas as hpandas
import helpers.hunit_test as hunitest
import im_v2.ig.data.client.ig_historical_pq_by_date_taq_bar_client as imvidcihpbdtbc

_LOG = logging.getLogger(__name__)


# TODO(gp): Use ImClientTestCase.
# @pytest.mark.skip(
#     reason="Fix after CmTask2053_Add_a_proxy_for_the_ImClients_in_equities_and_futures"
# )
class TestIgHistoricalPqByDateTaqBarClient1(hunitest.TestCase):
    def read_data_helper(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        # Execute.
        im_client = imvidcihpbdtbc.IgHistoricalPqByDateTaqBarClient()
        actual = im_client.read_data(*args, **kwargs)
        # Check the output values.
        actual_string = hpandas.df_to_str(actual, print_shape_info=True, tag="df")
        _LOG.debug("actual_string=%s", actual_string)
        self.check_string(actual_string)

    def test_read_data1(self) -> None:
        """
        - Read data for one symbol
        - With normalization
        """
        full_symbols = ["17085"]
        start_ts = pd.Timestamp("2021-12-27 9:00:00-05:00")
        end_ts = pd.Timestamp("2021-12-27 16:00:00-05:00")
        columns = ["end_time", "ticker", "igid", "close"]
        aws_profile = None
        root_data_dir = ""
        filter_data_mode = "assert"
        # Execute.
        self.read_data_helper(
            full_symbols,
            start_ts,
            end_ts,
            columns,
            filter_data_mode,
        )

    def test_read_data2(self) -> None:
        """
        - Read data for two symbols
        - With normalization
        """
        full_symbols = ["17085", "13684"]
        start_ts = pd.Timestamp("2021-12-23 9:00:00-05:00")
        end_ts = pd.Timestamp("2021-12-23 10:00:00-05:00")
        columns = ["end_time", "ticker", "igid", "close", "open"]
        filter_data_mode = "assert"
        # Execute.
        self.read_data_helper(
            full_symbols,
            start_ts=start_ts,
            end_ts=end_ts,
            columns=columns,
            filter_data_mode=filter_data_mode,
        )
