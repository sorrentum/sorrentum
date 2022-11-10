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

# %%
# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# %%
import logging
import os
import pprint

import numpy as np
import pandas as pd

import core.config as cconfig
import core.finance as cofinanc
import core.plotting as coplotti
import dataflow.model as dtfmod
import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import helpers.hsql as hsql
import im_v2.ccxt.data.client as icdcl
import im_v2.common.universe as ivcu
import im_v2.im_lib_tasks as imvimlita
import oms as oms

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

_LOG.info("%s", henv.get_system_signature()[0])

hprint.config_notebook()

# %% [markdown]
# # Config

# %%
#date_str = "20221028"
#date_str = "20221031"
#date_str = "20221103"
#date_str = "20221104"
date_str = "20221107"
#prod_subdir = "system_log_dir_manual__2022-11-01T12:39:45.395761+00:00_2hours"
prod_subdir = "system_log_dir_manual__2022-11-07T15:12:00.832111+00:00_2hours"
#prod_subdir = None
config_list = oms.build_reconciliation_configs(date_str, prod_subdir)
config = config_list[0]
print(config)

# %% run_control={"marked": true}
system_log_path_dict, portfolio_path_dict, dag_path_dict = oms.get_path_dicts(config, log_level=logging.INFO)

# %%
date_str = config["meta"]["date_str"]
# TODO(gp): @Grisha infer this from the data from prod Portfolio df, but allow to overwrite.
if True:
    start_time = "10:15:00"
    end_time = "12:10:00"
else:
    start_time = "08:45:00"
    end_time = "10:40:00"
start_timestamp = pd.Timestamp(date_str + " " + start_time, tz="America/New_York")
end_timestamp = pd.Timestamp(date_str + " " + end_time, tz="America/New_York")
_LOG.info("start_timestamp=%s", start_timestamp)
_LOG.info("end_timestamp=%s", end_timestamp)


# %% [markdown]
# # Compare configs

# %%
# This dict points to `system_log_dir/process_forecasts/portfolio` for different experiments.
data_type = "portfolio"
portfolio_path_dict = oms.get_system_log_paths(system_log_path_dict, data_type)
portfolio_path_dict

# %%
# # Get the universe.
# # TODO(Grisha): get the version from the config.
# vendor = "CCXT"
# mode = "trade"
# version = "v7.1"
# as_full_symbol = True
# full_symbols = ivcu.get_vendor_universe(
#     vendor,
#     mode,
#     version=version,
#     as_full_symbol=as_full_symbol,
# )
# full_symbols

# %%
# # Load the data for the reconciliation date.
# # `ImClient` operates in UTC timezone.
# start_ts = pd.Timestamp(date_str, tz="UTC")
# end_ts = start_ts + pd.Timedelta(days=1)
# columns = None
# filter_data_mode = "assert"
# df = im_client.read_data(
#     full_symbols, start_ts, end_ts, columns, filter_data_mode
# )
# hpandas.df_to_str(df, num_rows=5, log_level=logging.INFO)

# %%
# # TODO(Grisha): move to a lib.
# # Compute delay in seconds.
# df["delta"] = (df["knowledge_timestamp"] - df.index).dt.total_seconds()
# # Plot the delay over assets with the errors bars.
# minimums = df.groupby(by=["full_symbol"]).min()["delta"]
# maximums = df.groupby(by=["full_symbol"]).max()["delta"]
# means = df.groupby(by=["full_symbol"]).mean()["delta"]
# errors = [means - minimums, maximums - means]
# df.groupby(by=["full_symbol"]).mean()["delta"].sort_values(ascending=False).plot(
#     kind="bar", yerr=errors
# )

# %% [markdown]
# # Compare configs (prod vs vim)

