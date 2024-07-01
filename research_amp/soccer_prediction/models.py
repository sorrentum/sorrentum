"""
Import as:

import research_amp.soccer_prediction.models as rasoprmo
"""

import logging
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import sklearn.linear_model as slm
import statsmodels.api as sm
import statsmodels.formula.api as smf

# import xgboost as xgb
import jpickle

import sklearn.metrics as skm
import sklearn.model_selection as sms

import helpers.haws as haws
import helpers.hdbg as hdbg
import research_amp.soccer_prediction.utils as rasoprut

_LOG = logging.getLogger(__name__)


class BaseModel:
    """
    Define standard interface for models with fit and predict methods.
    """

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Fit the model using the training data.

        :param X: Feature matrix.
        :param y: Target vector.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict using the fitted model.

        :param X: Feature matrix.
        :return: Predictions as a NumPy array.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class PoissonModel(BaseModel):
    """
    PoissonModel implements a Poisson regression model using statsmodels.
    """

    def __init__(self, *, hyperparams: Optional[Dict[str, Any]] = None):
        self.hyperparams = hyperparams or {}
        self.model = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Fit the Poisson regression model.

        :param X: Feature matrix as a DataFrame.
        :param y: Target vector as a Series.
        """
        hdbg.dassert_isinstance(X, pd.DataFrame)
        hdbg.dassert_isinstance(y, pd.Series)
        data = pd.concat([X, y], axis=1)
        formula = self.hyperparams.get("formula", "")
        max_iter = self.hyperparams.get("maxiter", 10)
        self.model = smf.glm(
            formula=formula, data=data, family=sm.families.Poisson()
        ).fit(maxiter=max_iter)
        _LOG.info("Poisson model fitted successfully.")
        _LOG.info(self.model.summary())

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict using the fitted Poisson regression model.

        :param X: Feature matrix as a DataFrame.
        :return: Predictions as a NumPy array.
        """
        if self.model is not None:
            y_pred = self.model.predict(X)
        else:
            raise ValueError("Model is not fitted yet.")
        return y_pred


# class XGBoostModel(BaseModel):
#    """
#    XGBoostModel implements a regression model using xgboost.XGBRegressor.
#    """
#
#   def __init__(self, hyperparams: Optional[Dict[str, Any]] = None):
#        self.hyperparams = hyperparams or {}
#        self.model = xgb.XGBRegressor(**self.hyperparams, random_state=42)

#    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
#        """
#        Fit the XGBoost regression model.

#        :param X: Feature matrix as a DataFrame.
#        :param y: Target vector as a Series.
#        """
#        hdbg.dassert_isinstance(X, pd.DataFrame)
#        hdbg.dassert_isinstance(y, pd.Series)
#        self.model.fit(X, y)
#        _LOG.info("XGBoost model fitted successfully.")
#        _LOG.info("Feature importances: %s", self.model.feature_importances_)

#    def predict(self, X: pd.DataFrame) -> np.ndarray:
#        """
#        Predict using the fitted XGBoost regression model.
#
#        :param X: Feature matrix as a DataFrame.
#        :return: Predictions as a NumPy array.
#        """
#        if self.model is not None:
#            y_pred = self.model.predict(X)
#        else:
#            raise ValueError("Model is not fitted yet.")
#        return y_pred


class LinearRegressionModel(BaseModel):
    """
    LinearRegressionModel implements a linear regression model using sklearn.
    """

    def __init__(self, *, hyperparams: Optional[Dict[str, Any]] = None):
        self.hyperparams = hyperparams or {}
        self.model = slm.LinearRegression(**self.hyperparams)

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Fit the linear regression model.

        :param X: Feature matrix as a DataFrame.
        :param y: Target vector as a Series.
        """
        hdbg.dassert_isinstance(X, pd.DataFrame)
        hdbg.dassert_isinstance(y, pd.Series)
        self.model.fit(X, y)
        _LOG.info("Linear regression model fitted successfully.")
        _LOG.info("Coefficients: %s", self.model.coef_)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict using the fitted linear regression model.

        :param X: Feature matrix as a DataFrame.
        :return: Predictions as a NumPy array.
        """
        if self.model is not None:
            y_pred = self.model.predict(X)
        else:
            raise ValueError("Model is not fitted yet.")
        return y_pred


