"""
Import as:

import im_v2.ccxt.universe.universe as imvccunun
"""
import os
from typing import Dict, List, Union

import helpers.hdbg as hdbg
import helpers.hgit as hgit
import helpers.hio as hio
import im_v2.common.data.client as icdc
import im_v2.common.universe.universe_utils as imvcuunut

_LATEST_UNIVERSE_VERSION = "v03"


def get_trade_universe(
    version: str = _LATEST_UNIVERSE_VERSION,
) -> Dict[str, Dict[str, List[str]]]:
    """
    Load trade universe for which we have historical data on S3.

    :param version: release version
    :return: trade universe
    """
    file_name = "".join(["universe_", version, ".json"])
    file_path = os.path.join(
        hgit.get_amp_abs_path(), "im_v2/ccxt/universe", file_name
    )
    hdbg.dassert_exists(file_path)
    universe = hio.from_json(file_path)
    return universe  # type: ignore[no-any-return]


# TODO(Dan): remove default values for `vendor` param #832.
def get_vendor_universe(
    version: str = _LATEST_UNIVERSE_VERSION, vendor: str = "CCXT"
) -> Union[List[icdc.FullSymbol], List[int]]:
    """
<<<<<<< HEAD
    Load vendor universe as full symbols or numerical ids.

    :param version: release version
    :param vendor: vendor to load data for (e.g., CCXT, CDD)
    :param as_asset_ids: if True return universe as numerical ids, otherwise universe as full symbols
=======
    Load vendor universe as full symbols.

    :param version: release version
    :param vendor: vendor to load data for (e.g., CCXT, CDD)
>>>>>>> 06992d9b2b8c1de0e3c00a1ad3a6fc03e6e66929
    :return: vendor universe as full symbols (e.g., gateio::XRP_USDT)
    """
    # Get vendor universe.
    vendor_universe = get_trade_universe(version)[vendor]
    # Convert vendor universe dict to a sorted list of full symbols.
    universe = [
        icdc.build_full_symbol(exchange_id, currency_pair)
        for exchange_id, currency_pairs in vendor_universe.items()
        for currency_pair in currency_pairs
    ]
<<<<<<< HEAD
    if as_asset_ids:
        # Convert universe symbols to numerical ids.
        universe_tuple = tuple(universe)
        universe = list(
            imvcuunut.build_numerical_to_string_id_mapping(universe_tuple).keys()
        )
=======
<<<<<<< HEAD
>>>>>>> master
=======
>>>>>>> 8b50dc45745d85cc64827368c95143fe05d339ae
>>>>>>> 06992d9b2b8c1de0e3c00a1ad3a6fc03e6e66929
    # Sort list of symbols in the universe.
    universe = sorted(universe)
    return universe