# %%
configs = oms.load_config_from_pickle(system_log_path_dict)
# Diff configs.
# TODO(Grisha): the output is only on subconfig level, we should
# compare value vs value instead.
diff_config = cconfig.build_config_diff_dataframe(
    {
        "prod_config": configs["prod"],
        "sim_config": configs["sim"],
    }
)
diff_config.T

# %% [markdown]
# # DAG io

# %% [markdown]
# ## Compare DAG io (prod vs sim)

# %%
if False:
    file_name1 = "/shared_data/prod_reconciliation/20221025/prod/system_log_dir_scheduled__2022-10-24T10:00:00+00:00_2hours/dag/node_io/node_io.data/predict.8.process_forecasts.df_out.20221025_061000.parquet"
    df1 = pd.read_parquet(file_name1)

    file_name2 = "/shared_data/prod_reconciliation/20221025/simulation/system_log_dir/dag/node_io/node_io.data/predict.8.process_forecasts.df_out.20221025_061000.parquet"
    df2 = pd.read_parquet(file_name2)

    #asset_id = 1030828978
    asset_id = 9872743573
    #df1['vwap.ret_0.vol_adj_2_hat', asset_id] == df2['vwap.ret_0.vol_adj_2_hat', asset_id]
    #column = 'vwap.ret_0.vol_adj_2_hat'
    column = 'close'

    #pd.concat()

    compare_visually_dataframes_kwargs = {"diff_mode": "pct_change", "background_gradient": False}
    subset_multiindex_df_kwargs = {"columns_level0": [column],
                                   #"columns_level1": [asset_id]
                                  }

    hpandas.compare_multiindex_dfs(df1, df2,
                                   subset_multiindex_df_kwargs=subset_multiindex_df_kwargs,
                                   compare_visually_dataframes_kwargs=compare_visually_dataframes_kwargs )#.dropna().abs().max()

# %% [markdown]
# ## Read last node

# %%
# Select a specific node and timestamp to analyze.
log_level = logging.DEBUG
dag_node_names = oms.get_dag_node_names(dag_path_dict["prod"], log_level=log_level)
dag_node_name = dag_node_names[-1]
print(hprint.to_str("dag_node_name"))

dag_node_timestamps = oms.get_dag_node_timestamps(
    dag_path_dict["prod"], dag_node_name, as_timestamp=True, log_level=log_level
)

dag_node_timestamp = dag_node_timestamps[-1][0]
print("dag_node_timestamp=%s" % str(dag_node_timestamp))

# %%
# Load DAG output for different experiments.
dag_start_timestamp = None
dag_end_timestamp = None
dag_df_dict = oms.load_dag_outputs(
    dag_path_dict,
    # TODO(Grisha): maybe load just the last node and timestamp otherwise
    # it takes 2 minutes to load the data.
    only_last_node=False,
    only_last_timestamp=False,
)
# Get DAG output for the last node and the last timestamp.
# TODO(Grisha): use 2 dicts -- one for the last node, last timestamp,
# the other one for all nodes, all timestamps for comparison.
dag_df_prod = dag_df_dict["prod"][dag_node_names[-1]][dag_node_timestamps[-1][0]]
dag_df_sim = dag_df_dict["sim"][dag_node_names[-1]][dag_node_timestamps[-1][0]]
hpandas.df_to_str(dag_df_prod, num_rows=5, log_level=logging.INFO)

# %%
compare_dfs_kwargs ={
    "diff_mode": "pct_change",
    "assert_diff_threshold": None,
}
dag_diff_df = oms.compute_dag_outputs_diff(
    dag_df_dict, compare_dfs_kwargs
)

# %%
max_diff = dag_diff_df.abs().max().max()
_LOG.info("Maximum absolute difference for DAG output=%s", max_diff)

# %%
if False:
    dag_diff_detailed_stats = oms.compute_dag_output_diff_detailed_stats(
        dag_diff_df
    )