def train_model(
    train_df: pd.DataFrame,
    model: BaseModel,
    hyperparameters: Dict,
    *,
    target_column: str = "goals",
    logging_level: int = logging.INFO,
    n_splits: int = 5,
    **kwargs: Any,
) -> BaseModel:
    """
    Train a model log the results, and save the trained model to S3.

    :param train_df: Input training set.
    :param model: Model object that implements fit() and predict().
    :param hyperparameters: dictionary of hyperparameters for models.
    :param target_columns: target column/variable of interest.
    :param logging_level: Logging level for the model summary.
    :param n_splits: Number of splits for cross-validation.
    :return: Trained model.
    """
    # Configure logging.
    logging.basicConfig(level=logging_level)
    train_accuracies = []
    val_accuracies = []
    train_mae = []
    val_mae = []
    model.hyperparams = hyperparameters
    sample_sizes = kwargs.get("sample_sizes")
    # Split the data into training and validation sets.
    for sample_size in sample_sizes:
        # Sample the training data.
        sample_train_data = train_df.sample(n=sample_size, random_state=42)
        train_data, val_data = sms.train_test_split(
            sample_train_data, test_size=0.2, random_state=42
        )
        y_train = train_data[target_column]
        X_train = train_data.drop(target_column, axis=1)
        y_val = val_data[target_column]
        X_val = val_data.drop(target_column, axis=1)
        # Fit the Poisson regression model on the sampled training data.
        model.fit(X_train, y_train)
        train_preds = model.predict(X_train)
        val_preds = model.predict(X_val)
        # Predict on training and validation sets.
        train_preds_rounded = np.round(train_preds).astype(int)
        val_preds_rounded = np.round(val_preds).astype(int)
        y_train = y_train.astype(int)
        y_val = y_val.astype(int)
        train_acc = skm.accuracy_score(y_train, train_preds_rounded)
        val_acc = skm.accuracy_score(y_val, val_preds_rounded)
        train_accuracies.append(train_acc)
        val_accuracies.append(val_acc)
        # Calculate MAE for training and validation sets.
        train_mae_value = skm.mean_absolute_error(y_train, train_preds)
        val_mae_value = skm.mean_absolute_error(y_val, val_preds)
        train_mae.append(train_mae_value)
        val_mae.append(val_mae_value)
        logging.info(
            "Sample Size: %f, Train MAE: %f, Validation MAE: %f",
            sample_size,
            train_mae_value,
            val_mae_value,
        )
    # Plot metrics.
    rasoprut.plot_learning_curves(train_mae, val_mae, sample_sizes)
    coeffs = model.model.params
    # Plot the residuals.
    residuals = model.model.resid_deviance
    rasoprut.plot_metrics(
        train_accuracies=train_accuracies,
        val_accuracies=val_accuracies,
        coeffs=coeffs,
        residuals=residuals,
        n_splits=len(sample_sizes),
    )
    max_index = np.argmax(val_accuracies)
    train_data = train_df.sample(n=sample_sizes[max_index], random_state=42)
    y_train = train_data[target_column]
    X_train = train_data.drop(target_column, axis=1)
    # Fit the Poisson regression model on the sampled training data
    model.fit(X_train, y_train)
    return model


def save_model_to_s3(
    model: BaseModel,
    local_path: str,
    s3_bucket: str,
    s3_path: str,
    aws_profile: str,
) -> None:
    """
    Save the model locally and upload to S3.

    :param model: Trained model to be saved.
    :param local_path: Local path to save the model.
    :param s3_bucket: S3 bucket name.
    :param s3_path: S3 path where the model will be uploaded.
    :param aws_profile: AWS profile name.
    """
    # Save the model locally.
    jpickle.dump(model, local_path)
    # Upload the model to S3.
    s3 = haws.get_service_resource(aws_profile=aws_profile, service_name="s3")
    s3.Bucket(s3_bucket).upload_file(local_path, s3_path)
