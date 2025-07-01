import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from src.dashboard.utils.feature_engineering import preprocess
import streamlit as st
from typing import Dict, List, Tuple, Optional
import threading
import time


class PredictionCache:
    """Thread-safe prediction cache for better performance"""

    def __init__(self, max_size: int = 1000, ttl: int = 60):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.Lock()

    def _generate_key(self, data: pd.DataFrame) -> str:
        """Generate cache key from DataFrame hash"""
        try:
            # Use first and last row data + shape as key
            if len(data) > 0:
                first_row = str(data.iloc[0].values)
                last_row = str(data.iloc[-1].values) if len(data) > 1 else ""
                return f"{len(data)}_{hash(first_row + last_row)}"
            return "empty"
        except:
            return str(time.time())

    def get(self, data: pd.DataFrame) -> Optional[Tuple]:
        """Get cached prediction if available and fresh"""
        key = self._generate_key(data)

        with self.lock:
            if key in self.cache:
                if time.time() - self.timestamps[key] < self.ttl:
                    return self.cache[key]
                else:
                    del self.cache[key]
                    del self.timestamps[key]

        return None

    def set(self, data: pd.DataFrame, result: Tuple):
        """Cache prediction result"""
        key = self._generate_key(data)

        with self.lock:
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(
                    self.timestamps.keys(), key=lambda k: self.timestamps[k]
                )
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]

            self.cache[key] = result
            self.timestamps[key] = time.time()


# Global prediction cache
_prediction_cache = PredictionCache()


def preprocess_for_inference(data: pd.DataFrame) -> pd.DataFrame:
    """Optimized preprocessing for inference only"""
    if data.empty:
        return data

    # Use cached preprocessing if available
    cache_key = f"preprocess_{hash(str(data.values.tobytes()))}"

    # Check if we have processed this data recently
    if hasattr(st.session_state, "preprocess_cache"):
        if cache_key in st.session_state.preprocess_cache:
            cache_time, cached_result = st.session_state.preprocess_cache[cache_key]
            if time.time() - cache_time < 30:  # 30 second cache
                return cached_result
    else:
        st.session_state.preprocess_cache = {}

    # Process data
    processed_data = preprocess(data)

    # Cache result
    st.session_state.preprocess_cache[cache_key] = (time.time(), processed_data)

    # Clean old cache entries
    current_time = time.time()
    st.session_state.preprocess_cache = {
        k: v
        for k, v in st.session_state.preprocess_cache.items()
        if current_time - v[0] < 300
    }

    return processed_data


@st.cache_data(ttl=30, max_entries=10)
def batch_inference_cached(
    data_hash: str,
    _estimator: Pipeline,
    classes: Dict = {0: "Normal", 1: "Warning", 2: "Leak"},
) -> Tuple[List[str], List[float]]:
    """Cached version of batch inference using data hash"""
    # This function gets the actual data from session state
    if "temp_inference_data" not in st.session_state:
        return [], []

    data = st.session_state.temp_inference_data

    if data.empty:
        return [], []

    # Preprocess data
    X = preprocess_for_inference(data)

    # Batch processing with optimized batch size
    batch_size = min(50, len(X))  # Smaller batches for better performance
    predictions = []
    probabilities = []

    try:
        for i in range(0, len(X), batch_size):
            batch = X.iloc[i : i + batch_size]

            # Predict in batches
            batch_preds = _estimator.predict(batch)
            batch_probs = _estimator.predict_proba(batch)

            # Convert predictions
            batch_pred_labels = [classes.get(pred, "Unknown") for pred in batch_preds]
            batch_max_probs = [probs.max() for probs in batch_probs]

            predictions.extend(batch_pred_labels)
            probabilities.extend(batch_max_probs)

    except Exception as e:
        st.error(f"Error in batch inference: {str(e)}")
        return [], []

    return predictions, probabilities


