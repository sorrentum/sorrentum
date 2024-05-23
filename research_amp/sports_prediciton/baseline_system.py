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
# !pip install pymc

# %% [markdown]
# # Load datasets

# %%
import sqlite3
import pandas as pd
import numpy as np
import seaborn as sns
import itertools
import matplotlib.pyplot as plt
import os
import calendar
from datetime import datetime, timedelta, date
import warnings
#import kaggle 
import zipfile
import pandas as pd
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kde
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.impute import SimpleImputer
import pymc as pm
import arviz as az
import warnings
pd.set_option('display.max_columns', None)

# %%
database_path = "datasets/football/european-football/database.sqlite" 
conn = sqlite3.connect(database_path)
tables = pd.read_sql("""SELECT *
                        FROM sqlite_master
                        WHERE type='table';""", conn)
print(tables)

# %%
dataframes = {}
for idx, name in enumerate(tables['name']):
    if name.lower() != "sqlite_sequence":
        file = ((name.lower() + '_df'))
        if file != "_df":
            query = f"\
                    SELECT * \
                    FROM {name}\
                    "
            df = pd.read_sql(query, conn)
            exec(f'{file} = df.copy()')
            print(file, df.shape)
            df = df.drop_duplicates()
            dataframes[file]= df
print("Data imported")

# %%
# Set the directory path.
kaggle_dataset_path = 'davidcariboo/player-scores'
directory_path = 'datasets/football/player-scores'
# Download the datasets
#directory_path = os.path.expanduser('~/src/sorrentum1/research_llm/player-scores')
#os.makedirs(directory_path, exist_ok=True)
#kaggle.api.dataset_download_files(kaggle_dataset_path, path=directory_path, unzip=True)
# Manually unzip the files.
#for dirname, _, filenames in os.walk(local_directory):
#    for filename in filenames:
#        if filename.endswith('.zip'):
#            zip_path = os.path.join(dirname, filename)
#            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                zip_ref.ref.extractall(local_directory)
# Load the datasets into pandas dataframes.            
dataframes_2={}
for dirname, _, filenames in os.walk(directory_path):
    for filename in filenames:
        if filename.endswith(".csv"):
            file=filename.split('.')
            file=((file[0]+"_df"))
            if file !="_df":
                filepath=os.path.join(dirname,filename)
                df=pd.read_csv(filepath,sep=",",encoding = "UTF-8")
                exec(f'{file} = df.copy()')
                print(file, df.shape)
                df = df.drop_duplicates()
                dataframes_2[file]= df
print('Data imported')

# %%
# Set the directory path.
kaggle_dataset_path2 = 'davidcariboo/player-scores'
directory_path = 'datasets/football/player_attributes'
# Download the datasets
#directory_path = os.path.expanduser('~/src/sorrentum1/research_llm/player-scores')
#os.makedirs(directory_path, exist_ok=True)
#kaggle.api.dataset_download_files(kaggle_dataset_path, path=directory_path, unzip=True)
# Manually unzip the files.
#for dirname, _, filenames in os.walk(local_directory):
#    for filename in filenames:
#        if filename.endswith('.zip'):
#            zip_path = os.path.join(dirname, filename)
#            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                zip_ref.ref.extractall(local_directory)
# Load the datasets into pandas dataframes.            
dataframes_3={}
for dirname, _, filenames in os.walk(directory_path):
    for filename in filenames:
        if filename.endswith(".csv"):
            file=filename.split('.')
            file=((file[0]+"_df"))
            if file !="_df":
                filepath=os.path.join(dirname,filename)
                df=pd.read_csv(filepath,sep=";",encoding = "UTF-8")
                exec(f'{file} = df.copy()')
                print(file, df.shape)
                df = df.drop_duplicates()
                dataframes_3[file]= df
print('Data imported')

# %% [markdown]
# ## Create a master_player (for all player_attributes each season against year) and master_games to capture the details of individual games

# %%
# Iterate over the dictionary.
all_data = []
for key, df in dataframes_3.items():
    # Extract year from the key.
    df['year'] = int('20' + key[-5:-3])
    dataframes_3[key] = df
    all_data.append(df)
for i in range(3):
    df['year'] = 2022 + i
    all_data.append(df)
master_player = pd.concat(all_data, ignore_index=True)
# Drop the columns with NaN values.
master_player = master_player.dropna(axis=1)
# Create a master_games df.
master_games = games_df


# %% [markdown]
# Determine home win in `home_win`. When the value is `1`, home club won, value is `0` home club lost and `-1` in case of a draw  

