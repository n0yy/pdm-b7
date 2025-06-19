import pandas as pd


def convert_time_to_seconds(time_str):
    """Convert hh:mm:ss string to total seconds"""
    try:
        h, m, s = map(int, str(time_str).split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0


def get_machine_status(df):
    if df.empty:
        return "Unknown", "⚪", 0

    latest = df.iloc[0]

    if "Output Time (hh:mm:ss)" in df.columns:
        df["Output Time (s)"] = df["Output Time (hh:mm:ss)"].apply(
            convert_time_to_seconds
        )
        latest_output_time_diff = (
            df["Output Time (s)"].iloc[0] - df["Output Time (s)"].iloc[1]
            if len(df) > 1
            else 0
        )
    else:
        latest_output_time_diff = 0

    if latest["Status"] == 2 and (
        latest["Counter Output (pack)"] > 0 or latest_output_time_diff > 0
    ):
        return "Running", "🟢", latest_output_time_diff
    elif latest["Status"] == 1 or latest["Status"] == 3 and latest["Speed(rpm)"] == 0:
        return "Idle", "🟡", latest_output_time_diff

    return "Unknown", "⚪", latest_output_time_diff


def preprocess_dataframe(df: pd.DataFrame, set_index: bool = True) -> pd.DataFrame:
    """
    Preprocess DataFrame untuk visualisasi dan analisis
    Args:
        df: DataFrame yang akan diproses
        set_index: Apakah times column harus dijadikan index
    Returns:
        DataFrame yang sudah diproses
    """
    if df.empty:
        return df

    df = df.copy()

    # Handle missing values
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[numeric_cols] = df[numeric_cols].fillna(method="ffill").fillna(method="bfill")

    # Set index jika diperlukan
    if set_index and "times" in df.columns:
        df.set_index("times", inplace=True)

    return df


def get_processed_dataframes(
    historical_df: pd.DataFrame, latest_df: pd.DataFrame
) -> tuple:
    """
    Memproses historical dan latest DataFrame untuk visualisasi
    Returns:
        Tuple dari (processed_historical_df, processed_latest_df)
    """
    return (
        preprocess_dataframe(historical_df, set_index=True),
        preprocess_dataframe(latest_df, set_index=False),
    )
