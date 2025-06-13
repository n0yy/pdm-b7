import pandas as pd
from sqlalchemy import create_engine
import streamlit as st


def get_time_filter_query(time_range):
    """Generate SQL query based on time range selection"""
    base_query = "SELECT * FROM datalog_ilapak3"

    if time_range == "Last 1 Hour":
        return (
            f"{base_query} WHERE times >= NOW() - INTERVAL 1 HOUR ORDER BY times DESC"
        )
    elif time_range == "Last 6 Hours":
        return (
            f"{base_query} WHERE times >= NOW() - INTERVAL 6 HOUR ORDER BY times DESC"
        )
    elif time_range == "Last 24 Hours":
        return f"{base_query} WHERE times >= NOW() - INTERVAL 1 DAY ORDER BY times DESC"
    elif time_range == "Last 7 Days":
        return f"{base_query} WHERE times >= NOW() - INTERVAL 7 DAY ORDER BY times DESC"
    elif time_range == "Last 30 Days":
        return (
            f"{base_query} WHERE times >= NOW() - INTERVAL 30 DAY ORDER BY times DESC"
        )
    else:
        # Default to last 6 hours for safety
        return (
            f"{base_query} WHERE times >= NOW() - INTERVAL 6 HOUR ORDER BY times DESC"
        )


@st.cache_data(ttl=30)  # Cache for 30 seconds only for real-time data
def load_latest_data(uri: str) -> pd.DataFrame:
    """Load only the latest data for real-time monitoring"""
    try:
        engine = create_engine(uri)
        # Get only the latest 10 records for real-time metrics
        query = "SELECT * FROM datalog_ilapak3 ORDER BY times DESC LIMIT 10"
        df = pd.read_sql(query, engine, parse_dates=["times"])
        return df
    except Exception as e:
        st.error(f"Error loading latest data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes for historical data
def load_historical_data(uri: str, time_range: str) -> pd.DataFrame:
    """Load historical data based on time range with optimized caching"""
    try:
        engine = create_engine(uri)
        query = get_time_filter_query(time_range)

        # Add sampling for large datasets
        if time_range in ["Last 7 Days", "Last 30 Days"]:
            query = query.replace(
                "ORDER BY times DESC",
                "AND MOD(UNIX_TIMESTAMP(times), 10) = 0 ORDER BY times DESC",
            )

        df = pd.read_sql(query, engine, parse_dates=["times"])
        return df
    except Exception as e:
        st.error(f"Error loading historical data: {e}")
        return pd.DataFrame()
