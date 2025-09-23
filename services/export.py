# services/export.py
# -*- coding: utf-8 -*-
"""
Export aligned to the client columns:
  path, event names, edit_types, years, days, dates, stages, camera_types, camera_models, artist_names
- Multi-valued lists are joined with '; ' per cell.
- Full path is preserved exactly.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

try:
    import pandas as pd
except Exception:
    raise RuntimeError("pandas is required by services.export; pip install pandas openpyxl")

from services.tagging_rule import map_categories_from_path

EXPORT_COLUMNS: List[str] = [
    "path",
    "event names",
    "edit_types",
    "years",
    "days",
    "dates",
    "stages",
    "camera_types",
    "camera_models",
    "artist_names",
]

def _coerce_path(row: Dict[str, Any]) -> str:
    v = row.get("path") if isinstance(row, dict) else None
    if v is None and isinstance(row, dict):
        v = row.get("Path")
    return "" if v is None else str(v)

def _join(values: List[str]) -> str:
    return "; ".join(values) if values else ""

def export_to_excel(rows: List[Dict[str, Any]],
                    save_path: str,
                    header_note: Optional[str] = None) -> None:
    records: List[Dict[str, Any]] = []
    for row in rows:
        p = _coerce_path(row)
        rec = map_categories_from_path(p)
        out: Dict[str, Any] = {"path": p}
        for col in EXPORT_COLUMNS:
            if col == "path":
                continue
            out[col] = _join(rec.get(col, []))
        records.append(out)

    df = pd.DataFrame.from_records(records, columns=EXPORT_COLUMNS)
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="tags")
        if header_note:
            pd.DataFrame({"note": [header_note]}).to_excel(writer, index=False, sheet_name="notes")

def export_to_csv(rows: List[Dict[str, Any]], save_path: str) -> None:
    records: List[Dict[str, Any]] = []
    for row in rows:
        p = _coerce_path(row)
        rec = map_categories_from_path(p)
        out: Dict[str, Any] = {"path": p}
        for col in EXPORT_COLUMNS:
            if col == "path":
                continue
            out[col] = _join(rec.get(col, []))
        records.append(out)

    df = pd.DataFrame.from_records(records, columns=EXPORT_COLUMNS)
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    df.to_csv(save_path, index=False, encoding="utf-8")
