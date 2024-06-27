# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Establish a baseline Poisson Regression Model
# - Use the International soccer database (ISDB) to predict the goals scored by each team.
# - Database Description:
#     - ISDBv2: 218,916 entries. 52 leagues, from 2000/01 to 2016/17 seasons
#               completed leagues only.
#     - ISDBv1: 216,743 entries. 52 leagues, from 2000/01 to 2017/18 seasons.
#               Some leagues incomplete and some cover only subset of seasons.
# - Metadata:
#     - `'Date'`: Date on which the match took place.
#     - `'Sea'` : Describes the yearly season in which the match happened.
#     - `'Lea'` : League of in which the match is part of.
#     - `'HT'`  : Home Team.
#     - `'AT'`  : Away Team.
#     - `'HS'`  : Goals scored by Home Team.
#     - `'AS'`  : Goals scored by Away Team.
#     - `'GD'`  : Goal difference (`HS - AS`)
#     - `'WDL'` : Match outcome w/r to Home team (home win, home loss, draw)
# - Use the poisson regressor of the GLM model in stats models
# - Evaluate the model performance

# %%
import logging
import warnings

import numpy as np
import pandas as pd

import helpers.hdbg as hdbg
import research_amp.soccer_prediction.models as rasoprmo
import research_amp.soccer_prediction.preproccesing as rasoprpr
import research_amp.soccer_prediction.utils as rasoprut

pd.set_option("display.max_columns", None)
warnings.filterwarnings("ignore")

# %%
_LOG = logging.getLogger(__name__)


# %%
def calculate_match_outcome_and_probabilities(
    df: pd.DataFrame,
    *,
    max_goals: int = 10,
    apply_dixon_coles: bool = False,
    rho: float = -0.2,
) -> pd.DataFrame:
    """
    Calculate match outcome probabilities for the entire DataFrame.

    :param df: Input DataFrame with predicted goals.
    :param max_goals: Maximum goals to consider for calculating the
        probabilities.
    :param apply_dixon_coles: Flag to apply Dixon-Coles adjustment.
    :param rho: Dixon-Coles adjustment parameter.
    :return: DataFrame with added probabilities for home win, away win,
        and draw.
    """
    hdbg.dassert_isinstance(df, pd.DataFrame)
    # Calculate Poisson probabilities for Home team goals.
    home_goals_probs = np.array(
        [
            np.exp(-df["Lambda_HS"]) * df["Lambda_HS"] ** i / np.math.factorial(i)
            for i in range(max_goals)
        ]
    )
    # Calculate Poisson probabilities for Away team goals.
    away_goals_probs = np.array(
        [
            np.exp(-df["Lambda_AS"]) * df["Lambda_AS"] ** i / np.math.factorial(i)
            for i in range(max_goals)
        ]
    )
    # Initialize probabilities.
    prob_home_win = np.zeros(len(df))
    prob_away_win = np.zeros(len(df))
    prob_draw = np.zeros(len(df))
    # Calculate the probabilities of home win, away win, and draw.
    for i in range(max_goals):
        for j in range(max_goals):
            prob = home_goals_probs[i] * away_goals_probs[j]
            if apply_dixon_coles:
                prob *= dixon_coles_adjustment(
                    i, j, df["Lambda_HS"], df["Lambda_AS"], rho
                )
            prob_home_win += np.where(i > j, prob, 0)
            prob_away_win += np.where(i < j, prob, 0)
            prob_draw += np.where(i == j, prob, 0)
    # Add probabilities to the DataFrame.
    df["prob_home_win"] = prob_home_win
    df["prob_away_win"] = prob_away_win
    df["prob_draw"] = prob_draw
    # Predict the outcomes based on probabilities.
    df["predicted_outcome"] = np.where(
        df["prob_home_win"] > df["prob_away_win"],
        "home_win",
        np.where(df["prob_away_win"] > df["prob_home_win"], "away_win", "draw"),
    )
    # Calculate actual outcomes for comparison.
    df["actual_outcome"] = np.where(
        df["HS"] > df["AS"],
        "home_win",
        np.where(df["HS"] < df["AS"], "away_win", "draw"),
    )
    # Round off the predicted goals to integers.
    df["Lambda_HS"] = df["Lambda_HS"].round().astype(int)
    df["Lambda_AS"] = df["Lambda_AS"].round().astype(int)
    print(df.head())
    return df


