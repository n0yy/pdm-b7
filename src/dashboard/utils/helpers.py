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
    elif latest["Status"] == 1 and latest["Speed(rpm)"] == 0:
        return "Idle", "🟡", latest_output_time_diff
    elif latest["Status"] == 3:
        return "Stopped", "🔴", latest_output_time_diff

    return "Unknown", "⚪", latest_output_time_diff
