# Movie Revenue Analyzer - Enhanced app

## Run as follows

From this folder:

```powershell
uv sync
uv run streamlit run app.py --server.port 8504
```

Open http://localhost:8504.

## Overall

- Includes all 3,000 valid source movies rather than requiring every CSV field.
- Adds median revenue per movie alongside movie count, total revenue, and years.
- Shows yearly movie count and median revenue on chart hover.
- Defaults to ranked genre bars, with a radio button for the pie chart.
- Shows active sidebar filters and matching movie count above the summaries.
- Explains that revenue is assumed USD, nominal (not inflation-adjusted), and
  grouped by release year. These are neither annual receipts nor profit.

The five searchable multi-select sidebar filters affect every tab and summary.
Different filters combine with AND; selections within one filter use OR.
Explorer text search and year drill-down remain local to their respective tabs.
The year chart stays a line without filters, becomes bars with filters, and
remains visible for a single matching year. Clear filters restores the dataset.

## Dataset preparation

`train.csv` is a copy of the original source. Neither original CSV is overwritten.
`train_analyzer.csv` is the prepared seven-column analysis input. Rebuild it with:

```powershell
uv run python -m movies.prepare
```

The builder requires a unique integer ID, a nonempty title, valid release date,
and finite nonnegative revenue. Zero revenue is retained as supplied; very low
revenues are not corrected without evidence. Excluded records and reasons go to
`preparation_report.json`. Optional missing/empty metadata becomes Unknown.
Malformed optional lists also become Unknown and are counted separately in the
report. Existing names are deduplicated, and nested image nulls are irrelevant.
The current source retains 3,000/3,000 rows, with no malformed optional lists.
Unknown metadata: genres 7, cast 26, crew 16 movies.

Dates with two-digit years use the fixed 2017 source cutoff: 00-17 map to
2000-2017, 18-99 to 1918-1999. Prepared dates are ISO YYYY-MM-DD.

Each movie contributes revenue equally to its unique genres, including Unknown
when no genre is available. A genre filter selects movies; their full genre
allocations remain visible. Allocated totals preserve movie revenue before
rounding, with possible sub-cent floating-point differences. Display uses USD.
The dataset is a sample, not complete industry coverage.

## Verification and organization

```powershell
uv run pytest -q
```

`movies/prepare.py` builds the dataset and report. `movies/data.py` validates the
prepared input. `movies/analytics.py` handles search and aggregation.
`movies/views/` renders the sidebar and three tabs; `app.py` coordinates them.
Tests cover preparation, missing metadata, currency totals, search, shared
filters, year state/reset, single-year graphs, and genre chart switching.
