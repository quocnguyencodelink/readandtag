#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import filedialog
from boxsdk import Client

from auth import get_box_client
from ui.folder_picker import BoxFolderPicker
from services.traversal import iterate_tree
from services.export import export_to_excel
from config import OUTPUT_XLSX

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

    # Traverse and collect rows (video files in subfolders)
    rows = iterate_tree(client, folder_id, base_name)

    # Ask user where to save the Excel file
    default_dir = os.path.dirname(OUTPUT_XLSX) if OUTPUT_XLSX else os.path.expanduser("~")
    safe_base = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in base_name).strip() or "box"
    default_name = f"{safe_base}_videos.xlsx"

    root = tk.Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(
        title="Save Excel As",
        defaultextension=".xlsx",
        initialdir=default_dir,
        initialfile=default_name,
        filetypes=[("Excel Workbook", "*.xlsx"), ("All Files", "*.*")]
    )
    root.destroy()

    if not save_path:
        print("No save location selected. Exiting.")
        return

    # Export to the chosen path
    export_to_excel(rows, save_path)
    print(f"Exported {len(rows)} rows to {save_path}")

if __name__ == "__main__":
    main()
