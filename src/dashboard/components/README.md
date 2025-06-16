# Dashboard Components Documentation

## Overview

Reusable UI components for the predictive maintenance dashboard.

## Files

### charts.py

Interactive chart creation using Plotly.

```python
def create_realtime_chart(
    df: pd.DataFrame,
    columns: list,
    title: str = None,
    max_points: int = 100,
    y_lim: tuple = None,
    secondary_y_cols: list = None
) -> go.Figure
```

**Features:**

- **Performance Optimization**: Smart point sampling for large datasets
- **Dual Y-axis**: Support for different metric scales
- **Interactive**: Hover tooltips, zoom, pan capabilities
- **Responsive**: Adapts to container width
- **Color Coding**: Consistent color scheme across charts

**Usage:**

```python
# Basic chart
fig = create_realtime_chart(df, ['Temperature', 'Pressure'])

# With secondary Y-axis
fig = create_realtime_chart(
    df,
    ['Output', 'Rejects'],
    secondary_y_cols=['Rejects']
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)
```

### sidebar.py

Dashboard control panel with real-time settings.

```python
def render_sidebar() -> tuple[bool, int, str]
```

**Controls:**

- **Auto-refresh Toggle**: Enable/disable live updates
- **Refresh Intervals**: 30s, 60s, 120s, 300s options
- **Time Range Selection**: Historical data filtering
- **Manual Refresh**: Force immediate data reload
- **Connection Status**: Database health indicator

**Returns:**

- `auto_refresh`: Boolean flag for auto-refresh state
- `refresh_interval`: Selected interval in seconds
- `time_range`: Selected historical time range

**Features:**

- **Session Persistence**: Settings maintained across refreshes
- **Visual Feedback**: Color-coded status indicators
- **Error Handling**: Connection failure notifications
- **Performance Info**: Data sampling notifications for large ranges

## Design Principles

### Consistency

- Uniform color schemes across components
- Standardized spacing and typography
- Consistent interaction patterns

### Performance

- Efficient rendering for real-time updates
- Smart data sampling for large datasets
- Memory-conscious component design

### Accessibility

- High contrast color combinations
- Semantic HTML structure
- Keyboard navigation support

## Integration

Components integrate seamlessly with main dashboard:

```python
# In app.py
from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.components.charts import create_realtime_chart

# Sidebar integration
with st.sidebar:
    auto_refresh, refresh_interval, time_range = render_sidebar()

# Chart integration
fig = create_realtime_chart(data, columns)
st.plotly_chart(fig, use_container_width=True)
```
