import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from movies.analytics import movies_for_year, yearly_revenue
from movies.views.explorer import movie_table


def _select_chart_year(chart_key: str, valid_years: list[int]) -> None:
    event = st.session_state.get(chart_key, {})
    points = event.get("selection", {}).get("points", [])
    if points:
        year = int(points[-1]["x"])
        if year in valid_years:
            st.session_state.selected_year = year


def _clear_chart() -> None:
    st.session_state.year_chart_version = st.session_state.get("year_chart_version", 0) + 1


def _reset_year() -> None:
    st.session_state.selected_year = None
    _clear_chart()


def render(movies: pd.DataFrame, filtered: bool = False) -> None:
    st.subheader("Revenue of selected movies by release year" if filtered else "Revenue by release year")
    if movies.empty:
        st.info("No movies match the sidebar filters. Adjust or clear the filters to see the trend.")
        return
    st.caption("Revenue is grouped by movie release year, not the year revenue was received.")
    totals = yearly_revenue(movies)
    years = totals.release_year.astype(int).tolist()
    use_bars = filtered or len(years) == 1
    st.caption("Click a bar to see that year's movies. Gaps indicate no matching movies, "
               "not zero industry revenue." if use_bars else
               "Click a marker to see that year's movies below.")
    picker, reset = st.columns([4, 1], vertical_alignment="bottom")
    with picker:
        year = st.selectbox("Drill down to a year", [None, *years],
                            format_func=lambda value: "All years" if value is None else str(value),
                            key="selected_year", on_change=_clear_chart)
    with reset:
        st.button("Reset year", key="reset_year", on_click=_reset_year, width="stretch")

    counts = movies.groupby("release_year").size().reindex(years).tolist()
    medians = movies.groupby("release_year").revenue.median().reindex(years).tolist()
    common = dict(x=years, y=totals.revenue.tolist(), customdata=list(zip(counts, medians)),
                  hovertemplate="Release year: %{x}<br>Revenue (USD): $%{y:,.2f}"
                                "<br>Movies: %{customdata[0]}"
                                "<br>Median per movie (USD): $%{customdata[1]:,.2f}<extra></extra>")
    if use_bars:
        trace = go.Bar(**common, width=0.8,
                       marker_color=["#1e40af" if value == year else "#2563eb" for value in years])
    else:
        trace = go.Scatter(**common, mode="lines+markers",
                           line=dict(color="#2563eb", width=3),
                           marker=dict(size=[13 if value == year else 8 for value in years]))
    figure = go.Figure(trace)
    figure.update_layout(height=390, clickmode="event+select", dragmode=False,
                         xaxis_title="Release year", yaxis_title="Total revenue (USD)",
                         margin=dict(l=20, r=20, t=20, b=30), showlegend=False)
    figure.update_xaxes(tickformat="d", type="linear")
    if len(years) == 1:
        figure.update_xaxes(tickmode="array", tickvals=years,
                            range=[years[0] - 1, years[0] + 1])
    figure.update_yaxes(tickprefix="$", tickformat="~s")
    chart_key = f"year_chart_{st.session_state.get('year_chart_version', 0)}"
    st.plotly_chart(figure, key=chart_key, width="stretch", selection_mode="points",
                    on_select=lambda: _select_chart_year(chart_key, years),
                    config={"displayModeBar": False})

    selected = movies_for_year(movies, year)
    st.subheader("All movies" if year is None else f"Movies released in {year}")
    st.caption(f"{len(selected):,} movies · Total revenue (USD): ${selected.revenue.sum():,.2f}")
    st.caption(f"Median revenue per movie (USD): ${selected.revenue.median():,.2f}" if not selected.empty
               else "Median revenue per movie: unavailable")
    movie_table(selected.sort_values("revenue", ascending=False), "year_movies")