# %%
# Create 'home_win' column
def determine_home_win(row):
    if row['home_club_goals'] > row['away_club_goals']:
        return 1
    elif row['home_club_goals'] < row['away_club_goals']:
        return 0
    else:
        return -1
    
master_games['home_win'] = master_games.apply(determine_home_win, axis=1)
master_games.head()

# %% [markdown]
# Merge the player statistics for each player in the game_lineups_df and tag the top 1% potential players as impact_players

# %%
# Step 1: Extract year from the date column in game_lineups_df.
game_lineups_df['year'] = pd.to_datetime(game_lineups_df['date']).dt.year
# Step 2: Calculate the top 1% threshold for potential rating each year
thresholds = master_player.groupby('year')['potential_rating'].quantile(0.99).reset_index()
thresholds = thresholds.rename(columns={'potential_rating': 'threshold'})

# Step 3: Merge the thresholds back to the master_player dataframe
master_player = pd.merge(master_player, thresholds, on='year', how='left')

# Step 4: Tag impact players
master_player['impact_player'] = master_player['potential_rating'] >= master_player['threshold']

# Step 5: Merge the tagged master_player dataframe with game_lineups_df
lineups_master = pd.merge(game_lineups_df, master_player, left_on=['player_name', 'year'], right_on=['Fullname', 'year'], how='left')

# Output the merged dataframe
lineups_master.head()


# %% [markdown]
# Create an aggregated skill dataframe for each team of each match. Impact players are given most weightage, captains second most. If a player is both captain and impact, then multiplicative weights are used.  

# %%
# Define weights
impact_weight = 1.5
captain_weight = 1.2

# Combine weights (multiplicative approach)
lineups_master['weight'] = 1
lineups_master['weight'] *= lineups_master['impact_player'].apply(lambda x: impact_weight if x else 1)
lineups_master['weight'] *= lineups_master['team_captain'].apply(lambda x: captain_weight if x else 1)

# List of skill columns
skill_columns = [
    'ball_control', 'dribbling', 'marking', 'aggression', 'composure', 'crossing',
    'short_pass', 'long_pass', 'acceleration', 'stamina', 'strength', 'heading',
    'shot_power', 'finishing', 'long_shots', 'gk_positioning', 'gk_diving'
]

# Apply weights to skill columns
for col in skill_columns:
    lineups_master[col + '_weighted'] = lineups_master[col] * lineups_master['weight']

# Aggregate weighted skill columns by game_id and club_id
aggregate_lineups_master = lineups_master.groupby(['game_id', 'club_id']).apply(
    lambda x: pd.Series({
        col: (x[col + '_weighted'].sum() / x['weight'].sum()) for col in skill_columns
    })
).reset_index()

aggregate_lineups_master.head()

# %% [markdown]
# Calculate aggregate skill score for each team in each match.

# %%
# Define weights for each skill
weights = {
    'ball_control': 1,
    'dribbling': 1.2,
    'marking': 0.8,
    'aggression': 0.9,
    'composure': 1,
    'crossing': 1,
    'short_pass': 1,
    'long_pass': 1,
    'acceleration': 1,
    'stamina': 1,
    'strength': 0.8,
    'heading': 0.8,
    'shot_power': 1.2,
    'finishing': 1.2,
    'long_shots': 1,
    'gk_positioning': 0.5,
    'gk_diving': 0.5
}

# Calculate weighted average for each row
def calculate_weighted_average(row, weights):
    total_weight = sum(weights.values())
    weighted_sum = sum(row[col] * weights[col] for col in weights)
    return weighted_sum / total_weight

aggregate_lineups_master['aggregate_skill_score'] = aggregate_lineups_master.apply(
    calculate_weighted_average, axis=1, weights=weights
)
aggregate_lineups_master.head()

# %% [markdown]
# Merge the aggregate skill information with master_games

# %%
# Separate home and away teams in aggregate_lineups_master
home_skills = aggregate_lineups_master.rename(columns=lambda x: 'home_' + x if x not in ['game_id', 'club_id'] else x)
away_skills = aggregate_lineups_master.rename(columns=lambda x: 'away_' + x if x not in ['game_id', 'club_id'] else x)

# Merge home and away skills with master_games
merged_df = pd.merge(master_games, home_skills, left_on=['game_id', 'home_club_id'], right_on=['game_id', 'club_id'], how='left')
merged_df = pd.merge(merged_df, away_skills, left_on=['game_id', 'away_club_id'], right_on=['game_id', 'club_id'], how='left')

# Drop duplicate columns
merged_master = merged_df.drop(columns=['club_id_x', 'club_id_y'])

