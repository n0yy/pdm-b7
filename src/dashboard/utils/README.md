Utils Documentation
Overview
Utility functions for database operations, data processing, and ML predictions.
Files
database.py
Optimized database operations with caching.
Key Functions:
python@st.cache_data(ttl=10)
def load_latest_data(uri: str, limit: int = 20) -> pd.DataFrame

@st.cache_data(ttl=30)  
def load_historical_data(uri: str, time_range: str, max_records: int = 1000) -> pd.DataFrame

def get_data_freshness(df: pd.DataFrame) -> dict
Features:

Connection pooling with SQLAlchemy
Smart sampling for large datasets (7+ days)
Multi-level caching (10-30s TTL)
Data freshness monitoring
Query optimization with time-based filtering

helpers.py
General utility functions for data processing.
Key Functions:
pythondef get_machine_status(df) -> tuple[str, str, float]
def preprocess_dataframe(df: pd.DataFrame, set_index: bool = True) -> pd.DataFrame
def convert_time_to_seconds(time_str) -> int
Features:

Machine status detection (Running/Idle/Stopped)
DataFrame preprocessing and cleaning
Time format conversion (hh:mm:ss to seconds)
Missing value handling

predicting.py
ML prediction pipeline with advanced caching.
Key Functions:
pythondef inference(data: pd.DataFrame, \_estimator, classes: dict) -> tuple[str, np.ndarray]
def batch_inference(data: pd.DataFrame, \_estimator, classes: dict) -> tuple[list, list]
Features:

Thread-safe prediction caching
Batch processing for historical data
Single prediction for real-time analysis
Optimized preprocessing pipeline
Error handling and recovery

Cache Classes:

PredictionCache: Thread-safe cache with TTL
Cache cleanup and memory management
Performance optimization for repeated predictions

feature_engineering.py
Data preprocessing for ML models.
Key Function:
pythondef preprocess(data: pd.DataFrame) -> pd.DataFrame
Transformations:

Time features (day, hour, minute)
Time duration conversion (hh:mm:ss to seconds)
Derived features (temperature differences, output deltas)
Data differencing for trend analysis

Performance Optimizations
Caching Strategy

Data: 10-30s TTL based on update frequency
Predictions: 15-60s TTL with thread safety
Preprocessing: 30s cache for feature engineering

Memory Management

Automatic cache cleanup
Batch size optimization
Connection pooling
Smart sampling for large datasets