def poisson_model(label_encode: bool = False):
    # Define the S3 Buckets, dataset path and local directory for download.
    bucket = "cryptokaizen-data-test"
    dataset_path = "kaizen_ai/soccer_prediction/datasets/OSF_football/"
    local_dir = "datasets/OSF_football"
    # Download data from S3.
    rasoprut.download_data_from_s3(
        bucket_name=bucket, dataset_path=dataset_path, local_path=local_dir
    )
    # Load the data from S3 into pandas dataframe objects.
    dataframes = rasoprut.load_data_to_dataframe(local_path=local_dir)
    # Access the dataframes directly from the dictionary.
    dataframes.get("ISDBv1_df")
    ISDBv2_df = dataframes.get("ISDBv2_df")
    rasoprut.compute_stats(ISDBv2_df)
    # Preprocess and unravel data.
    preprocessed_df, pipeline = rasoprpr.preprocess_and_unravel_data(
        ISDBv2_df, add_epsilon_flag=True
    )
    train_df = preprocessed_df.get("train_df")
    test_df = preprocessed_df.get("test_df")
    # Train model
    hyperparameters = {
        "formula": "goals~ team - opponent + is_home",
        "maxiter": 10,
    }
    sample_sizes = [20000, 30000, 40000, 50000, 60000]
    columns = ["team", "opponent", "goals", "is_home"]
    poisson_model = rasoprmo.PoissonModel()
    trained_model = rasoprmo.train_model(
        train_df[columns],
        poisson_model,
        hyperparameters,
        sample_sizes=sample_sizes,
    )
    # Generate predictions.
    test_df["predicted_goals"] = trained_model.predict(
        test_df[["team", "opponent", "is_home"]]
    )
    # Recombine predictions.
    final_df = rasoprut.recombine_predictions(test_df)
    # Calculate match outcome probabilities.
    final_df = calculate_match_outcome_and_probabilities(final_df)
    # Evaluate model.
    rasoprut.evaluate_model_predictions(
        final_df["actual_outcome"], final_df["predicted_outcome"]
    )
    # Inverse transform.
    if label_encode:
        pipeline.named_steps["label_encoding"].inverse_transform(final_df)
    # Save data to S3.
    s3_path_predictions = "kaizen_ai/soccer_prediction/model_output/glm_poisson"
    rasoprut.save_data_to_s3(
        df=final_df,
        bucket_name=bucket,
        s3_path=s3_path_predictions,
        file_name="glm_poisson_predictions",
    )

# %%
poisson_model()

# %%
# Load predictions dataset.
bucket = "cryptokaizen-data-test"
dataset_path = "kaizen_ai/soccer_prediction/model_output/glm_poisson/"
local_dir = "model_output/glm_poisson"
# Download data from S3.
rasoprut.download_data_from_s3(
    bucket_name=bucket, dataset_path=dataset_path, local_path=local_dir, file_format = ".csv"
)
# Load the data from S3 into pandas dataframe objects.
dataframes = rasoprut.load_data_to_dataframe(local_path=local_dir, file_format = ".csv", sep = ",")
glm_poisson_prediction_df = dataframes["glm_poisson_predictions_df"]


# Dixon-Coles predictions.
def dixon_coles_adjustment(home_goals, away_goals, mu_home, mu_away, rho):
    """
    Apply Dixon-Coles adjustment for low-scoring outcomes.
    
    :param home_goals: Number of goals scored by home team.
    :param away_goals: Number of goals scored by away team.
    :param mu_home: Expected goals for home team.
    :param mu_away: Expected goals for away team.
    :param rho: Dixon-Coles adjustment parameter.
    :return: Adjustment factor.
    """
    # Implement Dixon-Coles adjustment.
    if home_goals <1 and away_goals <1:
        if home_goals == away_goals:
            adjustment = 1 + rho
        elif home_goals != away_goals:
            adjustment = 1 - rho
    else:
        adjustment = 1
    return adjustment


final_df_with_dixon = calculate_match_outcome_and_probabilities(glm_poisson_prediction_df, max_goals=10, apply_dixon_coles=True, rho=0.13)
# Evaluate model.
rasoprut.evaluate_model_predictions(
        final_df_with_dixon["actual_outcome"], final_df_with_dixon["predicted_outcome"]
    )


def calculate_rps(df: pd.DataFrame) -> float:
    """
    Calculate the Rank Probability Score (RPS) for three-way outcome predictions in a DataFrame.

    :param df: DataFrame containing the columns:
                       'prob_home_win', 'prob_draw', 'prob_away_win',
                       'actual_outcome'.
    :return: The Rank Probability Score (RPS) for the entire model.
    """
    # Initialize RPS sum.
    rps_sum = 0
    M = len(df)
    # Iterate over each row in the DataFrame.
    for index, row in df.iterrows():
        # Extract predicted probabilities
        probs = np.array([row['prob_home_win'], row['prob_draw']])
        # Calculate cumulative predicted probabilities.
        cum_probs = probs.cumsum()
        # Determine actual outcomes.
        if row['actual_outcome'] == 'home_win':
            actuals = np.array([1, 0])
        elif row['actual_outcome'] == 'draw':
            actuals = np.array([0, 1])
        else:
            actuals = np.array([0, 0])
        # Calculate cumulative actual outcomes.
        cum_actuals = actuals.cumsum()
        # Calculate RPS for the current match.
        rps = (np.sum((cum_probs - cum_actuals) ** 2)) / 2
        # Add the RPS of the current match to the total RPS sum.
        rps_sum += rps
    # Average RPS over all matches.
    rps_avg = rps_sum / M
    _LOG.info("RPS value for the model: %.4f", rps_avg)
    return rps_avg

rps_avg = calculate_rps(glm_poisson_prediction_df)
