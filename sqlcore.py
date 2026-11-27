"""
sqlcore.py - the engine behind the SQL Browser.

Does all the work for the other two of interpreting, running, and modifying sql queries.
"""
import json
import re
import sqlite3
from pathlib import Path

ALIAS_FILE = Path(__file__).with_name("aliases.json")
FULL_BLOCKS = 3      # up to this many related rows get a full block; more become a short list
BULLET_LIMIT = 30    # max rows in a short list before "...and N more"
# housekeeping columns that clutter every block (hidden unless they are all a table has)
BOOKKEEPING = {"last_update", "updated_at", "modified_at", "last_modified",
               "updated_on", "date_modified"}

OPS = ["is", "is not", "contains", "starts with", "ends with",
       "is more than", "is less than", "is at least", "is at most",
       "is blank", "is not blank"]
BLANK_OPS = {"is blank", "is not blank"}

# Built-in guesses for common abbreviations. Anything here can be overridden
# in aliases.json (see alias_admin.py).
DEFAULT_WORDS = {
    "fname": "first name", "firstname": "first name", "lname": "last name",
    "lastname": "last name", "mname": "middle name", "fullname": "full name",
    "uname": "user name", "usr": "user", "pwd": "password", "pw": "password",
    "dob": "date of birth", "bday": "birthday", "addr": "address",
    "addr1": "address line 1", "addr2": "address line 2", "zip": "zip code",
    "zipcode": "zip code", "ph": "phone", "tel": "telephone",
    "qty": "quantity", "amt": "amount", "desc": "description",
    "descr": "description", "num": "number", "nbr": "number", "cnt": "count",
    "pct": "percent", "avg": "average", "min": "minimum", "max": "maximum",
    "dmg": "damage", "cat": "category", "cust": "customer",
    "emp": "employee", "dept": "department", "mgr": "manager",
    "org": "organization", "prod": "product", "img": "image",
    "lat": "latitude", "lon": "longitude", "lng": "longitude",
    "dt": "date", "ts": "timestamp", "tbl": "table", "src": "source",
    "dest": "destination", "stam": "stamina",
}
ACRONYMS = {"id": "ID", "url": "URL", "hp": "HP", "sku": "SKU", "ssn": "SSN",
            "ip": "IP", "gps": "GPS", "uuid": "UUID", "api": "API",
            "html": "HTML", "pdf": "PDF", "usa": "USA", "uk": "UK"}
SMALL_WORDS = {"of", "and", "the", "to", "in", "on", "for", "a"}


TOKEN = re.compile(
    r"""('(?:[^'\\]|\\.|'')*'|"(?:[^"\\]|\\.|"")*"|`[^`]*`)"""   # 1 quoted bit
    r"""|(--[^\n]*|/\*.*?\*/)"""                                 # 2 comment
    r"""|(;)"""                                                  # 3 end of statement
    r"""|([^'"`;/-]+|.)""",                                      # 4 anything else
    re.S)
