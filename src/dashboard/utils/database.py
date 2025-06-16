import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_time_filter_query(time_range: str) -> str:
    """Generate SQL query based on time range selection"""
    base_query = "SELECT * FROM datalog_ilapak3"

    time_filters = {
        "Last 1 Hour": "1 HOUR",
        "Last 6 Hours": "6 HOUR",
        "Last 24 Hours": "1 DAY",
        "Last 7 Days": "7 DAY",
        "Last 30 Days": "30 DAY",
    }

    interval = time_filters.get(time_range, "6 HOUR")
    return (
        f"{base_query} WHERE times >= NOW() - INTERVAL {interval} ORDER BY times DESC"
    )


@st.cache_data(ttl=15)  # Cache for 15 seconds for real-time data
def load_latest_data(uri: str) -> pd.DataFrame:
    """
    Load only the latest data for real-time monitoring
    Args:
        uri: Database connection URI
    Returns:
        DataFrame dengan data terbaru
    """
    try:
        engine = create_engine(uri)
        query = "SELECT * FROM datalog_ilapak3 ORDER BY times DESC LIMIT 10"
        df = pd.read_sql(query, engine, parse_dates=["times"])

        if df.empty:
            logger.warning("No data returned from latest data query")
            return pd.DataFrame()

        return df

    except Exception as e:
        logger.error(f"Error loading latest data: {str(e)}")
        st.error(f"❌ Error loading latest data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes for historical data
def load_historical_data(uri: str, time_range: str) -> pd.DataFrame:
    """
    Load historical data based on time range with optimized caching
    Args:
        uri: Database connection URI
        time_range: Range waktu yang dipilih
    Returns:
        DataFrame dengan data historis
    """
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

        if df.empty:
            logger.warning(f"No data returned for time range: {time_range}")
            return pd.DataFrame()

        return df

    except Exception as e:
        logger.error(f"Error loading historical data: {str(e)}")
        st.error(f"❌ Error loading historical data: {str(e)}")
        return pd.DataFrame()
