"""Build the analysis input without rejecting movies for optional metadata."""
import json
import math
from pathlib import Path

import pandas as pd

from movies.data import _names, _release_date

MISSING = {"", "#n/a", "n/a", "nan", "none", "null", "<na>"}


def prepare_dataset(source: Path, output: Path, report: Path) -> dict:
    if source.resolve() in {output.resolve(), report.resolve()}:
        raise ValueError("Output paths must not overwrite the source.")
    raw = pd.read_csv(source, dtype=str, keep_default_na=False)
    required = {"id", "title", "release_date", "revenue"}
    if not required.issubset(raw.columns):
        raise ValueError("Missing required columns: " + ", ".join(sorted(required - set(raw.columns))))
    records, exclusions, seen = [], [], set()
    unknown = {field: 0 for field in ("genres", "cast", "crew")}
    malformed = dict(unknown)
    for index, row in raw.iterrows():
        try:
            identity = int(row.id)
            if identity in seen:
                raise ValueError("duplicate movie ID")
            title = row.title.strip()
            if title.casefold() in MISSING:
                raise ValueError("missing title")
            date = _release_date(row.release_date.strip())
            revenue = float(row.revenue)
            if not math.isfinite(revenue) or revenue < 0:
                raise ValueError("revenue must be finite and nonnegative")
        except (ValueError, TypeError, OverflowError) as exc:
            exclusions.append({"record": int(index + 1), "id": row.id, "reason": str(exc)})
            continue
        seen.add(identity)
        record = dict(id=identity, title=title, release_date=date.strftime("%Y-%m-%d"),
                      revenue=int(revenue) if revenue.is_integer() else revenue)
        for field in unknown:
            text = row.get(field, "").strip()
            names = []
            if text.casefold() not in MISSING:
                try:
                    names = _names(text, field)
                except ValueError:
                    malformed[field] += 1
            if not names:
                unknown[field] += 1
                names = ["Unknown"]
            record[field] = json.dumps([{"name": name} for name in names], ensure_ascii=False)
        records.append(record)
    if not records:
        raise ValueError("No valid movies remain after essential-field validation.")
    summary = dict(source=source.name, input_rows=len(raw), included_rows=len(records),
                   excluded_rows=len(exclusions), unknown_metadata=unknown,
                   malformed_optional_fields=malformed, exclusions=exclusions)
    pd.DataFrame(records).to_csv(output, index=False, encoding="utf-8")
    report.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(json.dumps(prepare_dataset(root / "train.csv", root / "train_analyzer.csv",
                                    root / "preparation_report.json"), indent=2))