# %%
if False:
    # Compute correlations.
    prod_sim_dag_corr = dtfmod.compute_correlations(
        dag_df_prod,
        dag_df_sim,
    )
    hpandas.df_to_str(
        prod_sim_dag_corr.min(),
        num_rows=None,
        precision=3,
        log_level=logging.INFO,
    )

# %% [markdown]
# ## Compute DAG delay

# %%
delay_in_secs = oms.compute_dag_delay_in_seconds(dag_node_timestamps, display_plot=False)

# %% [markdown]
# # Portfolio

# %% [markdown]
# ## Compute research portfolio equivalent

# %%
if False:
    # Compute correlations.
    prod_sim_dag_corr = dtfmod.compute_correlations(
        dag_df_dict["prod"],
        dag_df_dict["sim"],
    )
    hpandas.df_to_str(
        prod_sim_dag_corr.min(),
        num_rows=None,
        precision=3,
        log_level=logging.INFO,
    )

# %% [markdown]
# # Compute research portfolio

# %%
# Build the ForecastEvaluator.
forecast_evaluator_from_prices_kwargs = config["research_forecast_evaluator_from_prices"]["init"]
print(hprint.to_str("forecast_evaluator_from_prices_kwargs", mode="pprint"))
fep = dtfmod.ForecastEvaluatorFromPrices(**forecast_evaluator_from_prices_kwargs)
# Run.
annotate_forecasts_kwargs = config["research_forecast_evaluator_from_prices"][
    "annotate_forecasts_kwargs"
]
print(hprint.to_str("annotate_forecasts_kwargs", mode="pprint"))
research_portfolio_df, research_portfolio_stats_df = fep.annotate_forecasts(
    dag_df_dict["prod"],
    **annotate_forecasts_kwargs.to_dict(),
    compute_extended_stats=True,
)
# TODO(gp): Move it to annotate_forecasts?
research_portfolio_df = research_portfolio_df.sort_index(axis=1)

# Align index with prod and sim portfolios.
research_portfolio_df = research_portfolio_df.loc[start_timestamp:end_timestamp]
research_portfolio_stats_df = research_portfolio_stats_df.loc[
    start_timestamp:end_timestamp
]
#
hpandas.df_to_str(research_portfolio_stats_df, num_rows=5, log_level=logging.INFO)

# %% [markdown]
# ## Load logged portfolios (prod & sim)

# %%
portfolio_config = cconfig.Config.from_dict(
    {
        "start_timestamp": start_timestamp,
        "end_timestamp": end_timestamp,
        "freq": config["meta"]["bar_duration"],
        "normalize_bar_times": True,
    }
)
portfolio_config.to_dict()

# %%
portfolio_dfs, portfolio_stats_dfs = oms.load_portfolio_dfs(
    portfolio_path_dict,
    portfolio_config,
)
# Add research portfolio.
portfolio_dfs["research"] = research_portfolio_df
#
hpandas.df_to_str(portfolio_dfs["prod"], num_rows=5, log_level=logging.INFO)

# %%
# Add research df and combine into a single df.
portfolio_stats_dfs["research"] = research_portfolio_stats_df
portfolio_stats_df = pd.concat(portfolio_stats_dfs, axis=1)
#
hpandas.df_to_str(portfolio_stats_df[["prod", "research"]], num_rows=5, log_level=logging.INFO)

# %% [markdown]
# ## Compute Portfolio statistics (prod vs research vs sim)

# %%
bars_to_burn = 1
coplotti.plot_portfolio_stats(portfolio_stats_df.iloc[bars_to_burn:])

# %%
stats_computer = dtfmod.StatsComputer()
stats_sxs, _ = stats_computer.compute_portfolio_stats(
    portfolio_stats_df.iloc[bars_to_burn:], config["meta"]["bar_duration"]
)
display(stats_sxs)

# %% [markdown]
# ## Compare portfolios pairwise (prod vs research vs sim)

# %% [markdown]
# ### Differences

# %% [markdown]
# #### Prod vs sim

