"""Read the source without changing it; normalize fields used by the dashboard."""
import ast
import json
import math
from datetime import datetime
from pathlib import Path

import pandas as pd

REQUIRED = ["id", "title", "release_date", "genres", "cast", "crew", "revenue"]


def _names(text: str, field: str) -> list[str]:
    try:
        try:
            items = json.loads(text)
        except json.JSONDecodeError:
            items = ast.literal_eval(text)
    except (ValueError, SyntaxError) as exc:
        raise ValueError(f"{field} must contain a list of objects") from exc
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError(f"{field} must contain a list of objects")
    names = [item["name"].strip() for item in items
             if isinstance(item.get("name"), str) and item["name"].strip()]
    return list(dict.fromkeys(names))


def _release_date(text: str) -> pd.Timestamp:
    if "/" in text:
        month, day, year = map(int, text.split("/"))
        if len(text.split("/")[-1]) == 2:
            year += 2000 if year <= 17 else 1900
        return pd.Timestamp(datetime(year, month, day))
    return pd.Timestamp(datetime.strptime(text, "%Y-%m-%d"))


def load_movies(path: str | Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = sorted(set(REQUIRED) - set(raw.columns))
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    if raw.empty:
        raise ValueError("The dataset contains no movies.")
    records = []
    for index, row in raw.iterrows():
        try:
            if not row.title.strip():
                raise ValueError("title is empty")
            revenue = float(row.revenue)
            if not math.isfinite(revenue) or revenue < 0:
                raise ValueError("revenue must be finite and nonnegative")
            date = _release_date(row.release_date.strip())
            records.append(dict(
                id=int(row.id), title=row.title.strip(), release_date=date,
                release_year=date.year, genres=_names(row.genres, "genres"),
                cast_names=_names(row.cast, "cast"), crew_names=_names(row.crew, "crew"),
                revenue=int(revenue) if revenue.is_integer() else revenue,
            ))
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError(f"CSV record {index + 1} ({row.title!r}): {exc}") from exc
    result = pd.DataFrame(records)
    if not result.id.is_unique:
        raise ValueError("Movie IDs must be unique; duplicate IDs would double-count revenue.")
    return result
