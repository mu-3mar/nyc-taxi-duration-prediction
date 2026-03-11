"""Evaluation utilities for trip duration model."""

import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score

from .preprocessing import TripDataPreprocessor


def evaluate_dataset(df, model, label="Dataset"):
    """
    Evaluate model on a preprocessed dataset with trip_duration.

    Parameters
    ----------
    df : pd.DataFrame
        Preprocessed data including 'trip_duration'.
    model : fitted regressor
        Model with .predict(X).
    label : str
        Name for logging.

    Returns
    -------
    dict
        Keys: 'r2', 'mse', 'label'.
    """
    X = df.drop(columns=["trip_duration"])
    y = df["trip_duration"]
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    print(f"{label} — R²: {r2 * 100:.2f}%, MSE: {mse:.4f}")
    return {"r2": r2, "mse": mse, "label": label}


def load_and_evaluate(val_path, test_path, model_path, preprocessor=None):
    """
    Load validation and test CSVs, preprocess, load model, and evaluate both.

    Parameters
    ----------
    val_path : str
        Path to validation CSV.
    test_path : str
        Path to test CSV.
    model_path : str
        Path to joblib-saved model (.pkl).
    preprocessor : TripDataPreprocessor, optional
        If None, a new instance is used.
    """
    import joblib

    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)
    val_df["__set__"] = "val"
    test_df["__set__"] = "test"
    combined = pd.concat([val_df, test_df], ignore_index=True)

    if preprocessor is None:
        preprocessor = TripDataPreprocessor()
    combined = preprocessor.fit_transform(combined)

    model = joblib.load(model_path)

    val_processed = combined[combined["__set__"] == "val"].drop(columns=["__set__"])
    test_processed = combined[combined["__set__"] == "test"].drop(columns=["__set__"])

    evaluate_dataset(val_processed, model, label="Validation")
    evaluate_dataset(test_processed, model, label="Test")
