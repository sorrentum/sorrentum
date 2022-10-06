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
from typing import List, Tuple

import pandas as pd

import core.config as cconfig
import core.finance as cofinanc
import core.plotting as coplotti
import dataflow.model as dtfmod
import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import helpers.hsystem as hsystem
import oms as oms

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

_LOG.info("%s", henv.get_system_signature()[0])

hprint.config_notebook()

# %%
config_list = oms.get_reconciliation_config()
config = config_list[0]
print(config)

# %% [markdown]
# # Specify data to load

# %% run_control={"marked": false}
# TODO(Grisha): factor out common code.
prod_dir = config["load_data_config"]["prod_dir"]
print(prod_dir)
hdbg.dassert(prod_dir)
hdbg.dassert_dir_exists(prod_dir)

cand_dir = config["load_data_config"]["cand_dir"]
print(cand_dir)
hdbg.dassert(cand_dir)
hdbg.dassert_dir_exists(cand_dir)

sim_dir = config["load_data_config"]["sim_dir"]
print(sim_dir)
hdbg.dassert(sim_dir)
hdbg.dassert_dir_exists(sim_dir)

# %%
# TODO(Grisha): factor out common code.

prod_portfolio_dir = os.path.join(prod_dir, "process_forecasts/portfolio")
hdbg.dassert_dir_exists(prod_portfolio_dir)
print("prod_portfolio_dir=", prod_portfolio_dir)
prod_dag_dir = os.path.join(prod_dir, "dag/node_io/node_io.data")
hdbg.dassert_dir_exists(prod_dag_dir)
#
cand_portfolio_dir = os.path.join(cand_dir, "process_forecasts/portfolio")
hdbg.dassert_dir_exists(cand_portfolio_dir)
print("cand_portfolio_dir=", cand_portfolio_dir)
cand_dag_dir = os.path.join(cand_dir, "dag/node_io/node_io.data")
hdbg.dassert_dir_exists(cand_dag_dir)
#
sim_portfolio_dir = os.path.join(sim_dir, "process_forecasts/portfolio")
hdbg.dassert_dir_exists(sim_portfolio_dir)
print("sim_portfolio_dir=", sim_portfolio_dir)
sim_dag_dir = os.path.join(sim_dir, "dag/node_io/node_io.data")
hdbg.dassert_dir_exists(sim_dag_dir)

# TODO(gp): Load the TCA data for crypto.
if config["meta"]["run_tca"]:
    tca_csv = os.path.join(root_dir, date_str, "tca/sau1_tca.csv")
    hdbg.dassert_file_exists(tca_csv)

# %%
portfolio_path_dict = {
    "prod": prod_portfolio_dir,
    "cand": cand_portfolio_dir,
    "sim": sim_portfolio_dir,
}

# %%
# TODO(gp): @Grisha infer this from the data from df.
date_str = config["meta"]["date_str"]
start_timestamp = pd.Timestamp(date_str + " 10:05:00", tz="America/New_York")
_LOG.info("start_timestamp=%s", start_timestamp)
end_timestamp = pd.Timestamp(date_str + " 12:00:00", tz="America/New_York")
_LOG.info("end_timestamp=%s", end_timestamp)


# %% [markdown]
# # Compare DAG io

# %%
def get_latest_output_from_last_dag_node(dag_dir: str) -> pd.DataFrame:
    """
    Retrieve the most recent output from the last DAG node.

    This function relies on our file naming conventions.
    """
    parquet_files = list(filter(lambda x: "parquet" in x, sorted(os.listdir(cand_dag_dir))))
    _LOG.info("Tail of files found=%s", parquet_files[-3:])
    file_name = parquet_files[-1]
    _LOG.info("DAG file selected=%s", file_name)
    dag_parquet_path = os.path.join(cand_dag_dir, file_name)
    # _LOG.info("DAG parquet path=%s", dag_parquet_path)
    dag_df = pd.read_parquet(dag_parquet_path)
    return dag_df


