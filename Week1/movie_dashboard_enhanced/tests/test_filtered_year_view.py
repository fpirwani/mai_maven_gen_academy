import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app.py"


def year_charts(app):
    return [json.loads(chart.proto.spec) for chart in app.get("plotly_chart")
            if "year_chart_" in chart.proto.id]


def test_overall_line_becomes_filtered_bars_with_movie_counts():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert year_charts(app)[0]["data"][0]["type"] == "scatter"
    app.multiselect(key="filter_years").set_value([1965, 2017]).run()
    assert not app.exception
    chart = year_charts(app)[0]
    trace = chart["data"][0]
    assert trace["type"] == "bar"
    assert trace["x"] == [1965, 2017]
    assert all(count > 0 for count, median in trace["customdata"])
    assert "Movies:" in trace["hovertemplate"]
    assert chart["layout"]["xaxis"]["type"] == "linear"
    assert any("no matching movies" in item.value.lower() for item in app.caption)
    app.selectbox(key="selected_year").select(2017).run()
    assert app.dataframe[1].value.release_date.str.startswith("2017").all()
    app.button(key="clear_filters").click().run()
    assert year_charts(app)[0]["data"][0]["type"] == "scatter"


def test_single_filtered_year_shows_one_bar_and_movies():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.multiselect(key="filter_years").select(1965).run()
    assert not app.exception
    chart = year_charts(app)[0]
    assert chart["data"][0]["type"] == "bar"
    assert chart["data"][0]["x"] == [1965]
    assert chart["data"][0]["y"] == [int(app.dataframe[1].value.revenue.sum())]
    assert app.dataframe[1].value.release_date.str.startswith("1965").all()
    assert app.selectbox(key="selected_year").value is None
