# -*- coding: utf-8 -*-
import os
from boxsdk import Client

# Common video file extensions (lowercase)
VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v",
    ".mpeg", ".mpg", ".3gp", ".3g2", ".ts", ".m2ts", ".mts", ".ogv",
}

def iterate_tree(client: Client, start_folder_id: str, start_folder_name: str):
    """
    Return rows for video files located in the selected folder and any of its subfolders.
    Each row: {'path': full_path_including_filename, 'file_name': name, 'tag': ''}

    - Includes files at the selected folder level and any depth below.
    - Filters by VIDEO_EXTENSIONS (case-insensitive).
    - Traverses with pagination (limit=1000) to handle large folders.
    """
    rows = []

    def walk(folder_id: str, path_prefix: str, depth: int):
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
                    # Recurse into subfolder
                    walk(item.id, folder_path, depth + 1)
                elif item.type == "file":
                    # Include files at any depth (including selected folder)
                    ext = os.path.splitext(item.name)[1].lower()
                    if ext in VIDEO_EXTENSIONS:
                        file_path = f"{path_prefix}/{item.name}"
                        rows.append({"path": file_path, "file_name": item.name, "tag": ""})
                else:
                    # skip other types (e.g., web_link)
                    pass

            if len(batch) < limit:
                break
            offset += len(batch)

    # Start from the selected folder (no folder rows added)
    start_path = f"/{start_folder_name}"
    walk(start_folder_id, start_path, depth=0)
    return rows
