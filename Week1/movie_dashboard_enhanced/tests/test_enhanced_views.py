import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app.py"


def test_median_active_filters_and_genre_view_toggle():
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    assert not app.exception
    table = app.dataframe[0].value
    median = next(metric for metric in app.metric if metric.label == "Median revenue per movie (USD)")
    assert median.value == f"${table.revenue.median():,.2f}"
    charts = [json.loads(chart.proto.spec) for chart in app.get('plotly_chart')]
    assert charts[-1]['data'][0]['type'] == 'bar'
    app.radio(key='genre_view').set_value('Pie chart').run()
    charts = [json.loads(chart.proto.spec) for chart in app.get('plotly_chart')]
    assert charts[-1]['data'][0]['type'] == 'pie'
    app.multiselect(key='filter_genres').select('Unknown').run()
    assert not app.exception
    assert app.metric[0].value == '7'
    assert any('Genre: Unknown' in caption.value for caption in app.caption)
    assert all('Unknown' in genres for genres in app.dataframe[0].value.genres)