# %%
report_stats = False
display_plot = False
compare_dfs_kwargs = {
    "column_mode": "inner",
    "diff_mode": "pct_change",
    "remove_inf": True,
    "assert_diff_threshold": None,
}
portfolio_diff_df = oms.compare_portfolios(
    portfolio_dfs,
    report_stats=report_stats,
    display_plot=display_plot,
    compare_dfs_kwargs=compare_dfs_kwargs,
)
hpandas.df_to_str(portfolio_diff_df, num_rows=None, log_level=logging.INFO)

# %% [markdown]
# ### Correlations

# %% [markdown]
# #### Prod vs sim

# %%
if False:
    dtfmod.compute_correlations(
        portfolio_dfs["prod"],
        portfolio_dfs["sim"],
        allow_unequal_indices=False,
        allow_unequal_columns=False,
    )

# %% [markdown]
# #### Prod vs research

# %%
if False:
    dtfmod.compute_correlations(
        research_portfolio_df,
        portfolio_dfs["prod"],
        allow_unequal_indices=True,
        allow_unequal_columns=True,
    )

# %% [markdown]
# #### Sim vs research

# %%
if False:
    dtfmod.compute_correlations(
        research_portfolio_df,
        portfolio_dfs["sim"],
        allow_unequal_indices=True,
        allow_unequal_columns=True,
    )

# %% [markdown]
# # Target positions

# %% [markdown]
# ## Load target positions (prod)

# %%
prod_target_position_df = oms.load_target_positions(
    portfolio_path_dict["prod"].strip("portfolio"),
    start_timestamp,
    end_timestamp,
    config["meta"]["bar_duration"],
    normalize_bar_times=True
)
hpandas.df_to_str(prod_target_position_df, num_rows=5, log_level=logging.INFO)
if False:
    # TODO(Grisha): compare prod vs sim at some point.
    sim_target_position_df = oms.load_target_positions(
        portfolio_path_dict["sim"].strip("portfolio"),
        start_timestamp,
        end_timestamp,
        config["meta"]["bar_duration"],
        normalize_bar_times=True
    )

# %% [markdown]
# ## Compare positions target vs executed (prod)

# %%
# TODO(Grisha): use `hpandas.compare_dfs()`.
df1 = prod_target_position_df["target_holdings_shares"].shift(1)
df2 = prod_target_position_df["holdings_shares"]
diff = df1 - df2
hpandas.df_to_str(diff, num_rows=5, log_level=logging.INFO)

# %% [markdown]
# ## Compare target positions (prod vs research)

# %% [markdown]
# ### Price

# %% run_control={"marked": true}
# TODO(Grisha): wrap in a function since it's common for all columns.
column = "price"
prod_df = prod_target_position_df[column]
res_df = research_portfolio_df[column]

# Compute percentage difference.
diff_df = hpandas.compare_dfs(
    prod_df,
    res_df,
    diff_mode= "pct_change",
)
# Remove the sign and NaNs.
diff_df = diff_df.abs()
# Check that data is the same.
print(diff_df.max().max())
if False:
    hpandas.heatmap_df(diff_df.round(2))

# %% [markdown]
# ### Volatility

# %%
column = "volatility"
prod_df = prod_target_position_df[column]
res_df = research_portfolio_df[column]

# Compute percentage difference.
diff_df = hpandas.compare_dfs(
    prod_df,
    res_df,
    diff_mode= "pct_change",
)
# Remove the sign and NaNs.
diff_df = diff_df.abs()
# Check that data is the same.
print(diff_df.max().max())
if False:
    hpandas.heatmap_df(diff_df.round(2))

# %% [markdown]
# ### Prediction

# %%
column = "prediction"
prod_df = prod_target_position_df[column]
res_df = research_portfolio_df[column]

