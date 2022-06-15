"""
Import as:

import dataflow.model.forecast_evaluator_from_prices as dtfmfefrpr
"""
import collections
import logging
import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

import core.config as cconfig
import core.finance as cofinanc
import helpers.hdbg as hdbg
import helpers.hio as hio
import helpers.hpandas as hpandas

_LOG = logging.getLogger(__name__)


class ForecastEvaluatorFromPrices:
    """
    Evaluate returns/volatility forecasts.
    """

    def __init__(
        self,
        price_col: str,
        volatility_col: str,
        prediction_col: str,
        spread_col: Optional[str] = None,
        buy_price_col: Optional[str] = None,
        sell_price_col: Optional[str] = None,
    ) -> None:
        """
        Initialize column names.

        Note:
        - the `price_col` is unadjusted price (no adjustment for splits,
          dividends, or volatility); it is used for marking to market and,
          unless buy/sell prices columns are also supplied, execution
          simulation
        - the `volatility_col` is used for position sizing
        - the `prediction_col` is a prediction of vol-adjusted returns
          (presumably with volatility given by `volatility_col`)

        :param price_col: price per share
        :param volatility_col: volatility used for adjustment of forward returns
        :param prediction_col: prediction of volatility-adjusted returns, two
            steps ahead
        """
        # Initialize dataframe columns.
        hdbg.dassert_isinstance(price_col, str)
        self._price_col = price_col
        hdbg.dassert_isinstance(volatility_col, str)
        self._volatility_col = volatility_col
        hdbg.dassert_isinstance(prediction_col, str)
        self._prediction_col = prediction_col
        # Process optional columns.
        if spread_col is not None:
            hdbg.dassert_isinstance(spread_col, str)
            _LOG.debug("Initialized with spread_col=%s", spread_col)
        self._spread_col = spread_col
        if buy_price_col is not None:
            hdbg.dassert_isinstance(buy_price_col, str)
            # If `buy_price_col` is not `None`, then `sell_price_col` must also
            # not be `None`.
            hdbg.dassert_isinstance(sell_price_col, str)
            _LOG.debug("Initialized with buy_price_col=%s", buy_price_col)
        self._buy_price_col = buy_price_col
        if sell_price_col is not None:
            hdbg.dassert_isinstance(sell_price_col, str)
            # If `sell_price_col` is not `None`, then `buy_price_col` must also
            # not be `None`.
            hdbg.dassert_isinstance(buy_price_col, str)
            _LOG.debug("Initialized with sell_price_col=%s", sell_price_col)
        self._sell_price_col = sell_price_col

    @staticmethod
    def read_portfolio(
        log_dir: str,
        *,
        file_name: Optional[str] = None,
        tz: str = "America/New_York",
        cast_asset_ids_to_int: bool = True,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Read and process logged portfolio.

        :param log_dir: directory for reading log files of portfolio state
        :param file_name: if `None`, find and use the latest
        :param tz: timezone to apply to timestamps (this information is lost in
            the logging/reading round trip)
        :param cast_asset_ids_to_int: cast asset ids from integers-as-strings
            to integers (the data type is lost in the logging/reading round
            trip)
        """
        if file_name is None:
            dir_name = os.path.join(log_dir, "price")
            pattern = "*"
            only_files = True
            use_relative_paths = True
            files = hio.listdir(dir_name, pattern, only_files, use_relative_paths)
            files.sort()
            file_name = files[-1]
            _LOG.info("`file_name`=%s", file_name)
        price = ForecastEvaluatorFromPrices._read_df(
            log_dir, "price", file_name, tz
        )
        volatility = ForecastEvaluatorFromPrices._read_df(
            log_dir, "volatility", file_name, tz
        )
        predictions = ForecastEvaluatorFromPrices._read_df(
            log_dir, "prediction", file_name, tz
        )
        holdings = ForecastEvaluatorFromPrices._read_df(
            log_dir, "holdings", file_name, tz
        )
        positions = ForecastEvaluatorFromPrices._read_df(
            log_dir, "position", file_name, tz
        )
        flows = ForecastEvaluatorFromPrices._read_df(
            log_dir, "flow", file_name, tz
        )
        pnl = ForecastEvaluatorFromPrices._read_df(log_dir, "pnl", file_name, tz)
        if cast_asset_ids_to_int:
            for df in [
                price,
                volatility,
                predictions,
                holdings,
                positions,
                flows,
                pnl,
            ]:
                ForecastEvaluatorFromPrices._cast_cols_to_int(df)
        dfs = {
            "price": price,
            "volatility": volatility,
            "prediction": predictions,
            "holdings": holdings,
            "position": positions,
            "flow": flows,
            "pnl": pnl,
        }
        portfolio_df = ForecastEvaluatorFromPrices._build_multiindex_df(dfs)
        statistics_df = ForecastEvaluatorFromPrices._read_df(
            log_dir, "statistics", file_name, tz
        )
        return portfolio_df, statistics_df

    def to_str(
        self,
        df: pd.DataFrame,
        **kwargs,
    ) -> str:
        """
        Return the state of the Portfolio as a string.

        :param df: as in `compute_portfolio`
        :param kwargs: forwarded to `compute_portfolio()`
        :return: portfolio state (rounded) as a string
        """
        holdings, positions, flows, pnl, stats = self.compute_portfolio(
            df,
            **kwargs,
        )
        act = []
        round_precision = 6
        precision = 2
        act.append(
            "# holdings=\n%s"
            % hpandas.df_to_str(
                holdings.round(round_precision),
                num_rows=None,
                precision=precision,
            )
        )
        act.append(
            "# holdings marked to market=\n%s"
            % hpandas.df_to_str(
                positions.round(round_precision),
                num_rows=None,
                precision=precision,
            )
        )
        act.append(
            "# flows=\n%s"
            % hpandas.df_to_str(
                flows.round(round_precision),
                num_rows=None,
                precision=precision,
            )
        )
        act.append(
            "# pnl=\n%s"
            % hpandas.df_to_str(
                pnl.round(round_precision),
                num_rows=None,
                precision=precision,
            )
        )
        act.append(
            "# statistics=\n%s"
            % hpandas.df_to_str(
                stats.round(round_precision), num_rows=None, precision=precision
            )
        )
        act = "\n".join(act)
        return act

    def log_portfolio(
        self,
        df: pd.DataFrame,
        log_dir: str,
        **kwargs,
    ) -> str:
        """
        Log portfolio state to the file system.

        :param df: as in `compute_portfolio()`
        :param log_dir: directory for writing log files of portfolio state
        :param kwargs: forwarded to `compute_portfolio()`
        :return: name of log files with timestamp
        """
        hdbg.dassert(log_dir, "Must specify `log_dir` to log portfolio.")
        holdings, position, flow, pnl, statistics = self.compute_portfolio(
            df,
            **kwargs,
        )
        last_timestamp = df.index[-1]
        hdbg.dassert_isinstance(last_timestamp, pd.Timestamp)
        last_timestamp_str = last_timestamp.strftime("%Y%m%d_%H%M%S")
        file_name = f"{last_timestamp_str}.csv"
        #
        ForecastEvaluatorFromPrices._write_df(
            df[self._price_col], log_dir, "price", file_name
        )
        ForecastEvaluatorFromPrices._write_df(
            df[self._volatility_col], log_dir, "volatility", file_name
        )
        ForecastEvaluatorFromPrices._write_df(
            df[self._prediction_col], log_dir, "prediction", file_name
        )
        ForecastEvaluatorFromPrices._write_df(
            holdings, log_dir, "holdings", file_name
        )
        ForecastEvaluatorFromPrices._write_df(
            position, log_dir, "position", file_name
        )
        ForecastEvaluatorFromPrices._write_df(flow, log_dir, "flow", file_name)
        ForecastEvaluatorFromPrices._write_df(pnl, log_dir, "pnl", file_name)
        ForecastEvaluatorFromPrices._write_df(
            statistics, log_dir, "statistics", file_name
        )
        return file_name

    def compute_portfolio(
        self,
        df: pd.DataFrame,
        *,
        style: str = "cross_sectional",
        quantization: str = "no_quantization",
        liquidate_at_end_of_day: bool = True,
        reindex_like_input: bool = False,
        burn_in_bars: int = 3,
        burn_in_days: int = 0,
        compute_extended_stats: bool = False,
        **kwargs,
    ) -> Tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ]:
        """
        Compute target positions, PnL, and portfolio stats.

        :param df: multiindexed dataframe with predictions, price, volatility
        :param reindex_like_input: output dataframes to have the same input as
            `df` (e.g., including any weekends or values outside of the
            `start_time`-`end_time` range)
        :param style: belongs to
            - "cross_sectional": cross-sectionally normalize predictions,
              possibly remove a portion of the bulk of the distribution,
              and allocate a target GMV
            - "longitudinal": normalize and threshold predictions
              longitudinally, allocating an equal dollar risk to each name
              independently
        :param quantization: indicate whether to round to nearest share, lot
        :param liquidate_at_end_of_day: force holdings to zero at the last
            trade if true (otherwise hold overnight)
        :param reindex_like_input: if `False`, only return dataframes indexed
            by the inferred "active index" of datetimes
        :param burn_in_bars: number of leading bars to trim (to remove warm-up
            artifacts)
        :param burn_in_days: number of leading days to trim (to remove warm-up
            artifacts). Applied independently of `burn_in_bars`.
        :param compute_extended_stats: compute additional stats beyond the
            five "core" stats.
        :param kwargs: forwarded to either
            `compute_target_positions_cross_sectionally()` or
            `compute_target_positions_longitudinally()` depending upon the
            value of `style`
        :return: (holdings, position, flow, pnl, stats)
        """
        self._validate_df(df)
        # Record index in case we reindex the results.
        if reindex_like_input:
            idx = df.index
        df = self._apply_trimming(df)
        # Extract prediction and volatility dataframes.
        prediction_df = ForecastEvaluatorFromPrices._get_df(
            df, self._prediction_col
        )
        _LOG.debug("prediction_df=\n%s", hpandas.df_to_str(prediction_df))
        volatility_df = ForecastEvaluatorFromPrices._get_df(
            df, self._volatility_col
        )
        _LOG.debug("volatility_df=\n%s", hpandas.df_to_str(volatility_df))
        # Handle `kwargs` as config params for computing target positions.
        if kwargs:
            target_positions_config = cconfig.get_config_from_flattened_dict(
                kwargs
            )
        else:
            target_positions_config = cconfig.Config()
        _LOG.debug("target_positions_config=\n%s", target_positions_config)
        #
        spread_df = None
        if self._spread_col is not None:
            spread_df = ForecastEvaluatorFromPrices._get_df(df, self._spread_col)
        # The values of`target_positions` represent cash values.
        if style == "cross_sectional":
            target_positions = (
                cofinanc.compute_target_positions_cross_sectionally(
                    prediction_df,
                    volatility_df,
                    target_positions_config,
                )
            )
        elif style == "longitudinal":
            target_positions = cofinanc.compute_target_positions_longitudinally(
                prediction_df,
                volatility_df,
                target_positions_config,
                spread_df,
            )
        else:
            raise ValueError("Unsupported `style`=%s", style)
        self._validate_target_position_df(target_positions, prediction_df)
        # Extract price. Use for marking to market and, unless separate
        # execution prices are provided, for estimating execution.
        mark_to_market_price_df = ForecastEvaluatorFromPrices._get_df(
            df, self._price_col
        )
        # Compute holdings.
        # Compute target holdings based on prices available at decision time.
        target_holdings = target_positions.divide(mark_to_market_price_df)
        # Quantize holdings (e.g., nearest share).
        target_holdings = ForecastEvaluatorFromPrices._apply_quantization(
            target_holdings, quantization
        )
        ffill_limit = 4
        ideal_holdings = ForecastEvaluatorFromPrices._compute_ideal_holdings(
            target_holdings,
            mark_to_market_price_df,
            liquidate_at_end_of_day,
            ffill_limit,
        )
        #
        holdings = self._adjust_holdings_for_underfills(
            df, ideal_holdings, mark_to_market_price_df
        )
        # Determine execution prices for buys/sells and holds, based on changes in
        # `target_positions`.
        execution_price_df = self._compute_execution_prices(
            df,
            holdings,
            mark_to_market_price_df,
        )
        flows = self._compute_flows(
            execution_price_df,
            mark_to_market_price_df,
            holdings,
        )
        # Compute current positions in dollars.
        positions = holdings.multiply(mark_to_market_price_df)
        # Compute PnL.
        pnl = positions.subtract(positions.shift(1), fill_value=0).add(
            flows, fill_value=0
        )
        # Compute statistics.
        stats = self._compute_statistics(
            positions, flows, pnl, spread_df, compute_extended_stats
        )
        # Remove initial bars.
        if burn_in_bars > 0:
            holdings = holdings.iloc[burn_in_bars:]
            positions = positions.iloc[burn_in_bars:]
            flows = flows.iloc[burn_in_bars:]
            pnl = pnl.iloc[burn_in_bars:]
            stats = stats.iloc[burn_in_bars:]
        if burn_in_days > 0:
            # TODO(Paul): Consider making this more efficient (and less
            # awkward).
            date_idx = df.groupby(lambda x: x.date()).count().index
            hdbg.dassert_lt(burn_in_days, date_idx.size)
            first_date = pd.Timestamp(date_idx[burn_in_days], tz=df.index.tz)
            _LOG.info("Initial date after burn-in=%s", first_date)
            holdings = holdings.loc[first_date:]
            positions = positions.loc[first_date:]
            flows = flows.loc[first_date:]
            pnl = pnl.loc[first_date:]
            stats = stats.loc[first_date:]
        # Possibly reindex dataframes.
        if reindex_like_input:
            holdings = holdings.reindex(idx)
            positions = positions.reindex(idx)
            flows = flows.reindex(idx)
            pnl = pnl.reindex(idx)
            stats = stats.reindex(idx)
        return holdings, positions, flows, pnl, stats

    def annotate_forecasts(
        self,
        df: pd.DataFrame,
        **kwargs,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Wraps `compute_portfolio()`, returns a single multiindexed dataframe.

        :param df: as in `compute_portfolio()`
        :param kwargs: forwarded to `compute_portfolio()`
        :return: multiindexed dataframe with level-0 columns
            "returns", "volatility", "prediction", "position", "pnl"
        """
        holdings, position, flow, pnl, statistics_df = self.compute_portfolio(
            df,
            **kwargs,
        )
        dfs = {
            "price": df[self._price_col],
            "volatility": df[self._volatility_col],
            "prediction": df[self._prediction_col],
            "holdings": holdings,
            "position": position,
            "flow": flow,
            "pnl": pnl,
        }
        if self._spread_col is not None:
            dfs["spread"] = df[self._spread_col]
        portfolio_df = ForecastEvaluatorFromPrices._build_multiindex_df(dfs)
        return portfolio_df, statistics_df

    def get_cols(self) -> List[str]:
        """
        Return the names of the price, volatility, and prediction columns.
        """
        cols = [
            self._price_col,
            self._volatility_col,
            self._prediction_col,
        ]
        optional_cols = [
            self._spread_col,
            self._buy_price_col,
            self._sell_price_col,
        ]
        for col in optional_cols:
            if col is not None:
                cols = cols + [col]
        return cols

    def compute_counts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute data counts by column grouped by time.
        """
        self._validate_df(df)

        def _compute_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
            return df[col].groupby(lambda x: x.time()).count()

        count_to_col = {
            "price_count": self._price_col,
            "volatility_count": self._price_col,
            "prediction_count": self._price_col,
            "spread_count": self._spread_col,
            "buy_price_count": self._buy_price_col,
            "sell_price_count": self._sell_price_col,
        }
        dfs = collections.OrderedDict()
        for key, value in count_to_col.items():
            if value is not None:
                dfs[key] = _compute_counts(df, value)
        count_df = pd.concat(dfs.values(), axis=1, keys=dfs.keys())
        return count_df

    def _validate_target_position_df(
        self, target_positions: pd.DataFrame, predictions: pd.DataFrame
    ) -> None:
        hpandas.dassert_time_indexed_df(
            target_positions, allow_empty=True, strictly_increasing=True
        )
        hdbg.dassert_eq(target_positions.columns.nlevels, 1)
        hpandas.dassert_columns_equal(target_positions, predictions)
        hpandas.dassert_indices_equal(target_positions, predictions)

    @staticmethod
    def _build_multiindex_df(dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        portfolio_df = pd.concat(dfs.values(), axis=1, keys=dfs.keys())
        return portfolio_df

    @staticmethod
    def _cast_cols_to_int(
        df: pd.DataFrame,
    ) -> None:
        # If integers are converted to floats and then strings, then upon
        # being read they must be cast to floats before being cast to ints.
        df.columns = df.columns.astype("float64").astype("int64")

    @staticmethod
    def _write_df(
        df: pd.DataFrame,
        log_dir: str,
        name: str,
        file_name: str,
    ) -> None:
        path = os.path.join(log_dir, name, file_name)
        hio.create_enclosing_dir(path, incremental=True)
        df.to_csv(path)

    @staticmethod
    def _read_df(
        log_dir: str,
        name: str,
        file_name: str,
        tz: str,
    ) -> pd.DataFrame:
        path = os.path.join(log_dir, name, file_name)
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        df.index = df.index.tz_convert(tz)
        return df

    @staticmethod
    def _apply_quantization(
        holdings: pd.DataFrame,
        quantization: str,
    ) -> pd.DataFrame:
        """
        Keep factional holdings or round to nearest share or lot.
        """
        if quantization == "no_quantization":
            quantized_holdings = holdings
        elif quantization == "nearest_share":
            quantized_holdings = np.rint(holdings)
        elif quantization == "nearest_lot":
            quantized_holdings = 100 * np.rint(holdings / 100)
        else:
            raise ValueError(f"Invalid quantization strategy `{quantization}`")
        _LOG.debug(
            "`quantized_holdings`=\n%s", hpandas.df_to_str(quantized_holdings)
        )
        return quantized_holdings

    @staticmethod
    def _compute_statistics(
        positions: pd.DataFrame,
        flows: pd.DataFrame,
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
        then a "tc" column is generated by penalizing transactions (flows) by
        half of the spread.
        """
        # Gross market value (gross exposure).
        gmv = positions.abs().sum(axis=1, min_count=1)
        # Net market value (net asset value or net exposure).
        nmv = positions.sum(axis=1, min_count=1)
        # Compute gross and net volume stats.
        traded_volume = -1 * flows
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
            gpc = np.sign(positions).abs().sum(axis=1, min_count=1)
            stats_dict["gpc"] = gpc
            # Net position count.
            npc = np.sign(positions).sum(axis=1, min_count=1)
            stats_dict["npc"] = npc
            # Winners and losers.
            wnl = np.sign(pnl).sum(axis=1, min_count=1)
            stats_dict["wnl"] = wnl
            if spread is not None:
                tc = 0.5 * flows.abs().multiply(spread).sum(axis=1, min_count=1)
                stats_dict["tc"] = tc
        stats = pd.DataFrame(stats_dict)
        return stats

    @staticmethod
    def _get_df(df: pd.DataFrame, col: str) -> pd.DataFrame:
        hdbg.dassert_in(col, df.columns)
        return df[col]

    def _validate_df(self, df: pd.DataFrame) -> None:
        hpandas.dassert_time_indexed_df(
            df, allow_empty=True, strictly_increasing=True
        )
        hdbg.dassert_eq(df.columns.nlevels, 2)
        hdbg.dassert_is_subset(
            [self._price_col, self._volatility_col, self._prediction_col],
            df.columns.levels[0].to_list(),
        )

    def _apply_trimming(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Trim `df` according to ATH, weekends, missing data.
        """
        # Restrict to required columns.
        cols = [self._price_col, self._volatility_col, self._prediction_col]
        optional_cols = [
            self._spread_col,
            self._buy_price_col,
            self._sell_price_col,
        ]
        for col in optional_cols:
            if col is not None:
                cols += [col]
        df = df[cols]
        active_index = cofinanc.infer_active_bars(df[self._price_col])
        # Drop rows with no prices (this is an approximate way to handle weekends,
        # market holidays, and shortened trading sessions).
        df = df.reindex(index=active_index)
        # Drop indices with prices that proceed any returns prediction or
        # volatility computation.
        first_valid_prediction_index = df[
            self._prediction_col
        ].first_valid_index()
        first_valid_volatility_index = df[
            self._volatility_col
        ].first_valid_index()
        first_valid_index = max(
            first_valid_prediction_index, first_valid_volatility_index
        )
        df = df.loc[first_valid_index:]
        _LOG.debug("trimmed df=\n%s", hpandas.df_to_str(df))
        return df

    def _compute_flows(
        self,
        execution_price_df: pd.DataFrame,
        mark_to_market_price_df: pd.DataFrame,
        holdings: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Compute trade inflows and outflows.
        """
        # TODO(Paul): Factor out bod_timestamp generation.
        # Determine beginning-of-day timestamps.
        timestamps = pd.DataFrame(
            mark_to_market_price_df.index.to_list(),
            mark_to_market_price_df.index,
            ["timestamp"],
        )
        bod_timestamps = timestamps.groupby(lambda x: x.date()).min()
        # Compute trades as the difference in (share) holdings.
        trades = holdings.subtract(holdings.shift(1), fill_value=0)
        # Set overnight trades to zero.
        trades.loc[bod_timestamps["timestamp"]] *= 0
        _LOG.debug("`trades`=\n%s", hpandas.df_to_str(trades))
        # Change in shares priced at end of bar. Only valid intraday.
        # Note that the overnight flow is zero because there are no
        # overnight trades.
        # TODO(Paul): Factor out ffill_limit.
        ffill_limit = 2
        flows = -trades.multiply(execution_price_df.ffill(limit=ffill_limit))
        return flows

    def _compute_execution_prices(
        self,
        df: pd.DataFrame,
        holdings: pd.DataFrame,
        mark_to_market_price_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute execution prices from buy/sell price columns if available.
        """
        # Use separate buy/sell prices if available.
        if self._buy_price_col is not None and self._sell_price_col is not None:
            buy_price_df = ForecastEvaluatorFromPrices._get_df(
                df, self._buy_price_col
            )
            sell_price_df = ForecastEvaluatorFromPrices._get_df(
                df, self._sell_price_col
            )
            # Generate a signal indicating when we should buy or sell.
            trade_signal = holdings.diff()
            _LOG.debug("trade_signal=\n%s", hpandas.df_to_str(trade_signal))
            # Generate a filter for when we should use "buy price".
            use_buy_price = trade_signal > 0
            use_buy_price = use_buy_price.replace(True, 1.0).replace(
                False, np.nan
            )
            # Generate a filter for when we should use "sell price".
            use_sell_price = trade_signal < 0
            use_sell_price = use_sell_price.replace(True, 1.0).replace(
                False, np.nan
            )
            # Splice buy and sell prices.
            execution_price_df = buy_price_df.multiply(use_buy_price).add(
                sell_price_df.multiply(use_sell_price), fill_value=0.0
            )
            # Use mark to market price at close.
            timestamps = pd.DataFrame(
                mark_to_market_price_df.index.to_list(),
                mark_to_market_price_df.index,
                ["timestamp"],
            )
            eod_timestamps = timestamps.groupby(lambda x: x.date()).max()
            execution_price_df.loc[
                eod_timestamps["timestamp"], :
            ] = mark_to_market_price_df.loc[eod_timestamps["timestamp"], :]
        else:
            execution_price_df = mark_to_market_price_df
        return execution_price_df

    @staticmethod
    def _compute_ideal_holdings(
        target_holdings: pd.DataFrame,
        mark_to_market_price: pd.DataFrame,
        liquidate_at_end_of_day: bool,
        ffill_limit: int,
    ) -> pd.DataFrame:
        """
        Generate endtime-indexed holdings assuming perfect fills.

        :param target_holdings: next bar target holdings (in shares)
        :param mark_to_market_price: end-of-bar mark-to-market price
        :param liquidate_at_end_of_day: liquidate at EOD iff `True`
        :param ffill_limit: limit on forward-filling holdings (e.g., useful
            if a bar is missing a mark-to-market price)
        :return: dataframe of share holdings (endtime-indexed)
        """
        # Assume target shares are obtained.
        holdings = target_holdings.shift(1)
        # Determine beginning-of-day and possibly end-of-day timestamps.
        timestamps = pd.DataFrame(
            mark_to_market_price.index.to_list(),
            mark_to_market_price.index,
            ["timestamp"],
        )
        bod_timestamps = timestamps.groupby(lambda x: x.date()).min()
        if liquidate_at_end_of_day:
            eod_timestamps = timestamps.groupby(lambda x: x.date()).max()
            holdings.loc[eod_timestamps["timestamp"], :] = 0.0
            holdings.loc[bod_timestamps["timestamp"], :] *= 0
        # TODO(Paul): Give the user the option of supplying the share
        # adjustment factors. Infer as below if they are not supplied.
        else:
            split_factors = cofinanc.infer_splits(mark_to_market_price)
            splits = split_factors.merge(
                bod_timestamps, left_index=True, right_index=True
            ).set_index("timestamp")
            eod_holdings = cofinanc.retrieve_end_of_day_values(holdings)
            bod_holdings = (
                eod_holdings.shift(1)
                .merge(bod_timestamps, left_index=True, right_index=True)
                .set_index("timestamp")
                .multiply(splits)
            )
            # Set beginning-of-day holdings.
            holdings.loc[bod_timestamps["timestamp"], :] = bod_holdings
            holdings = holdings.groupby(lambda x: x.date()).ffill(limit=2)
        holdings = holdings.ffill(limit=ffill_limit)
        return holdings

    def _adjust_holdings_for_underfills(
        self,
        df: pd.DataFrame,
        holdings: pd.DataFrame,
        mark_to_market_price: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Adapt holdings by taking into account underfills.

        :param holdings: ideal holdings (assuming complete fills)
        :param mark_to_market_price: mark-to-market price, used in the day's
            last bar of execution
        :return: dataframe of holdings adjusted to account for underfills
        """
        # Do not perform an adjustment if separate buy/sell prices are not
        # provided.
        if self._buy_price_col is None:
            return holdings
        # Extract buy and sell price dataframes from `df`.
        buy_price_df = ForecastEvaluatorFromPrices._get_df(
            df, self._buy_price_col
        ).copy()
        sell_price_df = ForecastEvaluatorFromPrices._get_df(
            df, self._sell_price_col
        ).copy()
        # Use mark to market price at close.
        timestamps = pd.DataFrame(
            mark_to_market_price.index.to_list(),
            mark_to_market_price.index,
            ["timestamp"],
        )
        eod_timestamps = timestamps.groupby(lambda x: x.date()).max()
        # TODO(Paul): Factor out ffill_limit.
        ffill_limit = 2
        prices = mark_to_market_price.ffill(limit=ffill_limit)
        buy_price_df.loc[eod_timestamps["timestamp"]] = prices.loc[
            eod_timestamps["timestamp"]
        ]
        sell_price_df.loc[eod_timestamps["timestamp"]] = prices.loc[
            eod_timestamps["timestamp"]
        ]
        # Create filters to indicate where no buy price is available (leading
        # to underfills for buy orders) or no sell price is available (leading
        # to underfills for sell orders).
        no_buy_price = buy_price_df.isna()
        no_sell_price = sell_price_df.isna()
        # Create a copy of `holdings` to perform the adjustment.
        adjusted_holdings = holdings.copy()
        iteration_count = 1
        while True:
            _LOG.debug("Underfill adjustment iteration cycle=%d", iteration_count)
            # If we want to buy but no buy price is available, or we want to
            # sell and no sell price is available, then hold.
            force_hold = ((adjusted_holdings.diff() > 0) & no_buy_price) | (
                (adjusted_holdings.diff() < 0) & no_sell_price
            )
            if force_hold is None or (force_hold.sum().sum() == 0):
                _LOG.info(
                    "Performed %d iterations of underfill adjustments",
                    iteration_count - 1,
                )
                break
            # Impute NaN and forward fill to force holding. This is a heuristic
            # that should provide a reasonable approximation in many (not
            # necessarily all) scenarios.
            adjusted_holdings[force_hold.values] = np.nan
            adjusted_holdings.ffill(limit=1, inplace=True)
            adjusted_holdings = adjusted_holdings.combine_first(holdings)
            iteration_count += 1
            hdbg.dassert_lt(
                iteration_count,
                100,
                "Exceeded underfill adjustment iteration limit",
            )
        return adjusted_holdings
