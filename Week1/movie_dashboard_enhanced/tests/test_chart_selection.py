from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_chart_event_sets_year_and_reset_clears_it():
    app = AppTest.from_string('''
import streamlit as st
from movies.views.yearly_revenue import _select_chart_year, _reset_year
st.session_state["chart"] = {"selection": {"points": [{"x": 2005}]}}
_select_chart_year("chart", [2000, 2005])
st.write(st.session_state.selected_year)
st.button("Reset", on_click=_reset_year)
if st.session_state.get("year_chart_version"):
    st.write(st.session_state.selected_year is None)
''').run()
    assert not app.exception
    assert app.markdown[0].value == "`2005`"
    # Verify the reset callback in its own run, without injecting a fresh click.
    reset = AppTest.from_string('''
import streamlit as st
from movies.views.yearly_revenue import _reset_year
st.session_state.selected_year = 2005
_reset_year()
st.write(st.session_state.selected_year is None)
st.write(st.session_state.year_chart_version)
''').run()
    assert not reset.exception
    assert reset.markdown[0].value == "`True`"
    assert reset.markdown[1].value == "`1`"


def test_real_dataset_reconciles_to_independent_total():
    import csv
    from movies.data import load_movies
    from movies.analytics import yearly_revenue, genre_revenue
    import pytest

    path = Path(__file__).parents[1] / "train_analyzer.csv"
    with path.open(encoding="utf-8", newline="") as source:
        expected = sum(int(row["revenue"]) for row in csv.DictReader(source))
    movies = load_movies(path)
    assert expected == 200177555666
    assert yearly_revenue(movies).revenue.sum() == expected
    assert genre_revenue(movies).revenue.sum() == pytest.approx(expected, abs=0.01)
