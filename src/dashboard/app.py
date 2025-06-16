import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pickle

from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.utils.database import (
    load_latest_data,
    load_historical_data,
    get_data_freshness,
)
from src.dashboard.utils.helpers import get_machine_status
from src.dashboard.config.settings import (
    DB_URI,
    DEFAULT_TIME_RANGE,
)
from src.dashboard.utils.predicting import inference, clear_prediction_cache
from src.dashboard.tabs.overview import overview_tab
from src.dashboard.tabs.temperature import temperature_tab
from src.dashboard.tabs.production import production_tab
from src.dashboard.tabs.leakage import leakage_tab


def load_model():
    """Load model with caching"""
    if "model" not in st.session_state:
        try:
            with open("src/models/v1/ilapak3/lgbm-model-ilapak3-v1.0.0.pkl", "rb") as f:
                st.session_state.model = pickle.load(f)
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
            st.stop()


def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        "last_update": time.time(),
        "auto_refresh_enabled": True,
        "time_range": DEFAULT_TIME_RANGE,
        "data_refresh_count": 0,
        "last_data_hash": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def check_data_changes(latest_df):
    """Check if data has changed to trigger refresh"""
    if latest_df.empty:
        return False

    # Create hash of current data
    current_hash = hash(str(latest_df.iloc[0].values.tobytes()))

    if st.session_state.last_data_hash != current_hash:
        st.session_state.last_data_hash = current_hash
        st.session_state.data_refresh_count += 1
        return True

    return False


def render_data_freshness_indicator(latest_df):
    """Show data freshness status"""
    freshness = get_data_freshness(latest_df)

    if freshness["is_fresh"]:
        st.success(
            f"🟢 Live Data (Updated: {freshness['last_update'].strftime('%H:%M:%S')})"
        )
    else:
        delay_min = freshness.get("delay_minutes", 0)
        if delay_min < 1.2:
            st.warning(f"🟡 Data Delay: {delay_min:.1f} minutes")
        else:
            st.error(f"🔴 Data Stale: {delay_min:.1f} minutes behind")
            st.rerun()


def render_metrics(latest_df):
    """Render main dashboard metrics"""
    if latest_df.empty:
        st.error("❌ No data available")
        return

    # Get machine status
    status, status_icon, output_time = get_machine_status(latest_df)

    # Create metrics columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(label="Machine Status", value=f"{status_icon} {status}")

    # Helper function for metric calculation
    def get_metric_delta(col_name):
        if len(latest_df) > 1:
            current = latest_df[col_name].iloc[0]
            previous = latest_df[col_name].iloc[1]
            return current - previous
        return None

    with col2:
        current = latest_df["Availability(%)"].iloc[0]
        delta = get_metric_delta("Availability(%)")
        st.metric(
            "Availability",
            f"{current:.1f}%",
            f"{delta:.1f}%" if delta is not None else None,
        )

    with col3:
        current = latest_df["Performance(%)"].iloc[0]
        delta = get_metric_delta("Performance(%)")
        st.metric(
            "Performance",
            f"{current:.1f}%",
            f"{delta:.1f}%" if delta is not None else None,
        )

    with col4:
        current = latest_df["Quality(%)"].iloc[0]
        delta = get_metric_delta("Quality(%)")
        st.metric(
            "Quality", f"{current:.1f}%", f"{delta:.1f}%" if delta is not None else None
        )

    with col5:
        current = latest_df["OEE(%)"].iloc[0]
        delta = get_metric_delta("OEE(%)")
        st.metric(
            "OEE", f"{current:.1f}%", f"{delta:.1f}%" if delta is not None else None
        )

    with col6:
        # Prediction with error handling
        try:
            pred, probs = inference(latest_df, st.session_state.model)
            max_prob = probs.max() * 100 if len(probs) > 0 else 0

            # Color based on prediction
            if pred == "Normal":
                delta_color = "normal"
            elif pred == "Warning":
                delta_color = "inverse"
            else:
                delta_color = "inverse"

            st.metric(
                "Leakage Prediction",
                pred,
                f"Confidence: {max_prob:.1f}%",
            )
        except Exception as e:
            st.metric("Leakage Prediction", "Error", f"Model Error")


def main():
    # Page configuration
    st.set_page_config(
        page_title="PdM Dashboard - Ilapak 3",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Custom CSS
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .status-good { color: #28a745; font-weight: bold; }
        .status-warning { color: #ffc107; font-weight: bold; }
        .status-danger { color: #dc3545; font-weight: bold; }
        .refresh-info {
            font-size: 0.8rem;
            color: #666;
            text-align: center;
            margin-top: 0.5rem;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Initialize session state
    if "last_data_hash" not in st.session_state:
        st.session_state.last_data_hash = None
    if "data_refresh_count" not in st.session_state:
        st.session_state.data_refresh_count = 0
    if "auto_refresh_enabled" not in st.session_state:
        st.session_state.auto_refresh_enabled = True
    if "time_range" not in st.session_state:
        st.session_state.time_range = "Last 24 Hours"
    if "last_update" not in st.session_state:
        st.session_state.last_update = time.time()

    # Initialize
    initialize_session_state()
    load_model()

    # Sidebar
    with st.sidebar:
        auto_refresh, refresh_interval, time_range = render_sidebar()

    # Main header
    st.markdown(
        '<h1 class="main-header">🏭 Predictive Maintenance Dashboard - Ilapak 3</h1>',
        unsafe_allow_html=True,
    )

    # Auto-refresh logic with 1-minute interval
    if auto_refresh:
        count = st_autorefresh(
            interval=refresh_interval * 1000,
            key="dashboard_refresh",  # Convert minutes to milliseconds
        )
        if count > 0:
            st.session_state.last_update = time.time()

    # Load data with error handling
    try:
        with st.spinner("Loading data..."):
            latest_df = load_latest_data(DB_URI, limit=20)
            historical_df = load_historical_data(DB_URI, time_range, max_records=1000)
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

    if latest_df.empty:
        st.error("❌ No data available. Check database connection.")
        st.stop()

    # Check for data changes
    data_changed = check_data_changes(latest_df)

    # Data freshness indicator
    render_data_freshness_indicator(latest_df)

    # Main metrics
    render_metrics(latest_df)

    # Tabs with real-time data
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Overview", "🌡️ Temperature", "📈 Production", "🚨 Leakage Detection"]
    )

    # Pass data to tabs
    with tab1:
        overview_tab(historical_df, latest_df, time_range)

    with tab2:
        temperature_tab(historical_df, latest_df, time_range)

    with tab3:
        production_tab(historical_df, latest_df, time_range)

    with tab4:
        leakage_tab(historical_df, latest_df, time_range)

    # Footer info
    # Fixed minimal elegant footer
    # Fixed transparent blurred footer
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            backdrop-filter: blur(6px);
            background-color: rgba(255, 255, 255, 0.6);
            padding: 0.6rem 1rem;
            text-align: center;
            font-size: 0.75rem;
            color: #495057;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            z-index: 9999;
        }

        @media (prefers-color-scheme: dark) {
            .footer {
                background-color: rgba(33, 37, 41, 0.5);
                color: #dee2e6;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
        }
        </style>
        <div class="footer">
            © 2025 Built by <strong>@nangdosan</strong> — BTS Batch 3
        </div>
        """,
        unsafe_allow_html=True,
    )
