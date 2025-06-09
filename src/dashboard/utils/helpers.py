def get_machine_status(df):
    """Determine machine status based on latest data"""
    if df.empty:
        return "Unknown", "⚪"

    latest = df.iloc[0]

    # Check if machine is running
    if latest["Status"] == 2 and latest["Counter Output (pack)"] > 0:
        return "Running", "🟢"
    elif latest["Status"] == 1:
        return "Idle", "🟡"
    elif latest["Status"] == 0:
        return "Stopped", "🔴"