IDENT = r'(?:[`"\[][^`"\]]+[`"\]]|\w+)'
CREATE_RE = re.compile(
    r"^CREATE\s+(?:TEMP(?:ORARY)?\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    r"(?:%s\s*\.\s*)?(%s)\s*\(" % (IDENT, IDENT), re.I | re.S)
INSERT_RE = re.compile(
    r"^(?:INSERT|REPLACE)\s+(?:(?:LOW_PRIORITY|DELAYED|HIGH_PRIORITY|IGNORE)\s+)*"
    r"(?:INTO\s+)?(?:%s\s*\.\s*)?(%s)\s*(\([^)]*\))?\s*VALUES?\s*" % (IDENT, IDENT),
    re.I | re.S)
ALTER_RE = re.compile(
    r"^ALTER\s+TABLE\s+(?:ONLY\s+)?(?:%s\s*\.\s*)?(%s)\s+(.*)$" % (IDENT, IDENT),
    re.I | re.S)
VALUE = re.compile(
    r"""\s*(?:(?P<s>'(?:[^'\\]|\\.|'')*')|(?P<d>"(?:[^"\\]|\\.|"")*")"""
    r"""|(?P<n>NULL\b)|(?P<o>\()|(?P<c>\))|(?P<m>,)|(?P<w>[^\s,()'"]+))""",
    re.I | re.S)
ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", "b": "\b", "Z": "\x1a"}


def unquote(name):
    return name.strip().strip('`"[]')


def split_statements(text):
    """Split a dump into statements, dropping comments."""
    out, buf = [], []
    for m in TOKEN.finditer(text):
        if m.group(2):
            buf.append(" ")
        elif m.group(3):
            s = "".join(buf).strip()
            if s:
                out.append(s)
            buf = []
        else:
            buf.append(m.group(0))
    s = "".join(buf).strip()
    if s:
        out.append(s)
    return out


def match_paren(s, start):
    depth = 0
    for m in TOKEN.finditer(s, start):
        if m.group(1) or m.group(2):
            continue
        for k, ch in enumerate(m.group(0)):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return m.start() + k
    return len(s)


def split_top(s):
    """Split on commas that are not inside brackets or quotes."""
    parts, buf, depth = [], [], 0
    for m in TOKEN.finditer(s):
        tok = m.group(0)
        if m.group(1) or m.group(2):
            buf.append(tok)
            continue
        for ch in tok:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
    last = "".join(buf).strip()
    if last:
        parts.append(last)
    return parts


def unescape(body):
    return re.sub(r"\\(.)|''",
                  lambda m: ESCAPES.get(m.group(1), m.group(1)) if m.group(1) is not None else "'",
                  body, flags=re.S)


def parse_rows(s):
    """Turn "(1,'a'),(2,'b')" into [[1,'a'],[2,'b']]."""
    rows, cur = [], None
    for m in VALUE.finditer(s):
        kind = m.lastgroup
        tok = m.group(kind)
        if kind == "o":
            cur = []
        elif kind == "c":
            if cur is not None:
                rows.append(cur)
            cur = None
        elif kind == "m" or cur is None:
            continue
        elif kind in ("s", "d"):
            cur.append(unescape(tok[1:-1]))
        elif kind == "n":
            cur.append(None)
        else:
            try:
                cur.append(int(tok))
            except ValueError:
                try:
                    cur.append(float(tok))
                except ValueError:
                    low = tok.lower()
                    cur.append(1 if low == "true" else 0 if low == "false" else tok)
    return rows


def affinity(sqltype):
    t = (sqltype or "").lower()
    if re.match(r"(tiny|small|medium|big)?(int|serial)|bool|bit", t):
        return "INTEGER"
    if re.match(r"real|floa|doub|dec|num|money", t):
        return "REAL"
    return "TEXT"


def strip_prefix(col, table):
    """enemy_type_name in table enemy_type -> name"""
    lc, lt = col.lower(), table.lower()
    for p in (lt + "_", lt.rstrip("s") + "_"):
        if lc.startswith(p) and len(lc) > len(p):
            return col[len(p):]
    return col


def fmt(v):
    """How a raw value looks on screen."""
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v)
    return {"true": "Yes", "false": "No"}.get(s.lower(), s)


def sql_literal(v):
    """Format a Python value as a safe SQL literal for .sql dump export."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("'", "''")
    return "'%s'" % s


class Aliases:
    """Looks up display names. Order: this file's overrides, then the '*'
    (all files) overrides, then the built-in abbreviation list."""

    def __init__(self, filename, data=None):
        self.filename = filename
        self.set_data(load_alias_file() if data is None else data)

    def set_data(self, data):
        low = {k.lower(): v for k, v in data.items()}
        self.maps = []
        for src in (low.get(self.filename.lower(), {}), low.get("*", {})):
            self.maps.append({sec: {k.lower(): v for k, v in src.get(sec, {}).items()}
                              for sec in ("tables", "columns", "words")})

    def lookup(self, section, key):
        for m in self.maps:
            v = m[section].get(key.lower())
            if v:
                return v
        return None

    def word(self, w):
        return self.lookup("words", w) or DEFAULT_WORDS.get(w)

    def title(self, phrase):
        out = []
        for i, w in enumerate(phrase.split()):
            lw = w.lower()
            if lw in ACRONYMS:
                out.append(ACRONYMS[lw])
            elif lw in SMALL_WORDS and i:
                out.append(lw)
            else:
                out.append(w.capitalize())
        return " ".join(out)

    def humanize(self, raw):
        flat = re.sub(r"[\W_]+", "", raw).lower()
        whole = self.word(flat)
        if whole:
            return self.title(whole)
        spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", raw)
        toks = [t for t in re.split(r"[\W_]+", spaced) if t]
        return self.title(" ".join(self.word(t.lower()) or t.lower() for t in toks))

    def pretty_table(self, table):
        return self.lookup("tables", table) or self.humanize(table)

    def pretty_col(self, table, col):
        v = self.lookup("columns", "%s.%s" % (table, col)) or self.lookup("columns", col)
        if v:
            return v
        base = strip_prefix(col, table)
        if base.lower() in ("id", ""):
            base = col
        return self.humanize(base)


def load_alias_file():
    try:
        return json.loads(ALIAS_FILE.read_text("utf-8"))
    except (OSError, ValueError):
        return {}


class Col:
    def __init__(self, name, sqltype, notnull=False):
        self.name = name
        self.type = sqltype
        self.affinity = affinity(sqltype)
        self.notnull = notnull


class FK:
    def __init__(self, table, cols, ref, ref_cols):
        self.table, self.cols, self.ref, self.ref_cols = table, tuple(cols), ref, tuple(ref_cols)


class Field:
    """One thing you can filter on, possibly reached through linked tables."""
    def __init__(self, group, name, path, table, col):
        self.group, self.name = group, name          # e.g. "its City > Address", "Email"
        self.label = "%s: %s" % (group, name)
        self.path, self.table, self.col = tuple(path), table, col


class Table:
    def __init__(self, name):
        self.name = name
        self.cols, self.pk, self.fks = [], [], []
        self.name_col = None
        self.last_col = None   # surname column, when name_col is a first name
        self.raw_ddl = ""      # original CREATE TABLE statement if loaded from .sql

    @property
    def fk_cols(self):
        return {c.lower() for fk in self.fks for c in fk.cols}

    @property
    def payload(self):
        """Columns that carry real information (not just ids that link things)."""
        fkc, pk = self.fk_cols, {p.lower() for p in self.pk}
        return [c for c in self.cols if c.name.lower() not in fkc
                and not (c.name.lower() in pk and c.affinity == "INTEGER")]

    @property
    def info(self):
        return [c for c in self.payload if c.name.lower() not in BOOKKEEPING]

    @property
    def is_link(self):
        return not self.info and len(self.fks) >= 2

    @property
    def plain(self):
        """Columns shown as plain facts."""
        return self.info or ([] if self.fks else list(self.cols))


class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.aliases = Aliases(self.path.name)
        self.tables, self.reverse = {}, {}
        self._labels, self._shown = {}, set()
        self.dirty = False
        self.other_statements = []  # preserved non-table DDL (indexes, views, triggers, etc.)

        is_sqlite = False
        if self.path.exists():
            header = self.path.read_bytes()[:16]
            if header.startswith(b"SQLite format 3"):
                is_sqlite = True

        if is_sqlite:
            self.is_sqlite_file = True
            self.conn = sqlite3.connect(str(self.path))
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
            self._load_from_sqlite()
        else:
            self.is_sqlite_file = False
            self.conn = sqlite3.connect(":memory:")
            self.conn.row_factory = sqlite3.Row
            raw = self.path.read_bytes()
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw.decode("latin-1")
            for st in split_statements(text):
                head = st[:12].upper()
                if head.startswith("CREATE"):
                    if re.match(r"^CREATE\s+(?:TEMP(?:ORARY)?\s+)?TABLE\b", st, re.I):
                        self._create(st)
                    else:
                        self.other_statements.append(st)
                elif head.startswith(("INSERT", "REPLACE")):
                    self._insert(st)
                elif head.startswith("ALTER"):
                    self._alter(st)
            if not self.tables:
                raise ValueError("I could not find any tables in that file.")
        self._finish()
        if not self.is_sqlite_file:
            # Enable FK enforcement after dump import is complete
            self.conn.execute("PRAGMA foreign_keys = ON")

    def _load_from_sqlite(self):
        rows = self.conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        for r in rows:
            tn = r["name"]
            t = Table(tn)
            t.raw_ddl = r["sql"] or ""
            cols = self.conn.execute('PRAGMA table_info("%s")' % tn).fetchall()
            pk_cols = []
            for c in cols:
                t.cols.append(Col(c["name"], c["type"] or "", bool(c["notnull"])))
                if c["pk"]:
                    pk_cols.append((c["pk"], c["name"]))
            pk_cols.sort()
            t.pk = [name for _, name in pk_cols]

            fk_rows = self.conn.execute('PRAGMA foreign_key_list("%s")' % tn).fetchall()
            fk_groups = {}
            for fk in fk_rows:
                fk_groups.setdefault(fk["id"], {"ref": fk["table"], "pairs": []})["pairs"].append(
                    (fk["seq"], fk["from"], fk["to"])
                )
            for info in fk_groups.values():
                info["pairs"].sort()
                cols_from = [p[1] for p in info["pairs"]]
                cols_to = [p[2] for p in info["pairs"]]
                t.fks.append(FK(tn, cols_from, info["ref"], cols_to))
            self.tables[tn] = t
        if not self.tables:
            raise ValueError("I could not find any tables in that SQLite database.")

    def _find(self, name):
        for t in self.tables:
            if t.lower() == name.lower():
                return t
        return None

    @staticmethod
    def _idents(s):
        m = re.search(r"\(([^)]*)\)", s)
        if not m:
            return []
        return [unquote(x.strip().split()[0].split("(")[0]) for x in m.group(1).split(",") if x.strip()]

    def _part(self, t, p):
        up = p.upper()
        if re.match(r"(CONSTRAINT\s+\S+\s+)?PRIMARY\s+KEY", up):
            t.pk = self._idents(p)
        elif re.search(r"\bFOREIGN\s+KEY\b", up):
            m = re.search(r"FOREIGN\s+KEY\s*(?:[`\"\w]+\s*)?\(([^)]*)\)\s*REFERENCES\s+"
                          r"((?:%s\s*\.\s*)?%s)\s*(?:\(([^)]*)\))?" % (IDENT, IDENT), p, re.I)
            if m:
                cols = [unquote(x) for x in m.group(1).split(",")]
                ref = unquote(m.group(2).split(".")[-1])
                rcols = [unquote(x) for x in m.group(3).split(",")] if m.group(3) else []
                t.fks.append(FK(t.name, cols, ref, rcols))
        elif re.match(r"(UNIQUE\s+)?(KEY|INDEX)\b|FULLTEXT|SPATIAL|CHECK|UNIQUE|CONSTRAINT|EXCLUDE|PERIOD", up):
            return
        else:
            m = re.match(r"\s*(%s)\s*(\w*)" % IDENT, p)
            if not m:
                return
            name = unquote(m.group(1))
            notnull = bool(re.search(r"\bNOT\s+NULL\b", up))
            t.cols.append(Col(name, m.group(2), notnull=notnull))
            if re.search(r"\bPRIMARY\s+KEY\b", up):
                t.pk = [name]
            r = re.search(r"\bREFERENCES\s+((?:%s\s*\.\s*)?%s)\s*(?:\(([^)]*)\))?" % (IDENT, IDENT), p, re.I)
            if r:
                rc = [unquote(x) for x in r.group(2).split(",")] if r.group(2) else []
                t.fks.append(FK(t.name, [name], unquote(r.group(1).split(".")[-1]), rc))

    def _create(self, st):
        m = CREATE_RE.match(st)
        if not m:
            return
        name = unquote(m.group(1))
        if self._find(name):
            return
        start = m.end() - 1
        end = match_paren(st, start)
        t = Table(name)
        t.raw_ddl = st
        for p in split_top(st[start + 1:end]):
            self._part(t, p)
        if not t.cols:
            return

        col_defs = []
        for c in t.cols:
            is_single_int_pk = (len(t.pk) == 1 and t.pk[0].lower() == c.name.lower() and c.affinity == "INTEGER")
            if is_single_int_pk:
                col_defs.append('"%s" INTEGER PRIMARY KEY' % c.name)
            else:
                nn = " NOT NULL" if c.notnull else ""
                col_defs.append('"%s" %s%s' % (c.name, c.affinity, nn))

        if len(t.pk) > 1 or (len(t.pk) == 1 and not any(
                c.name.lower() == t.pk[0].lower() and c.affinity == "INTEGER" for c in t.cols)):
            col_defs.append("PRIMARY KEY (%s)" % ", ".join('"%s"' % p for p in t.pk))

        ddl = 'CREATE TABLE "%s" (%s)' % (name, ", ".join(col_defs))
        try:
            self.conn.execute(ddl)
        except sqlite3.Error:
            return
        self.tables[name] = t

    def _alter(self, st):
        m = ALTER_RE.match(st)
        tn = self._find(unquote(m.group(1))) if m else None
        if not tn:
            return
        for part in split_top(m.group(2)):
            part = re.sub(r"^\s*ADD\s+(COLUMN\s+)?", "", part, flags=re.I)
            if re.search(r"FOREIGN\s+KEY|PRIMARY\s+KEY", part, re.I):
                self._part(self.tables[tn], part)

    def _insert(self, st):
        m = INSERT_RE.match(st)
        tn = self._find(unquote(m.group(1))) if m else None
        if not tn:
            return
        t = self.tables[tn]
        if m.group(2):
            cols = [unquote(x.strip().split()[0]) for x in m.group(2)[1:-1].split(",")]
        else:
            cols = [c.name for c in t.cols]
        n = len(cols)
        rows = [(r + [None] * n)[:n] for r in parse_rows(st[m.end():])]
        sql = 'INSERT INTO "%s" (%s) VALUES (%s)' % (
            tn, ",".join('"%s"' % c for c in cols), ",".join("?" * n))
        try:
            self.conn.executemany(sql, rows)
        except sqlite3.Error:
            for r in rows:
                try:
                    self.conn.execute(sql, r)
                except sqlite3.Error:
                    pass

    def _finish(self):
        self.conn.commit()
        # fill in "REFERENCES table" with no column list
        for t in self.tables.values():
            for fk in list(t.fks):
                ref = self._find(fk.ref)
                if not ref:
                    t.fks.remove(fk)
                    continue
                fk.ref = ref
                if not fk.ref_cols:
                    fk.ref_cols = tuple(self.tables[ref].pk[:len(fk.cols)])
                if len(fk.ref_cols) != len(fk.cols):
                    t.fks.remove(fk)
        # guess links nobody declared: column named like another table's key
        keys = {}
        for t in self.tables.values():
            if len(t.pk) == 1:
                k = t.pk[0].lower()
                if k == "id":
                    names = {t.name.lower() + "_id", t.name.lower().rstrip("s") + "_id"}
                else:
                    names = {k}
                keys[t.name] = (t.pk[0], names)
        for t in self.tables.values():
            have = t.fk_cols
            for c in t.cols:
                lc = c.name.lower()
                if lc in have or (len(t.pk) == 1 and lc == t.pk[0].lower()):
                    continue
                for other, (pkc, names) in keys.items():
                    if other != t.name and any(lc == n or lc.endswith("_" + n) for n in names):
                        t.fks.append(FK(t.name, [c.name], other, [pkc]))
                        break
        for t in self.tables.values():
            for fk in t.fks:
                self.reverse.setdefault(fk.ref, []).append((t.name, fk))
            texty = [c for c in t.info if c.affinity == "TEXT"]
            bases = [(strip_prefix(c.name, t.name).lower(), c) for c in texty]
            own = {t.name.lower(), t.name.lower().rstrip("s")}
            pick = next((c for b, c in bases if b in ("name", "title", "label")), None) \
                or next((c for b, c in bases if b.endswith("name")), None) \
                or next((c for b, c in bases if b in own), None)
            t.name_col = pick.name if pick else None
            if pick and pick.name.lower().endswith(("first_name", "firstname", "fname")):
                last = next((c for b, c in bases if b in ("last_name", "lastname", "lname", "surname")), None)
                t.last_col = last.name if last else None

    # ---- CRUD & Persistence ---------------------------------------------

    def _coerce_value(self, col_obj, val):
        """Convert form text into an appropriate Python/SQLite value."""
        if val is None:
            return None
        if isinstance(val, str):
            s = val.strip()
            if s == "":
                return None
            if col_obj.affinity == "INTEGER":
                if s.lower() in ("yes", "true"):
                    return 1
                if s.lower() in ("no", "false"):
                    return 0
                try:
                    return int(s)
                except ValueError:
                    try:
                        f = float(s)
                        if f.is_integer():
                            return int(f)
                    except ValueError:
                        pass
                    raise ValueError('"%s" must be a whole number for "%s".' % (s, col_obj.name))
            elif col_obj.affinity == "REAL":
                try:
                    return float(s)
                except ValueError:
                    raise ValueError('"%s" must be a number for "%s".' % (s, col_obj.name))
            return s
        return val

    def fk_choices(self, fk):
        """Return [(ref_key_value, human_label)] for populating FK dropdowns."""
        ref_col = fk.ref_cols[0]
        rows = self.conn.execute(
            'SELECT rowid AS "__rid", * FROM "%s" ORDER BY rowid' % fk.ref
        ).fetchall()
        choices = []
        for r in rows:
            val = r[ref_col]
            if val is not None:
                choices.append((val, self.label(fk.ref, r)))
        choices.sort(key=lambda item: item[1].lower())
        return choices

    def child_reference_count(self, tn, row):
        """Count how many child rows in other tables point to this row."""
        total = 0
        for ct, fk in self.reverse.get(tn, []):
            total += len(self.children(fk, row))
        return total

    def insert_row(self, tn, values):
        """Insert a new record into table `tn` from {col_name: raw_value}. Returns new rowid."""
        t = self.tables[tn]
        col_map = {c.name: c for c in t.cols}
        cols, params = [], []
        for cname, raw_val in values.items():
            if cname not in col_map:
                continue
            coerced = self._coerce_value(col_map[cname], raw_val)
            # Omit None for an integer primary key so SQLite auto-assigns it
            if coerced is None and len(t.pk) == 1 and t.pk[0] == cname and col_map[cname].affinity == "INTEGER":
                continue
            cols.append(cname)
            params.append(coerced)

        if cols:
            sql = 'INSERT INTO "%s" (%s) VALUES (%s)' % (
                tn,
                ", ".join('"%s"' % c for c in cols),
                ", ".join("?" * len(cols)),
            )
        else:
            sql = 'INSERT INTO "%s" DEFAULT VALUES' % tn

        try:
            cur = self.conn.execute(sql, params)
            self.conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("Database constraint failed: %s" % exc)
        except sqlite3.Error as exc:
            raise ValueError("Could not insert row: %s" % exc)

        self._labels.clear()
        self.dirty = True
        return cur.lastrowid

    def update_row(self, tn, rowid, values):
        """Update an existing record identified by `rowid` in table `tn`."""
        t = self.tables[tn]
        col_map = {c.name: c for c in t.cols}
        sets, params = [], []
        for cname, raw_val in values.items():
            if cname not in col_map:
                continue
            coerced = self._coerce_value(col_map[cname], raw_val)
            sets.append('"%s" = ?' % cname)
            params.append(coerced)

        if not sets:
            return
        params.append(rowid)
        sql = 'UPDATE "%s" SET %s WHERE rowid = ?' % (tn, ", ".join(sets))
        try:
            self.conn.execute(sql, params)
            self.conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("Database constraint failed: %s" % exc)
        except sqlite3.Error as exc:
            raise ValueError("Could not update row: %s" % exc)

        self._labels.clear()
        self.dirty = True

    def delete_row(self, tn, rowid):
        """Delete a record identified by `rowid` from table `tn`."""
        sql = 'DELETE FROM "%s" WHERE rowid = ?' % tn
        try:
            self.conn.execute(sql, (rowid,))
            self.conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("Cannot delete this record because other records depend on it (%s)." % exc)
        except sqlite3.Error as exc:
            raise ValueError("Could not delete row: %s" % exc)

        self._labels.clear()
        self.dirty = True

    def save(self, target_path=None):
        """Persist current database state to disk (as .sqlite/.db or .sql dump)."""
        out_path = Path(target_path) if target_path else self.path
        ext = out_path.suffix.lower()

        if ext in (".sqlite", ".sqlite3", ".db"):
            if self.is_sqlite_file and out_path.resolve() == self.path.resolve():
                self.conn.commit()
            else:
                dest = sqlite3.connect(str(out_path))
                try:
                    self.conn.backup(dest)
                    dest.commit()
                finally:
                    dest.close()
                self.path = out_path
                self.is_sqlite_file = True
                self.aliases = Aliases(self.path.name)
            self.dirty = False
            return out_path

        # Export as a .sql dump preserving original CREATE TABLE DDL where available
        lines = ["-- Exported by SQL Browser", ""]
        for tn, t in self.tables.items():
            if t.raw_ddl:
                ddl = t.raw_ddl.strip()
                if not ddl.endswith(";"):
                    ddl += ";"
                lines.append(ddl)
            else:
                col_defs = ['"%s" %s' % (c.name, c.type or c.affinity) for c in t.cols]
                if t.pk:
                    col_defs.append("PRIMARY KEY (%s)" % ", ".join('"%s"' % p for p in t.pk))
                lines.append('CREATE TABLE "%s" (\n  %s\n);' % (tn, ",\n  ".join(col_defs)))
            lines.append("")

            col_names = [c.name for c in t.cols]
            quoted_cols = ", ".join('"%s"' % c for c in col_names)
            rows = self.conn.execute(
                'SELECT %s FROM "%s" ORDER BY rowid' % (quoted_cols, tn)
            ).fetchall()
            if rows:
                for r in rows:
                    vals = ", ".join(sql_literal(r[c]) for c in col_names)
                    lines.append('INSERT INTO "%s" (%s) VALUES (%s);' % (tn, quoted_cols, vals))
                lines.append("")

        for st in self.other_statements:
            s = st.strip()
            if not s.endswith(";"):
                s += ";"
            lines.append(s)

        out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        self.path = out_path
        self.is_sqlite_file = False
        self.aliases = Aliases(self.path.name)
        self.dirty = False
        return out_path

    # ---- Querying & Formatting ------------------------------------------

    def role(self, t, fk):
        """What a link means, e.g. 'Faction' or 'Minimum Material Tier'."""
        base = re.sub(r"_?id$", "", strip_prefix(fk.cols[0], t.name), flags=re.I)
        if not base or base.lower().replace("_", "") == fk.ref.lower().replace("_", ""):
            return self.aliases.pretty_table(fk.ref)
        return self.aliases.humanize(base)

    def child_heading(self, ct, fk):
        name = self.aliases.pretty_table(ct.name)
        if sum(1 for f in ct.fks if f.ref == fk.ref) > 1:
            name += " (as %s)" % self.role(ct, fk)
        return name

    def table_choices(self):
        """Tables worth offering in the picker: main tables first."""
        names = list(self.tables)
        return sorted(names, key=lambda n: self.tables[n].is_link)

    def parent_row(self, fk, row):
        vals = [row[c] for c in fk.cols]
        if any(v is None for v in vals):
            return None
        where = " AND ".join('"%s" = ?' % c for c in fk.ref_cols)
        return self.conn.execute('SELECT rowid AS "__rid", * FROM "%s" WHERE %s LIMIT 1'
                                 % (fk.ref, where), vals).fetchone()

    def children(self, fk, row):
        vals = [row[c] for c in fk.ref_cols]
        if any(v is None for v in vals):
            return []
        where = " AND ".join('"%s" = ?' % c for c in fk.cols)
        return self.conn.execute('SELECT rowid AS "__rid", * FROM "%s" WHERE %s ORDER BY rowid'
                                 % (fk.table, where), vals).fetchall()

    def label(self, tn, row, depth=0):
        """A short human name for any row, even in tables with no name column."""
        key = (tn, row["__rid"])
        if key in self._labels:
            return self._labels[key]
        t = self.tables[tn]
        s = ""
        if t.name_col and row[t.name_col] not in (None, ""):
            s = fmt(row[t.name_col])
            if t.last_col and row[t.last_col]:
                s += " " + fmt(row[t.last_col])
        elif t.fks and depth < 3:
            parts = []
            for fk in t.fks:
                p = self.parent_row(fk, row)
                if p is not None:
                    parts.append(self.label(fk.ref, p, depth + 1))
            s = " + ".join(parts)
            if s and len(t.fks) == 1:
                s += " (%s)" % self.aliases.pretty_table(tn)
        if not s:
            vals = [fmt(row[c.name]) for c in t.info if row[c.name] not in (None, "")]
            s = vals[0] if vals else "%s %s" % (self.aliases.pretty_table(tn), fmt(row[t.cols[0].name]))
        self._labels[key] = s
        return s

    def display_cols(self, tn):
        """[(header, fk_or_None, column_name)] for the results list."""
        t = self.tables[tn]
        fkmap = {}
        for fk in t.fks:
            fkmap.setdefault(fk.cols[0].lower(), fk)
        plain = {c.name for c in t.plain}
        out = []
        for c in t.cols:
            lc = c.name.lower()
            if lc in fkmap:
                out.append((self.role(t, fkmap[lc]), fkmap[lc], c.name))
            elif lc in t.fk_cols:
                continue
            elif c.name in plain:
                out.append((self.aliases.pretty_col(tn, c.name), None, c.name))
        return out or [(self.aliases.pretty_col(tn, t.cols[0].name), None, t.cols[0].name)]

    def cell(self, row, fk, cname):
        if fk is None:
            return fmt(row[cname])
        p = self.parent_row(fk, row)
        return self.label(fk.ref, p) if p is not None else ""

    def fields_for(self, root, max_hops=2):
        """Everything the person can filter this table by, including facts
        stored in linked tables (up to max_hops links away)."""
        out, group_of, used = [], {}, {}

        def add(tn, path, steps):
            sig = tuple((id(fk), fwd) for fk, fwd in path)
            if sig not in group_of:
                if not path:
                    g = self.aliases.pretty_table(root) + " itself"
                else:
                    g = "its " + " > ".join(steps or [self.aliases.pretty_table(tn)])
                n = used.get(g, 0) + 1
                used[g] = n
                group_of[sig] = g if n == 1 else "%s (%d)" % (g, n)
            names = set()
            for c in self.tables[tn].plain:
                name = self.aliases.pretty_col(tn, c.name)
                while name in names:
                    name += " (2)"
                names.add(name)
                out.append(Field(group_of[sig], name, path, tn, c.name))

        add(root, [], [])
        queue = [(root, [], [root], [])]
        while queue and len(out) < 400:
            tn, path, seen, steps = queue.pop(0)
            if len(path) >= max_hops:
                continue
            t = self.tables[tn]
            nexts = [(fk, True, fk.ref) for fk in t.fks] + \
                    [(fk, False, c) for c, fk in self.reverse.get(tn, [])]
            for fk, fwd, nt in nexts:
                if nt in seen:
                    continue
                if fwd:
                    step = self.role(t, fk)
                else:
                    step = None if self.tables[nt].is_link else self.child_heading(self.tables[nt], fk)
                nsteps = steps + ([step] if step else [])
                npath = path + [(fk, fwd)]
                add(nt, npath, nsteps)
                queue.append((nt, npath, seen + [nt], nsteps))
        return out

    def suggestions(self, tn, col):
        rows = self.conn.execute('SELECT DISTINCT "%s" FROM "%s" WHERE "%s" IS NOT NULL '
                                 'ORDER BY 1 LIMIT 300' % (col, tn, col)).fetchall()
        vals = []
        for r in rows:
            s = fmt(r[0])
            if s and len(s) <= 60 and s not in vals:
                vals.append(s)
        return vals

    def _cond(self, alias, tn, col, op, val, params):
        c = '%s."%s"' % (alias, col)
        numeric = next(x.affinity for x in self.tables[tn].cols if x.name == col) in ("INTEGER", "REAL")
        if op in BLANK_OPS:
            e = "(%s IS NULL OR TRIM(CAST(%s AS TEXT)) = '')" % (c, c)
            return e if op == "is blank" else "NOT " + e
        if op in ("is", "is not"):
            try:
                num = float(val)
            except ValueError:
                num = None
            if numeric and num is not None:
                e = "%s = ?" % c
                params.append(num)
            else:
                variants = [val.lower()]
                if val.lower() == "yes":
                    variants += ["true", "1"]
                elif val.lower() == "no":
                    variants += ["false", "0"]
                e = "LOWER(CAST(%s AS TEXT)) IN (%s)" % (c, ",".join("?" * len(variants)))
                params.extend(variants)
            return e if op == "is" else "NOT COALESCE(%s, 0)" % e
        if op in ("contains", "starts with", "ends with"):
            esc = val.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            params.append({"contains": "%" + esc + "%", "starts with": esc + "%",
                           "ends with": "%" + esc}[op])
            return "CAST(%s AS TEXT) LIKE ? ESCAPE '\\'" % c
        try:
            num = float(val)
        except ValueError:
            raise ValueError('"%s" is not a number. Please type a number to use "%s".' % (val, op))
        params.append(num)
        sym = {"is more than": ">", "is less than": "<", "is at least": ">=", "is at most": "<="}[op]
        return "CAST(%s AS REAL) %s ?" % (c, sym)

    def build_query(self, root, conditions, joiner="and"):
        """conditions: [(Field, operator, value)] -> (sql, params, readable_sql)"""
        params, parts = [], []
        for f, op, val in conditions:
            if not f.path:
                parts.append(self._cond("t0", f.table, f.col, op, val, params))
                continue
            sub, cur = 'SELECT s0.rowid FROM "%s" s0' % root, "s0"
            for i, (fk, fwd) in enumerate(f.path, 1):
                nxt = "s%d" % i
                if fwd:
                    on = " AND ".join('%s."%s" = %s."%s"' % (cur, a, nxt, b) for a, b in zip(fk.cols, fk.ref_cols))
                    nt = fk.ref
                else:
                    on = " AND ".join('%s."%s" = %s."%s"' % (cur, b, nxt, a) for a, b in zip(fk.cols, fk.ref_cols))
                    nt = fk.table
                sub += ' JOIN "%s" %s ON %s' % (nt, nxt, on)
                cur = nxt
            parts.append("t0.rowid IN (%s WHERE %s)" % (sub, self._cond(cur, f.table, f.col, op, val, params)))
        sql = 'SELECT t0.rowid AS "__rid", t0.* FROM "%s" t0' % root
        if parts:
            sql += " WHERE " + (" %s " % joiner.upper()).join(parts)
        sql += " ORDER BY t0.rowid"
        shown = sql
        for p in params:
            shown = shown.replace("?", repr(p), 1)
        return sql, params, shown

    def brief(self, tn, row):
        """One short line describing a row: its name plus up to three facts."""
        t = self.tables[tn]
        head = self.label(tn, row) if t.name_col else ""
        skip = {t.name_col, t.last_col}
        extras = []
        for c in t.plain:
            v = fmt(row[c.name])
            if c.name not in skip and v:
                extras.append("%s: %s" % (self.aliases.pretty_col(tn, c.name), v))
            if len(extras) == 3:
                break
        if head and extras:
            return "%s (%s)" % (head, ", ".join(extras))
        return head or ", ".join(extras) or self.label(tn, row)

    def detail(self, tn, row):
        """Returns [(text, style, depth)]; style is title, sub, head, lab, val or dim.

        What gets shown, to keep it relevant:
          root row     its facts, its parents in full, its children
          parent       just its facts (its own links become one-liners)
          child        its facts (its parents become one-liners); we stop there
          link tables  (many-to-many) are passed through to the thing on the far side
        """
        segs = [(self.label(tn, row) + "\n", "title", 0),
                (self.aliases.pretty_table(tn) + "\n", "sub", 0)]
        self._shown = set()
        self._render(segs, tn, row, 0, (), None, "root")
        return segs

    def _render(self, segs, tn, row, depth, path, via, mode):
        t = self.tables[tn]
        for c in t.plain:
            segs += [(self.aliases.pretty_col(tn, c.name) + ": ", "lab", depth),
                     (fmt(row[c.name]) or "(none)", "val", depth), ("\n", "val", depth)]
        path = path + ((tn, row["__rid"]),)
        self._shown.add(path[-1])
        seen = {p[0] for p in path}
        for fk in t.fks:
            if fk is via:
                continue
            p = self.parent_row(fk, row)
            if p is None or (fk.ref, p["__rid"]) in path:
                continue
            if mode != "root" and (fk.ref, p["__rid"]) in self._shown:
                continue    # already described elsewhere on this page
            if mode == "root":
                segs.append((self.role(t, fk) + "\n", "head", depth))
                self._render(segs, fk.ref, p, depth + 1, path, fk, "parent")
            else:
                segs += [(self.role(t, fk) + ": ", "lab", depth),
                         (self.brief(fk.ref, p) + "\n", "val", depth)]
        if mode == "parent":
            return
        for ct, fk in self.reverse.get(tn, []):
            if fk is via or (ct in seen and ct != tn):
                continue
            kids = self.children(fk, row)
            if not kids:
                continue
            total, ctab = len(kids), self.tables[ct]
            others = [f for f in ctab.fks if f is not fk]
            if ctab.is_link:
                far = "parent" if mode == "child" else "target"
                if total > FULL_BLOCKS and len(others) == 1:
                    segs.append(("%s (%d)\n" % (self.role(ctab, others[0]), total), "head", depth))
                    items = []
                    for k in kids[:BULLET_LIMIT]:
                        p = self.parent_row(others[0], k)
                        if p is not None:
                            items.append(self.brief(others[0].ref, p))
                    self._bullets(segs, items, total, depth + 1)
                    continue
                if total > FULL_BLOCKS:
                    segs.append(("...%d connections in all, showing the first %d\n" % (total, FULL_BLOCKS), "dim", depth))
                for k in kids[:FULL_BLOCKS]:
                    kp = path + ((ct, k["__rid"]),)
                    for fk2 in others:
                        p = self.parent_row(fk2, k)
                        if p is None or (fk2.ref, p["__rid"]) in kp:
                            continue
                        segs.append((self.role(ctab, fk2) + "\n", "head", depth))
                        self._render(segs, fk2.ref, p, depth + 1, kp, fk2, far)
            elif mode != "child":
                name = self.child_heading(ctab, fk)
                if total > FULL_BLOCKS:
                    segs.append(("%s (%d)\n" % (name, total), "head", depth))
                    self._bullets(segs, [self.brief(ct, k) for k in kids[:BULLET_LIMIT]], total, depth + 1)
                else:
                    for i, k in enumerate(kids, 1):
                        segs.append((name + (" (%d of %d)" % (i, total) if total > 1 else "") + "\n", "head", depth))
                        self._render(segs, ct, k, depth + 1, path, fk, "child")

    @staticmethod
    def _bullets(segs, items, total, depth):
        for it in items:
            segs.append(("\u2022 " + it + "\n", "val", depth))
        if total > len(items):
            segs.append(("...and %d more\n" % (total - len(items)), "dim", depth))