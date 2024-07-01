"""
Import as:

import research_amp.soccer_prediction.preproccesing as rasoprpr
"""
import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, LabelEncoder

import helpers.hdbg as hdbg
import research_amp.soccer_prediction.utils as rasoprut

_LOG = logging.getLogger(__name__)


class GeneralPreprocessing(BaseEstimator, TransformerMixin):
    """
    Perform general preprocessing on the dataframe.
    - Filter and select matches from seasons starting from 2009.
      Adds `season` column that takes the first year of a `Sea` as integer value.
      (e.g if `Sea` == "09-10" then `season` == 2009).
    - Convert 'Date' to datetime and sort.
    - Drop rows with NaNs.
    """

    def fit(
        self,
        X: pd.DataFrame,
    ) -> "GeneralPreprocessing":
        """
        Fit method, which does nothing and is here for compatibility.

        :param X: input DataFrame.
        :return: self
        """
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform method to apply general preprocessing.

        :param X: input DataFrame.
        :return: preprocessed DataFrame.
        """
        # Validate input.
        hdbg.dassert_isinstance(X, pd.DataFrame)
        rows_before = len(X)
        # Add 'season' column.
        X["season"] = X["Sea"].apply(lambda x: int("20" + str(x)[:2]))
        # Filter out seasons before 2009.
        X = X[X["season"] >= 2009]
        len(X)
        _LOG.info(
            "Rows removed after the operation: %s ", rows_before - rows_before
        )
        # Convert 'Date' to datetime and sort.
        X["Date"] = pd.to_datetime(X["Date"], dayfirst=True)
        X.sort_values(by="Date", inplace=True)
        # Convert categorical columns to 'category' type.
        categorical_columns = ["HT", "AT"]
        for col in categorical_columns:
            X[col] = X[col].astype("category")
        return X


class LabelEncoding(BaseEstimator, TransformerMixin):
    """
    Apply Label Encoding to specified categorical columns.

    :param columns: List of columns to encode.
    """

    def __init__(self, columns: List[str]):
        self.columns = columns
        self.label_encoders = {}

    def fit(
        self,
        X: pd.DataFrame,
    ) -> "LabelEncoding":
        """
        Fit method to learn the encoding for each column.

        :param X: input DataFrame.
        :param y: ignored.
        :return: self
        """
        hdbg.dassert_isinstance(X, pd.DataFrame)
        hdbg.dassert_lt(0, X.shape[0])
        for col in self.columns:
            # Check if the column is present.
            hdbg.dassert_in(col, X.columns)
            # Encode the column values.
            le = LabelEncoder()
            le.fit(X[col])
            self.label_encoders[col] = le
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform method to apply label encoding.

        :param X: Input DataFrame.
        :return: DataFrame with encoded columns.
        """
        hdbg.dassert_isinstance(X, pd.DataFrame)
        hdbg.dassert_lt(0, X.shape[0])
        for col in self.columns:
            # Check if the column is present.
            hdbg.dassert_in(col, X.columns)
            # Apply label encoding.
            le = self.label_encoders[col]
            X[col] = le.transform(X[col])
        return X

    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform method to revert label encoding.

        :param X: Input DataFrame.
        :return: DataFrame with decoded columns.
        """
        hdbg.dassert_isinstance(X, pd.DataFrame)
        hdbg.dassert_lt(0, X.shape[0])
        X_inverse_transformed = X.copy()
        for col in self.columns:
            # Check if the column is present.
            assert (
                col in X.columns
            ), f"Column '{col}' not found in input DataFrame."
            # Apply the inverse label encoding.
            X_inverse_transformed[col] = self.label_encoders[
                col
            ].inverse_transform(X[col])
        return X_inverse_transformed


def add_epsilon(
    X: pd.DataFrame, *, epsilon: float = 0.5, columns: Optional[List[Any]] = None
) -> pd.DataFrame:
    """
    Add epsilon to specified columns to avoid log(0).

    :param X: Input DataFrame.
    :param epsilon: Value to add to columns. Default is 0.5.
    :param columns: List of columns to add epsilon to.
    :return: DataFrame with epsilon added to specified columns.
    """
    hdbg.dassert_isinstance(X, pd.DataFrame)
    hdbg.dassert_lt(0, X.shape[0])
    if columns is not None:
        for column in columns:
            hdbg.dassert_in(column, X.columns)
            # Add epsilon to specified columns.
            affected_rows_count = X[column].apply(lambda x: x == 0).sum()
            X[column] = X[column].apply(lambda x: x + epsilon if x == 0 else x)
            _LOG.info(
                "Column '%s' had %d rows affected.", column, affected_rows_count
            )
    else:
        raise ValueError("Columns parameter cannot be None.")
    return X


class UnravelData(BaseEstimator, TransformerMixin):
    """
    Unravel the dataset by creating two entries for each row as team-opponent
    pairs.
    """

    def fit(
        self,
        X: pd.DataFrame,
    ) -> "UnravelData":
        """
        Fit method, which does nothing and is here for compatibility.

        :param X: input DataFrame.
        :return: self
        """
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform method to unravel data into team-opponent pairs.

        :param X: Input DataFrame.
        :return: Unraveled DataFrame.
        """
        hdbg.dassert_isinstance(X, pd.DataFrame)
        # Create entry for home team 'HT'.
        home_df = X[["Date", "Sea", "Lge", "HT", "AT", "HS"]].copy()
        home_df.rename(
            columns={"HT": "team", "AT": "opponent", "HS": "goals"}, inplace=True
        )
        home_df["is_home"] = 1
        # Create entry for away team 'AT'.
        away_df = X[["Date", "Sea", "Lge", "HT", "AT", "AS"]].copy()
        away_df.rename(
            columns={"AT": "team", "HT": "opponent", "AS": "goals"}, inplace=True
        )
        away_df["is_home"] = 0
        # Concatenate the two splits.
        unraveled_df = pd.concat([home_df, away_df], ignore_index=True)
        return unraveled_df


