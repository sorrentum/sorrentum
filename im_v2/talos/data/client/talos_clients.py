"""
Import as:

import im_v2.talos.data.client.talos_clients as imvtdctacl
"""

import abc
import logging
import os
from typing import Any, List, Optional

import pandas as pd

import core.pandas_helpers as cpanh
import helpers.hdatetime as hdateti
import helpers.hdbg as hdbg
import helpers.hparquet as hparque
import helpers.hs3 as hs3
import helpers.hsql as hsql
import im_v2.common.data.client as icdc

_LOG = logging.getLogger(__name__)


# #############################################################################
# TalosClient
# #############################################################################


class TalosClient(icdc.ImClient, abc.ABC):
    """
    Contain common code for all the `Talos` clients, e.g.,

    - getting `Talos` universe
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        vendor = "talos"
        super().__init__(vendor)

    def get_universe(self) -> List[icdc.FullSymbol]:
        """
        See description in the parent class.
        """
        # TODO(Dan): CmTask1318.
        return []


# #############################################################################
# TalosParquetByAssetClient
# #############################################################################


class TalosParquetByAssetClient(
    TalosClient, icdc.ImClientReadingOneSymbol
):
    """
    Read data from a Parquet file storing data for a single `Talos` asset.

    It can read data from local or S3 filesystem as backend.
    """

    def __init__(
        self,
        root_dir: str,
        *,
        aws_profile: Optional[str] = None,
    ) -> None:
        """
        Load `Talos` data from local or S3 filesystem.

        :param root_dir: either a local root path (e.g., "/app/im") or
            an S3 root path (e.g., "s3://cryptokaizen-data/historical") to `Talos` data
        :param aws_profile: AWS profile name (e.g., "ck")
        """
        super().__init__()
        self._root_dir = root_dir
        self._aws_profile = aws_profile

    def get_metadata(self) -> pd.DataFrame:
        """
        See description in the parent class.
        """
        raise NotImplementedError

    def _read_data_for_one_symbol(
        self,
        full_symbol: icdc.FullSymbol,
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        See the `_read_data_for_one_symbol()` in the parent class.
        """
        # Split full symbol into exchange and currency pair.
        exchange_id, currency_pair = icdc.parse_full_symbol(full_symbol)
        # Get path to a dir with all the data for specified exchange id.
        exchange_dir_path = os.path.join(self._root_dir, exchange_id)
        # Read raw crypto price data.
        _LOG.info(
            "Reading data for `Talos`, exchange id='%s', currencies='%s'...",
            exchange_id,
            currency_pair,
        )
        # Initialize list of filters.
        filters = [("currency_pair", "==", currency_pair)]
        if start_ts:
            # Add filtering by start timestamp if specified.
            start_ts = hdateti.convert_timestamp_to_unix_epoch(start_ts)
            filters.append(("timestamp", ">=", start_ts))
        if end_ts:
            # Add filtering by end timestamp if specified.
            end_ts = hdateti.convert_timestamp_to_unix_epoch(end_ts)
            filters.append(("timestamp", "<=", end_ts))
        if filters:
            # Add filters to kwargs if any were set.
            kwargs["filters"] = filters
        # Specify column names to load.
        columns = ["open", "high", "low", "close", "volume"]
        # Load data.
        data = hparque.from_parquet(
            exchange_dir_path,
            columns=columns,
            filters=filters,
            aws_profile=self._aws_profile,
        )
        data.index.name = None
        return data
