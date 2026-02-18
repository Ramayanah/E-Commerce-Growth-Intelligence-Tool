"""
visualization.py — Reusable Plotly Chart Builder
Provides chart factory functions with consistent styling.
Pure function — no Streamlit calls.
"""

import plotly.graph_objects as go
import plotly.express as px
import config


def line_chart(df, x, y, title, y_label="", color=None):
    """Create a Plotly line chart.

    Args:
        df: DataFrame with the data.
        x: Column name for x-axis.
        y: Column name (or list) for y-axis.
        title: Chart title.
        y_label: Optional y-axis label.
        color: Optional column for color grouping.

    Returns:
        plotly.graph_objects.Figure
    """
    if df.empty:
        return _empty_chart(title)

    if color:
        fig = px.line(df, x=x, y=y, color=color, title=title,
                      color_discrete_sequence=config.CHART_COLORS)
    else:
        fig = px.line(df, x=x, y=y, title=title,
                      color_discrete_sequence=config.CHART_COLORS)

    fig.update_layout(**_base_layout(y_label))
    return fig


def bar_chart(df, x, y, title, y_label="", horizontal=False):
    """Create a Plotly bar chart.

    Returns:
        plotly.graph_objects.Figure
    """
    if df.empty:
        return _empty_chart(title)

    orientation = "h" if horizontal else "v"
    if horizontal:
        fig = px.bar(df, x=y, y=x, title=title, orientation="h",
                     color_discrete_sequence=config.CHART_COLORS)
    else:
        fig = px.bar(df, x=x, y=y, title=title,
                     color_discrete_sequence=config.CHART_COLORS)

    fig.update_layout(**_base_layout(y_label))
    return fig


def stacked_bar(df, x, y, color, title, y_label=""):
    """Create a Plotly stacked bar chart.

    Returns:
        plotly.graph_objects.Figure
    """
    if df.empty:
        return _empty_chart(title)

    fig = px.bar(df, x=x, y=y, color=color, title=title, barmode="stack",
                 color_discrete_sequence=config.CHART_COLORS)
    fig.update_layout(**_base_layout(y_label))
    return fig


def pie_chart(df, names, values, title):
    """Create a Plotly pie chart.

    Returns:
        plotly.graph_objects.Figure
    """
    if df.empty:
        return _empty_chart(title)

    fig = px.pie(df, names=names, values=values, title=title,
                 color_discrete_sequence=config.CHART_COLORS)
    fig.update_layout(**_base_layout())
    return fig


def heatmap(z_values, x_labels, y_labels, title, color_label=""):
    """Create a Plotly heatmap.

    Args:
        z_values: 2D list or numpy array of values.
        x_labels: Labels for x-axis.
        y_labels: Labels for y-axis.
        title: Chart title.
        color_label: Label for the color bar.

    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        colorscale="Blues",
        colorbar_title=color_label,
        hoverongaps=False,
    ))
    fig.update_layout(title=title, **_base_layout())
    return fig


def multi_line_chart(df, x, y_columns, title, y_label=""):
    """Create a multi-line chart with several y-columns.

    Args:
        df: DataFrame.
        x: Column name for x-axis.
        y_columns: List of column names for y-axis lines.
        title: Chart title.

    Returns:
        plotly.graph_objects.Figure
    """
    if df.empty:
        return _empty_chart(title)

    fig = go.Figure()
    for i, col in enumerate(y_columns):
        if col in df.columns:
            color = config.CHART_COLORS[i % len(config.CHART_COLORS)]
            fig.add_trace(go.Scatter(
                x=df[x], y=df[col], mode="lines+markers",
                name=col.replace("_", " ").title(),
                line=dict(color=color, width=2),
            ))

    fig.update_layout(title=title, **_base_layout(y_label))
    return fig


def format_number(value, prefix="", suffix="", decimals=0):
    """Format a number with optional prefix/suffix and thousand separators.

    Args:
        value: Number to format.
        prefix: e.g. '₹' or '$'.
        suffix: e.g. '%'.
        decimals: Number of decimal places.

    Returns:
        Formatted string.
    """
    if value is None:
        return "N/A"
    try:
        if decimals == 0:
            formatted = f"{int(value):,}"
        else:
            formatted = f"{value:,.{decimals}f}"
        return f"{prefix}{formatted}{suffix}"
    except (ValueError, TypeError):
        return "N/A"


def _base_layout(y_label=""):
    """Return common layout settings for charts."""
    layout = {
        "template": config.CHART_TEMPLATE,
        "height": config.CHART_HEIGHT,
        "margin": dict(l=40, r=20, t=50, b=40),
        "font": dict(size=12),
        "autosize": True,
    }
    if y_label:
        layout["yaxis_title"] = y_label
    return layout


def _empty_chart(title):
    """Return an empty chart with a 'No data' message."""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template=config.CHART_TEMPLATE,
        height=config.CHART_HEIGHT,
        annotations=[dict(
            text="Not enough data to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray"),
        )],
    )
    return fig
