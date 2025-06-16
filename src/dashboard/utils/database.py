import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_time_filter_query(time_range: str) -> str:
    """Generate SQL query based on time range selection"""
    base_query = "SELECT * FROM datalog_ilapak3"

    time_filters = {
        "Last 6 Hours": "6 HOUR",
        "Last 24 Hours": "1 DAY",
        "Last 7 Days": "7 DAY",
        "Last 30 Days": "30 DAY",
    }

    interval = time_filters.get(time_range, "1 DAY")

    # Add sampling for larger datasets to improve performance
    if time_range in ["Last 7 Days", "Last 30 Days"]:
        # Sample every 10th record for better performance
        return f"""
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (ORDER BY times DESC) as rn 
            FROM {base_query.replace('SELECT * FROM ', '')}
            WHERE times >= NOW() - INTERVAL {interval}
        ) t WHERE MOD(rn, 10) = 1 ORDER BY times DESC
        """
    else:
        return f"{base_query} WHERE times >= NOW() - INTERVAL {interval} ORDER BY times DESC"


def load_latest_data(uri: str, limit: int = 20) -> pd.DataFrame:
    """
    Load latest data without caching for real-time updates
    """
    try:
        engine = create_engine(uri, pool_pre_ping=True, pool_recycle=300)
        query = f"SELECT * FROM datalog_ilapak3 ORDER BY times DESC LIMIT {limit}"

        with engine.connect() as conn:
            df = pd.read_sql(query, conn, parse_dates=["times"])

        if df.empty:
            logger.warning("No data returned from latest data query")
            return pd.DataFrame()

        # Sort by times descending for consistent ordering
        df = df.sort_values("times", ascending=False).reset_index(drop=True)
        return df

    except Exception as e:
        logger.error(f"Error loading latest data: {str(e)}")
        st.error(f"❌ Error loading latest data: {str(e)}")
        return pd.DataFrame()


def load_historical_data(
    uri: str, time_range: str, max_records: int = 1000
) -> pd.DataFrame:
    """
    Load historical data without caching for real-time updates
    """
    try:
        engine = create_engine(uri, pool_pre_ping=True, pool_recycle=300)
        query = get_time_filter_query(time_range)

        # Add limit to prevent memory issues
        if "LIMIT" not in query:
            query += f" LIMIT {max_records}"

        with engine.connect() as conn:
            df = pd.read_sql(query, conn, parse_dates=["times"])

        if df.empty:
            logger.warning(f"No data returned for time range: {time_range}")
            return pd.DataFrame()

        # Sort by times for consistent ordering
        df = df.sort_values("times", ascending=True).reset_index(drop=True)
        return df

    except Exception as e:
        logger.error(f"Error loading historical data: {str(e)}")
        st.error(f"❌ Error loading historical data: {str(e)}")
        return pd.DataFrame()


def get_data_freshness(df: pd.DataFrame) -> dict:
    """
    Check data freshness for real-time monitoring
    """
    if df.empty:
        return {"is_fresh": False, "last_update": None, "delay_minutes": None}

    latest_time = df["times"].max()
    current_time = pd.Timestamp.now()
    delay = (current_time - latest_time).total_seconds() / 60

    return {
        "is_fresh": delay
        < 1.5,  # Fresh if less than 1.5 minutes old (allowing for 30s processing time)
        "last_update": latest_time,
        "delay_minutes": delay,
        "needs_refresh": delay > 1.2,  # Force refresh if more than 1.2 minutes old
    }


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Get summary statistics for dashboard without caching
    """
    if df.empty:
        return {}

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    summary = {}

    for col in numeric_cols:
        if col in df.columns:
            summary[col] = {
                "current": df[col].iloc[0] if len(df) > 0 else 0,
                "previous": df[col].iloc[1] if len(df) > 1 else 0,
                "avg": df[col].mean(),
                "min": df[col].min(),
                "max": df[col].max(),
            }

    return summary
