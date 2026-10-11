import pandas as pd
import pytest

from movies.analytics import display_table, search_movies, yearly_revenue, genre_revenue, movies_for_year


@pytest.fixture
def movies():
    return pd.DataFrame([
        dict(id=1, title="Alpha [One]", release_date=pd.Timestamp("2000-01-02"),
             release_year=2000, genres=["Drama", "Action", "Drama"],
             cast_names=["Alice", "Sam"], crew_names=["Bob"], revenue=90),
        dict(id=2, title="Beta", release_date=pd.Timestamp("2002-02-03"),
             release_year=2002, genres=["Drama"], cast_names=["Carol"],
             crew_names=["Dave"], revenue=30),
    ])


def test_all_six_columns_and_comma_names(movies):
    table = display_table(movies)
    assert list(table) == ["title", "release_date", "genres", "cast name", "crew name", "revenue"]
    assert table.iloc[0]["cast name"] == "Alice, Sam"
    assert table.iloc[0].revenue == 90


@pytest.mark.parametrize("query,ids", [("ALP", [1]), ("lic", [1]), ("dav", [2]),
    ("act", [1]), ("2002", [2]), ("90", [1]), ("[", [1]), (".*", []), (" ", [1, 2])])
def test_partial_literal_search_across_columns(movies, query, ids):
    assert search_movies(movies, query).id.tolist() == ids


def test_year_aggregation_and_drill_down(movies):
    assert yearly_revenue(movies).to_dict("records") == [
        {"release_year": 2000, "revenue": 90}, {"release_year": 2002, "revenue": 30}]
    assert movies_for_year(movies, 2002).id.tolist() == [2]
    assert len(movies_for_year(movies, None)) == 2


def test_genre_split_deduplicates_and_preserves_total(movies):
    totals = genre_revenue(movies).set_index("genre").revenue.to_dict()
    assert totals == {"Drama": 75, "Action": 45}
    assert sum(totals.values()) == 120


def test_unknown_genre_and_empty_dataset(movies):
    movies.at[0, "genres"] = []
    assert genre_revenue(movies).set_index("genre").loc["Unknown", "revenue"] == 90
    assert genre_revenue(movies.iloc[:0]).empty
    assert yearly_revenue(movies.iloc[:0]).empty