merged_master.head()


# %%
# Helper function to calculate normalized performance metrics
def calculate_performance(df, club_id_col, goals_for_col, goals_against_col, win_col):
    df['goal_diff'] = df[goals_for_col] - df[goals_against_col]
    df['win'] = df[win_col].astype(int)
    
    df['goals_scored'] = df.groupby(club_id_col)[goals_for_col].rolling(10, min_periods=1).sum().reset_index(level=0, drop=True)
    df['goals_conceded'] = df.groupby(club_id_col)[goals_against_col].rolling(10, min_periods=1).sum().reset_index(level=0, drop=True)
    df['wins'] = df.groupby(club_id_col)['win'].rolling(10, min_periods=1).sum().reset_index(level=0, drop=True)
    df['goal_diff_sum'] = df.groupby(club_id_col)['goal_diff'].rolling(10, min_periods=1).sum().reset_index(level=0, drop=True)
    
    max_goals_scored = df['goals_scored'].max()
    max_goals_conceded = df['goals_conceded'].max()
    max_wins = df['wins'].max()
    max_goal_diff = df['goal_diff_sum'].max()
    
    df['goals_scored_norm'] = df['goals_scored'] / max_goals_scored if max_goals_scored != 0 else 0
    df['goals_conceded_norm'] = df['goals_conceded'] / max_goals_conceded if max_goals_conceded != 0 else 0
    df['wins_norm'] = df['wins'] / max_wins if max_wins != 0 else 0
    df['goal_diff_norm'] = df['goal_diff_sum'] / max_goal_diff if max_goal_diff != 0 else 0
    
    df['performance_score'] = (df['goals_scored_norm'] * 0.4) + (df['wins_norm'] * 0.3) + (df['goal_diff_norm'] * 0.2) - (df['goals_conceded_norm'] * 0.1)
    return df

# Calculate home and away performance scores
home_performance = calculate_performance(merged_master.copy(), 'home_club_id', 'home_club_goals', 'away_club_goals', 'home_win')
away_performance = calculate_performance(merged_master.copy(), 'away_club_id', 'away_club_goals', 'home_club_goals', 'home_win')

# Merge the performance scores back into the original dataframe
merged_master['home_aggregate_performance'] = home_performance['performance_score']
merged_master['away_aggregate_performance'] = away_performance['performance_score']
merged_master.head()

# %%
df_safe = merged_master.copy()


# %% [markdown]
# Calculate manager win scores.

# %%
# Calculate the number of games and wins for each manager
manager_game_counts = merged_master['home_club_manager_name'].value_counts()
manager_wins = merged_master[merged_master['home_win'] == 1]['home_club_manager_name'].value_counts()

# Define prior parameters for the Beta distribution
alpha_prior = 2
beta_prior = 2

# Calculate Bayesian win probability for each manager
manager_scores = {}
for manager in manager_game_counts.index:
    wins = manager_wins.get(manager, 0)
    games = manager_game_counts[manager]
    alpha_post = alpha_prior + wins
    beta_post = beta_prior + games - wins
    win_prob = alpha_post / (alpha_post + beta_post)
    manager_scores[manager] = win_prob

# Add win scores to the merged_master dataset
merged_master['home_manager_score'] = merged_master['home_club_manager_name'].apply(lambda x: manager_scores.get(x, 0))
merged_master['away_manager_score'] = merged_master['away_club_manager_name'].apply(lambda x: manager_scores.get(x, 0))


