# Dashboard Tabs Documentation

## Overview

Tab implementations for different monitoring aspects of the dashboard.

## Files

### overview.py

Main dashboard overview with key metrics.

```python
def overview_tab(historical_df, latest_df, time_range)
```

**Features:**

- Efficiency trends (Availability, Performance, Quality, OEE)
- Recent data table with key metrics
- Historical analysis over selected time range

### temperature.py

Temperature monitoring for sealing sensors.

```python
def temperature_tab(historical_df, latest_df, time_range)
```

**Displays:**

- Current temperatures from 4 sealing sensors
- Color-coded temperature readings (normal/warning/danger)
- Statistical summary (min, max, average)
- Historical temperature trends

**Temperature Zones:**

- Blue (<50°C): Normal
- Green (50-80°C): Optimal
- Red (>80°C): High

### production.py

Production metrics and performance tracking.

```python
def production_tab(historical_df, latest_df, time_range)
```

**Metrics:**

- Current speed (RPM)
- Output counters with delta calculations
- Reject tracking
- Speed and output trend charts

### leakage.py

ML-powered leakage prediction interface.

```python
def leakage_tab(historical_df, latest_df, time_range)
```

**Features:**

- Real-time prediction statistics
- Batch inference for historical data
- Prediction trend visualization
- Recent predictions table
- Color-coded prediction results (Normal/Warning/Leak)

## Data Flow

Each tab receives:

- `historical_df`: Time-filtered historical data
- `latest_df`: Most recent data points
- `time_range`: Selected time range string

Data processing:

1. Preprocess dataframes using helper functions
2. Calculate metrics and deltas
3. Create visualizations
4. Display results in Streamlit interface

## Integration

Tabs are integrated in main app.py:

```python
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🌡️ Temperature",
    "📈 Production",
    "🚨 Leakage Detection"
])

with tab1:
    overview_tab(historical_df, latest_df, time_range)
# ... other tabs
```
