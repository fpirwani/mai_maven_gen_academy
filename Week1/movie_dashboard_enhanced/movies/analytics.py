"""Pure transformations shared by the three views."""
import pandas as pd


def display_table(movies: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "title": movies.title,
        "release_date": movies.release_date.dt.strftime("%Y-%m-%d"),
        "genres": movies.genres.map(lambda values: ", ".join(dict.fromkeys(values))),
        "cast name": movies.cast_names.map(", ".join),
        "crew name": movies.crew_names.map(", ".join),
        "revenue": movies.revenue,
    })


def search_movies(movies: pd.DataFrame, query: str) -> pd.DataFrame:
    query = query.strip().casefold()
    if not query:
        return movies
    table = display_table(movies)
    matches = pd.Series(False, index=movies.index)
    for column in table:
        text = table[column].astype(str).str.casefold()
        matches |= text.str.contains(query, regex=False, na=False)
    # Also accept the comma-formatted revenue visible in the table.
    matches |= movies.revenue.map(lambda value: f"{value:,.0f}").str.contains(query, regex=False)
    matches |= movies.revenue.map(lambda value: f"${value:,.2f}").str.contains(query, regex=False)
    return movies.loc[matches]


def yearly_revenue(movies: pd.DataFrame) -> pd.DataFrame:
    return movies.groupby("release_year", as_index=False, sort=True).revenue.sum()


def movies_for_year(movies: pd.DataFrame, year: int | None) -> pd.DataFrame:
    return movies if year is None else movies.loc[movies.release_year == year]


def genre_revenue(movies: pd.DataFrame) -> pd.DataFrame:
    records = []
    for movie in movies.itertuples():
        genres = list(dict.fromkeys(movie.genres)) or ["Unknown"]
        records.extend((genre, movie.revenue / len(genres)) for genre in genres)
    allocated = pd.DataFrame(records, columns=["genre", "revenue"])
    return (allocated.groupby("genre", as_index=False).revenue.sum()
            .sort_values(["revenue", "genre"], ascending=[False, True]).reset_index(drop=True))
