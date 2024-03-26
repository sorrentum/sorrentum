# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: amp.client_venv
#     language: python
#     name: amp.client_venv
# ---

# %% [markdown]
# # Binance-futures-connector library overview

# %%
# The lib conflicts with docker-compose -- i've simply uninstalled docker-compose temporarily
# !pip install binance-futures-connector

# %% [markdown]
# ## WebSocket Stream Client - examples

# %%
# Set up imports and message handler
import time
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient


def message_handler(_, message: str):
    print(type(message), message)


# %% [markdown]
# ### Agg trade

# %%
# Open the connection
my_client = UMFuturesWebsocketClient(on_message=message_handler, is_combined=True)

# Subscribe to a single symbol stream
my_client.agg_trade(symbol="bnbusdt")

time.sleep(5)

# Unsubscribe
my_client.agg_trade(symbol="bnbusdt", action=UMFuturesWebsocketClient.ACTION_UNSUBSCRIBE)
time.sleep(5)

# Close the connection
print("closing ws connection")
my_client.stop()

# %% [markdown]
# ### Kline

# %%
# Open the connection
my_client = UMFuturesWebsocketClient(on_message=message_handler)

my_client.kline(
    symbol="btcusdt",
    id=1,
    interval="1m",
)

time.sleep(10)


# Close the connection
print("closing ws connection")
my_client.stop()

# %% [markdown]
# ### Partial book depth - TODO - skontrolovat unsubscribe

# %%
# Open the connection
my_client = UMFuturesWebsocketClient(on_message=message_handler)

# Subscribe to a single symbol stream
my_client.partial_book_depth(
    symbol="bnbusdt",
    level=10,
    speed=100,
)

time.sleep(10)

# Close the connection
print("closing ws connection")
my_client.stop()

# %% [markdown]
# ## Download 5 minutes of streams

# %%
import csv
import time
import threading
from typing import Callable, List, Optional


class BinanceWebsocketService:
    SUPPORTED_STREAM_METHODS = ["agg_trade", "kline", "partial_book_depth"]
    
    def __init__(self, stream_method: str, output_csv_file: str):
        if stream_method not in self.SUPPORTED_STREAM_METHODS:
            raise ValueError(f"Stream method '{stream_method}' is not supported.")
        self.stream_method = stream_method
        self.output_csv_file = output_csv_file
        
    def get_client_stream_function(self, client: UMFuturesWebsocketClient) -> Optional[Callable]:
        if self.stream_method == "agg_trade":
            return client.agg_trade
        elif self.stream_method == "kline":
            return client.kline
        elif self.stream_method == "partial_book_depth":
            return client.partial_book_depth
        else:
            return None
        
            
    def download_stream_data_to_csv(self, symbols: List[str], download_time_seconds: int = 300, **kwargs):
        stream_data = []
        
        def service_message_handler(_, message: str):
            data = json.loads(message)
            if 'result' not in data.keys():
                data['data']['stream'] = data['stream']
                
                # kline
                if "k" in data['data']:
                    # flatten kline output to single level
                    for key, value in data['data']['k'].items():
                        data['data'][f'k_{key}'] = value
                    del data['data']['k']
                    
                stream_data.append(data['data'])
        
        # Open the connection
        client = UMFuturesWebsocketClient(on_message=service_message_handler, is_combined=True)
        stream_function = self.get_client_stream_function(client)
        print(f"Opening connection for {self.stream_method}")
        
        # Subscribe to streams for each symbol
        for symbol in symbols:
            stream_function(symbol=symbol, **kwargs)
        
        # Let the download run for X seconds
        time.sleep(download_time_seconds)

        # Close the connection
        print(f"Closing connection for {self.stream_method}")
        client.stop()
        
        # Export to JSON
        print("Exporting data to csv.")
        with open(self.output_csv_file, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=stream_data[0].keys())
            writer.writeheader()
            writer.writerows(stream_data)
        print("Data exported to csv.")

# %%
SYMBOLS = ["btcusdt", "ethusdt", "xrpusdt"]

agg_trade_service = BinanceWebsocketService("agg_trade", "agg_trade.csv")
kline_service = BinanceWebsocketService("kline", "kline.csv")
partial_book_depth_service = BinanceWebsocketService("partial_book_depth", "partial_book_depth.csv")

thread1 = threading.Thread(target=agg_trade_service.download_stream_data_to_csv,
                           kwargs={"symbols": SYMBOLS})
thread2 = threading.Thread(target=kline_service.download_stream_data_to_csv,
                           kwargs={"symbols": SYMBOLS, "interval": "1m"})
thread3 = threading.Thread(target=partial_book_depth_service.download_stream_data_to_csv,
                           kwargs={"symbols": SYMBOLS, "level": 10, "speed": 100})
                           
thread1.start()
thread2.start()
thread3.start()

thread1.join()
thread2.join()
thread3.join()

# %% [markdown]
# ## Load data from csv and compute statistics

# %%
# !pip install pandas
import pandas as pd

# %% [markdown]
# ### Agg_trade

# %%
agg_trade_df = pd.read_csv("agg_trade.csv")

# %%
# Preview of data
agg_trade_df.head()

# %%
# Check null values
agg_trade_df.isnull().sum()

# %%
# Number of rows for each symbol
agg_trade_df.groupby("s").size()

# %% [markdown]
# ### Kline

# %%
kline_df = pd.read_csv("kline.csv")

# %%
# Preview of data
kline_df.head()

# %%
# Check null values
kline_df.isnull().sum()

# %%
# Number of rows for each symbol
kline_df.groupby("s").size()

# %% [markdown]
# ### Partial_book_depth

# %%
partial_book_depth_df = pd.read_csv("partial_book_depth.csv")

# %%
# Preview of data
partial_book_depth_df.head()

# %%
# Check null values
partial_book_depth_df.isnull().sum()

# %%
# Number of rows for each symbol
partial_book_depth_df.groupby("s").size()

# %%
