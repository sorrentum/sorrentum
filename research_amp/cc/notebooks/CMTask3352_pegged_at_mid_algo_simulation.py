# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Description

# %% [markdown]
# The notebook simulates the performance of a "pegged-at-mid" trading algorithm.
#
# - Load the 1sec bid/ask data
# - Conduct a sanity check
# - Calculate the midpoint limit buy/sell prices
# - Aggregate to 5T and check the success of trades in historical data
#
# ```
# dataset_signature=periodic.airflow.downloaded_EOD.parquet.bid_ask.futures.v3.cryptochassis.binance.v1_0_0
# ```

# %%
# %load_ext autoreload
# %autoreload 2
import logging

import pandas as pd

import core.config as cconfig
import core.finance as cofinanc
import dataflow.core as dtfcore
import dataflow.system as dtfsys
import dataflow.universe as dtfuniver
import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import im_v2.crypto_chassis.data.client as iccdc
import market_data as mdata

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

_LOG.info("%s", henv.get_system_signature()[0])

hprint.config_notebook()

# %% [markdown]
# # Load CryptoChassis data.

# %% [markdown]
# - Latest universe (v3)
# - Resampled to 1sec
# - For 1 asset and 1 day
# - Using DataFlow `read_data` node

# %% [markdown]
# ## Initialize a config for `read_data` node

# %%
dict_ = {
    "load_data": {
        "start_ts": pd.Timestamp("2022-12-14 00:00:00+00:00"),
        "end_ts": pd.Timestamp("2022-12-15 00:00:00+00:00"),
    },
    "universe": {
        "full_symbols": ["binance::ADA_USDT"],
    },
}
config = cconfig.Config.from_dict(dict_)

# %%
# Set up the parameters for initialization of the IM Client.
universe_version = "v3"
resample_1min = False
contract_type = "futures"
tag = "downloaded_1sec"
client = iccdc.get_CryptoChassisHistoricalPqByTileClient_example2(
    universe_version, resample_1min, contract_type, tag
)

# %%
start_ts = config.get_and_mark_as_used(("load_data", "start_ts"))
end_ts = config.get_and_mark_as_used(("load_data", "end_ts"))

intervals = [
    (
        start_ts,
        end_ts,
    ),
]

# %%
# Verify that provided symbols are present in the client.
universe_full_symbols = dtfuniver.get_universe("crypto_chassis_v3-all")
config_full_symbols = config.get_and_mark_as_used(("universe", "full_symbols"))
hdbg.dassert_is_subset(config_full_symbols, universe_full_symbols)
# Convert to asset ids.
config["universe"]["asset_ids"] = client.get_asset_ids_from_full_symbols(
    config_full_symbols
)
asset_ids = config.get_and_mark_as_used(("universe", "asset_ids"))

# %%
# Initialize market data.
columns = None
columns_remap = None
wall_clock_time = pd.Timestamp("2100-01-01T00:00:00+00:00")
stage = "read_data"
ts_col_name = "end_ts"
multiindex_output = True
col_names_to_remove = []
market_data = mdata.get_HistoricalImClientMarketData_example1(
    client,
    asset_ids,
    columns,
    columns_remap,
)


# %% [markdown]
# ## Initialize DAG

# %%
def _run_dag_node(dag):
    dag_runner = dtfcore.FitPredictDagRunner(dag)
    dag_runner.set_fit_intervals(intervals)
    fit_result_bundle = dag_runner.fit()
    df = fit_result_bundle.result_df
    return df


# %%
# Create an empty DAG.
dag = dtfcore.DAG(mode="strict")
dtfcore.draw(dag)

# %%
# TODO(gp): @danya, see if we have also close or trade.
stage = "read_data"
ts_col_name = "end_ts"
multiindex_output = True
col_names_to_remove = []
node = dtfsys.HistoricalDataSource(
    stage,
    market_data,
    ts_col_name,
    multiindex_output,
    col_names_to_remove=col_names_to_remove,
)
dag.insert_at_head(node)
dtfcore.draw(dag)

# %% [markdown]
# ## Read data

# %%
df_original = _run_dag_node(dag)
df_original.shape
df_original.head(5)

# %%
# Drop multiindex in single-asset dataframes for human readability.
if len(asset_ids) < 2:
    df_flat = df_original.droplevel(1, axis=1)
else:
    df_flat = df_original.copy()

# %%
df_flat.head()

# %% [markdown]
# ## Sanity check

# %% [markdown]
# A quick sanity-check for the following:
# - What percentage of 1 sec bars are missing?
# - How often is bid_size = 0, ask_size = 0, volume=0?
# - How often is bid !< ask?
#

# %%
# Check for missing data.
df_flat.isna().sum()

# %%
# Check for zeroes.
(df_flat == 0).astype(int).sum(axis=1).sum()

# %% run_control={"marked": false}
# Check bid price !< ask price.
(df_flat["bid_price"] >= df_flat["ask_price"]).any().any()

