#!/usr/bin/env python3
"""
Name Editor for the Friendly SQL Browser.

Select an sql file and edit any of the generated names as desired. Handles most common names (fname is read as First Name), but it's not omnipotent.
"""
import json
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from sqlcore import ALIAS_FILE, Database, load_alias_file


class Admin(tk.Tk):
    def __init__(self, path=None):
        super().__init__()
        self.title("Name Editor for the Friendly SQL Browser")
        self.geometry("980x620")
        self.data = load_alias_file()
        self.db = None
        self.entry = None

        bar = ttk.Frame(self, padding=10)
        bar.pack(fill="x")
        ttk.Button(bar, text="Open a .sql file...", command=self.open_dialog).pack(side="left")
        self.file_lbl = ttk.Label(bar, text="(no file open)")
        self.file_lbl.pack(side="left", padx=10)
        ttk.Button(bar, text="Save", command=self.save).pack(side="right")
        ttk.Button(bar, text="Add word rule...", command=self.add_word).pack(side="right", padx=8)

        ttk.Label(self, padding=(10, 0), foreground="#555",
                  text="Double-click a row to rename it. Leave the box empty to go back to the automatic name."
                  ).pack(anchor="w")

        cols = ("kind", "where", "original", "shown", "custom")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, text, w in (("kind", "Type", 70), ("where", "Table", 200), ("original", "Column in file", 220),
                           ("shown", "Shown on screen as", 230), ("custom", "Your override", 200)):
            self.tree.heading(c, text=text)
            self.tree.column(c, width=w)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", pady=10)
        self.tree.pack(fill="both", expand=True, padx=(10, 0), pady=10)
        self.tree.bind("<Double-1>", self.edit)

        self.words_lbl = ttk.Label(self, padding=10, foreground="#555", wraplength=900)
        self.words_lbl.pack(side="bottom", anchor="w")
        if path:
            self.load(path)
        else:
            self.after(100, self.open_dialog)

    def open_dialog(self):
        path = filedialog.askopenfilename(title="Open a SQL file",
                                          filetypes=[("SQL files", "*.sql"), ("All files", "*.*")])
        if path:
            self.load(path)
        elif self.db is None:
            self.destroy()

    def load(self, path):
        try:
            self.db = Database(path)
        except Exception as exc:
            messagebox.showerror("Could not open that file", str(exc))
            return
        name = self.db.path.name
        key = next((k for k in self.data if k.lower() == name.lower()), name)
        self.entry = self.data.setdefault(key, {})
        for section in ("tables", "columns", "words"):
            self.entry.setdefault(section, {})
        self.file_lbl.config(text=name)
        self.refresh()

    def refresh(self):
        self.db.aliases.set_data(self.data)
        self.tree.delete(*self.tree.get_children())
        al, cust = self.db.aliases, self.entry
        for tn, t in self.db.tables.items():
            self.tree.insert("", "end", iid="t:" + tn, tags=("table",),
                             values=("Table", tn, "", al.pretty_table(tn), cust["tables"].get(tn, "")))
            for c in t.cols:
                over = cust["columns"].get("%s.%s" % (tn, c.name)) or cust["columns"].get(c.name) or ""
                self.tree.insert("", "end", iid="c:%s.%s" % (tn, c.name),
                                 values=("Column", tn, c.name, al.pretty_col(tn, c.name), over))
        self.tree.tag_configure("table", background="#e8f0fb")
        words = ", ".join("%s = %s" % kv for kv in cust["words"].items())
        self.words_lbl.config(text="Word rules for this file: " + (words or "(none yet)"))

    def edit(self, _event):
        iid = self.tree.focus()
        if not iid or not self.entry:
            return
        kind, rest = iid.split(":", 1)
        new = simpledialog.askstring("Rename", "What should \"%s\" be called on screen?" % rest,
                                     initialvalue=self.tree.set(iid, "shown"), parent=self)
        if new is None:
            return
        new = new.strip()
        if kind == "t":
            target, keys = self.entry["tables"], [rest]
        else:
            col = rest.split(".", 1)[1]
            target, keys = self.entry["columns"], [rest, col]
            if new and messagebox.askyesno(
                    "Same name everywhere?",
                    "Use \"%s\" for every column called \"%s\" in this file?\n\n"
                    "Yes = all tables.   No = only this table." % (new, col)):
                keys = [col]
        if new:
            target[keys[0]] = new
            if kind == "c" and keys[0] == rest:
                target.pop(col, None)
        else:
            for k in keys:
                target.pop(k, None)
        self.refresh()

    def add_word(self):
        if not self.entry:
            return
        short = simpledialog.askstring("Word rule", "Short word or abbreviation (for example: qty):", parent=self)
        if not short or not short.strip():
            return
        full = simpledialog.askstring("Word rule", "What does \"%s\" mean?" % short.strip(), parent=self)
        if full and full.strip():
            self.entry["words"][short.strip().lower()] = full.strip()
            self.refresh()

    def save(self):
        for entry in self.data.values():
            for section in [s for s, v in entry.items() if not v]:
                del entry[section]
        clean = {k: v for k, v in self.data.items() if v}
        ALIAS_FILE.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
        for section in ("tables", "columns", "words"):
            if self.entry is not None:
                self.entry.setdefault(section, {})
        messagebox.showinfo("Saved", "Saved to %s" % ALIAS_FILE)


if __name__ == "__main__":
    Admin(sys.argv[1] if len(sys.argv) > 1 else None).mainloop()
