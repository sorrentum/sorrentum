# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# - CCXT data = CCXT realtime bid-ask data collection for futures
# - CC data = CryptoChassis bid ask futures data

# %% [markdown]
# # Imports

# %%
import logging
import os

import pandas as pd

import core.config.config_ as cconconf
import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import helpers.hs3 as hs3
import helpers.hsql as hsql
import im_v2.ccxt.data.client as icdcl
import im_v2.crypto_chassis.data.client.crypto_chassis_clients as imvccdcccc
import im_v2.im_lib_tasks as imvimlita

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

_LOG.info("%s", henv.get_system_signature()[0])

hprint.config_notebook()


# %% [markdown]
# # Config

# %%
def get_cmtask2703_config() -> cconconf.Config:
    """
    Get task2360-specific config.
    """
    config = cconconf.Config()
    param_dict = {
        "data": {
            # Parameters for client initialization.
            "cc_im_client": {
                "universe_version": None,
                "resample_1min": True,
                "root_dir": os.path.join(
                    hs3.get_s3_bucket_path("ck"),
                    "reorg",
                    "daily_staged.airflow.pq",
                ),
                "partition_mode": "by_year_month",
                "dataset": "bid_ask",
                "contract_type": "futures",
                "data_snapshot": "",
                "aws_profile": "ck",
            },
            "ccxt_im_client": {
                "resample_1min": False,
                "db_connection": hsql.get_connection(
                    *hsql.get_connection_info_from_env_file(
                        imvimlita.get_db_env_path("dev")
                    )
                ),
                "table_name": "ccxt_bid_ask_futures_test",
            },
            # Parameters for data query.
            "read_data": {
                # DB data starts from here.
                "start_ts": pd.Timestamp("2022-09-08 22:06:00+00:00"),
                "end_ts": pd.Timestamp("2022-09-12 00:00:00+00:00"),
                "columns": None,
                "filter_data_mode": "assert",
            },
        },
        "column_names": {
            "bid_ask_cols": [
                "bid_price",
                "bid_size",
                "ask_price",
                "ask_size",
                "full_symbol",
            ],
        },
    }
    config = cconconf.Config.from_dict(param_dict)
    return config


config = get_cmtask2703_config()
print(config)


# %% [markdown]
# # Functions

# %%
def load_and_transform_the_data(
    universe,
    bid_ask_cols,
    is_ccxt: bool,
    start_ts,
    end_ts,
    columns,
    filter_data_mode,
):
    if is_ccxt:
        df = cc_parquet_client.read_data(
            universe, start_ts, end_ts, columns, filter_data_mode
        )
    else:
        df = ccxt_im_client.read_data(
            universe, start_ts, end_ts, columns, filter_data_mode
        )
        df.index = df.reset_index()["timestamp"].apply(
            lambda x: x.round(freq="T")
        )
    df = df[bid_ask_cols]
    df = df.reset_index().set_index(["timestamp", "full_symbol"])
    return df


# %% [markdown]
# # Initiate clients

# %% run_control={"marked": false}
# CCXT client.
ccxt_im_client = icdcl.CcxtSqlRealTimeImClient(**config["data"]["ccxt_im_client"])
# CC client.
cc_parquet_client = imvccdcccc.CryptoChassisHistoricalPqByTileClient(
    **config["data"]["cc_im_client"]
)

# %% [markdown]
# # Specify universe

# %%
# DB universe
ccxt_universe = ccxt_im_client.get_universe()
# CC universe.
cc_universe = cc_parquet_client.get_universe()
# Intersection of universes that will be used for analysis.
universe = list(set(ccxt_universe) & set(cc_universe))

# %%
compare_universe = hprint.set_diff_to_str(
    cc_universe, ccxt_universe, add_space=True
)
print(compare_universe)

# %% [markdown]
# # Load the data

# %% [markdown]
# ## Adjust universe

# %%
# Even though they're in the intersected universe,
# they are not downloaded in CC.
universe.remove("binance::XRP_USDT")
universe.remove("binance::DOT_USDT")
universe

# %% [markdown]
# ## Load data

# %%
# CCXT data.
bid_ask_cols = config["column_names"]["bid_ask_cols"]
is_ccxt = True

