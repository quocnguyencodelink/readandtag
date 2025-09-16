#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from auth import get_box_client
from ui.folder_picker import BoxFolderPicker
from services.traversal import iterate_tree
from services.export import export_to_excel
from config import OUTPUT_XLSX
from boxsdk import Client

def main():
    client: Client = get_box_client()

    # UI: pick a folder (starting from root "0")
    picker = BoxFolderPicker(client)
    folder_id, folder_path = picker.show()

    if not folder_id:
        print("No folder selected. Exiting.")
        return

    # Resolve the selected folder name for path base
    if folder_id == "0":
        base_name = "All Files"
    else:
        info = client.folder(folder_id=folder_id).get()
        base_name = info.name

    rows = iterate_tree(client, folder_id, base_name)

    # Export to Excel
    export_to_excel(rows, OUTPUT_XLSX)
    print(f"Exported {len(rows)} rows to {OUTPUT_XLSX}")

if __name__ == "__main__":
    main()
