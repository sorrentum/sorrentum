"""
Import as:

import helpers.hpandas as hpandas
"""
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

import helpers.hdatetime as hdateti
import helpers.hdbg as hdbg
import helpers.hprint as hprint

_LOG = logging.getLogger(__name__)


_LOG.verb_debug = hprint.install_log_verb_debug(_LOG, verbose=False)


# #############################################################################


def to_series(df: pd.DataFrame) -> pd.Series:
    """
    Convert a pd.DataFrame with a single column into a pd.Series.

    The problem is that empty df or df with a single row are not
    converted correctly to a pd.Series.
    """
    # See https://stackoverflow.com/questions/33246771
    hdbg.dassert_isinstance(df, pd.DataFrame)
    hdbg.dassert_eq(df.shape[1], 1, "df=%s doesn't have a single column", df)
    if df.empty:
        srs = pd.Series()
    elif df.shape[0] > 1:
        srs = df.squeeze()
    else:
        srs = pd.Series(df.iloc[0, 0], index=[df.index.values[0]])
        srs.name = df.index.name
    hdbg.dassert_isinstance(srs, pd.Series)
    return srs


def dassert_is_days(
    timedelta: pd.Timedelta, *, min_num_days: Optional[int] = None
) -> None:
    hdbg.dassert(
        (timedelta / pd.Timedelta(days=1)).is_integer(),
        "timedelta='%s' is not an integer number of days",
        timedelta,
    )
    if min_num_days is not None:
          hdbg.dassert_lte(1, timedelta.days)


# #############################################################################


def _get_index(obj: Union[pd.Index, pd.DataFrame, pd.Series]) -> pd.Index:
    """
    Return the index of a Pandas object.
    """
    if isinstance(obj, pd.Index):
        index = obj
    else:
        hdbg.dassert_isinstance(obj, (pd.Series, pd.DataFrame))
        index = obj.index
    return index


# TODO(gp): Maybe for symmetry with the other functions, rename to
#  dassert_datetime_index
def dassert_index_is_datetime(
    obj: Union[pd.Index, pd.DataFrame, pd.Series],
    msg: Optional[str] = None,
    *args: Any,
) -> None:
    """
    Ensure that the dataframe has an index containing datetimes.
    """
    index = _get_index(obj)
    hdbg.dassert_isinstance(index, pd.DatetimeIndex, msg, *args)


def dassert_unique_index(
    obj: Union[pd.Index, pd.DataFrame, pd.Series],
    msg: Optional[str] = None,
    *args: Any,
) -> None:
    """
    Ensure that a Pandas object has a unique index.
    """
    index = _get_index(obj)
    if not index.is_unique:
        dup_indices = index.duplicated(keep=False)
        df_dup = obj[dup_indices]
        dup_msg = "Duplicated rows are:\n%s\n" % hpandas.dataframe_to_str(df_dup)
        if msg is None:
            msg = dup_msg
        else:
            msg = dup_msg + msg
        hdbg.dassert(index.is_unique, msg=msg, *args)


# TODO(gp): Add more info in case of failures and unit tests.
def dassert_strictly_increasing_index(
    obj: Union[pd.Index, pd.DataFrame, pd.Series],
    msg: Optional[str] = None,
    *args: Any,
) -> None:
    """
    Ensure that a Pandas object has a strictly increasing index.
    """
    dassert_unique_index(obj, msg=msg, *args)
    # TODO(gp): Understand why mypy reports:
    #   error: "dassert" gets multiple values for keyword argument "msg"
    index = _get_index(obj)
    hdbg.dassert(index.is_monotonic_increasing, msg=msg, *args)


# TODO(gp): Factor out common code related to extracting the index from several
#  pandas data structures.
# TODO(gp): Not sure it's used or useful?
def dassert_monotonic_index(
    obj: Union[pd.Index, pd.DataFrame, pd.Series],
    msg: Optional[str] = None,
    *args: Any,
) -> None:
    """
    Ensure that a Pandas object has a monotonic (i.e., strictly increasing or
    decreasing index).
    """
    dassert_unique_index(obj, msg=msg, *args)
    # TODO(gp): Understand why mypy reports:
    #   error: "dassert" gets multiple values for keyword argument "msg"
    index = _get_index(obj)
    cond = index.is_monotonic_increasing or index.is_monotonic_decreasing
    hdbg.dassert(cond, msg=msg, *args)