# Compute percentage difference.
diff_df = hpandas.compare_dfs(
    prod_df,
    res_df,
    diff_mode= "pct_change",
)
# Remove the sign and NaNs.
diff_df = diff_df.abs()
# Check that data is the same.
print(diff_df.max().max())
if False:
    hpandas.heatmap_df(diff_df.round(2))

# %% [markdown]
# ### Current holdings

# %%
column = "holdings_shares"
prod_df = prod_target_position_df[column]
res_df = research_portfolio_df[column]

# Compute percentage difference.
diff_df = hpandas.compare_dfs(
    prod_df,
    res_df,
    diff_mode= "pct_change",
    assert_diff_threshold=None,
)
# Remove the sign and NaNs.
diff_df = diff_df.abs()
# Check that data is the same.
print(diff_df.max().max())
if False:
    hpandas.heatmap_df(diff_df.round(2))

# %% [markdown]
# ### Target holdings

# %% [markdown]
# ## Prod vs sim

# %%
prod_df = prod_target_position_df["target_holdings_shares"].shift(1)
res_df = research_portfolio_df["holdings_shares"]

# Compute percentage difference.
diff_df = hpandas.compare_dfs(
    prod_df,
    res_df,
    diff_mode= "pct_change",
    assert_diff_threshold=None,
)
# Remove the sign and NaNs.
diff_df = diff_df.abs()
# Check that data is the same.
print(diff_df.max().max())
if False:
    hpandas.heatmap_df(diff_df.round(2))

# %% [markdown]
# # Orders 

# %% [markdown]
# ## Load orders (prod & sim)

# %%
prod_order_df = oms.TargetPositionAndOrderGenerator.load_orders(
    portfolio_path_dict["prod"].strip("portfolio"),
)
hpandas.df_to_str(prod_order_df, num_rows=5, log_level=logging.INFO)
sim_order_df = oms.TargetPositionAndOrderGenerator.load_orders(
    portfolio_path_dict["sim"].strip("portfolio"),
)
hpandas.df_to_str(sim_order_df, num_rows=5, log_level=logging.INFO)

# %% [markdown]
# ## Compare orders (prod vs sim)

# %%
# TODO(Grisha): add comparison using the usual `pct_change` approach.

# %% [markdown]
# # Fills statistics

# %%
fills = oms.compute_fill_stats(prod_target_position_df)
hpandas.df_to_str(fills, num_rows=5, log_level=logging.INFO)
fills["fill_rate"].plot()

# %% [markdown]
# # Slippage

# %%
slippage = oms.compute_share_prices_and_slippage(portfolio_dfs["prod"])
hpandas.df_to_str(slippage, num_rows=5, log_level=logging.INFO)
slippage["slippage_in_bps"].plot()

# %%
stacked = slippage[["slippage_in_bps", "is_benchmark_profitable"]].stack()
stacked[stacked["is_benchmark_profitable"] > 0]["slippage_in_bps"].hist(bins=31)
stacked[stacked["is_benchmark_profitable"] < 0]["slippage_in_bps"].hist(bins=31)

# %% [markdown]
# # Total cost accounting

# %%
notional_costs = oms.compute_notional_costs(
    portfolio_dfs["prod"],
    prod_target_position_df, 
)
hpandas.df_to_str(notional_costs, num_rows=5, log_level=logging.INFO)


# %%
# Analyze per stock

# TODO(gp): Chack amp Master looking for get_asset_slice 

def plot_together(df1, df2, suffix):
    df1 = pd.DataFrame(df1)
    df2 = pd.DataFrame(df2)
    df = df1.merge(df2,
                   left_index=True, right_index=True, 
                   how="outer", suffixes=suffix)
    return df
    

asset_id = 1966583502
#display(oms.get_asset_slice(research_portfolio_df, asset_id).head(5))

#display(oms.get_asset_slice(portfolio_dfs["prod"], asset_id).head(5))

def add_prices(df):
    df = pd.DataFrame(df)
    df["computed_price"] = df["holdings_notional"] / df["holdings_shares"]
    return df


