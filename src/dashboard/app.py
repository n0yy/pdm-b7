import streamlit as st
import pandas as pd
from datetime import datetime

from .components.charts import create_realtime_chart
from .components.sidebar import render_sidebar
from .utils.database import load_latest_data, load_historical_data
from .utils.helpers import get_machine_status
from .config.settings import (
    DB_URI,
    DEFAULT_TIME_RANGE,
    TEMP_WARNING_THRESHOLD,
    TEMP_DANGER_THRESHOLD,
)

# Page configuration
st.set_page_config(
    page_title="PdM Dashboard - Ilapak 3",
    layout="wide",
    initial_sidebar_state="expanded",
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
    st.session_state.last_update = datetime.now()
if "auto_refresh_enabled" not in st.session_state:
    st.session_state.auto_refresh_enabled = True
if "time_range" not in st.session_state:
    st.session_state.time_range = DEFAULT_TIME_RANGE

# Render sidebar and get controls
auto_refresh, refresh_interval, time_range = render_sidebar()

# Auto-refresh implementation
if auto_refresh:
    # Create a placeholder for the auto-refresh timer
    refresh_placeholder = st.sidebar.empty()

    # Check if it's time to refresh
    time_since_update = (datetime.now() - st.session_state.last_update).total_seconds()

    if time_since_update >= refresh_interval:
        # Clear all caches
        st.cache_data.clear()
        # Update last update time
        st.session_state.last_update = datetime.now()
        # Force rerun
        st.rerun()
    else:
        # Show countdown
        remaining = refresh_interval - time_since_update
        progress = 1 - (remaining / refresh_interval)
        refresh_placeholder.progress(progress)
        refresh_placeholder.write(f"⏱️ Next refresh in: {remaining:.0f}s")

# Main dashboard content
st.markdown(
    '<h1 class="main-header">🏭 Predictive Maintenance Dashboard - Ilapak 3</h1><br><br>',
    unsafe_allow_html=True,
)

# Load data efficiently
latest_df = load_latest_data(DB_URI)
historical_df = load_historical_data(DB_URI, time_range)

if latest_df.empty:
    st.error("❌ No data available. Please check your database connection.")
    st.stop()

# Get machine status
status, status_icon = get_machine_status(latest_df)

# Top metrics row
col1, col2, col3, col4, col5 = st.columns(5)

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

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Overview",
        "🌡️ Temperature",
        "📈 Production",
        "🚨 Anomaly Detection",
    ]
)

with tab1:
    # Historical trends - using sampled historical data
    if not historical_df.empty:
        st.subheader(f"📈 Trends - {time_range}")
        efficiency_cols = ["Availability(%)", "Performance(%)", "Quality(%)", "OEE(%)"]
        fig_trends = create_realtime_chart(
            historical_df, efficiency_cols, f"Efficiency Trends - {time_range}"
        )
        st.plotly_chart(fig_trends, use_container_width=True)

    # Recent data table - limited rows
    st.subheader("📋 Recent Data")
    display_cols = [
        "Status",
        "Speed(rpm)",
        "Counter Output (pack)",
        "Counter Reject (pack)",
        "Availability(%)",
        "Performance(%)",
        "Quality(%)",
        "OEE(%)",
    ]
    st.dataframe(latest_df[display_cols].head(5), use_container_width=True)

with tab2:
    temp_cols = [
        "Suhu Sealing Vertikal Bawah (oC)",
        "Suhu Sealing Vertical Atas (oC)",
        "Suhu Sealing Horizontal Depan/Kanan (oC)",
        "Suhu Sealing Horizontal Belakang/Kiri (oC )",
    ]

    # Current temperatures
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🌡️ Current Temperatures")
        for col in temp_cols:
            current_temp = latest_df[col].iloc[0]
            status_class = (
                "status-danger"
                if current_temp > TEMP_DANGER_THRESHOLD
                else (
                    "status-warning"
                    if current_temp > TEMP_WARNING_THRESHOLD
                    else "status-good"
                )
            )
            short_name = (
                col.replace("Suhu Sealing ", "")
                .replace(" (oC)", "")
                .replace("(oC )", "")
            )
            st.markdown(
                f"<div class='{status_class}'>{short_name}: {current_temp:.1f}°C</div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.subheader("📊 Temperature Stats")
        if not historical_df.empty:
            temp_stats = historical_df[temp_cols].describe().loc[["mean", "min", "max"]]
            temp_stats.index = ["Average", "Minimum", "Maximum"]
            st.dataframe(temp_stats.round(1))

    # Temperature trend chart
    if not historical_df.empty:
        st.subheader(f"📈 Temperature Trends - {time_range}")
        fig_temp = create_realtime_chart(
            historical_df, temp_cols, f"Temperature Trends - {time_range}"
        )
        st.plotly_chart(fig_temp, use_container_width=True)

with tab3:
    st.header("📈 Production Metrics")

    # Current production metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        current_speed = latest_df["Speed(rpm)"].iloc[0]
        st.metric("Current Speed", f"{current_speed:.1f} RPM")

    with col2:
        current_output = latest_df["Counter Output (pack)"].iloc[0]
        previous_output = (
            latest_df["Counter Output (pack)"].iloc[1] if len(latest_df) > 1 else None
        )

        delta_output = (
            ((current_output - previous_output) / previous_output * 100)
            if previous_output and previous_output != 0
            else None
        )

        st.metric(
            label="Recent Output",
            value=f"{current_output:,} packs",
            delta=f"{delta_output:.1f}%" if delta_output is not None else None,
        )

    with col3:
        current_reject = latest_df["Counter Reject (pack)"].iloc[0]
        delta_reject = (
            (
                latest_df["Counter Reject (pack)"].iloc[0]
                - latest_df["Counter Reject (pack)"].iloc[1]
            )
            if len(latest_df) > 1
            else None
        )
        st.metric(
            label="Recent Rejects",
            value=f"{current_reject}",
            delta=f"{delta_reject:.1f}%" if delta_reject is not None else None,
        )

    # Production charts
    if not historical_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            speed_cols = ["Speed(rpm)"]
            fig_speed = create_realtime_chart(
                historical_df, speed_cols, f"Speed Trend - {time_range}"
            )
            st.plotly_chart(fig_speed, use_container_width=True)

        with col2:
            output_cols = ["Counter Output (pack)", "Counter Reject (pack)"]
            fig_output = create_realtime_chart(
                historical_df, output_cols, f"Output Trend - {time_range}"
            )
            st.plotly_chart(fig_output, use_container_width=True)

with tab4:
    st.header("🚨 Anomaly Detection")

# Auto-refresh status
if auto_refresh:
    st.markdown(
        f'<div class="refresh-info">🔄 Auto-refresh enabled: Every {refresh_interval} seconds | '
        f'Last updated: {st.session_state.last_update.strftime("%H:%M:%S")}</div>',
        unsafe_allow_html=True,
    )
