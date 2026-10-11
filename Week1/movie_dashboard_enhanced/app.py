"""Start with: uv run streamlit run app.py."""
from pathlib import Path

import pandas as pd
import streamlit as st

from movies.data import load_movies
from movies.views import explorer, filters, genre_revenue, yearly_revenue

st.set_page_config(page_title="Movie Revenue Analyzer · Enhanced", page_icon="🎬", layout="wide")


@st.cache_data(show_spinner=False)
def cached_movies(path: str, modified_ns: int) -> pd.DataFrame:
    """The modification time invalidates the cache when the source changes."""
    return load_movies(path)


st.title("Movie Revenue Analyzer · Enhanced")
st.caption("Explore the movies, follow revenue by release year, and compare genres.")
source = Path(__file__).parent / "train_analyzer.csv"
try:
    movies = cached_movies(str(source), source.stat().st_mtime_ns)
except (OSError, ValueError) as exc:
    st.error(f"Could not load train_analyzer.csv: {exc}. Run uv run python -m movies.prepare to rebuild it.")
    st.stop()

dataset = movies
movies = filters.render(dataset)

left, middle, median, right = st.columns(4)
left.metric("Movies", f"{len(movies):,}")
middle.metric("Total revenue (USD)", f"${movies.revenue.sum():,.2f}")
median.metric("Median revenue per movie (USD)", "—" if movies.empty else f"${movies.revenue.median():,.2f}")
right.metric("Release years", "—" if movies.empty else
             f"{movies.release_year.min()}–{movies.release_year.max()}")
st.caption("Source: train_analyzer.csv, prepared from train.csv · All revenue assumed USD")
st.caption("Movie revenues grouped by release year—not annual receipts or profit. "
           "Amounts are not inflation-adjusted. This dataset is a sample, not the entire movie market.")
with st.expander("About this comparison version"):
    st.write(f"This version includes {len(dataset):,} prepared movies, compared with 203 in the original app. "
             "Only essential identity, title, date, and revenue values determine inclusion. "
             "Missing homepage, tagline, collection, cast, crew, or genre metadata does not exclude a movie.")
    unknown_genres = dataset.genres.map(lambda names: names == ["Unknown"]).sum()
    unknown_cast = dataset.cast_names.map(lambda names: names == ["Unknown"]).sum()
    unknown_crew = dataset.crew_names.map(lambda names: names == ["Unknown"]).sum()
    st.write(f"Unknown metadata: {unknown_genres:,} movies lack genres, {unknown_cast:,} lack cast names, "
             f"and {unknown_crew:,} lack crew names. The preparation report records exclusions and metadata issues.")

movie_tab, year_tab, genre_tab = st.tabs(["Movie explorer", "Revenue by year", "Genre revenue share"])
with movie_tab:
    explorer.render(movies)
with year_tab:
    yearly_revenue.render(movies, filtered=any(st.session_state.get(key) for key in filters.FILTER_KEYS))
with genre_tab:
    genre_revenue.render(movies)