#research_portfolio_df = add_prices(research_portfolio_df)
#portfolio_dfs["prod"] = add_prices(portfolio_dfs["prod"])

#column = "executed_trades_notional"
column = "holdings_notional"
#column = "computed_price"
df1 = oms.get_asset_slice(research_portfolio_df, asset_id)
df1 = add_prices(df1)

df2 = oms.get_asset_slice(portfolio_dfs["prod"], asset_id)
df2 = add_prices(df2)

df = plot_together(df1, df2, ["_res", "_prod"])
#display(df.head(3))
#df = df[["price", "computed_price_res", "computed_price_prod"]].pct_change()
#df = df[["price", "computed_price_res", "computed_price_prod"]]
#df = df[["pnl_res", "pnl_prod"]]
df = df[["holdings_notional_res", "holdings_notional_prod"]]
display(df)
#df.plot()

#df.plot()


# %% [markdown]
# ## Research vs sim

# %%
cost_df = oms.apply_costs_to_baseline(
    portfolio_stats_dfs["research"],
    portfolio_stats_dfs["prod"],
    portfolio_dfs["prod"],
    prod_target_position_df, 
)
hpandas.df_to_str(cost_df, num_rows=5, log_level=logging.INFO)

# %%
cost_df[["pnl", "baseline_pnl_minus_costs", "baseline_pnl"]].plot()
cost_df[["pnl", "baseline_pnl_minus_costs"]].plot()

# %% [markdown]
# # TCA

# %%
research_portfolio_df["holdings_shares"].head(10)

# %% [markdown]
# # Orders

# %%
prod_order_df = oms.TargetPositionAndOrderGenerator.load_orders(
    portfolio_path_dict["prod"].strip("portfolio"),
)
hpandas.df_to_str(prod_order_df, log_level=logging.INFO)

# %%
sim_order_df = oms.TargetPositionAndOrderGenerator.load_orders(
    portfolio_path_dict["sim"].strip("portfolio"),
)
hpandas.df_to_str(sim_order_df, log_level=logging.INFO)

# %%
prod_order_df.groupby(["creation_timestamp", "asset_id"]).count()

# %%
asset_id = 6051632686

mask = prod_order_df["asset_id"] == asset_id
prod_order_df[mask].head(6)

# %% [markdown]
# ## Target vs executed

# %%
#df1 = prod_target_position_df["target_holdings_shares"][asset_id].shift(1)
#df2 = prod_target_position_df["holdings_shares"][asset_id]

df1 = prod_target_position_df["target_holdings_shares"].shift(1)
df2 = prod_target_position_df["holdings_shares"]

#df1
df1 - df2

# %%
#display(prod_target_position_df["holdings_shares"].loc["2022-11-01 09:10:00-04:00"])
#display(prod_target_position_df["target_holdings_shares"].loc["2022-11-01 09:10:00-04:00"])

# %%
# We are getting the fills that correspond to the orders and to the change of holdings.
prod_target_position_df["holdings_shares"][asset_id].diff()

# %% [markdown]
# # Fill stats

# %%
fills = oms.compute_fill_stats(prod_target_position_df)
fills["underfill_share_count"].plot()

# %%
fills["underfill_share_count"].round(4)

# %%
print(fills.columns.levels[0])
fills["tracking_error_shares"]

# TODO(gp): Add a check to ensure that this is never positive.

# %%
fills["fill_rate"].head()

# %%
fills["fill_rate"].plot()

# %% [markdown]
# # Slippage

# %%
slippage = oms.compute_share_prices_and_slippage(portfolio_dfs["prod"])
slippage["slippage_in_bps"].plot()

# %%
slippage["slippage_in_bps"].stack().hist(bins=31)

# %%
# Load forecast dataframes

# %%
# %%
stacked = slippage[["slippage_in_bps", "is_benchmark_profitable"]].stack()

