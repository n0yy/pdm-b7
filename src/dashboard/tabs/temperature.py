import streamlit as st
from src.dashboard.components.charts import create_realtime_chart
from src.dashboard.utils.helpers import get_processed_dataframes


def temperature_tab(historical_df, latest_df, time_range):
    # Process dataframes
    historical_df, latest_df = get_processed_dataframes(historical_df, latest_df)

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
            short_name = col.replace(" (oC)", "").replace("(oC )", "")

            if current_temp < 50:
                color = "#1f77b4"
            elif 50 <= current_temp <= 80:
                color = "#2ca02c"
            else:
                color = "#d62728"

            st.markdown(
                f"""
                <div>
                    <strong>{short_name}:</strong> 
                    <span style="color:{color}; font-weight:bold;">{current_temp:.1f}</span> °C
                </div>
                """,
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
        if "times" in historical_df.columns:
            historical_df.set_index("times", inplace=True)
        fig_temp = create_realtime_chart(historical_df, temp_cols, y_lim=(150, 250))
        st.plotly_chart(fig_temp, use_container_width=True)
