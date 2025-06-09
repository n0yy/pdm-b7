from plotly.subplots import make_subplots
import plotly.graph_objects as go


def create_realtime_chart(
    df,
    columns,
    title: str = None,
    max_points=100,
    y_lim: tuple = None,
    secondary_y_cols: list = None,
):
    """Create real-time line chart with optional dual Y-axis support"""

    if len(df) > max_points:
        df_sample = df.iloc[:: len(df) // max_points]
    else:
        df_sample = df

    secondary_y_cols = secondary_y_cols or []
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for i, col in enumerate(columns):
        if col in df_sample.columns:
            is_secondary = col in secondary_y_cols
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
                ),
                secondary_y=is_secondary,
            )

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        hovermode="x unified",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        yaxis=dict(range=y_lim) if y_lim else {},
    )

    # Sumbu Y utama dan sekunder
    fig.update_yaxes(title_text="Value", secondary_y=False)
    fig.update_yaxes(title_text="Secondary Value", secondary_y=True)

    return fig
