import streamlit as st
from datetime import datetime
import time
from dashboard.utils.database import load_latest_data
from dashboard.config.settings import (
    DB_URI,
    REFRESH_INTERVALS,
    DEFAULT_REFRESH_INTERVAL,
)


def render_sidebar():
    """Render the sidebar with controls and status information"""
    st.header("⚙️ Dashboard Controls")

    # Auto-refresh controls
    st.subheader("🔄 Auto Refresh")
    auto_refresh = st.toggle(
        "Enable Auto Refresh", value=st.session_state.auto_refresh_enabled
    )
    st.session_state.auto_refresh_enabled = auto_refresh

    if auto_refresh:
        refresh_interval = st.selectbox(
            "Refresh Interval",
            REFRESH_INTERVALS,
            index=REFRESH_INTERVALS.index(DEFAULT_REFRESH_INTERVAL),
            format_func=lambda x: f"{x} seconds",
        )
    else:
        refresh_interval = DEFAULT_REFRESH_INTERVAL

    # Manual refresh button
    if st.button("🔄 Refresh Now", type="primary"):
        st.cache_data.clear()
        st.session_state.last_update = time.time()
        st.rerun()

    # Time range selector for historical data
    st.subheader("📅 Time Range")
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 1 Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
        index=[
            "Last 1 Hour",
            "Last 6 Hours",
            "Last 24 Hours",
            "Last 7 Days",
            "Last 30 Days",
        ].index(st.session_state.time_range),
    )
    st.session_state.time_range = time_range

    # Data sampling info
    if time_range in ["Last 7 Days", "Last 30 Days"]:
        st.info("📊 Data is sampled for better performance on longer time ranges")

    # Status info
    st.subheader("ℹ️ Status")
    st.write(
        f"**Last Updated:** {datetime.fromtimestamp(st.session_state.last_update).strftime('%H:%M:%S')}"
    )

    # Connection status
    try:
        test_df = load_latest_data(DB_URI)
        if not test_df.empty:
            st.success("🟢 Database Connected")
            st.write(f"**Latest Data:** {test_df.index[0].strftime('%H:%M:%S')}")
        else:
            st.warning("🟡 No Recent Data")
    except:
        st.error("🔴 Database Connection Failed")

    return auto_refresh, refresh_interval, time_range