# %%
prod_dag_df = get_latest_output_from_last_dag_node(prod_dag_dir)
hpandas.df_to_str(prod_dag_df, num_rows=5, log_level=logging.INFO)


# %%
sim_dag_df = get_latest_output_from_last_dag_node(sim_dag_dir)
hpandas.df_to_str(sim_dag_df, num_rows=5, log_level=logging.INFO)

# %%
prod_sim_dag_corr = dtfmod.compute_correlations(
    prod_dag_df,
    sim_dag_df,
)
hpandas.df_to_str(
    prod_sim_dag_corr.min(),
    num_rows=None,
    precision=3,
    log_level=logging.INFO,
)

# %%
# TODOO(gp): @grisha
# Problem: given two multi-index dfs, we want to compare how similar they are

# Check if they have the same columns (in the same order)
#  - switch to ignore certain columns
#  - switch to reorder the columns to sort them

# Check if they have the same index
#  - switch to perform intersection

# Check if they are exactly the same, e.g., the difference is less than a threshold <1e-6.
#   Show the rows with the max difference (use the `differ_visually_...`)
#   Allow to subset by columns (e.g., close)

# %%
# TODO(gp): @grisha

# Given two multi-index dfs, allow to slice the values by index or by column
# Create a df with sliced 2 columns or rows and do the diff so that it's easy to plot / inspect
#
# #col_name = "price"
# col_name = "executed_trades_notional"
# #asset_id = 1030828978
# #asset_id = 5115052901
# asset_id = 5118394986
# #df1 = adapted_sim_df[col_name][asset_id]
# df1 = adapted_prod_df[col_name][asset_id]
# df2 = research_portfolio_df[col_name][asset_id]

# (df1 - df2).dropna().plot()

# df = pd.DataFrame(df1).merge(pd.DataFrame(df2), how="outer", left_index=True, right_index=True, suffixes=["_prod", "_research"])

# #df["diff"] = df["1030828978_prod"] - df["1030828978_research"]

# #display(df)

# df.dropna().plot()

# %%
# TODO(gp): Add function to compare duration of different dfs
# E.g., duration_df = compute_duration_df(tag_to_df)
#  Compute min / max index
#  Compute min / max index with all values non-nans
#  The output is multi-index indexed by tag and has (min_idx, max_idx, )

duration_df = pd.MultiIndex

# %% [markdown]
# # Compute research portfolio equivalent

# %%
fep = dtfmod.ForecastEvaluatorFromPrices(**config["research_forecast_evaluator_from_prices"]["init"])

# %%
research_portfolio_df, research_portfolio_stats_df = fep.annotate_forecasts(
    prod_dag_df,
    **config["research_forecast_evaluator_from_prices"]["annotate_forecasts_kwargs"],
    compute_extended_stats=True
)

# %%
# TODO(gp): Move it to annotate_forecasts?
research_portfolio_df = research_portfolio_df.sort_index(axis=1)

# %%
hpandas.df_to_str(research_portfolio_stats_df, log_level=logging.INFO)

# %% [markdown]
# # Orders

# %%
prod_order_df = oms.ForecastProcessor.read_logged_orders(
    portfolio_path_dict["prod"] + "/.."
)
hpandas.df_to_str(prod_order_df, log_level=logging.INFO)

# %%
sim_order_df = oms.ForecastProcessor.read_logged_orders(
    portfolio_path_dict["sim"] + "/.."
)
hpandas.df_to_str(sim_order_df, log_level=logging.INFO)

# %%
research_portfolio_df["executed_trades_shares"]

# %%
prod_order_df = prod_order_df.pivot(
    index="end_timestamp",
    columns="asset_id",
    values="diff_num_shares",
)
freq = "5T"
prod_order_df.index = prod_order_df.index.round(freq)

sim_order_df = sim_order_df.pivot(
    index="end_timestamp",
    columns="asset_id",
    values="diff_num_shares",
)
sim_order_df.index = sim_order_df.index.round(freq)

# %%
asset_id = 1030828978

# %% [markdown]
# # Load logged portfolios

