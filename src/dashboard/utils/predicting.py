import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from src.dashboard.utils.feature_engineering import preprocess
import streamlit as st


@st.cache_data(ttl=60)  # Cache predictions for 1 minute
def batch_inference(
    data: pd.DataFrame,
    _estimator: Pipeline,
    classes: dict = {0: "Normal", 1: "Warning", 2: "Leak"},
    batch_size: int = 100,
) -> tuple:
    """
    Melakukan inference secara batch untuk meningkatkan performa
    Args:
        data: DataFrame input
        _estimator: Model pipeline (tidak di-hash oleh Streamlit)
        classes: Mapping kelas
        batch_size: Ukuran batch untuk processing
    Returns:
        Tuple dari (predictions, probabilities)
    """
    if data.empty:
        return [], []

    # Preprocess data
    X = preprocess(data)

    # Batch processing
    predictions = []
    probabilities = []

    for i in range(0, len(X), batch_size):
        batch = X.iloc[i : i + batch_size]
        batch_preds = _estimator.predict(batch)
        batch_probs = _estimator.predict_proba(batch)

        predictions.extend([classes[pred] for pred in batch_preds])
        probabilities.extend([probs.max() for probs in batch_probs])

    return predictions, probabilities


def inference(
    data: pd.DataFrame,
    _estimator: Pipeline,
    classes: dict = {0: "Normal", 1: "Warning", 2: "Leak"},
) -> tuple:
    """
    Fungsi inference untuk single prediction
    """
    if data.empty:
        return "Unknown", np.array([0, 0, 0])

    X = preprocess(data)
    pred = classes[_estimator.predict(X)[0]]
    probs = _estimator.predict_proba(X)[0]

    return pred, probs