# Top 10 managers by win score
top_10_managers = sorted(manager_scores.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_managers_df = pd.DataFrame(top_10_managers, columns=['Manager', 'Win Score'])


# %%
# Sort the DataFrame by date
merged_master = merged_master.sort_values(by='date')

# Define prior parameters for the Beta distribution
alpha_prior = 2
beta_prior = 2

# Initialize cumulative win counts and game counts for home and away managers
merged_master['home_cum_wins'] = (merged_master['home_win'] == 1).groupby(merged_master['home_club_manager_name']).cumsum().shift().fillna(0)
merged_master['home_cum_games'] = merged_master.groupby('home_club_manager_name').cumcount().shift().fillna(0)

merged_master['away_cum_wins'] = (merged_master['home_win'] == 0).groupby(merged_master['away_club_manager_name']).cumsum().shift().fillna(0)
merged_master['away_cum_games'] = merged_master.groupby('away_club_manager_name').cumcount().shift().fillna(0)

# Calculate Bayesian win probability for home managers
merged_master['home_alpha_post'] = alpha_prior + merged_master['home_cum_wins']
merged_master['home_beta_post'] = beta_prior + merged_master['home_cum_games'] - merged_master['home_cum_wins']
merged_master['home_manager_score'] = merged_master['home_alpha_post'] / (merged_master['home_alpha_post'] + merged_master['home_beta_post'])

# Calculate Bayesian win probability for away managers
merged_master['away_alpha_post'] = alpha_prior + merged_master['away_cum_wins']
merged_master['away_beta_post'] = beta_prior + merged_master['away_cum_games'] - merged_master['away_cum_wins']
merged_master['away_manager_score'] = merged_master['away_alpha_post'] / (merged_master['away_alpha_post'] + merged_master['away_beta_post'])

# Drop intermediate columns
merged_master = merged_master.drop(columns=['home_cum_wins', 'home_cum_games', 'home_alpha_post', 'home_beta_post',
                                            'away_cum_wins', 'away_cum_games', 'away_alpha_post', 'away_beta_post'])
merged_master.head()

# %% [markdown]
# Head-to-head probability of winning.

# %%
# Sort the DataFrame by date
merged_master = merged_master.sort_values(by='date')
df_save = merged_master
# Initialize lists to store the calculated probabilities
home_head_head_probs = []

# Iterate through each game
for idx, row in merged_master.iterrows():
    # Filter games that happened before the current game
    past_games = merged_master[(merged_master['date'] < row['date']) & 
                               ((merged_master['home_club_id'] == row['home_club_id']) & (merged_master['away_club_id'] == row['away_club_id']) |
                                (merged_master['home_club_id'] == row['away_club_id']) & (merged_master['away_club_id'] == row['home_club_id']))]
    
    # Total head-to-head matches before the current game
    total_matches = len(past_games)
    
    # Head-to-head wins for the home team before the current game
    home_wins = past_games[(past_games['home_club_id'] == row['home_club_id']) & (past_games['home_win'] == 1)].shape[0] + \
                past_games[(past_games['away_club_id'] == row['home_club_id']) & (past_games['home_win'] == 0)].shape[0]
    
    # Calculate the head-to-head win probability for the home team
    home_head_head_prob = home_wins / total_matches if total_matches > 0 else np.nan
    
    # Append the calculated probability to the list
    home_head_head_probs.append(home_head_head_prob)

# Add the calculated probabilities as a new column in the DataFrame
merged_master['home_head_head_prob'] = home_head_head_probs
merged_master.head()

# %%
merged_master = merged_master.dropna(subset=['home_aggregate_skill_score','away_aggregate_skill_score'])
merged_master['home_head_head_prob'] = merged_master['home_head_head_prob'].fillna(0)
merged_master.head()

# %% [markdown]
# Create a train-test-val split

# %%
# Split the data into train, validation, and test sets (60% train, 20% validation, 20% test)
train_data, temp_data = train_test_split(merged_master, test_size=0.4, random_state=42)
validation_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)


# %%
# 1. Instances that home team won vs. away team won vs. draw
win_counts = train_data['home_win'].value_counts()
plt.figure(figsize=(8, 6))
sns.barplot(x=win_counts.index, y=win_counts.values, palette='viridis')
plt.title('Home Team Wins vs Away Team Wins vs Draws for Train set')
plt.xlabel('Home Win (1), Away Win (0), Draw (-1)')
plt.ylabel('Count')
plt.show()

win_counts = validation_data['home_win'].value_counts()
plt.figure(figsize=(8, 6))
sns.barplot(x=win_counts.index, y=win_counts.values, palette='viridis')
plt.title('Home Team Wins vs Away Team Wins vs Draws for validation set')
plt.xlabel('Home Win (1), Away Win (0), Draw (-1)')
plt.ylabel('Count')
plt.show()

win_counts = test_data['home_win'].value_counts()
plt.figure(figsize=(8, 6))
sns.barplot(x=win_counts.index, y=win_counts.values, palette='viridis')
plt.title('Home Team Wins vs Away Team Wins vs Draws for test set')
plt.xlabel('Home Win (1), Away Win (0), Draw (-1)')
plt.ylabel('Count')
plt.show()

# 2. Instances a team won given it won the last match, last 3 matches, and last 5 matches
def calculate_wins_after_streak(df, streak_length):
    df['win_streak'] = df['home_win'].rolling(streak_length).apply(lambda x: all(x == 1), raw=True)
    wins_after_streak = df[(df['win_streak'] == 1) & (df['home_win'] == 1)].shape[0]
    return wins_after_streak

streak_lengths = [1, 3, 5]
wins_after_streaks = [calculate_wins_after_streak(train_data, sl) for sl in streak_lengths]

