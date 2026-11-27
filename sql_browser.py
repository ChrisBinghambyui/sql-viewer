#!/usr/bin/env python3
"""
Newbie Friendly SQL Browser

Open any .sql dump (doesn't need to be in the same folder) and put together queries for results.

Needs Python 3.8+ only. Keep sqlcore.py in the same folder.
Friendly names for columns can be changed with alias_admin.py.
"""
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

from sqlcore import BLANK_OPS, OPS, Database

MAX_FILTERS = 4
MAX_DEPTH_TAGS = 8
INDENT = 22


class FilterRow:
    """One 'where [group] : [field] [is] [value]' line of the sentence."""

    def __init__(self, app, parent):
        self.app = app
        self.frame = ttk.Frame(parent)
        self.lead_lbl = ttk.Label(self.frame, text="where", width=6, anchor="e")
        self.lead_cmb = ttk.Combobox(self.frame, textvariable=app.join_var,
                                     values=["and", "or"], state="readonly", width=5)
        self.group = ttk.Combobox(self.frame, state="readonly", width=30, values=list(app.groups))
        self.colon = ttk.Label(self.frame, text=":")
        self.field = ttk.Combobox(self.frame, state="readonly", width=22)
        self.op = ttk.Combobox(self.frame, state="readonly", width=14, values=OPS)
        self.op.set("is")
        self.value = ttk.Combobox(self.frame, width=26)
        self.remove = ttk.Button(self.frame, text="x", width=3, command=lambda: app.remove_row(self))
        self.lead_lbl.grid(row=0, column=0, padx=(0, 6))
        self.lead_cmb.grid(row=0, column=0, padx=(0, 6))
        self.group.grid(row=0, column=1, padx=3)
        self.colon.grid(row=0, column=2)
        self.field.grid(row=0, column=3, padx=3)
        self.op.grid(row=0, column=4, padx=3)
        self.value.grid(row=0, column=5, padx=3)
        self.remove.grid(row=0, column=6, padx=(6, 0))
        self.group.bind("<<ComboboxSelected>>", lambda e: self.group_changed())
        self.field.bind("<<ComboboxSelected>>", self.field_changed)
        self.op.bind("<<ComboboxSelected>>", self.op_changed)
        self.value.bind("<Return>", lambda e: app.search())

    def place(self, first, removable):
        if first:
            self.lead_cmb.grid_remove()
            self.lead_lbl.grid()
        else:
            self.lead_lbl.grid_remove()
            self.lead_cmb.grid()
        if removable:
            self.remove.grid()
        else:
            self.remove.grid_remove()

    def current(self):
        return self.app.groups[self.group.get()].get(self.field.get())

    def group_changed(self, pick=None):
        names = list(self.app.groups[self.group.get()])
        self.field["values"] = names
        self.field.set(pick if pick in names else names[0])
        self.field_changed()

    def field_changed(self, _event=None):
        f = self.current()
        self.value.set("")
        self.value["values"] = self.app.db.suggestions(f.table, f.col) if f else []

    def op_changed(self, _event=None):
        if self.op.get() in BLANK_OPS:
            self.value.set("")
            self.value.state(["disabled"])
        else:
            self.value.state(["!disabled"])


