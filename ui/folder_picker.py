# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from boxsdk import Client

class BoxFolderPicker:
    """
    A Tkinter-based Box folder browser.
    Uses a hidden 'type' column to distinguish 'folder' vs 'file' deterministically.
    """

    def __init__(self, client: Client, title="Select a Box Folder"):
        self.client = client
        self.selected_folder_id = None
        self.selected_folder_path = None

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("700x500")

        # Hidden column to carry type metadata: 'folder' or 'file'
        self.tree = ttk.Treeview(self.root, columns=("type",), displaycolumns=())
        self.tree.heading("#0", text="Folder Browser (double-click folders to expand)")
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, pady=6)

        self.path_label_var = tk.StringVar(value="Current selection: None")
        tk.Label(self.root, textvariable=self.path_label_var, anchor="w").pack(fill=tk.X, padx=6, pady=4)

        select_btn = tk.Button(btn_frame, text="Select This Folder", command=self._select_current)
        select_btn.pack(side=tk.LEFT, padx=6)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self._cancel)
        cancel_btn.pack(side=tk.LEFT, padx=6)

        # Insert root (All Files) node, ID "0"
        root_id = "0"
        display_name = "All Files (root: 0)"
        # Mark root as a folder via hidden column
        self.tree.insert("", "end", iid=root_id, text=display_name, open=False, values=("folder",))
        # Add a dummy child to show expand arrow
        self.tree.insert(root_id, "end", iid=f"{root_id}_dummy", text="Loading...")

        # Bind canonical Treeview events
        self.tree.bind("<<TreeviewOpen>>", self._on_open)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Track which nodes have been loaded already
        self._loaded_nodes = set()

    def _on_open(self, event):
        # Populate children for the folder being opened
        folder_id = self.tree.focus()
        if not folder_id or folder_id.endswith("_dummy"):
            return
        self._populate_children(folder_id)

    def _clear_dummy(self, folder_id):
        for child in self.tree.get_children(folder_id):
            if child.endswith("_dummy"):
                self.tree.delete(child)

    def _populate_children(self, folder_id):
        # Prevent duplicate loads
        if folder_id in self._loaded_nodes:
            return

        self._clear_dummy(folder_id)
        try:
            for item in self._iterate_folder_items(folder_id):
                if item.type == "folder":
                    if not self.tree.exists(item.id):
                        self.tree.insert(
                            folder_id, "end",
                            iid=item.id,
                            text=f"[Folder] {item.name}",
                            open=False,
                            values=("folder",),  # store type in hidden column
                        )
                        # Add dummy to show expand arrow for folders
                        self.tree.insert(item.id, "end", iid=f"{item.id}_dummy", text="Loading...")
                elif item.type == "file":
                    if not self.tree.exists(item.id):
                        self.tree.insert(
                            folder_id, "end",
                            iid=item.id,
                            text=f"{item.name}",
                            open=False,
                            values=("file",),  # store type in hidden column
                        )
                else:
                    # Ignore other item types (e.g., web_link)
                    pass

            self._loaded_nodes.add(folder_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list folder items: {e}")

    def _on_select(self, event):
        cur = self.tree.focus()
        if not cur:
            self.path_label_var.set("Current selection: None")
            return

        # Compute a human-readable path by walking up the tree
        names = []
        node = cur
        while node:
            names.append(self.tree.item(node, "text"))
            node = self.tree.parent(node)
        path_str = "/" + "/".join(reversed([n.replace("[Folder] ", "") for n in names if n]))
        self.path_label_var.set(f"Current selection: {path_str}")

    def _on_double_click(self, event):
        # Double-click to expand/collapse folders
        cur = self.tree.identify_row(event.y)
        if not cur or cur.endswith("_dummy"):
            return
        # Toggle open state
        is_open = bool(self.tree.item(cur, "open"))
        self.tree.item(cur, open=not is_open)

    def _select_current(self):
        cur = self.tree.focus()
        if not cur:
            messagebox.showwarning("Select a folder", "Please select a folder node.")
            return

        # Read hidden 'type' column; treat root '0' as folder
        node_type = self.tree.set(cur, "type")
        if cur == "0":
            node_type = "folder"

        if node_type != "folder":
            messagebox.showwarning("Select a folder", "Please select a folder (not a file).")
            return

        # Build display path
        names = []
        node = cur
        while node:
            names.append(self.tree.item(node, "text"))
            node = self.tree.parent(node)
        path_str = "/" + "/".join(reversed([n.replace("[Folder] ", "") for n in names if n]))

        self.selected_folder_id = cur
        self.selected_folder_path = path_str
        self.root.destroy()

    def _cancel(self):
        self.selected_folder_id = None
        self.selected_folder_path = None
        self.root.destroy()

    def _iterate_folder_items(self, folder_id):
        # Use paging to be safe for large folders
        limit = 1000
        offset = 0
        while True:
            items = self.client.folder(folder_id=folder_id).get_items(limit=limit, offset=offset)
            batch = list(items)
            if not batch:
                break
            for it in batch:
                yield it
            if len(batch) < limit:
                break
            offset += len(batch)

    def show(self):
        self.root.mainloop()
        return self.selected_folder_id, self.selected_folder_path
