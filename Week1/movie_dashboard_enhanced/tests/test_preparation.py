import json
import pandas as pd

from movies.prepare import prepare_dataset
from movies.data import load_movies


def test_preparation_keeps_missing_optional_metadata_and_reports_invalid_rows(tmp_path):
    source = tmp_path / "source.csv"
    output = tmp_path / "prepared.csv"
    report = tmp_path / "report.json"
    pd.DataFrame([
        dict(id=1, title="Kept", release_date="1/1/10", revenue=100,
             genres="", cast="#N/A", crew="[]"),
        dict(id=2, title="Also kept", release_date="2/1/10", revenue=0,
             genres="[{'name':'Drama'}]", cast="broken", crew="[]"),
        dict(id=3, title="Bad date", release_date="2/30/10", revenue=1),
        dict(id=4, title="Bad revenue", release_date="1/1/10", revenue=-1),
    ]).to_csv(source, index=False)
    original = source.read_bytes()
    summary = prepare_dataset(source, output, report)
    movies = load_movies(output)
    assert movies.id.tolist() == [1, 2]
    assert movies.iloc[0].genres == ["Unknown"]
    assert movies.iloc[0].cast_names == ["Unknown"]
    assert movies.iloc[1].cast_names == ["Unknown"]
    assert summary["included_rows"] == 2
    assert summary["excluded_rows"] == 2
    assert summary["malformed_optional_fields"]["cast"] == 1
    assert len(json.loads(report.read_text())["exclusions"]) == 2
    assert source.read_bytes() == original