# %%
stacked[stacked["is_benchmark_profitable"] > 0]["slippage_in_bps"].hist(bins=31)

# %%
stacked[stacked["is_benchmark_profitable"] < 0]["slippage_in_bps"].hist(bins=31)

# %% [markdown]
# # Load forecast dataframes

# %%
# TODO(gp): @Grisha fix this
root_dir = "/shared_data/prod_reconciliation"
search_str = "system_log_dir"
runs = ["prod", "sim"]

run_dir_dict = oms.get_run_dirs(root_dir, date_str, search_str, runs)
_LOG.info(hprint.to_pretty_str(run_dir_dict))

bar_duration = "5T"
target_position_dfs = oms.load_target_position_versions(
    run_dir_dict,
    bar_duration,
)

target_position_dfs["prod"].columns.levels[0]

# TODO: Check prod_target_positions_df["holdings_shares"].subtract(prod_portfolio_df["holdings_shares"]) is zero.

fills = oms.compute_fill_stats(target_position_dfs["prod"])

fills["underfill_share_count"].plot()

fills["fill_rate"].plot()

# %% [markdown]
# # Total cost accounting

# %%
notional_costs = oms.compute_notional_costs(
    portfolio_dfs["prod"],
    target_position_dfs["prod"], 
)

# %%
notional_costs.head()

# %%
notional_costs["slippage_notional"].stack().hist(bins=101)

# %%
notional_costs["slippage_notional"].sum().sum()

# %%
notional_costs["underfill_notional_cost"].stack().hist(bins=31, log=True)

# %%
notional_costs["underfill_notional_cost"].sum().sum()

# %%
cost_df = oms.apply_costs_to_baseline(
    portfolio_stats_dfs["research"],
    portfolio_stats_dfs["prod"],
    portfolio_dfs["prod"],
    target_position_dfs["prod"], 
)

# %%
cost_df.plot()

# %%
cost_df[["baseline_pnl_minus_costs_minus_pnl", "underfill_notional_cost", "slippage_notional"]].iloc[2:].plot()

# %%
cost_df.columns

# baseline_pnl -> research
# baseline_pnl_minus_cost -> research with 
# pnl -> production
cost_df[["pnl", "baseline_pnl_minus_costs", "baseline_pnl"]].plot()
cost_df[["pnl", "baseline_pnl_minus_costs"]].plot()

# %% [markdown]
# # Multiday reconciliation

# %%
assert 0

# %%
date_strs = oms.get_dir_dates(root_dir)
display(date_strs)

# %% run_control={"marked": false}
(
    dag_df,
    portfolio_df,
    portfolio_stats_df,
    target_position_df,
    slippage_df,
    fills_df,
) = oms.load_and_process_artifacts(root_dir, date_strs, search_str, "prod", "15T")

# %%
fep_dict

# %%
research_portfolio_df, research_portfolio_stats_df = fep.annotate_forecasts(
    dag_df,
    quantization="nearest_share",
    target_gmv=20000.,
    compute_extended_stats=True,
)

# %%
research_portfolio_stats_df["pnl"].resample("B").sum().cumsum().plot()

# %% [markdown]
# # Total cost accounting

# %%
notional_costs = oms.compute_notional_costs(
    portfolio_dfs["prod"],
    target_position_dfs["prod"],
)

# %%
notional_costs.head()

# %%
notional_costs["slippage_notional"].stack().hist(bins=101)

# %%
notional_costs["slippage_notional"].sum().sum()

# %%
notional_costs["underfill_notional_cost"].stack().hist(bins=31, log=True)

# %%
notional_costs["underfill_notional_cost"].sum().sum()

# %%
cost_df = oms.apply_costs_to_baseline(
    portfolio_stats_dfs["research"],
    portfolio_stats_dfs["prod"],
    portfolio_dfs["prod"],
    target_position_dfs["prod"],
)
