import plotly.graph_objects as go


def create_realtime_chart(df, columns, title, max_points=100):
    """Create real-time line chart with limited data points for performance"""
    # Limit data points for better performance
    if len(df) > max_points:
        df_sample = df.iloc[:: len(df) // max_points]
    else:
        df_sample = df

    fig = go.Figure()

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for i, col in enumerate(columns):
        if col in df_sample.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_sample.index,
                    y=df_sample[col],
                    mode="lines",
                    name=col.replace("(oC)", "")
                    .replace("(pack)", "")
                    .replace("(%)", "%"),
                    line=dict(color=colors[i % len(colors)], width=2),
                    hovertemplate=f"{col}: %{{y}}<br>Time: %{{x}}<extra></extra>",
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Value",
        hovermode="x unified",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig
