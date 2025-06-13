import streamlit as st
from dashboard.components.charts import create_realtime_chart


def production_tab(historical_df, latest_df, time_range):
    st.header("📈 Production Metrics")

    # Current production metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        current_speed = latest_df["Speed(rpm)"].iloc[0]
        st.metric("Current Speed", f"{current_speed:.1f} RPM")

    with col2:
        current_output = latest_df["Counter Output (pack)"].iloc[0]
        previous_output = (
            latest_df["Counter Output (pack)"].iloc[1] if len(latest_df) > 1 else None
        )

        delta_output = (
            ((current_output - previous_output) / previous_output * 100)
            if previous_output and previous_output != 0
            else None
        )

        st.metric(
            label="Recent Output",
            value=f"{current_output:,} packs",
            delta=f"{delta_output:.1f}%" if delta_output is not None else None,
        )

    with col3:
        current_reject = latest_df["Counter Reject (pack)"].iloc[0]
        delta_reject = (
            (
                latest_df["Counter Reject (pack)"].iloc[0]
                - latest_df["Counter Reject (pack)"].iloc[1]
            )
            if len(latest_df) > 1
            else None
        )
        st.metric(
            label="Recent Rejects",
            value=f"{current_reject}",
            delta=f"{delta_reject:.1f}%" if delta_reject is not None else None,
        )

    # Production charts
    if not historical_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            speed_cols = ["Speed(rpm)"]
            fig_speed = create_realtime_chart(
                historical_df, speed_cols, f"Speed Trend - {time_range}"
            )
            st.plotly_chart(fig_speed, use_container_width=True)

        with col2:
            output_cols = ["Counter Output (pack)", "Counter Reject (pack)"]
            fig_output = create_realtime_chart(
                historical_df,
                output_cols,
                title=f"Output Trend - {time_range}",
                secondary_y_cols=["Counter Reject (pack)"],
            )
            st.plotly_chart(fig_output, use_container_width=True)