# %%
df_flat.head()

# %%
# Check the gaps inside the time series.
index_as_series = df_flat.index.to_series()
freq = "S"
gaps_in_seconds = hpandas.find_gaps_in_time_series(
    index_as_series, start_ts, end_ts, freq
)
gaps_in_seconds = gaps_in_seconds.to_series()

# %%
gaps_percent = len(gaps_in_seconds) / (len(df_flat) + len(gaps_in_seconds)) * 100
average_gap = gaps_in_seconds.diff().mean()
print(
    f"Overall {len(gaps_in_seconds)} gaps were found, \
for {gaps_percent}%% of all seconds in the given period, for an average frequency of {average_gap}"
)

# %%
# Display gaps distribution by hour.
gaps_in_seconds.groupby(gaps_in_seconds.dt.hour).count().plot(kind="bar")

# %% [markdown]
# ### Commentary

# %% [markdown]
# - No NaNs or zeroes were found with a simple general check, there is no need for an in-depth look.
# - 575 gaps were found, that mostly concentrate between 0am and 5am.

# %% [markdown]
# ## Augment data with new features

# %%
# Append `mid` data.
# # (bid + ask) / 2.
bid_col = "bid_price"
ask_col = "ask_price"
bid_volume_col = "bid_size"
ask_volume_col = "ask_size"
requested_cols = ["mid"]
join_output_with_input = True
df_mid = cofinanc.process_bid_ask(
    df_flat,
    bid_col,
    ask_col,
    bid_volume_col,
    ask_volume_col,
    requested_cols=requested_cols,
    join_output_with_input=join_output_with_input,
)
df_mid.head(10)

# %%
print(df_mid.shape)
print(df_mid.index.min())
print(df_mid.index.max())

# %%
df_features = df_mid.copy()

# %%
df_features["ask_value"] = df_features["ask_price"] * df_features["ask_size"]
df_features["bid_value"] = df_features["bid_price"] * df_features["bid_size"]

# This is really high. 100m USD per hour on top of the book.
df_features[["bid_value", "ask_value"]].resample("1H").sum().plot()


# %%
def add_limit_order_prices(df: pd.DataFrame, mid_col_name: str, *, resample_freq = "1T", passivity_factor = None, abs_spread = None):

    limit_buy_col = "limit_buy_price"
    limit_sell_col = "limit_sell_price"
    limit_buy_srs = df[mid_col_name]
    limit_buy_srs = limit_buy_srs.rename(limit_buy_col)
    limit_sell_srs = df[mid_col_name]
    limit_sell_srs = limit_sell_srs.rename(limit_buy_col)
    #
    if resample_freq:
        limit_buy_srs = limit_buy_srs.resample(resample_freq)
        limit_sell_srs = limit_sell_srs.resample(resample_freq)
    #
    limit_buy_srs = limit_buy_srs.mean().shift(1)
    limit_sell_srs = limit_sell_srs.mean().shift(1)
    #
    if abs_spread is not None and passivity_factor is None:
        limit_buy_srs = limit_buy_srs - abs_spread
        limit_sell_srs = limit_sell_srs + abs_spread
    elif passivity_factor is not None and abs_spread is None:
        limit_buy_srs = limit_buy_srs * (1 - passivity_factor)
        limit_sell_srs = limit_sell_srs * (1 - passivity_factor)
    df_limit_price = pd.DataFrame()
    df_limit_price[limit_buy_col] = limit_buy_srs
    df_limit_price[limit_sell_col] = limit_sell_srs
    df = df.merge(df_limit_price, right_index=True, left_index=True, how="outer")
    #
    df[limit_buy_col] = df[limit_buy_col].ffill()
    df[limit_sell_col] = df[limit_sell_col].ffill()
    return df


# %% run_control={"marked": false}
df_limit_order_prices = add_limit_order_prices(df_features,
                                              "mid",
                                              abs_spread = 0.0001)

# %%
df_limit_order_prices.head()

# %%
print(df_features.shape)





# %%
print(df_limit_order_prices.shape)




# %% run_control={"marked": true}
diff = df_limit_order_prices.index.difference(df_features.index)



# %%
df_limit_order_prices.loc[diff]




# %%
df_flat.loc[pd.Timestamp("2022-12-13 22:25:59-05:00"): pd.Timestamp("2022-12-13 22:27:00-05:00")]

# %% [markdown]
# #### Commentary

# %% [markdown]
# As we have seen during the sanity check above, missing data can congregate around certain time points.
#
# For the 4 missing minutes were minutes where the initial second was missing, and then added in the function due to due to resampling.

# %%
# TODO(gp): Not sure this is working as expected. I don't see the seconds.
# Assigning df columns with a df series with different time index might subsample.
# I would do a outmerge merge and then ffill.

# Let's always check the output of the df to make sure things are sane.
df4





# %% [markdown]
# #### Rechecking whether any rows disappeared

# %%

