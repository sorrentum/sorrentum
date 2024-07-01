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

# %%
import datetime
import math
import os
import warnings

import joblib
import numpy as np
import pandas as pd
import scipy.optimize as sopt

import helpers.haws as haws

pd.set_option("display.max_columns", None)
warnings.filterwarnings("ignore")

# %% [markdown]
# Set the s3 credentials

# %%
# Initialize a session.
s3 = haws.get_service_resource(aws_profile="ck", service_name="s3")

# Set the S3 bucket and dataset path.
s3_bucket_name = "cryptokaizen-data-test"
s3_dataset_path = "kaizen_ai/soccer_prediction/datasets/OSF_football/"

# Define the local directory to save the files.
local_directory = "datasets/OSF_football"
os.makedirs(local_directory, exist_ok=True)


def download_files_from_s3(bucket_name, prefix, local_dir):
    """
    Function to download files from S3.
    """
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=prefix):
        key = obj.key
        if key.endswith(".txt"):
            local_file_path = os.path.join(local_dir, os.path.basename(key))
            print(f"Downloading {key} to {local_file_path}")
            bucket.download_file(key, local_file_path)


# Call the function to download the files
download_files_from_s3(s3_bucket_name, s3_dataset_path, local_directory)

# Load the datasets into pandas dataframes
dataframes_3 = {}
for dirname, _, filenames in os.walk(local_directory):
    for filename in filenames:
        if filename.endswith(".txt"):
            file_key = filename.split(".")[0] + "_df"
            filepath = os.path.join(dirname, filename)
            print(f"Loading {filepath}")
            df = pd.read_csv(filepath, sep="\t", encoding="UTF-8")
            print(file_key, df.shape)
            df = df.drop_duplicates()
            dataframes_3[file_key] = df

print("Data imported")

# Verify the content of dataframes_3 dictionary.
for key, df in dataframes_3.items():
    print(f"{key}: {df.shape}")

# Access the dataframes directly from the dictionary.
ISDBv1_df = dataframes_3.get("ISDBv1_df")
ISDBv2_df = dataframes_3.get("ISDBv2_df")

# Print the shapes to confirm they are loaded correctly.
print(
    f"ISDBv1_df shape: {ISDBv1_df.shape if ISDBv1_df is not None else 'Not found'}"
)
print(
    f"ISDBv2_df shape: {ISDBv2_df.shape if ISDBv2_df is not None else 'Not found'}"
)

# %%
ISDBv2_df.head()

# %% [markdown]
# Make the season into a single interger for simplicity

# %%
ISDBv2_df["season"] = ISDBv2_df["Sea"].apply(lambda x: int("20" + str(x)[:2]))
df = ISDBv2_df[ISDBv2_df["season"] >= 2009]
# Preprocess the dataset
# Preprocess the dataset
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
df.sort_values(by="Date", inplace=True)


# Define the burn-in period and warm-up season removal
def remove_warmup_and_burnin(df, warmup_seasons, burnin_rounds=5):
    filtered_df = pd.DataFrame()
    leagues = df["Lge"].unique()

    for league in leagues:
        league_df = df[df["Lge"] == league]
        seasons = league_df["Sea"].unique()
        for season in seasons:
            season_df = league_df[league_df["Sea"] == season]
            if season == seasons[0] and season in warmup_seasons:
                continue
            season_df = season_df.iloc[burnin_rounds:]
            filtered_df = pd.concat([filtered_df, season_df])

    return filtered_df


warmup_seasons = {2009}
df_final = remove_warmup_and_burnin(df, warmup_seasons)
# Split the data into training, validation, and test sets
train_size = int(0.6 * len(df_final))
val_size = int(0.2 * len(df_final))
train_df = df_final[:train_size]
val_df = df_final[train_size : train_size + val_size]
test_df = df_final[train_size + val_size :]

# %%
df_final.columns

# %% [markdown]
# # Double Precision Model

# %% run_control={"marked": true}
# Check if the validation dataframe is empty
if val_df.empty:
    print("Validation dataframe is empty.")
else:
    print(f"Validation dataframe has {len(val_df)} records.")

# Check if the training dataframe is empty
if train_df.empty:
    print("Training dataframe is empty.")
else:
    print(f"Training dataframe has {len(train_df)} records.")


# Define the Double Poisson likelihood function with exponential time weighting
def double_poisson_log_likelihood(params, df, teams, alpha=0.0019):
    strength = dict(zip(teams, params[:-1]))
    home_advantage = params[-1]
    current_date = datetime.datetime.now()

    # Map team strengths to home and away teams
    home_teams = df["HT"].map(strength)
    away_teams = df["AT"].map(strength)
    home_goals = df["HS"].values
    away_goals = df["AS"].values
    t_deltas = (current_date - df["Date"]).dt.days
    weights = np.exp(-alpha * t_deltas)

    # Calculate expected goals
    lambda_home = np.exp(home_teams.values - away_teams.values + home_advantage)
    lambda_away = np.exp(away_teams.values - home_teams.values)

    # Calculate log-likelihoods for home and away goals
    log_likelihood_home = (
        home_goals * np.log(lambda_home)
        - lambda_home
        - np.log(np.vectorize(math.factorial)(home_goals))
    )
    log_likelihood_away = (
        away_goals * np.log(lambda_away)
        - lambda_away
        - np.log(np.vectorize(math.factorial)(away_goals))
    )

    # Sum the weighted log-likelihoods
    total_log_likelihood = np.sum(
        weights * (log_likelihood_home + log_likelihood_away)
    )

    return (
        -total_log_likelihood
    )  # Return negative log-likelihood to maximize it by minimizing