def batch_inference(
    data: pd.DataFrame,
    _estimator: Pipeline,
    classes: Dict = {0: "Normal", 1: "Warning", 2: "Leak"},
) -> Tuple[List[str], List[float]]:
    """
    Optimized batch inference with caching
    """
    if data.empty:
        return [], []

    # Check cache first
    cached_result = _prediction_cache.get(data)
    if cached_result is not None:
        return cached_result

    # Generate hash for caching
    data_hash = hash(str(data.values.tobytes()))

    # Store data temporarily for cached function
    st.session_state.temp_inference_data = data

    try:
        # Use cached function
        predictions, probabilities = batch_inference_cached(
            str(data_hash), _estimator, classes
        )

        # Cache the result
        result = (predictions, probabilities)
        _prediction_cache.set(data, result)

        return result

    finally:
        # Clean up temporary data
        if "temp_inference_data" in st.session_state:
            del st.session_state.temp_inference_data


def inference(
    data: pd.DataFrame,
    _estimator: Pipeline,
    classes: Dict = {0: "Normal", 1: "Warning", 2: "Leak"},
) -> Tuple[str, np.ndarray]:
    """
    Optimized single inference
    """
    if data.empty:
        return "Unknown", np.array([0, 0, 0])

    # Determine machine status from the first (most recent) row
    first_status = data["Status"].iloc[0] if "Status" in data.columns else None
    if first_status != 2:
        return "Excluded", np.array([0, 0, 0])

    try:
        # Use only the first row for single inference
        single_row = data.iloc[[0]]

        # Check if we have this exact prediction cached
        cache_key = f"single_{hash(str(single_row.values.tobytes()))}"

        if hasattr(st.session_state, "single_prediction_cache"):
            if cache_key in st.session_state.single_prediction_cache:
                cache_time, cached_result = st.session_state.single_prediction_cache[
                    cache_key
                ]
                if (
                    time.time() - cache_time < 15
                ):  # 15 second cache for single predictions
                    return cached_result
        else:
            st.session_state.single_prediction_cache = {}

        # Preprocess single row
        X = preprocess_for_inference(single_row)

        # Make prediction
        pred_num = _estimator.predict(X)[0]
        pred_label = classes.get(pred_num, "Unknown")
        probs = _estimator.predict_proba(X)[0]

        result = (pred_label, probs)

        # Cache result
        st.session_state.single_prediction_cache[cache_key] = (time.time(), result)

        # Clean old cache entries
        current_time = time.time()
        st.session_state.single_prediction_cache = {
            k: v
            for k, v in st.session_state.single_prediction_cache.items()
            if current_time - v[0] < 60
        }

        return result

    except Exception as e:
        st.error(f"Error in single inference: {str(e)}")
        return "Error", np.array([0, 0, 0])


def get_prediction_summary(predictions: List[str]) -> Dict:
    """Get summary of predictions for dashboard metrics"""
    if not predictions:
        return {"Normal": 0, "Warning": 0, "Leak": 0, "total": 0}

    from collections import Counter

    counts = Counter(predictions)
    total = len(predictions)

    return {
        "Normal": counts.get("Normal", 0),
        "Warning": counts.get("Warning", 0),
        "Leak": counts.get("Leak", 0),
        "total": total,
        "normal_pct": counts.get("Normal", 0) / total * 100 if total > 0 else 0,
        "warning_pct": counts.get("Warning", 0) / total * 100 if total > 0 else 0,
        "leak_pct": counts.get("Leak", 0) / total * 100 if total > 0 else 0,
    }


def clear_prediction_cache():
    """Clear all prediction caches"""
    global _prediction_cache
    _prediction_cache = PredictionCache()

    if hasattr(st.session_state, "preprocess_cache"):
        st.session_state.preprocess_cache = {}
    if hasattr(st.session_state, "single_prediction_cache"):
        st.session_state.single_prediction_cache = {}
