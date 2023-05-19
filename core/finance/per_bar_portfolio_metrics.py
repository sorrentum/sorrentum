"""
Import as:

import core.finance.per_bar_portfolio_metrics as cfpbpome
"""
import collections
import logging
from typing import Optional

import numpy as np
import pandas as pd

import helpers.hpandas as hpandas

_LOG = logging.getLogger(__name__)


def compute_bar_metrics(
    notional_positions: pd.DataFrame,
    notional_flows: pd.DataFrame,
    pnl: pd.DataFrame,
    spread: Optional[pd.DataFrame] = None,
    compute_extended_stats: bool = False,
) -> pd.DataFrame:
    """
    Compute core statistics and optionally additional stats.

    The core statistics are:
    - pnl
    - gross volume
    - net volume
    - gmv
    - nmv

    Optional stats include binary position-based versions of a subset of
    core stats:
    - gpc (gross position count: total number of positions on in a bar)
    - npc (net position count: net long/short position count in a bar)
    - wnl (winners and losers: net winning positions in a bar)

    If a spread column is available and `computed_extended_stats=True`,
    then a "tc" column is generated by penalizing transactions (notional_flows) by
    half of the spread.
    """
    # Perform data sanity-checks.
    hpandas.dassert_time_indexed_df(
        notional_positions, allow_empty=True, strictly_increasing=True
    )
    hpandas.dassert_time_indexed_df(
        notional_flows, allow_empty=True, strictly_increasing=True
    )
    hpandas.dassert_time_indexed_df(
        pnl, allow_empty=True, strictly_increasing=True
    )
    hpandas.dassert_axes_equal(notional_positions, pnl)
    hpandas.dassert_axes_equal(notional_flows, pnl)
    if spread is not None:
        hpandas.dassert_time_indexed_df(
            spread, allow_empty=True, strictly_increasing=True
        )
        hpandas.dassert_axes_equal(spread, pnl)
    # Compute "core" stats.
    # Gross market value (gross exposure).
    gmv = notional_positions.abs().sum(axis=1, min_count=1)
    # Net market value (net asset value or net exposure).
    nmv = notional_positions.sum(axis=1, min_count=1)
    # Compute gross and net volume stats.
    traded_volume = -1 * notional_flows
    # Absolute volume traded.
    gross_volume = traded_volume.abs().sum(axis=1, min_count=1)
    # Net volume traded.
    net_volume = traded_volume.sum(axis=1, min_count=1)
    # Aggregated PnL.
    portfolio_pnl = pnl.sum(axis=1, min_count=1)
    stats_dict = collections.OrderedDict(
        {
            "pnl": portfolio_pnl,
            "gross_volume": gross_volume,
            "net_volume": net_volume,
            "gmv": gmv,
            "nmv": nmv,
        }
    )
    if compute_extended_stats:
        # Gross position count.
        gpc = np.sign(notional_positions).abs().sum(axis=1, min_count=1)
        stats_dict["gpc"] = gpc
        # Net position count.
        npc = np.sign(notional_positions).sum(axis=1, min_count=1)
        stats_dict["npc"] = npc
        # Winners and losers.
        wnl = np.sign(pnl).sum(axis=1, min_count=1)
        stats_dict["wnl"] = wnl
        # Compute transaction costs based on notional_flows and half of the quoted
        # spread (the multiplier may be adjusted after the fact if desired).
        if spread is not None:
            tc = 0.5 * notional_flows.abs().multiply(spread).sum(
                axis=1, min_count=1
            )
            stats_dict["tc"] = tc
    stats = pd.DataFrame(stats_dict)
    return stats
