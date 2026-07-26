"""
utils/styling.py

A tiny shared helper so every plotly figure in the app matches the dark
Spotify-style theme without repeating the same layout block on every page.
Not requested explicitly, but it's the cleanest way to satisfy "ensure chart
backgrounds match the dark theme" without copy-pasting layout code 9 times.
"""

COLORS = {
    "green": "#1ED760",
    "green_soft": "#3ddc84",
    "red": "#FF6B6B",
    "amber": "#FFB347",
    "blue": "#5BC0F8",
    "gray": "#7A8579",
    "bg": "#0E1117",
    "card": "#181C1F",
    "text": "#FAFAFA",
    "text_muted": "#98A39C",
    "grid": "rgba(255,255,255,0.08)",
}


def style_fig(fig, height=380):
    """Apply consistent dark-theme styling to any plotly express figure."""
    fig.update_layout(
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(family="sans-serif", color=COLORS["text"], size=12),
        title=dict(font=dict(size=14, color=COLORS["text"])),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_muted"]),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        height=height,
    )
    fig.update_xaxes(
        gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], color=COLORS["text_muted"]
    )
    fig.update_yaxes(
        gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], color=COLORS["text_muted"]
    )
    return fig
