import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.predicting import batch_inference
from src.dashboard.utils.helpers import preprocess_dataframe


def leakage_tab(historical_df, latest_df, time_range):
    st.header("🚨 Leakage Prediction")

    # Preprocess dataframes
    historical_df = preprocess_dataframe(historical_df)

    # Get predictions for historical data using batch inference
    predictions, probabilities = batch_inference(
        data=historical_df, _estimator=st.session_state.model
    )

    # Create prediction statistics
    pred_df = pd.DataFrame(
        {"prediction": predictions, "probability": probabilities},
        index=historical_df.index,
    )

    # Count predictions
    pred_counts = pred_df["prediction"].value_counts()

    # Display metrics in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        normal_count = pred_counts.get("Normal", 0)
        st.metric(
            label="Normal Predictions",
            value=normal_count,
            delta=f"{normal_count/len(pred_df)*100:.1f}% of total",
        )

    with col2:
        warning_count = pred_counts.get("Warning", 0)
        st.metric(
            label="Warning Predictions",
            value=warning_count,
            delta=f"{warning_count/len(pred_df)*100:.1f}% of total",
        )

    with col3:
        leak_count = pred_counts.get("Leak", 0)
        st.metric(
            label="Leak Predictions",
            value=leak_count,
            delta=f"{leak_count/len(pred_df)*100:.1f}% of total",
        )

    # Create prediction trend chart
    st.subheader("📈 Prediction Trend")

    # Create color mapping for predictions
    color_map = {
        "Normal": "#28a745",
        "Warning": "#ffc107",
        "Leak": "#dc3545",
    }

    fig = px.scatter(
        pred_df,
        x=pred_df.index,
        y="probability",
        color="prediction",
        color_discrete_map=color_map,
        title=f"Leakage Prediction Trend - {time_range}",
        labels={
            "index": "Time",
            "probability": "Prediction Probability",
            "prediction": "Prediction",
        },
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Prediction Probability",
        legend_title="Prediction",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display recent predictions table
    st.subheader("📋 Recent Predictions")
    recent_preds = pred_df.sort_index(ascending=False).head(10)
    st.dataframe(
        recent_preds.style.format({"probability": "{:.2%}"}), use_container_width=True
    )
