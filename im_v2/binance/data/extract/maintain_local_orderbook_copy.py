#!/usr/bin/env python
"""
This is an example script implementing a method recommended by Binance
to maintain futures order book locally correctly
https://binance-docs.github.io/apidocs/futures/en/#how-to-manage-a-local-order-book-correctly

This is prototype implementation:
- supports only watching 1 symbol at a time.
- no error handling is implemented

The code is annotated by comments representing
numbered steps of the original guide.

Code inspired by
https://gist.github.com/DGabri/44c682da111ec99186e8550c28466e3c

Usage:
./im_v2/binance/data/extract/maintain_local_orderbook_copy.py
"""
import json
import logging
import time
from typing import Dict

import requests

import helpers.hdbg as hdbg
import im_v2.binance.websocket.websocket_client as imvbwwecl

_LOG = logging.getLogger(__name__)

_SYMBOL = "BTCUSDT"

# How long does the script run for.
_RUN_FOR_SECONDS = 10

# How often to receive updates in miliseconds,
# allowed values: 100, 250, 500ms.
_ORDER_BOOK_UPDATE_SPEED_MS = 500

_ORDER_BOOK = {
    "lastUpdateId": -1,
    "bids": [],
    "asks": [],
    "wasfirstProcessedEvent": False,
}


def _get_orderbook_snapshot() -> None:
    """
    Retrieve order book snapshot.

    From the guide:
    3. Get a depth snapshot from https://fapi.binance.com/fapi/v1/depth?symbol={symbol}&limit=1000.
    """
    resp = requests.get(
        f"https://fapi.binance.com/fapi/v1/depth?symbol={_SYMBOL}&limit=1000"
    )
    resp_json = resp.json()
    _ORDER_BOOK["lastUpdateId"] = resp_json["lastUpdateId"]
    _ORDER_BOOK["bids"] = resp_json["bids"]
    _ORDER_BOOK["asks"] = resp_json["asks"]


def _update_order_book(message: Dict) -> None:
    """
    Updates local order book's bid or ask lists based on the received message.
    """
    for side in ["bids", "asks"]:
        # "bids" -> "b" in a diff. book depth message
        for update in message[side[0]]:
            price, quantity = update
            for i in range(0, len(_ORDER_BOOK[side])):
                if price == _ORDER_BOOK[side][i][0]:
                    # 8. If the quantity is 0, remove the price level.
                    if float(quantity) == 0:
                        _ORDER_BOOK[side].pop(i)
                    else:
                        # 7. The data in each event is the absolute quantity for a price level.
                        _ORDER_BOOK[side][i] = quantity
                    break

            # Price not present, add new level
            # 9. Receiving an event that removes a price level that is not in your
            # local order book can happen and is normal.
            if float(quantity) != 0:
                _ORDER_BOOK[side].insert(-1, update)
                if side == "asks":
                    # Asks prices in ascendant order
                    _ORDER_BOOK[side] = sorted(
                        _ORDER_BOOK[side], key=lambda x: float(x[0])
                    )
                else:
                    # Bids prices in descendant order
                    _ORDER_BOOK[side] = sorted(
                        _ORDER_BOOK[side], key=lambda x: float(x[0]), reverse=True
                    )

            if len(_ORDER_BOOK[side]) > 1000:
                _ORDER_BOOK[side].pop(len(_ORDER_BOOK[side]) - 1)


# Two arguments are required by the library.
def _handle_message(_, message: Dict) -> None:
    if "depthUpdate" in message:
        message = json.loads(message)
        last_update_id = _ORDER_BOOK["lastUpdateId"]
        if message["u"] <= last_update_id:
            # 4. Drop any event where u is < lastUpdateId in the snapshot.
            return
        # 5. The first processed event should have U <= lastUpdateId AND u >= lastUpdateId.
        is_first_processed_event = (
            not _ORDER_BOOK["wasfirstProcessedEvent"]
            and message["U"] <= last_update_id <= message["u"]
        )
        # 6. While listening to the stream, each new event's pu should be equal
        # to the previous event's u, otherwise initialize the process from step 3.
        is_consecutive_event = (
            _ORDER_BOOK["wasfirstProcessedEvent"]
            and message["pu"] == last_update_id
        )
        if is_first_processed_event or is_consecutive_event:
            _ORDER_BOOK["wasfirstProcessedEvent"] = True
            _ORDER_BOOK["lastUpdateId"] = message["u"]
            _update_order_book(message)
        else:
            logging.info("Out of sync, re-syncing...")
            # 3. Get a depth snapshot from https://fapi.binance.com/fapi/v1/depth?symbol={symbol}&limit=1000
            _ORDER_BOOK["wasfirstProcessedEvent"] = False
            _get_orderbook_snapshot()


def _handle_error(_, exception) -> None:
    raise exception


def _listen_ws() -> imvbwwecl.UMFuturesWebsocketClient:
    """
    Subscribe to the websocket stream.
    """
    ws_client = imvbwwecl.UMFuturesWebsocketClient(
        on_message=_handle_message, on_error=_handle_error
    )
    # 1. Open a stream to wss://fstream.binance.com/stream?streams={symbol}@depth.
    ws_client.diff_book_depth(symbol=_SYMBOL.lower(), speed=_ORDER_BOOK_UPDATE_SPEED_MS)
    return ws_client


def _track_order_book() -> None:
    """
    Log order book periodically.
    """
    _LOG.info(f"Tracking orderbook for {_RUN_FOR_SECONDS} minute...")
    start = time.time()
    while time.time() - start < _RUN_FOR_SECONDS:
        # If we have gotten in sync with Binance's order book.
        if _ORDER_BOOK["lastUpdateId"] > 0:
            # Print only a few top levels of the book for demonstration.
            _LOG.info(f"Bids: {_ORDER_BOOK['bids'][:10]}")
            _LOG.info(f"Asks: {_ORDER_BOOK['asks'][:10]}")
            _LOG.info("\n#######################\n")
        time.sleep(2)


def _main():
    hdbg.init_logger(verbosity="INFO", use_exec_path=True)
    # Websocket order book 
    try:
        ws_client = _listen_ws()
        _track_order_book()
    finally:
        ws_client.stop()


_main()
