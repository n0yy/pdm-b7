import pandas as pd
from sklearn.pipeline import Pipeline
from src.dashboard.utils.feature_engineering import preprocess


def inference(
    data: pd.DataFrame,
    estimator: Pipeline,
    classes: dict = {0: "Normal", 1: "Warning", 2: "Leak"},
):
    X = preprocess(data)
    pred = classes[estimator.predict(X)[0]]
    probs = estimator.predict_proba(X)[0]

    return pred, probs
