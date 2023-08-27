"""
Centralize checking logical dependencies between values of various arguments
for ETL scripts.

Import as:

import im_v2.common.data.qa.validate_input_args as imvcdqviar
"""
import argparse

import helpers.hdbg as hdbg


def validate_vendor_arg(vendor: str, args: argparse.Namespace) -> None:
    """
    Validate vendor args.

    :param vendor: vendor name
    :param args: ETL script args
    :return: vendor data extractor
    """
    hdbg.dassert_in(
        vendor,
        ["binance", "ccxt", "crypto_chassis"],
        msg=f"Vendor {vendor} is not supported.",
    )
    if vendor == "crypto_chassis":
        if not args.get("universe_part"):
            raise RuntimeError(
                f"--universe_part argument is mandatory for {vendor}"
            )
    else:
        hdbg.dfatal(f"Vendor {vendor} is not supported.")
