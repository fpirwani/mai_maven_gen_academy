import pandas as pd
import streamlit as st

from movies.analytics import display_table, search_movies


def movie_table(movies: pd.DataFrame, key: str) -> None:
    st.dataframe(
        display_table(movies), hide_index=True, width="stretch", height=480, key=key,
        column_config={
            "title": st.column_config.TextColumn("title", width="medium"),
            "release_date": st.column_config.TextColumn("release_date"),
            "genres": st.column_config.TextColumn("genres", width="medium"),
            "cast name": st.column_config.TextColumn("cast name", width="large"),
            "crew name": st.column_config.TextColumn("crew name", width="large"),
            "revenue": st.column_config.NumberColumn("revenue (USD)", format="dollar", step=0.01),
        },
    )


def render(movies: pd.DataFrame) -> None:
    st.subheader("Find a movie")
    query = st.text_input("Search all six columns", key="movie_search",
                          placeholder="Try a title, actor, crew member, genre, year, or revenue…")
    filtered = search_movies(movies, query)
    st.caption(f"{len(filtered):,} of {len(movies):,} movies · Partial matches, ignoring case. "
               "Click a column heading to sort. Search affects this tab only.")
    if filtered.empty:
        st.info("No matching movies. Try a shorter term or clear the search.")
    movie_table(filtered, "explorer_table")
