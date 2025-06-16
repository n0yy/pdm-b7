# Dashboard Module Documentation

## Overview

The dashboard module provides a real-time web interface for monitoring industrial equipment and predictive maintenance analytics.

## Structure

```
src/dashboard/
├── app.py                    # Main application entry point
├── components/               # Reusable UI components
│   ├── charts.py            # Chart creation utilities
│   └── sidebar.py           # Sidebar controls
├── tabs/                    # Dashboard tab implementations
│   ├── overview.py          # Main metrics overview
│   ├── temperature.py       # Temperature monitoring
│   ├── production.py        # Production metrics
│   └── leakage.py          # Leakage prediction
├── utils/                   # Utility functions
│   ├── database.py          # Database operations
│   ├── helpers.py           # General helper functions
│   ├── predicting.y         # ML prediction utilities
│   └── feature_engineering.py # Data preprocessing
└── config/                  # Configuration
    └── settings.py          # Application settings
```

## Core Components

### app.py

Main dashboard application with:

- **Session State Management**: Handles user sessions and caching
- **Auto-refresh Logic**: Configurable real-time data updates
- **Model Loading**: ML model initialization and caching
- **Data Flow Control**: Coordinates between database, processing, and display
- **Error Handling**: Comprehensive error recovery and user feedback

Key Functions:

```python
def main()                    # Main application entry
def load_model()             # Model loading with caching
def initialize_session_state() # Session initialization
def render_metrics()         # Main dashboard metrics
def check_data_changes()     # Data change detection
```

### components/

#### charts.py

Chart creation utilities using Plotly:

```python
def create_realtime_chart(
    df, columns, title=None,
    max_points=100, y_lim=None,
    secondary_y_cols=None
)
```

- **Real-time Line Charts**: Optimized for live data
- **Dual Y-axis Support**: For different metric scales
- **Performance Optimization**: Smart point sampling
- **Interactive Features**: Hover, zoom, pan capabilities

#### sidebar.py

Dashboard control interface:

```python
def render_sidebar() -> tuple
```

- **Auto-refresh Controls**: Toggle and interval selection
- **Time Range Selection**: Historical data filtering
- **Connection Status**: Database health monitoring
- **Manual Refresh**: Force data reload

### tabs/

#### overview.py

Main dashboard overview:

- **Efficiency Trends**: OEE, Availability, Performance, Quality
- **Recent Data Table**: Latest operational data
- **Historical Analysis**: Time-series visualization

#### temperature.py

Temperature monitoring interface:

- **Multi-sensor Display**: 4 sealing temperature sensors
- **Real-time Values**: Current temperature readings
- **Statistical Summary**: Min, max, average calculations
- **Trend Analysis**: Historical temperature patterns
- **Alert System**: Color-coded temperature warnings

#### production.py

Production metrics dashboard:

- **Speed Monitoring**: RPM tracking and trends
- **Output Analysis**: Production counters with deltas
- **Quality Metrics**: Reject rate calculations
- **Dual Charts**: Correlated production visualizations

#### leakage.py

ML-powered anomaly detection:

- **Real-time Predictions**: Live anomaly classification
- **Confidence Scores**: Prediction probability display
- **Historical Trends**: Pattern analysis over time
- **Batch Processing**: Efficient historical analysis

### utils/

#### database.py

Database operations with optimization:

```python
@st.cache_data(ttl=10)
def load_latest_data(uri, limit=20) -> pd.DataFrame

@st.cache_data(ttl=30)
def load_historical_data(uri, time_range, max_records=1000) -> pd.DataFrame

def get_data_freshness(df) -> dict
```

- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Time-based filtering with sampling
- **Caching Strategy**: Multi-level data caching
- **Data Freshness**: Real-time monitoring of data delays

#### helpers.py

General utility functions:

```python
def get_machine_status(df) -> tuple
def preprocess_dataframe(df, set_index=True) -> pd.DataFrame
def get_processed_dataframes(historical_df, latest_df) -> tuple
```

- **Status Detection**: Machine operational state logic
- **Data Preprocessing**: DataFrame cleaning and formatting
- **Time Conversion**: String time to seconds conversion

#### predicting.py

ML prediction pipeline with advanced caching:

```python
def inference(data, _estimator, classes) -> tuple
def batch_inference(data, _estimator, classes) -> tuple
def get_prediction_summary(predictions) -> dict
```

- **Single Prediction**: Real-time anomaly detection
- **Batch Processing**: Historical data analysis
- **Thread-safe Caching**: Performance optimization
- **Error Handling**: Robust prediction pipeline

#### feature_engineering.py

Data preprocessing for ML:

```python
def preprocess(data: pd.DataFrame) -> pd.DataFrame
```

- **Time Features**: Extract day, hour, minute
- **Derived Features**: Temperature differences, output deltas
- **Data Transformation**: Time string to seconds conversion

### config/settings.py

Application configuration:

```python
# Database
DB_URI = "mysql+pymysql://..."

# Dashboard
DEFAULT_TIME_RANGE = "Last 24 Hours"
REFRESH_INTERVALS = [30, 60, 120, 300]
DEFAULT_REFRESH_INTERVAL = 60

# Thresholds
TEMP_WARNING_THRESHOLD = 150
PERFORMANCE_WARNING_THRESHOLD = 70
```

## Performance Features

### Caching Strategy

- **Data Cache**: 10-60s TTL based on update frequency
- **Prediction Cache**: Thread-safe ML result caching
- **Session Cache**: User-specific state management
- **Memory Management**: Automatic cleanup of expired entries

### Optimization Techniques

- **Smart Sampling**: Reduce data points for large time ranges
- **Batch Processing**: Process data in optimized chunks
- **Connection Pooling**: Reuse database connections
- **Lazy Loading**: Load components only when needed

### Error Handling

- **Database Failures**: Graceful connection error recovery
- **Model Errors**: ML prediction error handling
- **Data Issues**: Missing data and validation
- **User Feedback**: Clear error messages and recovery options

## Usage Examples

### Basic Dashboard Launch

```python
from src.dashboard.app import main
main()  # Starts dashboard on localhost:8501
```

### Custom Chart Creation

```python
from src.dashboard.components.charts import create_realtime_chart

fig = create_realtime_chart(
    df=data,
    columns=['Temperature', 'Pressure'],
    title="Sensor Readings",
    secondary_y_cols=['Pressure']
)
```

### Prediction Pipeline

```python
from src.dashboard.utils.predicting import inference

prediction, probabilities = inference(
    data=latest_data,
    _estimator=model,
    classes={0: "Normal", 1: "Warning", 2: "Leak"}
)
```

## Configuration

### Environment Variables

```env
DB_USER=username
DB_PASSWORD=password
DB_HOST=localhost
DB_NAME=database_name
```

### Streamlit Configuration

```toml
[server]
port = 8501
enableWebsocketCompression = false
enableCORS = true
```

## Development Guidelines

### Code Style

- Type hints for all functions
- Comprehensive error handling
- Inline documentation
- Consistent naming conventions

### Performance Considerations

- Cache frequently accessed data
- Minimize database queries
- Optimize DataFrame operations
- Monitor memory usage

### Testing Approach

- Unit tests for utility functions
- Integration tests for database operations
- UI tests for dashboard components
- Performance benchmarks for caching
