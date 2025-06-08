import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import numpy as np
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Real-time Machine Monitoring", page_icon="🏭", layout="wide"
)

# Judul
st.title("🏭 Real-time Machine Monitoring Dashboard")


# Fungsi untuk membaca data terbaru
def load_latest_data(file_path, last_n_minutes=5):
    if not os.path.exists(file_path):
        return pd.DataFrame()

    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Filter data dalam rentang waktu tertentu
    cutoff_time = datetime.now() - timedelta(minutes=last_n_minutes)
    df = df[df["timestamp"] >= cutoff_time]

    return df


# Fungsi untuk mendeteksi anomali menggunakan Z-score
def detect_anomalies(df, columns, threshold=3):
    scaler = StandardScaler()
    anomalies = pd.DataFrame(index=df.index)
    reconstruction_errors = {}

    for col in columns:
        if col in ["timestamp", "line", "enc_auger_direction"]:
            continue

        values = df[col].values.reshape(-1, 1)
        scaled = scaler.fit_transform(values)
        is_anomaly = abs(scaled) > threshold
        anomalies[col] = is_anomaly
        reconstruction_errors[col] = np.mean(abs(scaled))

    return anomalies, reconstruction_errors


# Fungsi untuk forecasting
def forecast_parameter(data, parameter, forecast_steps=10):
    if len(data) < 4:
        return None, None

    model = ExponentialSmoothing(
        data[parameter],
        seasonal_periods=4,
        trend="add",
        seasonal="add",
        use_boxcox=True,
    )

    try:
        fitted_model = model.fit()
        forecast = fitted_model.forecast(forecast_steps)
        return forecast, fitted_model.fittedvalues
    except:
        return None, None


# Layout dashboard
col1, col2, col3 = st.columns(3)

# Pilihan line
with col1:
    selected_line = st.selectbox("Pilih Line", [1, 2, 3, 4, 5, 6, 7, 8])

with col2:
    update_interval = st.slider("Interval Update (detik)", 1, 10, 5)

with col3:
    forecast_window = st.slider("Forecast Window (menit)", 1, 30, 5)

# Container untuk metrik
metrics_container = st.container()

# Container untuk grafik
charts_container = st.container()

# Container untuk forecasting
forecast_container = st.container()


# Fungsi update dashboard
def update_dashboard():
    df = load_latest_data("./data/streamed_synthetic_sig_5.csv")

    if df.empty:
        st.warning("Tidak ada data yang tersedia")
        return

    # Filter berdasarkan line yang dipilih
    df_filtered = df[df["line"] == selected_line]

    if df_filtered.empty:
        st.warning(f"Tidak ada data untuk line {selected_line}")
        return

    # Deteksi anomali
    anomalies, reconstruction_errors = detect_anomalies(
        df_filtered, df_filtered.columns
    )

    # Temukan parameter dengan reconstruction error tertinggi
    if reconstruction_errors:
        worst_parameter = max(reconstruction_errors.items(), key=lambda x: x[1])[0]

    with metrics_container:
        st.subheader("Metrik Real-time")
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            latest = df_filtered.iloc[-1]
            st.metric("RPM Auger", f"{latest['enc_auger_rpm']:.1f}")

        with m2:
            st.metric("Temperatur Heater 1", f"{latest['heater_cross_1']:.1f}°C")

        with m3:
            st.metric("Dosing", f"{latest['dosing']:.2f}")

        with m4:
            anomaly_count = anomalies.sum().sum()
            st.metric("Anomali Terdeteksi", anomaly_count)

    with charts_container:
        # Plot time series untuk beberapa parameter penting
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(
                df_filtered,
                x="timestamp",
                y="enc_auger_rpm",
                title="RPM Auger Over Time",
            )
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.line(
                df_filtered,
                x="timestamp",
                y=[
                    "heater_cross_1",
                    "heater_cross_2",
                    "heater_cross_3",
                    "heater_cross_4",
                ],
                title="Heater Temperatures",
            )
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            fig3 = px.line(
                df_filtered, x="timestamp", y="dosing", title="Dosing Over Time"
            )
            st.plotly_chart(fig3, use_container_width=True)

            # Heatmap anomali
            anomaly_counts = anomalies.sum()
            fig4 = go.Figure(
                data=go.Bar(
                    x=anomaly_counts.index, y=anomaly_counts.values, name="Anomalies"
                )
            )
            fig4.update_layout(title="Anomali per Parameter", xaxis_tickangle=-45)
            st.plotly_chart(fig4, use_container_width=True)

    with forecast_container:
        st.subheader(
            f"Forecasting untuk Parameter dengan Error Tertinggi: {worst_parameter}"
        )

        # Lakukan forecasting
        forecast_values, fitted_values = forecast_parameter(
            df_filtered, worst_parameter, forecast_steps=forecast_window
        )

        if forecast_values is not None:
            # Buat timestamps untuk forecast
            last_timestamp = df_filtered["timestamp"].iloc[-1]
            forecast_timestamps = pd.date_range(
                start=last_timestamp, periods=len(forecast_values), freq="1min"
            )

            # Plot hasil forecasting
            fig5 = go.Figure()

            # Plot data aktual
            fig5.add_trace(
                go.Scatter(
                    x=df_filtered["timestamp"],
                    y=df_filtered[worst_parameter],
                    name="Actual",
                    line=dict(color="blue"),
                )
            )

            # Plot fitted values
            if fitted_values is not None:
                fig5.add_trace(
                    go.Scatter(
                        x=df_filtered["timestamp"],
                        y=fitted_values,
                        name="Fitted",
                        line=dict(color="green", dash="dash"),
                    )
                )

            # Plot forecast
            fig5.add_trace(
                go.Scatter(
                    x=forecast_timestamps,
                    y=forecast_values,
                    name="Forecast",
                    line=dict(color="red", dash="dash"),
                )
            )

            fig5.update_layout(
                title=f"Forecasting {worst_parameter}",
                xaxis_title="Timestamp",
                yaxis_title="Value",
            )

            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.warning("Tidak cukup data untuk melakukan forecasting")


# Loop update
while True:
    update_dashboard()
    time.sleep(update_interval)
