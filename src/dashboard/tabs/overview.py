import streamlit as st
from src.dashboard.components.charts import create_realtime_chart
from src.dashboard.utils.helpers import get_processed_dataframes


def overview_tab(historical_df, latest_df, time_range):
    # Process dataframes
    historical_df, latest_df = get_processed_dataframes(historical_df, latest_df)

    # Historical trends - using sampled historical data
    if not historical_df.empty:
        st.subheader(f"📈 Trends - {time_range}")
        efficiency_cols = ["Availability(%)", "Performance(%)", "Quality(%)", "OEE(%)"]

        fig_trends = create_realtime_chart(
            historical_df, efficiency_cols, f"Efficiency Trends - {time_range}"
        )
        st.plotly_chart(fig_trends, use_container_width=True)

    st.subheader("📋 Recent Data")
    display_cols = [
        "Counter Output (pack)",
        "Counter Reject (pack)",
        "Availability(%)",
        "Performance(%)",
        "Quality(%)",
        "OEE(%)",
    ]
    st.dataframe(latest_df[display_cols].head(5), use_container_width=True)
