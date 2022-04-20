"""
Import as:

import im_v2.common.universe.full_symbol as imvcufusy
"""

import logging
import re
from typing import List, Tuple, Union

import pandas as pd

import helpers.hdbg as hdbg

_LOG = logging.getLogger(__name__)

# Store information about an exchange and a symbol (e.g., `binance::BTC_USDT`).
# Note that information about the vendor is carried in the `ImClient` itself,
# i.e. using `CcxtImClient` serves data from CCXT.
# Full symbols are transformed in `asset_ids` encoded by ints, by `ImClient` and
# used by `MarketData`.
FullSymbol = str


# TODO(gp): -> dassert_valid_full_symbol
def dassert_is_full_symbol_valid(
    full_symbol: Union[pd.Series, FullSymbol]
) -> None:
    """
    Check that a full symbol or all the symbols in a series have valid format,
    i.e. `exchange::symbol`.

    Note: digits and special symbols (except underscore) are not allowed.
    """
    # Only letters and underscores are allowed.
    # TODO(gp): I think we might need non-leading numbers.
    letter_underscore_pattern = "[a-zA-Z_]"
    # Exchanges and symbols must be separated by `::`.
    regex_pattern = rf"{letter_underscore_pattern}*::{letter_underscore_pattern}*"
    #
    if isinstance(full_symbol, pd.Series):
        # Assert that the series has no empty strings.
        full_symbol = full_symbol.replace("", None)
        no_nans = ~full_symbol.isna().any()
        hdbg.dassert(no_nans)
        # Set match pattern.
        full_match = full_symbol.str.fullmatch(regex_pattern).all()
    elif isinstance(full_symbol, FullSymbol):
        hdbg.dassert_isinstance(full_symbol, str)
        hdbg.dassert_ne(full_symbol, "")
        # Set match pattern.
        full_match = re.fullmatch(regex_pattern, full_symbol, re.IGNORECASE)
    else:
        raise TypeError(
            "Input type is `%s` but should be either a string or a `pd.Series`",
            type(full_symbol),
        )
    # Valid full symbols must match the pattern.
    hdbg.dassert(
        full_match,
        "Incorrect full_symbol '%s', it must be `exchange::symbol`",
        full_symbol,
    )


def parse_full_symbol(
    full_symbol: Union[pd.Series, FullSymbol]
) -> Tuple[Union[pd.Series, str], Union[pd.Series, str]]:
    """
    Split a full symbol into a tuple of exchange and symbol or a column of full
    symbols on columns of exchanges and symbols.
    """
    dassert_is_full_symbol_valid(full_symbol)
    if isinstance(full_symbol, pd.Series):
        # Get a dataframe with exchange and symbol columns.
        df_exchange_symbol = full_symbol.str.split("::", expand=True)
        # Get exchange and symbol columns.
        exchange = df_exchange_symbol[0]
        symbol = df_exchange_symbol[1]
    elif isinstance(full_symbol, FullSymbol):
        # Split full symbol on exchange and symbol.
        exchange, symbol = full_symbol.split("::")
    else:
        raise TypeError(
            "Input type is `%s` but should be either a string or a `pd.Series`",
            type(full_symbol),
        )
    return exchange, symbol


def build_full_symbol(
    exchange: Union[pd.Series, str], symbol: Union[pd.Series, str]
) -> Union[pd.Series, FullSymbol]:
    """
    Combine exchange and symbol in a full symbol or exchange and symbol columns
    in a full symbol column.
    """
    if isinstance(exchange, pd.Series) and isinstance(symbol, pd.Series):
        # Combine exchange and symbol columns in a full symbol column.
        full_symbol = exchange + "::" + symbol
        dassert_is_full_symbol_valid(full_symbol)
    elif isinstance(exchange, str) and isinstance(symbol, str):
        hdbg.dassert_ne(exchange, "")
        hdbg.dassert_ne(symbol, "")
        # Combine exchange and symbol in a full symbol.
        full_symbol = f"{exchange}::{symbol}"
        dassert_is_full_symbol_valid(full_symbol)
    else:
        raise TypeError(
            "type(exchange) = `%s`, type(symbol)= `%s` but both inputs should"
            "have the same type and be either a string or a `pd.Series`",
            type(exchange),
            type(symbol),
        )
    return full_symbol


def dassert_valid_full_symbols(full_symbols: List[FullSymbol]) -> None:
    """
    Verify that full symbols are passed in a list that has no duplicates.
    """
    hdbg.dassert_container_type(full_symbols, list, FullSymbol)
    hdbg.dassert_no_duplicates(full_symbols)
