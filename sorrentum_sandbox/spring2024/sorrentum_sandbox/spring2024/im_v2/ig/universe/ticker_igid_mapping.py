"""
Import as:

import im_v2.ig.universe.ticker_igid_mapping as imviutigma
"""

import datetime
import logging
import os
from typing import List

import pandas as pd
import pyarrow.parquet as parquet
import s3fs

import helpers.hdbg as hdbg
import im_v2.ig.data.client.historical_bars as imvidchiba
import im_v2.ig.ig_utils as imvigigut

_LOG = logging.getLogger(__name__)


def get_id_mapping(
    date: imvigigut.IgDate,
    root_data_dir: str,
) -> pd.DataFrame:
    """
    Get dataframe with unique "ticker" and "igid" pairs as of `date`.

    :param date:
    :param root_data_dir:
    """
    # TODO(gp): Maybe factor out as `is_valid_ig_date()`.
    hdbg.dassert_isinstance(date, str)
    hdbg.dassert_eq(len(date), 8, msg="Expected format is str YYYYMMDD")
    # Build the path.
    path = os.path.join(root_data_dir, date, "data.parquet")
    filesystem = (
        s3fs.S3FileSystem() if root_data_dir.startswith("s3://") else None
    )
    dataset = parquet.ParquetDataset(
        path,
        filesystem=filesystem,
    )
    table = dataset.read(columns=["ticker", "igid", "volume"])
    # TODO(gp): Print how many where dropped. Maybe we should have a dropna()
    #  function that always report the stats.
    df = table.to_pandas().dropna(subset=["igid"])
    # TODO(gp): Why sum? Maybe just to "merge" groups of 1.
    df = df.groupby(["ticker", "igid"], as_index=False).sum()
    df["igid"] = df["igid"].astype(int)
    return df


def rank_igid_by_traded_notional(date: datetime.date) -> pd.DataFrame:
    """
    Return data about igids for a single date ranked by traded notional.

    :param date:
    """
    # Get the data for an entire day.
    igids = None
    dates = [date]
    columns = ["close", "volume", "ticker"]
    df = imvidchiba.get_bar_data(igids, dates, columns=columns)
    # Accumulate data for the day.
    volume = df.groupby("igid")[["volume"]].sum()
    price = df.groupby("igid")[["close"]].mean()
    ticker_map = df.groupby("igid")[["ticker"]].first()
    # Compute the notional.
    df_tmp = pd.concat([volume, price, ticker_map], axis=1)
    df_tmp["notional"] = df_tmp["volume"] * df_tmp["close"]
    _LOG.debug("df_tmp=\n%s", df_tmp.head(3))
    # Sort.
    igid_by_trading_vol = df_tmp.sort_values(by="notional", ascending=False)
    return igid_by_trading_vol


# #############################################################################


def read_top_assets() -> List[int]:
    """
    Read the data generated by `rank_igid_by_traded_notional()` on 2020-06-01.

    That data was picked randomly.
    """
    # TODO(gp): Move to S3.
    file_name = "/cache/top_100_by_trading_volume.csv"
    df = pd.read_csv(file_name, index_col=0)
    _LOG.debug("df=\n%s", df.head(3))
    igids = [int(d) for d in df.index.tolist()]
    return igids
