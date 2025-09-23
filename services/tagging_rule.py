# services/tagging_rule.py
# -*- coding: utf-8 -*-
"""
Client-aligned, regex map–driven rule tagging.

- Reads regex maps from _maps/slash_string_counts_with_categories_v3_with_maps.xlsx
  (or MAPS_XLSX env var), using the client's sheet names (e.g., "Event Regex Map").
- Normalizes columns to {pattern, label, label_template} (supports "labeltemplate" in workbook).
- Applies maps case-insensitively to the full path (working copy replaces underscores with spaces).
- Returns multi-valued lists per category in keys matching the requested export schema:
  "event names", "edit_types", "years", "days", "dates", "stages", "camera_types",
  "camera_models", "artist_names".
- Provides rule_based_tag for legacy callers (single-line human-readable summary).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import pandas as pd
except Exception as e:
    raise RuntimeError("pandas is required by services.tagging_rule; pip install pandas")  # [3]

# Categories/columns requested for export
CATEGORIES: List[str] = [
    "event names",
    "edit_types",
    "years",
    "days",
    "dates",
    "stages",
    "camera_types",
    "camera_models",
    "artist_names",
]  # [3]

# Workbook sheet aliases to match the client's map sheets
SHEET_ALIASES: Dict[str, List[str]] = {
    "event names": ["Event Regex Map", "events", "event names", "event_names"],
    "edit_types": ["Edit Type Regex Map", "edit types", "edit_types", "edits"],
    "years": ["Year Regex Map", "years", "year"],
    "days": ["Day Regex Map", "days", "day"],
    "dates": ["Date Regex Map", "dates", "date"],
    "stages": ["Stage Regex Map", "stages", "stage"],
    "camera_types": ["Camera Type Regex Map", "camera types", "camera_types"],
    "camera_models": ["Camera Model Regex Map", "camera models", "camera_models"],
    "artist_names": ["Artist Regex Map", "artist names", "artist_names", "artists"],
}  # [1]

def _default_maps_path() -> str:
    """
    Resolve _maps/slash_string_counts_with_categories_v3_with_maps.xlsx
    relative to project layout: services/ is one level below the directory
    containing main.py, so _maps is at services/../_maps.
    """
    here = Path(__file__).resolve()
    # CHANGED: excel_files -> _maps (keep everything else unchanged)
    candidate = here.parent.parent / "_maps" / "slash_string_counts_with_categories_v3_with_maps.xlsx"
    return str(candidate)  # [1]

MAPS_XLSX = os.getenv("MAPS_XLSX", _default_maps_path())  # [1]

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c: c for c in df.columns}
    lower_map = {c: c.lower().strip() for c in df.columns}
    df = df.rename(columns=lower_map)
    if "label_template" not in df.columns and "labeltemplate" in df.columns:
        df = df.rename(columns={"labeltemplate": "label_template"})
    for col in ("pattern", "label", "label_template"):
        if col not in df.columns:
            df[col] = ""
    return df[["pattern", "label", "label_template"]].fillna("")  # [1]

def _load_maps_from_workbook(xlsx_path: str) -> Dict[str, pd.DataFrame]:
    maps: Dict[str, pd.DataFrame] = {}
    if not os.path.exists(xlsx_path):
        return maps
    try:
        with pd.ExcelFile(xlsx_path) as xf:
            available = {s.lower().strip(): s for s in xf.sheet_names}
            for cat in CATEGORIES:
                chosen_sheet: Optional[str] = None
                for alias in SHEET_ALIASES.get(cat, [cat]):
                    key = alias.lower().strip()
                    if key in available:
                        chosen_sheet = available[key]
                        break
                if not chosen_sheet:
                    continue
                df = pd.read_excel(xf, sheet_name=chosen_sheet, dtype=str)
                df = _normalize_columns(df)
                maps[cat] = df
    except Exception:
        return {}
    return maps  # [1]

def apply_regex_map(text: str, mapping_df: pd.DataFrame, flags: int = re.IGNORECASE) -> List[str]:
    t = (text or "").replace("_", " ")
    out: List[str] = []
    df = mapping_df.fillna("")
    for _i, m in df.iterrows():
        pat = str(m.get("pattern", "") or "").strip()
        if not pat:
            continue
        try:
            cre = re.compile(pat, flags)
        except re.error:
            continue
        matches = list(cre.finditer(t))
        if not matches:
            continue
        raw_label = str(m.get("label", "") or "")
        tmpl = str(m.get("label_template", "") or "")
        labels = [raw_label] if raw_label else [hit.expand(tmpl) for hit in matches if tmpl]
        for lbl in labels:
            if lbl and lbl not in out:
                out.append(lbl)
    return out  # [3]

_MAPS_BY_CATEGORY: Dict[str, pd.DataFrame] = _load_maps_from_workbook(MAPS_XLSX)  # [1]

def map_categories_from_path(path_str: str) -> Dict[str, List[str]]:
    text = "" if path_str is None else str(path_str)
    result: Dict[str, List[str]] = {"path": [text]}
    for cat in CATEGORIES:
        df = _MAPS_BY_CATEGORY.get(cat)
        result[cat] = apply_regex_map(text, df) if df is not None else []
    return result  # [3]

def rule_based_record(path_str: str) -> Dict[str, Any]:
    return map_categories_from_path(path_str)  # [3]

def rule_based_tag(path_str: str) -> str:
    rec = map_categories_from_path(path_str)
    def join(vals: List[str]) -> str:
        return "; ".join(vals) if vals else ""
    parts = []
    for cat in CATEGORIES:
        vals = join(rec.get(cat, []))
        if vals:
            parts.append(f"{cat} : {vals}")
    return ", ".join(parts)  # [3]
