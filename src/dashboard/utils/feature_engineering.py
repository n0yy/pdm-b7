import pandas as pd


def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    X = data.copy()
    # Convert to second
    time_cols = [
        "Downtime (hh:mm:ss)",
        "Output Time (hh:mm:ss)",
        "Total Time (hh:mm:ss)",
    ]

    for col in time_cols:
        X[col.split(" (")[0] + "_sec"] = pd.to_timedelta(X[col]).dt.total_seconds()

    if "times" in X.columns:
        X["day"] = X["times"].dt.day
        X["hour"] = X["times"].dt.hour
        X["minute"] = X["times"].dt.minute
    else:
        if isinstance(X.index, pd.DatetimeIndex):
            X["day"] = X.index.day
            X["hour"] = X.index.hour
            X["minute"] = X.index.minute
        else:
            X["day"] = 1
            X["hour"] = 0
            X["minute"] = 0

    # Diff
    X["diff_sealing_vertical"] = (
        X["Suhu Sealing Vertical Atas (oC)"] - X["Suhu Sealing Vertikal Bawah (oC)"]
    )
    X["diff_sealing_horizontal"] = (
        X["Suhu Sealing Horizontal Depan/Kanan (oC)"]
        - X["Suhu Sealing Horizontal Belakang/Kiri (oC )"]
    )
    X["diff_output"] = X["Counter Output (pack)"] - X["Counter Reject (pack)"]
    X["diff_counter_output"] = X["Counter Output (pack)"].diff().fillna(0)
    X["diff_counter_reject"] = X["Counter Reject (pack)"].diff().fillna(0)
    return X