# %%
# TODO(gp): @Danya
# def perform_spread_analysys(...)

# %%
spread = df4["ask_price"] - df4["bid_price"]
spread_in_bps = spread / df4["mid"] * 1e4

# %%
spread.hist(bins=101)

# %%
spread.plot()

# %%
spread_in_bps.plot()

# %%
# TODO(gp): Create a function:
# plot_limit_orders(df, start_timestamp: Optional[pd.timestamp] = None, end_timestamp:Optional[pd.Timestamp] = None)
df4[
    ["mid", "ask_price", "bid_price", "limit_buy_price", "limit_sell_price"]
].head(1000).plot()

(df4[["is_buy", "is_sell"]] * 1.0).head(1000).plot()

# %% [markdown]
# ## Resample to T_reprice

# %%
print(df4.shape)

# %%
# TODO(gp): @danya compute_repricing_df(df, report_stats):

# TODO(gp): ask_price -> buy_limit?
df4["exec_buy_price"] = df4["is_buy"] * df4["ask_price"]
mask = ~df4["is_buy"]
df4["exec_buy_price"][mask] = np.nan

# df4["exec_price"].plot()
# df4["exec_price"].mean()

# TODO(gp): Not sure this does what we want. We want to average only the values that are not nan.
# df4["exec_buy_price"].resample("5T").mean()

df4["exec_sell_price"] = df4["is_sell"] * df4["bid_price"]

mask = ~df4["is_sell"]
df4["exec_sell_price"][mask] = np.nan

# df4["exec_price"].plot()
# df4["exec_price"].mean()

# %%
# Display as percentages.
# if report_stats:
print("buy percentage at repricing freq: ", df4["is_buy"].sum() / df4.shape[0])
print(df4["is_sell"].sum() / df4.shape[0])
#
print(hprint.perc(df4["exec_buy_price"].isnull().sum(), df4.shape[0]))
print(hprint.perc(df4["exec_sell_price"].isnull().sum(), df4.shape[0]))

# %% [markdown]
# ## Resample to T_exec

# %%
# TODO(gp): @danya ->
# def compute_execution_df(df, t_exec: str, report_stats)

df5 = pd.DataFrame()
# Count how many executions there were in an interval.
df5["exec_buy_num"] = df4["is_buy"].resample("5T").sum()
df5["exec_buy_price"] = df4["exec_buy_price"].resample("5T").mean()
df5["exec_is_buy"] = df5["exec_buy_num"] > 0
print(hprint.perc(df5["exec_is_buy"].sum(), df5["exec_is_buy"].shape[0]))

# Estimate the executed volume.
df5["exec_buy_volume"] = (
    (df4["ask_size"] * df4["ask_price"] * df4["is_buy"]).resample("5T").sum()
)
print("million USD per 5T=", df5["exec_buy_volume"].mean() / 1e6)
# Estimate price as average of executed price.
# exec_buy_price = (close * exec_is_buy).groupby("5T").sum() / exec_buy_num

# Same for sell.
# exec_sell_volume = (is_sell * bid_size).group("5T").sum()
# exec_sell_price = (close * exec_is_sell).groupby("5T").sum() / exec_sell_num

df5["exec_sell_num"] = df4["is_sell"].resample("5T").sum()
df5["exec_sell_price"] = df4["exec_sell_price"].resample("5T").mean()
df5["exec_is_sell"] = df5["exec_sell_num"] > 0
print(hprint.perc(df5["exec_is_sell"].sum(), df5["exec_is_sell"].shape[0]))

# Estimate the executed volume.
df5["exec_sell_volume"] = (
    (df4["bid_size"] * df4["bid_price"] * df4["is_sell"]).resample("5T").sum()
)
print("million USD per 5T=", df5["exec_sell_volume"].mean() / 1e6)

# %% [markdown]
# ## Compare to benchmark price.

# %%
# TODO(gp): @danya
# def compute_benchmark_stats(...)

# %%
# This is the benchmark.
df5["twap_mid_price"] = df4["mid"].resample("5T").mean()

df5[["twap_mid_price", "exec_sell_price", "exec_buy_price"]].head(1000).plot()

# %%
slippage = df5[["twap_mid_price", "exec_sell_price", "exec_buy_price"]]

slippage["sell_slippage_bps"] = (
    (df5["exec_sell_price"] - df5["twap_mid_price"]) / df5["twap_mid_price"] * 1e4
)

# slippage = df["twap_mid_price"] /

slippage["sell_slippage_bps"].hist(bins=21)

print("sell_slippage_bps.mean=", slippage["sell_slippage_bps"].mean())
print("sell_slippage_bps.median=", slippage["sell_slippage_bps"].median())

# %%
df5.head()

# %% [markdown]
# ### Commentary

# %% [markdown]
# The quick look into the rate of successful trades indicated that for the given asset (`ADA/USDT`) and the date the successful "buy" order can be met for 16% of the time and a "sell" order is not met at all.
