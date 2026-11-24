from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modules.visual_intelligence import render_map


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

EVENTS = [
    "Strait of Hormuz disruption",
    "Red Sea shipping crisis",
    "Russia–Ukraine war",
]


@st.cache_data

def load_csv(filename: str) -> pd.DataFrame:
    """Load a CSV file from the project's local data folder."""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(
            f"Could not find {file_path}. Check that the file is inside the data folder."
        )
    return pd.read_csv(file_path)


def style_plotly_figure(fig: go.Figure, height: int = 340) -> go.Figure:
    """Apply the same dark visual style to dashboard charts."""
    fig.update_layout(
        template="plotly_dark",
        title_font=dict(color="#e9f1fb", size=16),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce8f5", size=12),
        margin=dict(l=40, r=25, t=60, b=75),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=["2020", "2021", "2022", "2023", "2024", "1H25"],
            automargin=True,
            showgrid=False,
            zeroline=False,
            linecolor="#35506c",
            tickfont=dict(color="#aebfd2"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(142, 165, 190, 0.16)",
            zeroline=False,
            linecolor="#35506c",
            tickfont=dict(color="#aebfd2"),
        ),
    )
    return fig


def render_event_pulse(highlights: pd.DataFrame) -> None:
    st.markdown("<div class='section-kicker'>01 / Event pulse</div>", unsafe_allow_html=True)
    st.subheader("Three events. Three economic transmission channels.")

    columns = st.columns(3, gap="medium")
    for column, (_, row) in zip(columns, highlights.iterrows()):
        with column:
            st.metric(
                label=row["event"],
                value=row["display_value"],
                
            )
            st.caption(row["period"])
            st.markdown(f"**{row['headline']}**")
            st.caption(row["context"])
            st.markdown(
                f"[Source: {row['source_name']}]({row['source_url']})",
                unsafe_allow_html=False,
            )


def render_flow_charts(indicators: pd.DataFrame) -> None:
    st.markdown("<div class='section-kicker'>02 / Critical route indicators</div>", unsafe_allow_html=True)
    st.subheader("Historical flow through major maritime chokepoints")

    chart_left, chart_right = st.columns(2, gap="large")

    hormuz = indicators[indicators["series"] == "Hormuz oil flows"].copy()
    hormuz = hormuz.sort_values("sort_order")
    hormuz_fig = px.line(
        hormuz,
        x="period",
        y="value",
        markers=True,
        labels={"period": "Period", "value": "Million barrels per day"},
        title="Strait of Hormuz · oil flows",
    )
    hormuz_fig.update_traces(
        line=dict(color="#f1ad58", width=3),
        marker=dict(size=8, color="#f1ad58"),
        hovertemplate="%{x}<br>%{y:.1f} million barrels/day<extra></extra>",
    )
    hormuz_fig = style_plotly_figure(hormuz_fig, height=430)

    shipping = indicators[
        indicators["series"].isin(
            ["Suez Canal + SUMED oil flows", "Bab el-Mandeb oil flows"]
        )
    ].copy()
    shipping = shipping.sort_values("sort_order")
    shipping_fig = px.line(
        shipping,
        x="period",
        y="value",
        color="series",
        markers=True,
        labels={
            "period": "Period",
            "value": "Million barrels per day",
            "series": "Route",
        },
        title="Red Sea approaches · oil flows",
        color_discrete_map={
            "Suez Canal + SUMED oil flows": "#65c5bb",
            "Bab el-Mandeb oil flows": "#a88ce0",
        },
    )
    shipping_fig.update_traces(
        hovertemplate="%{x}<br>%{y:.1f} million barrels/day<extra></extra>"
    )
    shipping_fig = style_plotly_figure(shipping_fig, height=430)
    shipping_fig.update_layout(legend=dict(title_text="", orientation="h", y=-0.25), margin=dict(b=115))

    with chart_left:
        st.plotly_chart(hormuz_fig, use_container_width=True, theme=None)
        st.caption(
            "Observed annual flows; 1H25 means the first half of 2025. "
            "Source: US Energy Information Administration (EIA)."
        )
    with chart_right:
        st.plotly_chart(shipping_fig, use_container_width=True, theme=None)
        st.caption(
            "Oil flows through the Suez Canal/SUMED pipeline and Bab el-Mandeb. "
            "These are oil-volume series, not counts of all ships. Source: EIA."
        )