# %%
portfolio_config_dict = {
    "start_timestamp": start_timestamp,
    "end_timestamp": end_timestamp,
    "freq": config["meta"]["bar_duration"],
    "normalize_bar_times": True,
}
portfolio_config_dict

# %%
portfolio_dfs = {}
portfolio_stats_dfs = {}
for name, path in portfolio_path_dict.items():
    _LOG.info("Processing portfolio=%s path=%s", name, path)
    portfolio_df, portfolio_stats_df = oms.load_portfolio_artifacts(
        path,
        **portfolio_config_dict,
    )
    #portfolio_df = portfolio_df.sort_index(axis=1)
    portfolio_dfs[name] = portfolio_df
    portfolio_stats_dfs[name] = portfolio_stats_df
    
portfolio_dfs["research"] = research_portfolio_df.loc[start_timestamp:end_timestamp]
portfolio_stats_dfs["research"] = research_portfolio_stats_df.loc[start_timestamp:end_timestamp]
portfolio_stats_df = pd.concat(portfolio_stats_dfs, axis=1)

# %%

# %%
hpandas.df_to_str(portfolio_stats_df, log_level=logging.INFO)

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
# # Compare pairwise portfolio correlations

# %%
adapted_prod_df = oms.adapt_portfolio_object_df_to_forecast_evaluator_df(portfolio_dfs["prod"])
adapted_cand_df = oms.adapt_portfolio_object_df_to_forecast_evaluator_df(portfolio_dfs["cand"])
adapted_sim_df = oms.adapt_portfolio_object_df_to_forecast_evaluator_df(portfolio_dfs["sim"])

# %%
adapted_prod_df.columns.levels

# %%
adapted_prod_df.columns.levels[0]

# %%
adapted_prod_df = adapted_prod_df.sort_index(axis=1)
research_portfolio_df = research_portfolio_df.sort_index(axis=1)

# %%
col_name = "holdings_shares"
#col_name = "price"
display(adapted_prod_df[col_name].tail(3))
display(research_portfolio_df[col_name].tail(3))

# %%
#col_name = "pnl"
#col_name = "executed_trades_shares"
col_name = "holdings_shares"
dtfmod.compute_correlations(
    adapted_prod_df.iloc[1:],
    research_portfolio_df.iloc[1:],
    allow_unequal_indices=True,
    allow_unequal_columns=True,
).sort_values([col_name], ascending=False)

# %%
#col_name = "price"
col_name = "executed_trades_notional"
#asset_id = 1030828978
#asset_id = 5115052901
asset_id = 5118394986
#df1 = adapted_sim_df[col_name][asset_id]
df1 = adapted_prod_df[col_name][asset_id]
df2 = research_portfolio_df[col_name][asset_id]

(df1 - df2).dropna().plot()

df = pd.DataFrame(df1).merge(pd.DataFrame(df2), how="outer", left_index=True, right_index=True, suffixes=["_prod", "_research"])

#df["diff"] = df["1030828978_prod"] - df["1030828978_research"]

#display(df)

df.dropna().plot()

# %%
dtfmod.compute_correlations(
    #research_portfolio_df,
    adapted_sim_df.iloc[1:],
    research_portfolio_df.iloc[1:],
    allow_unequal_indices=True,
    allow_unequal_columns=True,
).sort_values(["pnl"], ascending=False)

# %%
dtfmod.compute_correlations(
    adapted_prod_df,
    adapted_sim_df,
    allow_unequal_indices=False,
    allow_unequal_columns=False,
).sort_values(["pnl"], ascending=False)

# %%
dtfmod.compute_correlations(
    research_portfolio_df,
    adapted_sim_df,
    allow_unequal_indices=True,
    allow_unequal_columns=True,
).sort_values(["pnl"], ascending=False)

# %%
if config["meta"]["run_tca"]:
    tca = cofinanc.load_and_normalize_tca_csv(tca_csv)
    tca = cofinanc.compute_tca_price_annotations(tca, True)
    tca = cofinanc.pivot_and_accumulate_holdings(tca, "")

# %%