class Dropnan(BaseEstimator, TransformerMixin):
    """
    Drop rows with NaN and infinite values.
    """

    def fit(
        self,
        X: pd.DataFrame,
    ) -> "Dropnan":
        """
        Fit method, which does nothing and is here for compatibility.

        :param X: input DataFrame.
        :return: self
        """
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform method to drop rows with NaN and infinite values.

        :param X: Input DataFrame.
        :return: DataFrame with rows containing NaN and infinite values
            dropped.
        """
        hdbg.dassert_isinstance(X, pd.DataFrame)
        # Check if the the dataframe is empty
        hdbg.dassert_lt(0, X.shape[0])
        # Drop rows with NaN values.
        X.dropna(inplace=True)
        # Drop rows with infinite values.
        X.replace([np.inf, -np.inf], np.nan, inplace=True)
        X.dropna(inplace=True)
        return X


def preprocess_and_unravel_data(
    df: pd.DataFrame,
    *,
    add_epsilon_flag: bool = False,
    epsilon_columns: Optional[List[str]] = ["HS", "AS"],
    test_size: float = 0.2,
    stratify: bool = True,
    label_encode: bool = False,
    stratify_column: str = "HT",
) -> (Dict, LabelEncoder):
    """
    Preprocess, split, and unravel the ISDB dataframe of interest.

    :param df: Input DataFrame.
    :param add_epsilon_flag: Flag to indicate if epsilon should be added
        to scores.
    :param epsilon_columns: List of columns to which epsilon should be
        added.
    :param test_size: Proportion of the dataset to include in the test
        split.
    :param stratify: Whether to stratify the split based on the
        stratify_column.
    :param stratify_column: The column to use for stratification if
        stratify is True.
    :return: Dictionary containing the preprocessed and unraveled train
        and test DataFrames.
    """
    # Define the preprocessing pipeline.
    pipeline_steps = [
        ("general_preprocessing", GeneralPreprocessing()),
        ("drop_nan_and_inf", Dropnan()),
    ]
    if add_epsilon_flag:
        pipeline_steps.append(
            (
                "add_epsilon",
                FunctionTransformer(
                    add_epsilon,
                    kw_args={"epsilon": 0.5, "columns": epsilon_columns},
                ),
            )
        )
    pipeline = Pipeline(pipeline_steps)
    # Apply the initial pipeline to the combined data.
    preprocessed_df = pipeline.fit_transform(df)
    # Split the data into training and testing sets.
    split_data = rasoprut.create_train_test_split(
        preprocessed_df,
        stratify=stratify,
        stratify_column=stratify_column,
        test_size=test_size,
    )
    train_df, test_df = split_data["train_df"], split_data["test_df"]
    # Apply label encoding on the combined dataset.
    combined_df = pd.concat([train_df, test_df])
    if label_encode:
        label_encoder = LabelEncoding(columns=["HT", "AT"])
        combined_df_encoded = label_encoder.fit_transform(combined_df)
        # Split the encoded combined dataset back into train and test sets.
        train_df_encoded = combined_df_encoded.loc[train_df.index]
        test_df_encoded = combined_df_encoded.loc[test_df.index]
        # Apply the unravel step to both train and test sets.
        unravel = UnravelData()
        preprocessed_train_df = unravel.fit_transform(train_df_encoded)
        preprocessed_test_df = unravel.transform(test_df_encoded)
        return {
            "train_df": preprocessed_train_df,
            "test_df": preprocessed_test_df,
        }, label_encoder
    else:
        unravel = UnravelData()
        preprocessed_train_df = unravel.fit_transform(train_df)
        preprocessed_test_df = unravel.transform(test_df)
        return {
            "train_df": preprocessed_train_df,
            "test_df": preprocessed_test_df,
        }, {}