# Define the teams and initial parameters
teams = pd.unique(df[["HT", "AT"]].values.ravel("K"))
initial_strength = np.zeros(len(teams))
initial_home_advantage = 0.1


# Function to refit parameters after each league round
def refit_parameters(train_df, teams):
    # Initial guess for teams' strength.
    initial_strength = np.zeros(len(teams))
    # Initial guess for home advantage
    initial_home_advantage = 0.1
    initial_params = np.concatenate([initial_strength, [initial_home_advantage]])

    print("Starting optimization with initial parameters")
    result = sopt.minimize(
        double_poisson_log_likelihood,
        x0=initial_params,
        args=(train_df, teams),
        method="L-BFGS-B",
        options={"disp": True},
    )
    print("Optimization result:", result)
    if not result.success:
        print("Optimization failed.")
    return result.x


# Initial parameter fitting
params = refit_parameters(train_df, teams)

# Extract the optimized parameters
team_strengths = dict(zip(teams, params[:-1]))
home_advantage = params[-1]

print("Optimized Team Strengths:")
print(team_strengths)
print("Home Advantage:")
print(home_advantage)


# Function to predict match outcomes
def predict_match(home_team, away_team, team_strengths, home_advantage):
    lambda_home = np.exp(
        team_strengths[home_team] - team_strengths[away_team] + home_advantage
    )
    lambda_away = np.exp(team_strengths[away_team] - team_strengths[home_team])
    return lambda_home, lambda_away


# Function to calculate Ranked Probability Score (RPS)
def rps(predictions, actual):
    cumulative_preds = np.cumsum(predictions)
    cumulative_actual = np.cumsum(actual)
    return np.sum((cumulative_preds - cumulative_actual) ** 2) / (
        len(predictions) - 1
    )


# Function to evaluate the model
def evaluate_model(df, team_strengths, home_advantage):
    correct_predictions = 0
    total_predictions = 0
    total_rps = 0

    def calculate_metrics(row):
        nonlocal correct_predictions, total_predictions, total_rps
        home_team = row["HT"]
        away_team = row["AT"]
        home_goals = row["HS"]
        away_goals = row["AS"]

        # Check if team strengths are available
        if home_team not in team_strengths or away_team not in team_strengths:
            print(f"Missing strength for teams: {home_team}, {away_team}")
            return

        lambda_home, lambda_away = predict_match(
            home_team, away_team, team_strengths, home_advantage
        )
        predicted_home_goals = np.round(lambda_home)
        predicted_away_goals = np.round(lambda_away)

        if (predicted_home_goals == home_goals) and (
            predicted_away_goals == away_goals
        ):
            correct_predictions += 1

        # Determine the maximum number of goals to dynamically size the result arrays
        max_goals = (
            int(
                max(
                    home_goals,
                    away_goals,
                    predicted_home_goals,
                    predicted_away_goals,
                )
            )
            + 1
        )

        # Create actual result distribution
        actual_result = np.zeros(max_goals)
        actual_result[int(home_goals)] = 1
        actual_result[int(away_goals)] = 1

        # Create prediction distribution
        predictions = np.zeros(max_goals)
        predictions[int(predicted_home_goals)] = lambda_home
        predictions[int(predicted_away_goals)] = lambda_away

        total_rps += rps(predictions, actual_result)
        total_predictions += 1

    joblib.Parallel(n_jobs=-1)(
        joblib.delayed(calculate_metrics)(row) for idx, row in df.iterrows()
    )

    # Check if total_predictions is zero to avoid ZeroDivisionError
    if total_predictions == 0:
        print("No predictions made. Total predictions is zero.")
        return 0, 0

    accuracy = correct_predictions / total_predictions
    average_rps = total_rps / total_predictions

    return accuracy, average_rps


# Evaluate the model on the validation set
val_accuracy, val_rps = evaluate_model(val_df, team_strengths, home_advantage)

print("Validation Accuracy:")
print(val_accuracy)
print("Validation Ranked Probability Score (RPS):")
print(val_rps)

# Evaluate the model on the test set
test_accuracy, test_rps = evaluate_model(test_df, team_strengths, home_advantage)

# Calculate confidence intervals for hit rate
hit_rate = test_accuracy
z = 1.96  # 95% confidence interval
hit_rate_std = np.sqrt((hit_rate * (1 - hit_rate)) / len(test_df))
confidence_interval = (hit_rate - z * hit_rate_std, hit_rate + z * hit_rate_std)

print("Test Accuracy:")
print(test_accuracy)
print("Test Ranked Probability Score (RPS):")
print(test_rps)
print("Hit Rate:")
print(hit_rate)
print("Confidence Interval:")
print(confidence_interval)
