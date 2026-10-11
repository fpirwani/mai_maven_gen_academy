from pathlib import Path

import pandas as pd
import pytest

from movies.data import load_movies


def write_movie(tmp_path, **changes):
    row = dict(id=1, title="Example", release_date="5/4/67", revenue=90,
               genres="[{'name': 'Drama'}, {'name': 'Drama'}, {'name': 'Action'}]",
               cast="[{'name': 'Alice', 'profile_path': None}]",
               crew="[{'name': 'Bob'}, {'name': None}]")
    row.update(changes)
    path = tmp_path / "movies.csv"
    pd.DataFrame([row]).to_csv(path, index=False)
    return path


def test_normalizes_historical_date_unique_genres_and_nested_nulls(tmp_path):
    row = load_movies(write_movie(tmp_path)).iloc[0]
    assert row.release_year == 1967
    assert row.genres == ["Drama", "Action"]
    assert row.cast_names == ["Alice"]
    assert row.crew_names == ["Bob"]


@pytest.mark.parametrize("date,year", [("1/1/17", 2017), ("1/1/18", 1918),
                                           ("2005-03-04", 2005), ("3/4/2005", 2005)])
def test_date_centuries(tmp_path, date, year):
    assert load_movies(write_movie(tmp_path, release_date=date)).iloc[0].release_year == year


@pytest.mark.parametrize("change", [dict(revenue="bad"), dict(revenue=-1),
                                    dict(revenue="inf"), dict(release_date="2/30/10"),
                                    dict(genres="not a list"), dict(title="")])
def test_invalid_data_is_reported(tmp_path, change):
    with pytest.raises(ValueError):
        load_movies(write_movie(tmp_path, **change))


def test_missing_column_is_reported(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"title": ["Example"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="Missing columns"):
        load_movies(path)


def test_actual_dataset_has_3000_movies():
    movies = load_movies(Path(__file__).parents[1] / "train_analyzer.csv")
    assert len(movies) == 3000
    assert movies.id.is_unique
    assert movies.release_year.max() <= 2017