data_ccxt = load_and_transform_the_data(
    universe, bid_ask_cols, is_ccxt, **config["data"]["read_data"]
)

# %%
# CC data.
is_ccxt = False

data_cc = load_and_transform_the_data(
    universe, bid_ask_cols, is_ccxt, **config["data"]["read_data"]
)

# %% [markdown]
# # Analysis

# %% [markdown]
# ## Merge CC and DB data into one DataFrame

# %%
data = data_ccxt.merge(
    data_cc,
    how="outer",
    left_index=True,
    right_index=True,
    suffixes=("_ccxt", "_cc"),
)
_LOG.info("Start date = %s", data.reset_index()["timestamp"].min())
_LOG.info("End date = %s", data.reset_index()["timestamp"].max())
_LOG.info(
    "Avg observations per coin = %s",
    len(data) / len(data.reset_index()["full_symbol"].unique()),
)
# Move the same metrics from two vendors together.
data = data.reindex(sorted(data.columns), axis=1)
# NaNs observation.
_LOG.info(
    "Number of observations with NaNs in CryptoChassis = %s",
    len(data[data["bid_price_cc"].isna()]),
)
_LOG.info(
    "Number of observations with NaNs in CCXT = %s",
    len(data[data["bid_price_ccxt"].isna()]),
)
# Remove NaNs.
data = hpandas.dropna(data, report_stats=True)

display(data.tail())

# %% [markdown]
# ## Calculate differences

# %%
# Full symbol will not be relevant in calculation loops below.
bid_ask_cols.remove("full_symbol")
# Each bid ask value will have a notional and a relative difference between two sources.
for col in bid_ask_cols:
    # Notional difference: CC value - DB value.
    data[f"{col}_diff"] = data[f"{col}_cc"] - data[f"{col}_ccxt"]
    # Relative value: (CC value - DB value)/DB value.
    data[f"{col}_relative_diff_pct"] = (
        100 * (data[f"{col}_cc"] - data[f"{col}_ccxt"]) / data[f"{col}_ccxt"]
    )

data.head()

# %%
# Calculate the mean value of differences for each coin.
diff_stats = []
grouper = data.groupby(["full_symbol"])
for col in bid_ask_cols:
    diff_stats.append(grouper[f"{col}_diff"].mean())
    diff_stats.append(grouper[f"{col}_relative_diff_pct"].mean())

diff_stats = pd.concat(diff_stats, axis=1)

# %% [markdown]
# ## Show stats for differences

# %% [markdown]
# ### Prices

# %%
diff_stats[["bid_price_relative_diff_pct", "ask_price_relative_diff_pct"]]

# %% [markdown]
# As one can see, the difference between bid and ask prices in DB and CC are less than 1%.

# %% [markdown]
# ### Sizes

# %%
diff_stats[["bid_size_relative_diff_pct", "ask_size_relative_diff_pct"]]

# %% [markdown]
# The difference between bid and ask sizes in DB and CC is solid and accounts for more than 100% for each full symbol.

# %% [markdown]
# ## Correlations

# %% [markdown]
# ### Bid price

# %%
bid_price_corr_matrix = (
    data[["bid_price_cc", "bid_price_ccxt"]].groupby(level=1).corr()
)
bid_price_corr_matrix

# %% [markdown]
# Correlation stats confirms the stats above: bid prices in DB and CC are highly correlated.

# %% [markdown]
# ### Ask price

# %%
ask_price_corr_matrix = (
    data[["ask_price_cc", "ask_price_ccxt"]].groupby(level=1).corr()
)
ask_price_corr_matrix

# %% [markdown]
# Correlation stats confirms the stats above: ask prices in DB and CC are highly correlated.

# %% [markdown]
# ### Bid size

# %%
bid_size_corr_matrix = (
    data[["bid_size_cc", "bid_size_ccxt"]].groupby(level=1).corr()
)
bid_size_corr_matrix

# %% [markdown]
# Correlation stats confirms the stats above: bid sizes in DB and CC are not correlated.

# %% [markdown]
# ### Ask size

# %%
ask_size_corr_matrix = (
    data[["ask_size_cc", "ask_size_ccxt"]].groupby(level=1).corr()
)
ask_size_corr_matrix

# %% [markdown]
# Correlation stats confirms the stats above: ask sizes in DB and CC are not correlated.
