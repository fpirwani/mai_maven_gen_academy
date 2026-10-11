from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app.py"


def test_genre_filter_matches_any_selected_genre_and_clears():
    from movies.data import load_movies
    source = load_movies(APP.parent / "train_analyzer.csv")
    selected = ["Drama", "Action"]
    expected = source.loc[source.genres.map(lambda genres: bool(set(genres) & set(selected)))]
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.multiselect(key="filter_genres").set_value(selected).run()
    assert not app.exception
    assert set(app.dataframe[0].value.title) == set(expected.title)
    assert set(app.dataframe[1].value.title) == set(expected.title)
    assert app.metric[1].value == f"${expected.revenue.sum():,.2f}"
    import pytest
    assert app.dataframe[2].value.revenue.sum() == pytest.approx(expected.revenue.sum())
    title = expected.iloc[0].title
    app.multiselect(key="filter_titles").select(title).run()
    assert app.dataframe[0].value.title.tolist() == [title]
    app.button(key="clear_filters").click().run()
    assert app.multiselect(key="filter_genres").value == []
    assert app.metric[0].value == "3,000"


def test_tabs_search_and_year_filter_remain_independent():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    assert len(app.tabs) == 3
    assert len(app.dataframe[0].value) == 3000
    app.text_input(key="movie_search").set_value("zzzznotamovie").run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 0
    assert len(app.dataframe[1].value) == 3000
    years = app.selectbox(key="selected_year").options
    app.selectbox(key="selected_year").select(int(years[-1])).run()
    assert not app.exception
    assert 0 < len(app.dataframe[1].value) < 3000
    assert app.dataframe[1].value.release_date.str.startswith(years[-1]).all()
    app.button(key="reset_year").click().run()
    assert len(app.dataframe[1].value) == 3000
    assert len(app.dataframe[0].value) == 0


def test_sidebar_filters_update_all_tabs_and_clear():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    original = app.dataframe[0].value
    title = original.iloc[0].title
    revenue = original.iloc[0].revenue
    app.multiselect(key="filter_titles").select(title).run()
    assert not app.exception
    assert app.dataframe[0].value.title.tolist() == [title]
    assert app.dataframe[1].value.title.tolist() == [title]
    assert app.metric[0].value == "1"
    assert app.dataframe[2].value.revenue.sum() == revenue
    year = int(original.iloc[0].release_date[:4])
    other_year = next(int(y) for y in app.multiselect(key="filter_years").options if int(y) != year)
    app.multiselect(key="filter_years").select(other_year).run()
    assert not app.exception
    assert app.metric[0].value == "0"
    assert len(app.tabs) == 3
    app.button(key="clear_filters").click().run()
    assert not app.exception
    assert app.metric[0].value == "3,000"


def test_sidebar_change_clears_previous_year_drilldown():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.selectbox(key="selected_year").select(2017).run()
    app.multiselect(key="filter_years").select(1965).run()
    assert not app.exception
    assert app.selectbox(key="selected_year").value is None
    assert app.dataframe[1].value.release_date.str.startswith("1965").all()


def test_cast_and_crew_filters_combine_and_allow_multiple_names():
    from movies.data import load_movies
    source = load_movies(APP.parent / "train_analyzer.csv")
    first = source.iloc[0]
    actors = first.cast_names[:2]
    crew_member = first.crew_names[0]
    expected = source.loc[
        source.cast_names.map(lambda names: any(actor in names for actor in actors))
        & source.crew_names.map(lambda names: crew_member in names)
    ]
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.multiselect(key="filter_cast").set_value(actors).run()
    app.multiselect(key="filter_crew").select(crew_member).run()
    assert not app.exception
    assert set(app.dataframe[0].value.title) == set(expected.title)
    assert set(app.dataframe[1].value.title) == set(expected.title)
    assert app.metric[1].value == f"${expected.revenue.sum():,.2f}"