def render_exposure_matrix(exposure: pd.DataFrame) -> None:
    st.markdown("<div class='section-kicker'>04 / Country exposure lens</div>", unsafe_allow_html=True)
    st.subheader("Which economies should be watched most closely?")
    st.markdown(
        "This first-pass view compares potential sensitivity across six economies. "
        "It is a qualitative analyst assessment for the prototype, not an official "
        "country risk rating or a quantified estimate of economic loss."
    )

    selected_event = st.selectbox(
        "Filter by event",
        options=["All three events"] + EVENTS,
        index=0,
    )

    filtered = exposure.copy()
    if selected_event != "All three events":
        filtered = filtered[filtered["event"] == selected_event]

    pivot_scores = filtered.pivot(
        index="country", columns="event", values="score"
    ).sort_index()
    pivot_levels = filtered.pivot(
        index="country", columns="event", values="level"
    ).reindex(index=pivot_scores.index, columns=pivot_scores.columns)

    heatmap = go.Figure(
        data=go.Heatmap(
            z=pivot_scores.values,
            x=list(pivot_scores.columns),
            y=list(pivot_scores.index),
            text=pivot_levels.values,
            texttemplate="%{text}",
            textfont=dict(size=13, color="#101b2a"),
            zmin=1,
            zmax=3,
            colorscale=[
                [0.00, "#83c9b7"],
                [0.499, "#83c9b7"],
                [0.50, "#f0c36d"],
                [0.749, "#f0c36d"],
                [0.75, "#e58c83"],
                [1.00, "#e58c83"],
            ],
            colorbar=dict(
                title={"text": "Sensitivity", "font": {"color": "#dce8f5"}},
                tickmode="array",
                tickvals=[1, 2, 3],
                ticktext=["Lower", "Moderate", "Higher"],
                tickfont=dict(color="#dce8f5"),
            ),
            hovertemplate=(
                "Country: %{y}<br>Event: %{x}<br>Initial screen: %{text}<extra></extra>"
            ),
        )
    )
    heatmap.update_layout(
        height=365,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce8f5"),
        margin=dict(l=10, r=15, t=12, b=85),
        xaxis=dict(
            side="bottom",
            tickangle=-12,
            tickfont=dict(color="#c1d0e0", size=11),
            showgrid=False,
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#c1d0e0", size=12),
            showgrid=False,
        ),
    )
    st.plotly_chart(heatmap, use_container_width=True)

    st.markdown(
        "**How to read this:** Higher sensitivity means the event may transmit "
        "through an important energy, shipping, food or industrial-input channel. "
        "It does not mean the economy will necessarily suffer a net loss; commodity "
        "exporters can also benefit from some price increases."
    )

    with st.expander("View the reasoning behind the initial exposure labels"):
        st.dataframe(
            filtered[["country", "event", "level", "rationale"]],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "The labels are provisional judgements used to make the prototype interactive. "
            "Use the Country & Industry Impact Analyzer to explore additional historical context and industry "
            "transmission channels. The ratings remain qualitative."
        )


def render_sources(highlights: pd.DataFrame) -> None:
    st.markdown("<div class='section-kicker'>05 / Data transparency</div>", unsafe_allow_html=True)
    st.subheader("Sources and interpretation notes")

    for _, row in highlights.iterrows():
        st.markdown(
            f"- **{row['source_name']}** — [{row['source_title']}]({row['source_url']}) "
            f"· {row['classification']}"
        )

    with st.expander("Important data limitations", expanded=True):
        st.markdown(
            """
            - The dashboard uses local CSV files. It does not fetch live market prices.
            - The EIA route series are historical oil-flow estimates, not a live measure of current disruption.
            - The UNCTAD Suez Canal transit comparison is a historical June 2024 observation.
            - The World Bank wheat figure is a forecast published in April 2022. It is not presented as the actual realized price increase.
            - Country exposure labels are qualitative prototype assumptions. They are not official statistics, investment advice or forecasts.
            - A source link is provided beside each historical headline so the user can inspect the original publication.
            """
        )


def render_dashboard() -> None:
    try:
        highlights = load_csv("event_highlights.csv")
        indicators = load_csv("global_indicators.csv")
        exposure = load_csv("country_exposure.csv")
    except (FileNotFoundError, pd.errors.ParserError) as error:
        st.error(f"There is a problem with the local data files: {error}")
        st.info(
            "Check that the three CSV files are saved in the project's data folder "
            "and that their filenames match the code."
        )
        return

    st.markdown(
        """
        <div class="scope-hero">
            <div class="scope-eyebrow">Global event-to-economy intelligence · prototype 0.7</div>
            <div class="scope-title">Global Impact Dashboard</div>
            <p class="scope-subtitle">
                Track geopolitical disruptions, follow their economic transmission channels,
                and compare the initial exposure of six major economies.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_event_pulse(highlights)
    st.divider()
    render_flow_charts(indicators)
    st.divider()
    render_map(exposure)
    st.divider()
    render_exposure_matrix(exposure)
    st.divider()
    render_sources(highlights)

    st.markdown(
        "<div class='small-note'>SHOCKSCOPE · Academic startup prototype · Historical data and transparent assumptions · Not investment advice</div>",
        unsafe_allow_html=True,
    )
