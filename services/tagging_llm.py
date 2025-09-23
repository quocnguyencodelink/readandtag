# services/tagging_llm.py
# -*- coding: utf-8 -*-
"""
Rule-only tagging facade (LLM disabled).
- Keeps main.py unchanged while delegating to rule-based tagging.
- Preserves the 'path' value unchanged; adds a 'tag' field for legacy use.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from services.tagging_rule import rule_based_tag  # no other imports to avoid coupling

def tag_rows_with_budget(rows: List[Dict[str, Any]],
                         usd_budget: float = None) -> (List[Dict[str, Any]], Optional[str]):
    updated: List[Dict[str, Any]] = []
    for row in rows:
        path_val = row.get("path") if isinstance(row, dict) else None
        if path_val is None and isinstance(row, dict):
            path_val = row.get("Path")
        path_str = "" if path_val is None else str(path_val)

        new_row = dict(row)
        new_row["path"] = path_str
        new_row["tag"] = rule_based_tag(path_str)
        updated.append(new_row)

    header_note = "LLM disabled; rule-based tagging only (full path preserved)."
    return updated, header_note
