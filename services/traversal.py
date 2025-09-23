# services/traversal.py
# -*- coding: utf-8 -*-
import os
from typing import List, Dict
from pathlib import Path
from boxsdk import Client

# Common video file extensions (lowercase)
VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v",
    ".mpeg", ".mpg", ".3gp", ".3g2", ".ts", ".m2ts", ".mts", ".ogv",
}

def _safe_get_ancestors(folder_info) -> List[str]:
    """
    Extract ancestor names from Box folder.path_collection, skipping None values.
    Returns names excluding the current folder; order is from root toward the folder.
    """
    names: List[str] = []
    pc = getattr(folder_info, "path_collection", None)
    if not pc:
        return names

    # In SDK objects, path_collection can be dict-like or have an 'entries' attribute
    entries = pc.get("entries") if isinstance(pc, dict) else getattr(pc, "entries", None)
    if not entries:
        return names

    for e in entries:
        nm = e.get("name") if isinstance(e, dict) else getattr(e, "name", None)
        if nm:
            names.append(nm)
    return names

def _full_folder_path(client: Client, folder_id: str) -> str:
    """
    Build absolute path beginning with 'All Files' for any Box folder ID using path_collection.
    """
    if str(folder_id) == "0":
        return "All Files"

    # Request only fields needed to build absolute path
    info = client.folder(folder_id=folder_id).get(fields=["name", "path_collection"])
    ancestors = _safe_get_ancestors(info)

    # Ensure 'All Files' is the first element
    parts = ancestors[:] if ancestors else []
    if not parts or parts != "All Files":
        parts = ["All Files"] + parts
    parts.append(getattr(info, "name", "") or "")

    parts = [p for p in parts if p]
    return "/".join(parts)

def iterate_tree(client: Client, start_folder_id: str, _start_folder_name_ignored: str) -> List[Dict[str, str]]:
    """
    Return rows for video files located in the selected folder and any of its subfolders,
    with each 'path' set to the full absolute Box path starting at 'All Files'.
    Each row: {'path': full_path_including_filename, 'file_name': name, 'tag': ''}.
    """
    rows: List[Dict[str, str]] = []
    base_prefix = _full_folder_path(client, start_folder_id)

    def walk(folder_id: str, path_prefix: str):
        limit = 1000
        offset = 0
        while True:
            items = client.folder(folder_id=folder_id).get_items(limit=limit, offset=offset)
            batch = list(items)
            if not batch:
                break

            for item in batch:
                if item.type == "folder":
                    folder_path = f"{path_prefix}/{item.name}"
                    walk(item.id, folder_path)
                elif item.type == "file":
                    # Safe extension extraction: Path.suffix yields '' when no extension
                    ext = Path(item.name or "").suffix.lower()
                    if ext in VIDEO_EXTENSIONS:
                        file_path = f"{path_prefix}/{item.name}"
                        rows.append({"path": file_path, "file_name": item.name, "tag": ""})
                else:
                    # skip other item types (e.g., web_link)
                    pass

            if len(batch) < limit:
                break
            offset += len(batch)

    walk(start_folder_id, base_prefix)
    return rows
