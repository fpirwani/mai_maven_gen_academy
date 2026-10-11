"""Searchable sidebar selectors shared by every view."""
import pandas as pd
import streamlit as st

from movies.views.yearly_revenue import _reset_year

FILTER_KEYS = ("filter_titles", "filter_years", "filter_genres", "filter_cast", "filter_crew")


def _clear_filters() -> None:
    for key in FILTER_KEYS:
        st.session_state[key] = []
    _reset_year()


def render(movies: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.header("Filter movies")
        st.caption("Type in a dropdown to find options. Choose one or more. "
                   "Filters apply to all three tabs.")
        titles = st.multiselect("Movie name", sorted(movies.title.unique()),
                                key="filter_titles", on_change=_reset_year)
        years = st.multiselect("Release year", sorted(movies.release_year.unique().tolist()),
                               key="filter_years", on_change=_reset_year)
        genres = st.multiselect("Genre", sorted({genre for values in movies.genres for genre in values}),
                                key="filter_genres", on_change=_reset_year)
        cast = st.multiselect("Cast", sorted({name for names in movies.cast_names for name in names}),
                              key="filter_cast", on_change=_reset_year)
        crew = st.multiselect("Crew", sorted({name for names in movies.crew_names for name in names}),
                              key="filter_crew", on_change=_reset_year)
        st.button("Clear filters", key="clear_filters", on_click=_clear_filters)
        st.caption("Within each dropdown, any selected value matches. "
                   "Across dropdowns, all conditions must match. Empty means all.")
    mask = pd.Series(True, index=movies.index)
    if titles:
        mask &= movies.title.isin(titles)
    if years:
        mask &= movies.release_year.isin(years)
    if genres:
        mask &= movies.genres.map(lambda values: bool(set(values).intersection(genres)))
    if cast:
        mask &= movies.cast_names.map(lambda names: bool(set(names).intersection(cast)))
    if crew:
        mask &= movies.crew_names.map(lambda names: bool(set(names).intersection(crew)))
    result = movies.loc[mask]
    st.sidebar.caption(f"{len(result):,} of {len(movies):,} movies match")
    active = []
    for label, values in (("Movie", titles), ("Year", years), ("Genre", genres),
                          ("Cast", cast), ("Crew", crew)):
        if values:
            text = ", ".join(str(value) for value in values[:3])
            if len(values) > 3:
                text += f" (+{len(values) - 3} more)"
            active.append(f"{label}: {text}")
    st.caption("Active filters: " + (" · ".join(active) if active else "All movies")
               + f" · {len(result):,} matching movies")
    return result