plt.figure(figsize=(8, 6))
sns.lineplot(x=streak_lengths, y=wins_after_streaks, marker='o')
plt.title('Wins After Winning Streaks')
plt.xlabel('Streak Length (matches)')
plt.ylabel('Wins After Streak')
plt.show()

# 3. Number of wins for a club manager and raw probability
# Plot the win scores for the top 10 managers
plt.figure(figsize=(10, 6))
sns.barplot(x='Manager', y='Win Score', data=top_10_managers_df, palette='viridis')
plt.title('Top 10 Managers by Bayesian Win Score')
plt.xlabel('Club Manager')
plt.ylabel('Bayesian Win Score')
plt.xticks(rotation=45)
plt.show()

# Assuming the data is in train_data DataFrame
# Reclassify match outcomes
train_data['match_outcome'] = train_data['home_win'].apply(lambda x: 'Win' if x == 1 else ('Loss' if x == 0 else 'Draw'))

# 1. Scatter Plots for Skill Scores vs. Match Outcome
plt.figure(figsize=(14, 6))
plt.subplot(1, 2, 1)
sns.scatterplot(x='home_aggregate_skill_score', y='away_aggregate_skill_score', hue='match_outcome', data=train_data, palette='viridis')
plt.title('Skill Scores vs Match Outcome')
plt.xlabel('Home Aggregate Skill Score')
plt.ylabel('Away Aggregate Skill Score')

plt.subplot(1, 2, 2)
sns.scatterplot(x='home_aggregate_performance', y='away_aggregate_performance', hue='match_outcome', data=train_data, palette='viridis')
plt.title('Performance Scores vs Match Outcome')
plt.xlabel('Home Aggregate Performance Score')
plt.ylabel('Away Aggregate Performance Score')

plt.tight_layout()
plt.show()


# %% [markdown]
# # Baseline Model 

# %%
columns = ['home_club_id', 'away_club_id', 'home_aggregate_skill_score',
                   'away_aggregate_skill_score', 'home_aggregate_performance', 
                   'away_aggregate_performance', 'home_manager_score', 
                   'away_manager_score', 'home_head_head_prob']
X_train = train_data[columns]
y_train = train_data['home_win']
X_val = validation_data[columns]
y_val = validation_data['home_win']
X_test = test_data[columns]
y_test = test_data['home_win']

print(f"Training data shape: {X_train.shape}")
print(f"Validation data shape: {X_val.shape}")
print(f"Test data shape: {X_test.shape}")

# %%
# Identify the numeric columns for normalization
numeric_cols = X_train.select_dtypes(include=['int64', 'float64']).columns
# Normalize the numeric columns
scaler = StandardScaler()
X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
X_val[numeric_cols] = scaler.transform(X_val[numeric_cols])
X_test[numeric_cols] = scaler.transform(X_test[numeric_cols])

# Define the Logistic Regression model
model = LogisticRegression(multi_class='multinomial', max_iter=1000, solver='lbfgs')

# Define hyperparameter grid for tuning
param_grid = {
    'C': [0.01, 0.1, 1, 10, 100]
}

# Use GridSearchCV to find the best hyperparameters
grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Print the best parameters found by GridSearchCV
print(f"Best parameters: {grid_search.best_params_}")

# Train the model with the best parameters on the training set
best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)

# Evaluate the model on the validation set
y_val_pred = best_model.predict(X_val)
y_val_pred_prob = best_model.predict_proba(X_val)

val_accuracy = accuracy_score(y_val, y_val_pred)
val_f1 = f1_score(y_val, y_val_pred, average='weighted')
val_roc_auc = roc_auc_score(y_val, y_val_pred_prob, multi_class='ovr')

print(f"Validation Accuracy: {val_accuracy:.4f}")
print(f"Validation F1 Score: {val_f1:.4f}")
print(f"Validation ROC AUC Score: {val_roc_auc:.4f}")
print(classification_report(y_val, y_val_pred))

# Evaluate the best model on the test set
y_test_pred = best_model.predict(X_test)
y_test_pred_prob = best_model.predict_proba(X_test)

test_accuracy = accuracy_score(y_test, y_test_pred)
test_f1 = f1_score(y_test, y_test_pred, average='weighted')
test_roc_auc = roc_auc_score(y_test, y_test_pred_prob, multi_class='ovr')

print(f"Test Accuracy: {test_accuracy:.4f}")
print(f"Test F1 Score: {test_f1:.4f}")
print(f"Test ROC AUC Score: {test_roc_auc:.4f}")
print(classification_report(y_test, y_test_pred))

# %%