def dassert_valid_remap(to_remap: List[str], remap_dict: Dict[str, str]) -> None:
    """
    Ensure that remapping rows / columns is valid.
    """
    hdbg.dassert_isinstance(to_remap, list)
    hdbg.dassert_isinstance(remap_dict, dict)
    # All the rows / columns to remap, should exist.
    hdbg.dassert_is_subset(
        remap_dict.keys(),
        to_remap,
        "Keys to remap should be a subset of existing columns",
    )
    # The mapping is invertible.
    hdbg.dassert_no_duplicates(remap_dict.keys())
    hdbg.dassert_no_duplicates(remap_dict.values())
    # Rows / columns should not be remapped on existing rows / columns.
    hdbg.dassert_not_intersection(remap_dict.values(), to_remap)


def dassert_series_type_is(
    srs: pd.Series,
    type_: type,
    msg: Optional[str] = None,
    *args: Any,
) -> None:
    """
    Ensure that the data type of `srs` is `type_`.

    Examples of valid series types are
      - np.float64
      - np.int64
      - pd.Timestamp
    """
    hdbg.dassert_isinstance(srs, pd.Series)
    hdbg.dassert_isinstance(type_, type)
    hdbg.dassert_eq(srs.dtype.type, type_, msg, *args)


def dassert_series_type_in(
    srs: pd.Series,
    types: List[type],
    msg: Optional[str] = None,
    *args: Any,
) -> None:
    """
    Ensure that the data type of `srs` is one of the types in `types`.
    """
    hdbg.dassert_isinstance(srs, pd.Series)
    hdbg.dassert_container_type(types, list, type)
    hdbg.dassert_in(srs.dtype.type, types, msg, *args)


# #############################################################################


def resample_index(index: pd.DatetimeIndex, frequency: str) -> pd.DatetimeIndex:
    """
    Resample `DatetimeIndex`.

    :param index: `DatetimeIndex` to resample
    :param frequency: frequency from `pd.date_range()` to resample to
    :return: resampled `DatetimeIndex`
    """
    _LOG.debug(hprint.to_str("index frequency"))
    hdbg.dassert_isinstance(index, pd.DatetimeIndex)
    dassert_unique_index(index, msg="Index must have only unique values")
    min_date = index.min()
    max_date = index.max()
    _LOG.debug("min_date=%s max_date=%s", min_date, max_date)
    # TODO(gp): Preserve the index name.
    # index_name = index.name
    resampled_index = pd.date_range(
        start=min_date,
        end=max_date,
        freq=frequency,
    )
    if len(resampled_index) > len(index):
        # Downsample.
        _LOG.info(
            "Index length increased by %s = %s - %s",
            len(resampled_index) - len(index),
            len(resampled_index),
            len(index),
        )
    elif len(resampled_index) < len(index):
        # Upsample.
        _LOG.info(
            "Index length decreased by %s = %s - %s",
            len(index) - len(resampled_index),
            len(index),
            len(resampled_index),
        )
    else:
        _LOG.info("Index length=%s has not changed", len(index))
    # resampled_index.name = index_name
    return resampled_index


