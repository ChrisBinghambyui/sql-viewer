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

from sqlcore import BLANK_OPS, OPS, Database, fmt

MAX_FILTERS = 4
MAX_DEPTH_TAGS = 8
INDENT = 22


class RecordDialog(tk.Toplevel):
    """Modal dialog for inserting a new record or editing an existing one."""

    def __init__(self, parent, db, table_name, existing_row=None):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        self.table_obj = db.tables[table_name]
        self.existing_row = existing_row
        self.saved = False
        self.result_rowid = existing_row["__rid"] if existing_row is not None else None

        pretty_tbl = db.aliases.pretty_table(table_name)
        if existing_row is None:
            self.title("New %s" % pretty_tbl)
        else:
            self.title("Edit %s — %s" % (pretty_tbl, db.label(table_name, existing_row)))

        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        self.minsize(480, 260)

        # Map column names -> FK object (for single-column FKs)
        self.fk_by_col = {}
        for fk in self.table_obj.fks:
            if len(fk.cols) == 1:
                self.fk_by_col[fk.cols[0]] = fk

        self.widgets = {}      # col_name -> (kind, widget, extra_data)
        self._build_form()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_visibility()
        self.focus_set()

    def _build_form(self):
        outer = ttk.Frame(self, padding=14)
        outer.pack(fill="both", expand=True)

        # Scrollable canvas in case a table has many columns
        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        form = ttk.Frame(canvas, padding=(4, 4, 12, 4))

        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        pk_set = {p.lower() for p in self.table_obj.pk}
        first_focus = None

        for r_idx, col in enumerate(self.table_obj.cols):
            cname = col.name
            is_pk = cname.lower() in pk_set
            is_auto_int_pk = (
                is_pk and len(self.table_obj.pk) == 1 and col.affinity == "INTEGER"
            )

            label_text = self.db.aliases.pretty_col(self.table_name, cname)
            if cname in self.fk_by_col:
                label_text = self.db.role(self.table_obj, self.fk_by_col[cname])
            if col.notnull and not is_auto_int_pk:
                label_text += " *"

            lbl = ttk.Label(form, text=label_text + ":", anchor="e")
            lbl.grid(row=r_idx, column=0, sticky="e", padx=(0, 10), pady=5)

            cur_val = self.existing_row[cname] if self.existing_row is not None else None

            if cname in self.fk_by_col:
                fk = self.fk_by_col[cname]
                choices = self.db.fk_choices(fk)
                display_list = ["(None)"]
                label_to_id = {"(None)": None}
                id_to_label = {None: "(None)"}
                for raw_id, human_lbl in choices:
                    disp = "%s [#%s]" % (human_lbl, fmt(raw_id))
                    display_list.append(disp)
                    label_to_id[disp] = raw_id
                    id_to_label[raw_id] = disp

                cmb = ttk.Combobox(form, values=display_list, state="readonly", width=36)
                if cur_val in id_to_label:
                    cmb.set(id_to_label[cur_val])
                elif cur_val is not None:
                    fallback = "(Unknown #%s)" % fmt(cur_val)
                    cmb["values"] = [fallback] + display_list
                    label_to_id[fallback] = cur_val
                    cmb.set(fallback)
                else:
                    cmb.set("(None)")
                cmb.grid(row=r_idx, column=1, sticky="ew", pady=5)
                self.widgets[cname] = ("fk", cmb, label_to_id)
                if first_focus is None:
                    first_focus = cmb

            elif is_auto_int_pk:
                if self.existing_row is None:
                    ent = ttk.Entry(form, width=38)
                    ent.insert(0, "(auto-assigned)")
                    ent.state(["disabled"])
                    ent.grid(row=r_idx, column=1, sticky="ew", pady=5)
                    self.widgets[cname] = ("auto_pk", ent, None)
                else:
                    ent = ttk.Entry(form, width=38)
                    ent.insert(0, fmt(cur_val))
                    ent.state(["readonly"])
                    ent.grid(row=r_idx, column=1, sticky="ew", pady=5)
                    self.widgets[cname] = ("readonly_pk", ent, cur_val)
            else:
                ent = ttk.Entry(form, width=38)
                if cur_val is not None:
                    ent.insert(0, fmt(cur_val))
                ent.grid(row=r_idx, column=1, sticky="ew", pady=5)
                self.widgets[cname] = ("entry", ent, None)
                if first_focus is None:
                    first_focus = ent

        form.columnconfigure(1, weight=1)

        btn_bar = ttk.Frame(self, padding=(14, 6, 14, 14))
        btn_bar.pack(fill="x")
        ttk.Button(btn_bar, text="Save Record", style="Big.TButton", command=self._on_save).pack(side="right")
        ttk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side="right", padx=(0, 8))

        self.bind("<Escape>", lambda e: self.destroy())
        if first_focus is not None:
            first_focus.focus_set()

    def _collect_values(self):
        values = {}
        for cname, (kind, widget, extra) in self.widgets.items():
            if kind == "auto_pk":
                values[cname] = None
            elif kind == "readonly_pk":
                values[cname] = extra
            elif kind == "fk":
                values[cname] = extra.get(widget.get())
            else:
                values[cname] = widget.get()
        return values

    def _on_save(self):
        values = self._collect_values()
        try:
            if self.existing_row is None:
                self.result_rowid = self.db.insert_row(self.table_name, values)
            else:
                self.db.update_row(self.table_name, self.existing_row["__rid"], values)
        except ValueError as exc:
            messagebox.showerror("Cannot Save Record", str(exc), parent=self)
            return
        self.saved = True
        self.destroy()


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
        self.geometry("1220x740")
        self.minsize(920, 580)
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
        self.protocol("WM_DELETE_WINDOW", self.on_close)
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
        self.save_btn = ttk.Button(top, text="Save", command=self.save_file)
        self.save_btn.pack(side="left", padx=(6, 0))
        self.save_as_btn = ttk.Button(top, text="Save As...", command=self.save_file_as)
        self.save_as_btn.pack(side="left", padx=(6, 0))
        self.file_lbl = ttk.Label(top, text="(no file open)", foreground="#555")
        self.file_lbl.pack(side="left", padx=12)

        # Record editing toolbar on the right side of the top bar
        self.del_btn = ttk.Button(top, text="Delete", command=self.delete_record)
        self.del_btn.pack(side="right")
        self.edit_btn = ttk.Button(top, text="Edit Selected...", command=self.edit_record)
        self.edit_btn.pack(side="right", padx=(0, 6))
        self.new_btn = ttk.Button(top, text="+ New Record...", command=self.new_record)
        self.new_btn.pack(side="right", padx=(0, 6))

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
        self.tree.bind("<Double-1>", lambda e: self.edit_record())
        self.tree.bind("<Delete>", lambda e: self.delete_record())
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
        self._update_action_states()
        self.message("Pick something to look for above, then click a result on the left.")

    # ---- state & persistence --------------------------------------------
    def _update_title_and_file_label(self):
        if not self.db:
            self.file_lbl.config(text="(no file open)")
            self.title("SQL Browser")
            return
        mark = " *" if self.db.dirty else ""
        self.file_lbl.config(text=self.db.path.name + mark)
        self.title("SQL Browser — %s%s" % (self.db.path.name, mark))

    def _update_action_states(self):
        has_db = self.db is not None
        has_sel = has_db and bool(self.tree.selection())
        self.save_btn.state(["!disabled" if has_db else "disabled"])
        self.save_as_btn.state(["!disabled" if has_db else "disabled"])
        self.new_btn.state(["!disabled" if has_db else "disabled"])
        self.edit_btn.state(["!disabled" if has_sel else "disabled"])
        self.del_btn.state(["!disabled" if has_sel else "disabled"])

    def _confirm_discard_changes(self):
        if not self.db or not self.db.dirty:
            return True
        ans = messagebox.askyesnocancel(
            "Unsaved Changes",
            'Save changes to "%s" before continuing?' % self.db.path.name,
            parent=self,
        )
        if ans is None:
            return False
        if ans is True:
            return self.save_file()
        return True

    def on_close(self):
        if self._confirm_discard_changes():
            self.destroy()

    def save_file(self):
        if not self.db:
            return False
        try:
            self.db.save()
        except Exception as exc:
            messagebox.showerror("Save Failed", str(exc), parent=self)
            return False
        self._update_title_and_file_label()
        self.status.config(text='Saved to "%s".' % self.db.path.name, foreground="#1b5e20")
        return True

    def save_file_as(self):
        if not self.db:
            return False
        path = filedialog.asksaveasfilename(
            title="Save Database As",
            initialfile=self.db.path.name,
            defaultextension=self.db.path.suffix or ".sql",
            filetypes=[
                ("SQL dump", "*.sql"),
                ("SQLite database", "*.sqlite *.db"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return False
        try:
            self.db.save(path)
        except Exception as exc:
            messagebox.showerror("Save Failed", str(exc), parent=self)
            return False
        self._update_title_and_file_label()
        self.status.config(text='Saved to "%s".' % self.db.path.name, foreground="#1b5e20")
        return True

    # ---- loading --------------------------------------------------------
    def open_dialog(self):
        if not self._confirm_discard_changes():
            return
        path = filedialog.askopenfilename(
            title="Open a SQL or SQLite file",
            filetypes=[
                ("SQL & SQLite files", "*.sql *.sqlite *.sqlite3 *.db"),
                ("SQL files", "*.sql"),
                ("SQLite files", "*.sqlite *.sqlite3 *.db"),
                ("All files", "*.*"),
            ],
        )
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
        self._update_title_and_file_label()
        self.table_names = {db.aliases.pretty_table(n): n for n in db.table_choices()}
        self.table_combo["values"] = list(self.table_names)
        self.table_combo.current(0)
        self.on_table()

    # ---- CRUD actions ---------------------------------------------------
    def new_record(self):
        if not self.db or not self.table:
            return
        dlg = RecordDialog(self, self.db, self.table, existing_row=None)
        self.wait_window(dlg)
        if dlg.saved:
            self._update_title_and_file_label()
            self._refresh_filter_suggestions()
            self.search(select_rowid=dlg.result_rowid)

    def edit_record(self):
        if not self.db or not self.table:
            return
        sel = self.tree.selection()
        if not sel:
            return
        row = self.result_rows.get(sel[0])
        if row is None:
            return
        dlg = RecordDialog(self, self.db, self.table, existing_row=row)
        self.wait_window(dlg)
        if dlg.saved:
            self._update_title_and_file_label()
            self._refresh_filter_suggestions()
            self.search(select_rowid=row["__rid"])

    def delete_record(self):
        if not self.db or not self.table:
            return
        sel = self.tree.selection()
        if not sel:
            return
        row = self.result_rows.get(sel[0])
        if row is None:
            return

        label = self.db.label(self.table, row)
        pretty_tbl = self.db.aliases.pretty_table(self.table)
        ref_count = self.db.child_reference_count(self.table, row)

        msg = 'Delete %s "%s"?' % (pretty_tbl, label)
        if ref_count:
            msg += (
                "\n\nWarning: %d record(s) in other tables currently link to this item. "
                "Deleting it may fail if foreign keys are enforced or leave broken references."
                % ref_count
            )

        if not messagebox.askyesno("Confirm Delete", msg, icon="warning", parent=self):
            return

        try:
            self.db.delete_row(self.table, row["__rid"])
        except ValueError as exc:
            messagebox.showerror("Cannot Delete Record", str(exc), parent=self)
            return

        self._update_title_and_file_label()
        self._refresh_filter_suggestions()
        self.search()

    def _refresh_filter_suggestions(self):
        for r in self.rows:
            f = r.current()
            if f:
                r.value["values"] = self.db.suggestions(f.table, f.col)

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
    def search(self, select_rowid=None):
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

        target_iid = str(select_rowid) if select_rowid is not None else None
        if target_iid and target_iid in self.result_rows:
            self.tree.selection_set(target_iid)
            self.tree.see(target_iid)
        elif n == 0:
            self.message("Nothing matched your search. Click '+ New Record...' above to add one.")
        elif n == 1:
            self.tree.selection_set(self.tree.get_children()[0])
        else:
            self.message("Click any result on the left to see everything about it here.")
        self._update_action_states()

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
        self._update_action_states()
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