class App(tk.Tk):
    def __init__(self, path=None):
        super().__init__()
        self.title("SQL Browser")
        self.geometry("1200x720")
        self.minsize(900, 560)
        self.db = None
        self.table = None
        self.fields, self.groups = [], {}
        self.rows = []
        self.result_rows = {}
        self.join_var = tk.StringVar(value="and")
        self.show_sql = tk.BooleanVar(value=False)
        self.deep_var = tk.BooleanVar(value=False)
        self._setup_style()
        self._build()
        if path:
            self.load(path)
        else:
            self.after(100, self.open_dialog)

    # ---- look -----------------------------------------------------------
    def _setup_style(self):
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            tkfont.nametofont(name).configure(size=12)
        base = tkfont.nametofont("TkDefaultFont")
        self.option_add("*TCombobox*Listbox.font", base)
        style = ttk.Style(self)
        style.configure("Treeview", rowheight=30)
        style.configure("Treeview.Heading", font=(base.actual("family"), 12, "bold"))
        style.configure("Big.TButton", padding=(14, 6))
        style.configure("Sentence.TLabel", font=(base.actual("family"), 14))
        self.fonts = {
            "title": tkfont.Font(family=base.actual("family"), size=22, weight="bold"),
            "sub": tkfont.Font(family=base.actual("family"), size=12, slant="italic"),
            "head": tkfont.Font(family=base.actual("family"), size=14, weight="bold"),
            "lab": tkfont.Font(family=base.actual("family"), size=12, weight="bold"),
            "val": base,
        }

    def _build(self):
        top = ttk.Frame(self, padding=(12, 10, 12, 4))
        top.pack(fill="x")
        ttk.Button(top, text="Open a file...", command=self.open_dialog).pack(side="left")
        self.file_lbl = ttk.Label(top, text="(no file open)", foreground="#555")
        self.file_lbl.pack(side="left", padx=10)

        box = ttk.LabelFrame(self, text=" What would you like to see? ", padding=10)
        box.pack(fill="x", padx=12, pady=6)
        line = ttk.Frame(box)
        line.pack(anchor="w")
        ttk.Label(line, text="Show me every", style="Sentence.TLabel").pack(side="left")
        self.table_combo = ttk.Combobox(line, state="readonly", width=28, font=tkfont.nametofont("TkDefaultFont"))
        self.table_combo.pack(side="left", padx=8)
        self.table_combo.bind("<<ComboboxSelected>>", self.on_table)
        self.filter_frame = ttk.Frame(box)
        self.filter_frame.pack(anchor="w", pady=(6, 2))
        btns = ttk.Frame(box)
        btns.pack(anchor="w", pady=(4, 0))
        self.add_btn = ttk.Button(btns, text="+ Add another condition", command=self.add_row)
        self.add_btn.pack(side="left")
        ttk.Button(btns, text="Search", style="Big.TButton", command=self.search).pack(side="left", padx=12)
        ttk.Button(btns, text="Clear", command=self.on_table).pack(side="left")
        ttk.Checkbutton(btns, text="Include distant connections", variable=self.deep_var,
                        command=self.on_table).pack(side="left", padx=16)
        self.bind("<Return>", lambda e: self.search())

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=12, pady=6)

        left = ttk.Frame(panes)
        self.tree = ttk.Treeview(left, show="headings", selectmode="browse")
        vs = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        hs = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        panes.add(left, weight=2)

        right = ttk.Frame(panes)
        self.text = tk.Text(right, wrap="word", padx=16, pady=12, bg="white", relief="solid",
                            borderwidth=1, cursor="arrow", font=self.fonts["val"])
        ts = ttk.Scrollbar(right, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=ts.set)
        self.text.pack(side="left", fill="both", expand=True)
        ts.pack(side="right", fill="y")
        for style, font in self.fonts.items():
            self.text.tag_configure(style, font=font)
        self.text.tag_configure("title", spacing3=2)
        self.text.tag_configure("sub", foreground="#777", spacing3=10)
        self.text.tag_configure("head", foreground="#1a5fb4", spacing1=10, spacing3=2)
        self.text.tag_configure("lab", foreground="#333")
        self.text.tag_configure("dim", foreground="#888")
        for d in range(MAX_DEPTH_TAGS):
            self.text.tag_configure("ind%d" % d, lmargin1=d * INDENT, lmargin2=d * INDENT)
        panes.add(right, weight=3)

        bottom = ttk.Frame(self, padding=(12, 0, 12, 8))
        bottom.pack(fill="x")
        self.status = ttk.Label(bottom, text="")
        self.status.pack(side="left")
        ttk.Checkbutton(bottom, text="Show the SQL", variable=self.show_sql,
                        command=self._toggle_sql).pack(side="right")
        self.sql_lbl = ttk.Label(self, text="", foreground="#666", wraplength=1100,
                                 font=("Courier", 10), padding=(12, 0, 12, 8))
        self.after(300, lambda: panes.sashpos(0, int(self.winfo_width() * 0.4)))
        self.message("Pick something to look for above, then click a result on the left.")

    # ---- loading --------------------------------------------------------
    def open_dialog(self):
        path = filedialog.askopenfilename(title="Open a SQL file",
                                          filetypes=[("SQL files", "*.sql"), ("All files", "*.*")])
        if path:
            self.load(path)
        elif self.db is None:
            self.destroy()

    def load(self, path):
        try:
            db = Database(path)
        except Exception as exc:  # any parse problem should be explained, not crash
            messagebox.showerror("Could not open that file", str(exc))
            if self.db is None:
                self.after(50, self.open_dialog)
            return
        self.db = db
        self.file_lbl.config(text=db.path.name)
        self.table_names = {db.aliases.pretty_table(n): n for n in db.table_choices()}
        self.table_combo["values"] = list(self.table_names)
        self.table_combo.current(0)
        self.on_table()

    # ---- the sentence ---------------------------------------------------
    def on_table(self, _event=None):
        self.table = self.table_names[self.table_combo.get()]
        self.fields = self.db.fields_for(self.table, 3 if self.deep_var.get() else 2)
        self.groups = {}
        for f in self.fields:
            self.groups.setdefault(f.group, {})[f.name] = f
        for r in self.rows:
            r.frame.destroy()
        self.rows = []
        self.join_var.set("and")
        self.add_row()
        self.search()

    def add_row(self):
        if len(self.rows) >= MAX_FILTERS or not self.fields:
            return
        row = FilterRow(self, self.filter_frame)
        name_col = self.db.tables[self.table].name_col
        pick = next((f for f in self.fields if not f.path and f.col == name_col), self.fields[0])
        row.group.set(pick.group)
        row.group_changed(pick.name)
        self.rows.append(row)
        self.relayout()

    def remove_row(self, row):
        row.frame.destroy()
        self.rows.remove(row)
        self.relayout()

    def relayout(self):
        for i, r in enumerate(self.rows):
            r.frame.pack_forget()
            r.frame.pack(anchor="w", pady=2)
            r.place(i == 0, len(self.rows) > 1)
        self.add_btn.state(["disabled" if len(self.rows) >= MAX_FILTERS else "!disabled"])

    # ---- searching ------------------------------------------------------
    def search(self):
        if not self.db:
            return
        conds = []
        for r in self.rows:
            op, val = r.op.get(), r.value.get().strip()
            if op not in BLANK_OPS and not val:
                continue
            conds.append((r.current(), op, val))
        try:
            sql, params, shown = self.db.build_query(self.table, conds, self.join_var.get())
            found = self.db.conn.execute(sql, params).fetchall()
        except ValueError as exc:
            self.status.config(text=str(exc), foreground="#b00020")
            return
        cols = self.db.display_cols(self.table)
        self.tree.delete(*self.tree.get_children())
        ids = ["c%d" % i for i in range(len(cols))]
        self.tree.configure(columns=ids)
        for cid, (head, _fk, _name) in zip(ids, cols):
            self.tree.heading(cid, text=head, command=lambda c=cid: self.sort_tree(c, False))
            self.tree.column(cid, width=150, minwidth=60, stretch=True)
        self.result_rows = {}
        for row in found:
            iid = str(row["__rid"])
            self.result_rows[iid] = row
            self.tree.insert("", "end", iid=iid,
                             values=[self.db.cell(row, fk, name) for _h, fk, name in cols])
        n = len(found)
        self.status.config(foreground="#333", text=("1 result" if n == 1 else "%d results" % n)
                           if n else "Nothing matched. Try a different word, or remove a condition.")
        self.sql_lbl.config(text=shown)
        if n == 0:
            self.message("Nothing matched your search.")
        elif n == 1:
            self.tree.selection_set(self.tree.get_children()[0])
        else:
            self.message("Click any result on the left to see everything about it here.")

    def sort_tree(self, col, reverse):
        def key(item):
            try:
                return (0, float(item[0]), "")
            except ValueError:
                return (1, 0, item[0].lower())
        items = [(self.tree.set(i, col), i) for i in self.tree.get_children("")]
        items.sort(key=key, reverse=reverse)
        for pos, (_v, iid) in enumerate(items):
            self.tree.move(iid, "", pos)
        self.tree.heading(col, command=lambda: self.sort_tree(col, not reverse))

    def _toggle_sql(self):
        if self.show_sql.get():
            self.sql_lbl.pack(fill="x")
        else:
            self.sql_lbl.pack_forget()

    # ---- the detail panel -----------------------------------------------
    def message(self, text):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", text, ("dim",))
        self.text.config(state="disabled")

    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        row = self.result_rows[sel[0]]
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        for chunk, style, depth in self.db.detail(self.table, row):
            self.text.insert("end", chunk, (style, "ind%d" % min(depth, MAX_DEPTH_TAGS - 1)))
        self.text.config(state="disabled")
        self.text.yview_moveto(0)


def main():
    App(sys.argv[1] if len(sys.argv) > 1 else None).mainloop()


if __name__ == "__main__":
    main()
