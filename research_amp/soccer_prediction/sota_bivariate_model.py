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
import logging
import warnings

import numpy as np
import pandas as pd

import helpers.hdbg as hdbg
import research_amp.soccer_prediction.models as rasoprmo
import research_amp.soccer_prediction.preproccesing as rasoprpr
import research_amp.soccer_prediction.utils as rasoprut
from scipy.special import factorial
from scipy.optimize import minimize


pd.set_option("display.max_columns", None)
warnings.filterwarnings("ignore")

# %%
dataframes = rasoprut.load_data_to_dataframe("datasets/")

# %%
data = dataframes["ISDBv2_df"]


# %%
# Convert date column to datetime
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
# Define half-life period (e.g., 180 days)
half_life_period = 180
# Calculate the age of each match in days (relative to the most recent match)
data['Days_Ago'] = (data['Date'].max() - data['Date']).dt.days
# Calculate time weights
data['Time_Weight'] = 0.5 ** (data['Days_Ago'] / half_life_period)
# Generate unique team identifiers.
teams = pd.Series(data['HT'].tolist() + data['AT'].tolist()).unique()
team_to_id = {team: idx for idx, team in enumerate(teams)}
# Map teams to unique identifiers.
data['HT_id'] = data['HT'].map(team_to_id)
data['AT_id'] = data['AT'].map(team_to_id)
# Display the first few rows of the dataset
print(data.head())


# %%
def bivariate_poisson_log_likelihood(params, data):
    c, h, rho, *strengths = params
    log_likelihood = 0 
    for _, row in data.iterrows():
        i, j, goals_i, goals_j, time_weight = row['HT_id'], row['AT_id'], row['HS'], row['AS'], row['Time_Weight']
        lambda_i = np.exp(c + strengths[i] + h - strengths[j])
        lambda_j = np.exp(c + strengths[j] - strengths[i] - h)
        cov = rho * np.sqrt(lambda_i * lambda_j)
        # Calculate joint probability
        joint_prob = 0
        for k in range(min(goals_i, goals_j) + 1):
            joint_prob += (
                (np.exp(-lambda_i - lambda_j - cov) * lambda_i**goals_i * lambda_j**goals_j * cov**k) /
                (factorial(goals_i) * factorial(goals_j) * factorial(k))
            )
        log_likelihood += time_weight * np.log(joint_prob)
    return -log_likelihood 


# %%
# Number of teams
num_teams = len(teams)
# Initial parameters: [c, h, rho, *strengths]
initial_params = [0, 0, 0.1] + [1] * num_teams

# %%
# Select the data for the league and season.
final_data = data[(data['Lge'] == 'ENG5') & 
                     ((data['Sea'] == '07-08') | 
                      (data['Sea'] == '06-07') | 
                      (data['Sea'] == '08-09'))]
# Set optimization options.
options = {
    'maxiter': 10,  
    'disp': True      
}
# Optimize parameters using the BFGS algorithm with options.
result = minimize(bivariate_poisson_log_likelihood, initial_params, args=(final_data.iloc[:552],), method='L-BFGS-B', options=options)
optimized_params = result.x
print("Optimized Parameters:", optimized_params)

# %%
