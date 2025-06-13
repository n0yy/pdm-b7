import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time

from dashboard.components.sidebar import render_sidebar
from dashboard.utils.database import load_latest_data, load_historical_data
from dashboard.utils.helpers import get_machine_status
from dashboard.config.settings import (
    DB_URI,
    DEFAULT_TIME_RANGE,
)
from dashboard.utils.predicting import inference
from dashboard.tabs.overview import overview_tab
from dashboard.tabs.temperature import temperature_tab
from dashboard.tabs.production import production_tab
from dashboard.tabs.leakage import leakage_tab

# Page configuration
st.set_page_config(
    page_title="PdM Dashboard - Ilapak 3",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 2rem;
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
        margin-top: 1rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()
if "auto_refresh_enabled" not in st.session_state:
    st.session_state.auto_refresh_enabled = True
if "time_range" not in st.session_state:
    st.session_state.time_range = DEFAULT_TIME_RANGE
if "model" not in st.session_state:
    import pickle

    with open("src/models/v1/ilapak3/lgbm-model-ilapak3-v1.0.0.pkl", "rb") as f:
        st.session_state.model = pickle.load(f)


with st.sidebar:
    auto_refresh, refresh_interval, time_range = render_sidebar()


st.markdown(
    '<h1 class="main-header">🏭 Predictive Maintenance Dashboard - Ilapak 3</h1><br><br>',
    unsafe_allow_html=True,
)

if auto_refresh:
    st_autorefresh(interval=refresh_interval * 1000, key="dashboard_refresh")

latest_df = load_latest_data(DB_URI)
historical_df = load_historical_data(DB_URI, time_range)

if latest_df.empty:
    st.error("❌ No data available. Please check your database connection.")
    st.stop()

status, status_icon, output_time = get_machine_status(latest_df)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label="Machine Status", value=f"{status_icon} {status}", delta=None)


with col2:
    latest_availability = latest_df["Availability(%)"].iloc[0]
    delta_avail = (
        (latest_df["Availability(%)"].iloc[0] - latest_df["Availability(%)"].iloc[1])
        if len(latest_df) > 1
        else None
    )
    st.metric(
        label="Availability",
        value=f"{latest_availability:.1f}%",
        delta=f"{delta_avail:.1f}%" if delta_avail is not None else None,
    )

with col3:
    latest_performance = latest_df["Performance(%)"].iloc[0]
    delta_perf = (
        (latest_df["Performance(%)"].iloc[0] - latest_df["Performance(%)"].iloc[1])
        if len(latest_df) > 1
        else None
    )
    st.metric(
        label="Performance",
        value=f"{latest_performance:.1f}%",
        delta=f"{delta_perf:.1f}%" if delta_perf is not None else None,
    )

with col4:
    latest_quality = latest_df["Quality(%)"].iloc[0]
    delta_qual = (
        (latest_df["Quality(%)"].iloc[0] - latest_df["Quality(%)"].iloc[1])
        if len(latest_df) > 1
        else None
    )
    st.metric(
        label="Quality",
        value=f"{latest_quality:.1f}%",
        delta=f"{delta_qual:.1f}%" if delta_qual is not None else None,
    )

with col5:
    latest_oee = latest_df["OEE(%)"].iloc[0]
    delta_oee = (
        (latest_df["OEE(%)"].iloc[0] - latest_df["OEE(%)"].iloc[1])
        if len(latest_df) > 1
        else None
    )
    st.metric(
        label="OEE",
        value=f"{latest_oee:.1f}%",
        delta=f"{delta_oee:.1f}%" if delta_oee is not None else None,
    )

with col6:
    latest = latest_df.iloc[0]
    pred, probs = inference(latest_df, st.session_state.model)
    st.metric(
        label="Leakage Prediction",
        value=pred,
        delta=f"Probability: {probs.max() * 100:.2f} %",
    )

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Overview",
        "🌡️ Temperature",
        "📈 Production",
        "🚨 Leakage Detection",
    ]
)

with tab1:
    overview_tab(historical_df, latest_df, time_range)

with tab2:
    temperature_tab(historical_df, latest_df, time_range)

with tab3:
    production_tab(historical_df, latest_df, time_range)

with tab4:
    leakage_tab(historical_df, latest_df, time_range)