def resample_df(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    """
    Resample `DataFrame` by placing NaN in missing locations in the index.

    :param df: `DataFrame` to resample
    :param frequency: frequency from `pd.date_range()` to resample to
    :return: resampled `DataFrame`
    """
    hdbg.dassert_isinstance(df, pd.DataFrame)
    # Preserve the index name.
    index_name = df.index.name
    resampled_index = resample_index(df.index, frequency)
    df_reindex = df.reindex(resampled_index)
    df_reindex.index.name = index_name
    return df_reindex


def drop_duplicates(
    data: Union[pd.Series, pd.DataFrame],
    *args: Any,
    **kwargs: Any,
) -> Union[pd.Series, pd.DataFrame]:
    """
    Wrapper around `pandas.drop_duplicates()`.

    See the official docs:
    - https://pandas.pydata.org/docs/reference/api/pandas.Series.drop_duplicates.html
    - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html

    :return: data without duplicates
    """
    _LOG.debug("args=%s, kwargs=%s", str(args), str(kwargs))
    num_rows_before = data.shape[0]
    # Drop duplicates.
    data_no_dups = data.drop_duplicates(*args, **kwargs)
    # Report change.
    num_rows_after = data_no_dups.shape[0]
    if num_rows_before != num_rows_after:
        _LOG.debug(
            "Removed %s rows",
            hprint.perc(num_rows_before - num_rows_after, num_rows_before),
        )
    return data_no_dups


def reindex_on_unix_epoch(
    df: pd.DataFrame, in_col_name: str, unit: str = "s"
) -> pd.DataFrame:
    """
    Transform the column `in_col_name` into a datetime index. `in_col_name`
    contains Unix epoch (e.g., 1638194400) and it is converted into a UTC time.

    :param df: dataframe with a unix epoch
    :param in_col_name: column containing unix epoch
    :param unit: the unit of unix epoch
    """
    # Convert.
    temp_col_name = in_col_name + "_tmp"
    hdbg.dassert_in(in_col_name, df.columns)
    hdbg.dassert_not_in(temp_col_name, df.columns)
    # Save.
    df[temp_col_name] = pd.to_datetime(df[in_col_name], unit=unit, utc=True)
    df.set_index(temp_col_name, inplace=True, drop=True)
    df.index.name = None
    return df


def get_df_signature(df: pd.DataFrame, num_rows: int = 3) -> str:
    """
    Compute a simple signature of a dataframe in string format.

    The signature contains metadata about dataframe size and certain
    amount of rows from start and end of a dataframe. It is used for
    testing purposes.
    """
    hdbg.dassert_isinstance(df, pd.DataFrame)
    txt: List[str] = []
    txt.append("df.shape=%s" % str(df.shape))
    with pd.option_context(
        "display.max_colwidth", int(1e6), "display.max_columns", None
    ):
        txt.append("df.head=\n%s" % df.head(num_rows))
        txt.append("df.tail=\n%s" % df.tail(num_rows))
    txt = "\n".join(txt)
    return txt


# #############################################################################


def trim_df(
    df: pd.DataFrame,
    ts_col_name: Optional[str],
    start_ts: Optional[pd.Timestamp],
    end_ts: Optional[pd.Timestamp],
    left_close: bool,
    right_close: bool,
) -> pd.DataFrame:
    """
    Trim df using values in `ts_col_name` in interval bounded by `start_ts` and
    `end_ts`.

    :param ts_col_name: the name of the column. `None` means index
    :param start_ts, end_ts: boundaries of the desired interval
    :param left_close, right_close: encode what to do with the boundaries of the
        interval
        - E.g., [start_ts, end_ts), or (start_ts, end_ts]
    """
    _LOG.verb_debug(
        df_to_str(df, print_dtypes=True, print_shape_info=True, tag="df")
    )
    _LOG.debug(
        hprint.to_str("ts_col_name start_ts end_ts left_close right_close")
    )
    if df.empty:
        # If the df is empty there is nothing to trim.
        return df
    num_rows_before = df.shape[0]
    if start_ts is not None and end_ts is not None:
        hdateti.dassert_tz_compatible(start_ts, end_ts)
        hdbg.dassert_lte(start_ts, end_ts)
    # Handle the index.
    use_index = False
    if ts_col_name is None:
        # Convert the index into a regular column.
        # TODO(gp): Use binary search if there is an index.
        if df.index.name is None:
            _LOG.debug(
                "The df has no index\n%s",
                df_to_str(df.head()),
            )
            df.index.name = "index"
        ts_col_name = df.index.name
        df = df.reset_index()
        use_index = True
    # TODO(gp): This is inefficient. Make it faster by binary search, if ordered.
    hdbg.dassert_in(ts_col_name, df.columns)
    # Filter based on start_ts.
    _LOG.debug("Filtering by start_ts=%s", start_ts)
    if start_ts is not None:
        _LOG.verb_debug("start_ts=%s", start_ts)
        # Convert the column into `pd.Timestamp` to compare it to `start_ts`.
        # This is needed to sidestep the comparison hell involving `numpy.datetime64`
        # vs Pandas objects.
        tss = pd.to_datetime(df[ts_col_name])
        hdateti.dassert_tz_compatible(tss.iloc[0], start_ts)
        _LOG.verb_debug("tss=\n%s", df_to_str(tss))
        if left_close:
            mask = tss >= start_ts
        else:
            mask = tss > start_ts
        _LOG.verb_debug("mask=\n%s", df_to_str(mask))
        df = df[mask]
    # Filter based on end_ts.
    _LOG.debug("Filtering by end_ts=%s", end_ts)
    if not df.empty:
        if end_ts is not None:
            _LOG.debug("Filtering by start_ts=%s", start_ts)
            _LOG.verb_debug("end_ts=%s", end_ts)
            tss = pd.to_datetime(df[ts_col_name])
            hdateti.dassert_tz_compatible(tss.iloc[0], end_ts)
            _LOG.verb_debug("tss=\n%s", df_to_str(tss))
            if right_close:
                mask = tss <= end_ts
            else:
                mask = tss < end_ts
            _LOG.verb_debug("mask=\n%s", df_to_str(mask))
            df = df[mask]
    else:
        # If the df is empty there is nothing to trim.
        pass
    if use_index:
        df = df.set_index(ts_col_name, drop=True)
    # Report the changes.
    num_rows_after = df.shape[0]
    if num_rows_before != num_rows_after:
        _LOG.debug(
            "Removed %s rows",
            hprint.perc(num_rows_before - num_rows_after, num_rows_before),
        )
    return df


# #############################################################################


# TODO(gp): This seems redundant with hut.convert_df_to_string.
def df_to_str(
    df: pd.DataFrame,
    *,
    num_rows: int = 6,
    print_dtypes: bool = False,
    print_shape_info: bool = False,
    tag: Optional[str] = None,
    max_columns: int = 10000,
    max_colwidth: int = 2000,
    max_rows: int = 500,
    precision: int = 6,
    display_width: int = 10000,
    use_tabulate: bool = False,
) -> str:
    """
    Print a dataframe to string reporting all the columns without trimming.
    :param: num_rows: max number of rows to print (half from the top and half from
        the bottom of the dataframe)
    :param print_dtypes: reports dataframe types and information about the type of each
        column by looking at the first value
    :param print_shape_info: reports dataframe shape, index and columns
    """
    # TODO(Nikola): Couple of test are failing with
    #  AttributeError: 'NoneType' object has no attribute 'empty'
    #  or with totally misleading messages in form of duplicate keys in db, etc.
    if df is None:
        return ""
    out = []
    # Print the tag.
    if tag is not None:
        out.append(f"# {tag}=")
    # Print information about the shape and index.
    if print_shape_info:
        if not df.empty:
            out.append("df.index in [%s, %s]" % (df.index.min(), df.index.max()))
            out.append("df.columns=%s" % ",".join(map(str, df.columns)))
            # TODO(Nikola): Revisit and rename print_shape_info to print_axes_info
            out.append("df.shape=%s" % str(df.shape))
    # Print information about the types.
    if not df.empty:
        if print_dtypes:
            out.append("df.type=")

            def _report_type_of_first_element(srs: "pd.Series") -> str:
                """
                Report dtype, the first element, and its type of series.
                """
                elem = srs.values[0]
                val = "%10s %25s %s" % (srs.dtype, type(elem), elem)
                return val

            col_name = "index"
            fmt = "  %20s: %s"
            out.append(fmt % (col_name, _report_type_of_first_element(df.index)))
            for col_name in df.columns:
                out.append(
                    fmt % (col_name, _report_type_of_first_element(df[col_name]))
                )
    # Set dataframe print options.
    with pd.option_context(
        "display.max_colwidth",
        max_colwidth,
        # "display.height", 1000,
        "display.max_rows",
        max_rows,
        "display.precision",
        precision,
        "display.max_columns",
        max_columns,
        "display.width",
        display_width,
    ):
        if use_tabulate:
            import tabulate

            out.append(tabulate.tabulate(df, headers="keys", tablefmt="psql"))
        # Print the data frame.
        if df.shape[0] <= num_rows:
            out.append(str(df))
        else:
            # Print top and bottom of df.
            out.append(str(df.head(num_rows // 2)))
            out.append("...")
            tail_str = str(df.tail(num_rows // 2))
            # Remove index and columns.
            skipped_rows = 1
            if df.index.name:
                skipped_rows += 1
            tail_str = "\n".join(tail_str.split("\n")[skipped_rows:])
            out.append(tail_str)
    txt = "\n".join(out)
    # TODO(Nikola): Temporary strip
    txt.rstrip("\n")
    return txt
