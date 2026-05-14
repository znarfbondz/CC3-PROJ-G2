import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "download.png")
# ── Themes ────────────────────────────────────────────────────────────────
THEMES: dict[str, dict] = {
    "light": {
        "BG":         "#f0f4f8", "SIDEBAR_BG": "#1e3a5f", "SIDEBAR_FG": "#ffffff",
        "SIDEBAR_HV": "#2d5a8e", "ACCENT":     "#2d5a8e", "SUCCESS":    "#27ae60",
        "DANGER":     "#e74c3c", "WARNING":    "#e67e22", "TEXT":       "#2c3e50",
        "CARD":       "#ffffff", "ROW_ODD":    "#f4f6fb", "ROW_EVEN":   "#ffffff",
        "ENTRY_BG":   "#ffffff", "ENTRY_FG":   "#2c3e50", "GRAY":       "#95a5a6",
    },
    "dark": {
        "BG":         "#1c1c2e", "SIDEBAR_BG": "#12122a", "SIDEBAR_FG": "#e0e0e0",
        "SIDEBAR_HV": "#252545", "ACCENT":     "#5b8dee", "SUCCESS":    "#2ecc71",
        "DANGER":     "#e74c3c", "WARNING":    "#f39c12", "TEXT":       "#dde1e7",
        "CARD":       "#252545", "ROW_ODD":    "#2a2a4e", "ROW_EVEN":   "#252545",
        "ENTRY_BG":   "#2a2a4e", "ENTRY_FG":   "#dde1e7", "GRAY":       "#8888aa",
    },
}


class Dashboard:
    # ─────────────────────────────────────────────────────────────────────
    # INIT
    # ─────────────────────────────────────────────────────────────────────
    def __init__(self, root, username=None, on_logout=None, users=None):
        self.root = root
        self.username = username
        self.on_logout = on_logout
        self.users = users if users is not None else {
            "admin": "admin",
            "user": "1234",
        }
        self.root.title("Dashboard")
        self.root.title(f"Dashboard - {self.username}" if self.username else "Dashboard")
        self.theme_name = "light"
        self.T = THEMES[self.theme_name].copy()
        self.root.geometry("1230x720")
        self.root.minsize(950, 620)

        ttk.Style().theme_use("clam")

        # ── App state ──
        self.students:     list[dict] = []
        self.courses_data: list[dict] = [
            {"code": "BSIT",   "name": "BS Information Technology",  "instructor": "Prof. Lor",     "units": 180},
            {"code": "BSCE",   "name": "BS Civil Engineering",        "instructor": "Prof. Dela Cruz", "units": 192},
            {"code": "BSEd",   "name": "BS Education",                "instructor": "Prof. Garcia",    "units": 156},
            {"code": "BSBA",   "name": "BS Business Administration",  "instructor": "Prof. Torres",    "units": 168},
            {"code": "BSEE",   "name": "BS Electrical Engineering",   "instructor": "Prof. Mendoza",   "units": 192},
        ]
        self.activity_log: list[dict] = []
        self.current_user = username if username else "admin"

        self._log(f"User '{self.current_user}' logged in")
        self._edit_idx: int | None = None
        self.form_vars:    dict[str, tk.StringVar] = {}
        self.theme_name    = "light"
        self.T             = THEMES["light"].copy()

        self.root.configure(bg=self.T["BG"])
        self._build_main()

    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────
    def _log(self, action: str):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activity_log.insert(0, {"action": action, "timestamp": ts})
        if len(self.activity_log) > 300:
            self.activity_log = self.activity_log[:300]

    @property
    def _course_codes(self) -> list[str]:
        return [c["code"] for c in self.courses_data]

    def _apply_theme(self):
        self.T = THEMES[self.theme_name].copy()
        self.root.configure(bg=self.T["BG"])

    def _style_tree(self):
        s = ttk.Style()

        s.theme_use("clam")

        s.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=34,
            background=self.T["CARD"],
            fieldbackground=self.T["CARD"],
            foreground=self.T["TEXT"],
            borderwidth=0
        )

        s.configure(
            "Treeview.Heading",
            font=("Segoe UI Semibold", 10),
            background=self.T["ACCENT"],
            foreground="#ffffff",
            padding=8,
            relief="flat"
        )

        s.map(
            "Treeview",
            background=[("selected", "#3b82f6")],
            foreground=[("selected", "#ffffff")]
        )

    def _clear(self, widget=None):
        for c in (widget or self.root).winfo_children():
            c.destroy()

    def _clear_content(self):
        self._clear(self._content)

    def _header(self, parent, title: str):
        f = tk.Frame(parent, bg=self.T["ACCENT"], height=54)
        f.pack(fill="x")
        f.pack_propagate(False)
        tk.Label(f, text=title, font=("Arial", 15, "bold"),
                 bg=self.T["ACCENT"], fg="#ffffff").pack(side="left", padx=20)

    def _card(self, parent, **kw):
        return tk.Frame(parent, bg=self.T["CARD"], **kw)

    def _btn(self, parent, text, cmd, bg=None, fg="#ffffff", **kw):
        bg = bg or self.T["ACCENT"]
        b  = tk.Button(parent, text=text, command=cmd,
                       font=("Arial", 10, "bold"), bg=bg, fg=fg,
                       relief="flat", cursor="hand2",
                       activebackground=bg, activeforeground=fg,
                       padx=12, pady=5, **kw)
        b.bind("<Enter>", lambda e: b.config(bg=self._dk(bg)))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    @staticmethod
    def _dk(hex_col: str) -> str:
        try:
            r, g, b = int(hex_col[1:3],16), int(hex_col[3:5],16), int(hex_col[5:7],16)
            return "#{:02x}{:02x}{:02x}".format(max(r-30,0), max(g-30,0), max(b-30,0))
        except Exception:
            return hex_col

    def _scrollable(self, parent):
        canvas = tk.Canvas(parent, bg=self.T["BG"], highlightthickness=0)
        vsb    = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas, bg=self.T["BG"])
        win   = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        return canvas, inner

    def _entry(self, parent, var=None, **kw):
        if var is not None:
            kw["textvariable"] = var
        return tk.Entry(parent, font=("Arial", 10),
                        relief="solid", bd=1,
                        bg=self.T["ENTRY_BG"], fg=self.T["ENTRY_FG"],
                        insertbackground=self.T["ENTRY_FG"], **kw)

    # ═════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════
    # MAIN LAYOUT
    # ═════════════════════════════════════════════════════════════════════
    def _build_main(self):
        self._clear()
        self._apply_theme()
        self._sidebar = tk.Frame(self.root, bg=self.T["SIDEBAR_BG"], width=225)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._content = tk.Frame(self.root, bg=self.T["BG"])
        self._content.pack(side="right", fill="both", expand=True)
        self._build_sidebar()
        self._show_dashboard()

    def _build_sidebar(self):
        logo = tk.Frame(self._sidebar, bg=self.T["ACCENT"], height=80)
        logo.pack(fill="x"); logo.pack_propagate(False)
        self._build_sidebar_logo(logo)
        uframe = tk.Frame(self._sidebar, bg=self.T["SIDEBAR_BG"], pady=7)
        uframe.pack(fill="x")
        tk.Label(uframe, text=f"👤  {self.current_user}",
                 font=("Arial", 10), bg=self.T["SIDEBAR_BG"],
                 fg="#aed6f1").pack()

        ttk.Separator(self._sidebar).pack(fill="x", padx=10, pady=4)

        nav = [
            ("📊   Dashboard",    self._show_dashboard),
            ("➕   Add Student",  lambda: self._show_form()),
            ("📋   View Records", self._show_records),
            ("📚   Courses",      self._show_courses),
            ("📝   Activity Log", self._show_activity_log),
            ("⚙️   Settings",     self._show_settings),
        ]
        for txt, cmd in nav:
            b = tk.Button(self._sidebar, text=txt, font=("Arial", 11),
                          bg=self.T["SIDEBAR_BG"], fg=self.T["SIDEBAR_FG"],
                          relief="flat", anchor="w", padx=18, pady=9,
                          cursor="hand2",
                          activebackground=self.T["SIDEBAR_HV"],
                          command=cmd)
            b.pack(fill="x")
            b.bind("<Enter>", lambda e, w=b: w.config(bg=self.T["SIDEBAR_HV"]))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=self.T["SIDEBAR_BG"]))

        tk.Frame(self._sidebar, bg=self.T["SIDEBAR_BG"]).pack(fill="both", expand=True)

        lo = tk.Button(self._sidebar, text="🚪   Logout",
                       font=("Arial", 11), bg=self.T["SIDEBAR_BG"],
                       fg=self.T["DANGER"], relief="flat",
                       anchor="w", padx=18, pady=9, cursor="hand2",
                       command=self._logout)
        lo.pack(fill="x", side="bottom")
        lo.bind("<Enter>", lambda e: lo.config(bg="#c0392b", fg="#ffffff"))
        lo.bind("<Leave>", lambda e: lo.config(bg=self.T["SIDEBAR_BG"], fg=self.T["DANGER"]))

    def _build_sidebar_logo(self, parent):
        if Image and ImageTk and os.path.exists(LOGO_PATH):
            try:
                raw = Image.open(LOGO_PATH).convert("RGBA")
                raw.thumbnail((64, 64), Image.LANCZOS)
                self._sidebar_logo_photo = ImageTk.PhotoImage(raw)
                tk.Label(parent, image=self._sidebar_logo_photo,
                         bg=self.T["ACCENT"]).pack(expand=True)
                return
            except Exception:
                pass

        tk.Label(parent, text="SIS", font=("Arial", 17, "bold"),
                 bg=self.T["ACCENT"], fg="#ffffff").pack(expand=True)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self._log(f"User '{self.current_user}' logged out")
            self.root.destroy()
            if self.on_logout:
                self.on_logout()

            # ═════════════════════════════════════════════════════════════════════
    # DASHBOARD
    # ═════════════════════════════════════════════════════════════════════
    def _show_dashboard(self):
        self._clear_content()
        self._header(self._content, "📊   Dashboard")
        _, inner = self._scrollable(self._content)

        regular   = sum(1 for s in self.students if s.get("status") == "Regular")
        irregular = sum(1 for s in self.students if s.get("status") == "Irregular")
        loa       = sum(1 for s in self.students if s.get("status") == "LOA")

        stat_row = tk.Frame(inner, bg=self.T["BG"])
        stat_row.pack(fill="x", padx=20, pady=(20,10))

        stats = [
            ("👥 Total\nStudents",  str(len(self.students)),                     "#3498db"),
            ("📚 Active\nCourses",  str(len(self.courses_data)),                 self.T["SUCCESS"]),
            ("✅ Regular",           str(regular),                                self.T["SUCCESS"]),
            ("⚡ Irregular",         str(irregular),                              self.T["WARNING"]),
            ("🏥 LOA",              str(loa),                                    self.T["DANGER"]),
            ("📅 Today",            datetime.date.today().strftime("%b %d %Y"), "#8e44ad"),
        ]
        for i, (lbl, val, col) in enumerate(stats):
            c = self._card(stat_row)
            c.grid(row=0, column=i, padx=6, sticky="nsew")
            stat_row.grid_columnconfigure(i, weight=1)
            tk.Label(c, text=lbl, font=("Arial", 8),
                     bg=self.T["CARD"], fg=self.T["GRAY"],
                     justify="center").pack(pady=(12,3), padx=8)
            tk.Label(c, text=val, font=("Arial", 18, "bold"),
                     bg=self.T["CARD"], fg=col).pack(pady=(0,12))

        # Recent students
        tk.Label(inner, text="Recent Students", font=("Arial", 12, "bold"),
                 bg=self.T["BG"], fg=self.T["TEXT"]).pack(
            anchor="w", padx=28, pady=(16,4))
        tf = self._card(inner)
        tf.pack(fill="x", padx=20, pady=(0,14))
        self._style_tree()
        cols = ("Student ID","Name","Course","Year","Status","Date Added")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=8)
        vsb  = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="x", padx=8, pady=8)
        for col, w in zip(cols, [110,200,80,55,80,100]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center", minwidth=50)
        tree.tag_configure("odd",  background=self.T["ROW_ODD"])
        tree.tag_configure("even", background=self.T["ROW_EVEN"])
        for i, s in enumerate(reversed(self.students[-10:])):
            tree.insert("", "end", tags=("odd" if i%2 else "even",),
                        values=(s["student_id"], s["name"], s["course"],
                                s["year_level"], s.get("status","Regular"),
                                s.get("date_added","")))

        # Recent activity
        tk.Label(inner, text="Recent Activity", font=("Arial", 12, "bold"),
                 bg=self.T["BG"], fg=self.T["TEXT"]).pack(
            anchor="w", padx=28, pady=(16,4))
        lf = self._card(inner)
        lf.pack(fill="x", padx=20, pady=(0,20))
        entries = self.activity_log[:6]
        if entries:
            for entry in entries:
                r = tk.Frame(lf, bg=self.T["CARD"]); r.pack(fill="x", padx=12, pady=3)
                tk.Label(r, text=f"🔹 {entry['action']}", font=("Arial", 9),
                         bg=self.T["CARD"], fg=self.T["TEXT"],
                         anchor="w").pack(side="left")
                tk.Label(r, text=entry["timestamp"], font=("Arial", 8),
                         bg=self.T["CARD"], fg=self.T["GRAY"]).pack(side="right")
        else:
            tk.Label(lf, text="No activity yet.", font=("Arial", 9),
                     bg=self.T["CARD"], fg=self.T["GRAY"]).pack(pady=10)

    # ═════════════════════════════════════════════════════════════════════
    # ENROLLMENT FORM  (add / edit)
    # ═════════════════════════════════════════════════════════════════════
    YEAR_LEVELS = ["1","2","3","4"]
    STATUSES    = ["Regular","Irregular","LOA"]
    OVERALL_G = [("General Weighted Average" , "GWA")]

    def _show_form(self, prefill: dict | None = None):
        self._clear_content()
        self._edit_idx = prefill.pop("_idx", None) if prefill else None
        is_edit = self._edit_idx is not None
        self._header(self._content, "✏️   Edit Student" if is_edit else "➕   Add Student")
        _, inner = self._scrollable(self._content)

        card = self._card(inner)
        card.pack(padx=40, pady=25, fill="x")
        tk.Label(card, text="Enrollment Form", font=("Arial", 13, "bold"),
                 bg=self.T["CARD"], fg=self.T["TEXT"]).pack(
            anchor="w", padx=24, pady=(18,6))
        ttk.Separator(card).pack(fill="x", padx=20)

        body = tk.Frame(card, bg=self.T["CARD"], padx=28, pady=16)
        body.pack(fill="x")

        FIELDS = [
            ("Last Name *",  "last_name",  "entry", None),
            ("First Name *", "first_name", "entry", None),
            ("Student ID *", "student_id", "entry", None),
            ("Course *",     "course",     "combo", self._course_codes),
            ("Year Level *", "year_level", "combo", self.YEAR_LEVELS),
            ("Status *",     "status",     "combo", self.STATUSES),
            ("Section",      "section",    "entry", None),
            ("Email",        "email",      "entry", None),
            ("Contact No.",  "contact",    "entry", None),
            ("Address",      "address",    "entry", None),
        ]
        self.form_vars = {}
        for i, fi in enumerate(FIELDS):
            row, col = divmod(i, 2)
            c = col * 2
            body.grid_columnconfigure(c, weight=1)
            tk.Label(body, text=fi[0], font=("Arial", 9),
                     bg=self.T["CARD"], fg=self.T["TEXT"],
                     anchor="w").grid(row=row*2, column=c,
                                      sticky="w", padx=(0,28), pady=(8,1))
            val = prefill.get(fi[1], "") if prefill else ""
            var = tk.StringVar(value=val)
            self.form_vars[fi[1]] = var
            if fi[2] == "entry":
                self._entry(body, var, width=24).grid(
                    row=row*2+1, column=c, sticky="ew", padx=(0,28))
            else:
                cb = ttk.Combobox(body, textvariable=var, values=fi[3],
                                  font=("Arial", 10), state="readonly", width=22)
                cb.grid(row=row*2+1, column=c, sticky="ew", padx=(0,28))
                if not var.get() and fi[3]:
                    cb.current(0)

        # Grades
        base = (len(FIELDS)//2 + len(FIELDS)%2) * 2
        tk.Label(body, text="General Weighted Average: (0 – 100)",
                 font=("Arial", 10, "bold"),
                 bg=self.T["CARD"], fg=self.T["ACCENT"]).grid(
            row=base, column=0, columnspan=4, sticky="w", pady=(18,4))
        ttk.Separator(body).grid(row=base+1, column=0, columnspan=4,
                                 sticky="ew", pady=(0,8))
        for i, (lbl, key) in enumerate(self.OVERALL_G):
            r, ci = divmod(i, 2); c = ci * 2
            tk.Label(body, text=lbl, font=("Arial", 9),
                     bg=self.T["CARD"], fg=self.T["TEXT"],
                     anchor="w").grid(row=base+2+r*2, column=c,
                                      sticky="w", padx=(0,28), pady=(4,1))
            v = tk.StringVar(value=prefill.get(key,"0.00") if prefill else "0.00")
            self.form_vars[key] = v
            self._entry(body, v, width=12).grid(
                row=base+2+r*2+1, column=c, sticky="w", padx=(0,28))

        # Buttons
        bf = tk.Frame(card, bg=self.T["CARD"], padx=28, pady=18)
        bf.pack(fill="x")
        lbl = "💾 Update Record" if is_edit else "💾 Save Record"
        self._btn(bf, lbl, self._save_record, bg=self.T["SUCCESS"]).pack(side="left", padx=(0,8))
        self._btn(bf, "🗑 Clear",  self._clear_form,  bg=self.T["WARNING"]).pack(side="left", padx=(0,8))
        self._btn(bf, "❌ Cancel", self._show_records, bg=self.T["DANGER"]).pack(side="left")

    def _clear_form(self):
        for k, v in self.form_vars.items():
            v.set("0.00" if k.startswith("g_") else "")

    def _save_record(self):
        try:
            ln  = self.form_vars["last_name"].get().strip()
            fn  = self.form_vars["first_name"].get().strip()
            sid = self.form_vars["student_id"].get().strip()
            crs = self.form_vars["course"].get().strip()
            yr  = self.form_vars["year_level"].get().strip()
            st  = self.form_vars["status"].get().strip()

            # Required fields
            missing = [name for name, val in [
                ("Last Name", ln), ("First Name", fn), ("Student ID", sid),
                ("Course", crs), ("Year Level", yr), ("Status", st)
            ] if not val]
            if missing:
                raise ValueError(f"Required field(s) are empty: {', '.join(missing)}")

            # Student ID format
            if not all(c.isalnum() or c in "-_" for c in sid):
                raise ValueError(
                    "Student ID may only contain letters, digits, hyphens, or underscores.")

            # Email
            email = self.form_vars["email"].get().strip()
            if email and "@" not in email:
                raise ValueError("Invalid email address — must contain '@'.")

            # Contact
            contact = self.form_vars["contact"].get().strip()
            if contact:
                clean_c = contact.replace("+","").replace("-","").replace(" ","")
                if not clean_c.isdigit():
                    raise ValueError(
                        "Contact number may only contain digits, '+', '-', and spaces.")

            # Grades
            grades = {}
            for subj, key in self.OVERALL_G:
                raw = self.form_vars[key].get().strip()
                try:
                    g = float(raw)
                    if not (0.0 <= g <= 100.0):
                        raise ValueError()
                    grades[key] = f"{g:.2f}"
                except ValueError:
                    raise ValueError(
                        f"Grade for {subj} must be a number between 0 and 100.")

            # Duplicate Student ID (hard block)
            for i, s in enumerate(self.students):
                if s["student_id"].lower() == sid.lower() and i != self._edit_idx:
                    raise ValueError(
                        f"Student ID '{sid}' is already in use by {s['name']}.")

            # Duplicate Name+Course (soft warning)
            full = f"{ln} {fn}".lower()
            for i, s in enumerate(self.students):
                existing = s["name"].lower().replace(", ", " ")
                if existing == full and s["course"] == crs and i != self._edit_idx:
                    if not messagebox.askyesno(
                            "⚠ Possible Duplicate",
                            f"'{ln}, {fn}' is already enrolled in {crs}.\n"
                            "This might be a duplicate entry.\n\n"
                            "Do you want to save anyway?"):
                        return

            rec = {
                "last_name":  ln,   "first_name": fn,
                "name":       f"{ln}, {fn}",
                "student_id": sid,  "course":     crs,
                "year_level": yr,   "status":     st,
                "section":    self.form_vars["section"].get().strip(),
                "email":      email,
                "contact":    contact,
                "address":    self.form_vars["address"].get().strip(),
                "date_added": datetime.date.today().strftime("%Y-%m-%d"),
                **grades,
            }

            if self._edit_idx is not None:
                self.students[self._edit_idx] = rec
                self._log(f"Updated student '{rec['name']}' (ID: {sid})")
                messagebox.showinfo("✅ Updated",
                                    f"Record for {rec['name']} updated successfully!")
            else:
                self.students.append(rec)
                self._log(f"Added student '{rec['name']}' (ID: {sid}) — "
                          f"{crs}, Year {yr}, {st}")
                messagebox.showinfo("✅ Saved",
                                    f"Record for {rec['name']} saved!\n"
                                    f"Date/Time: {rec['date_added']}")
            self._show_records()

        except ValueError as e:
            messagebox.showwarning("⚠ Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("❌ Unexpected Error", str(e))

    # ═════════════════════════════════════════════════════════════════════
    # RECORDS
    # ═════════════════════════════════════════════════════════════════════
    def _show_records(self, term=""):
        self._clear_content()
        self._header(self._content, "📋   Student Records")
        self._sort_col: str | None = None
        self._sort_rev: bool = False

        # Toolbar
        tb = tk.Frame(self._content, bg=self.T["BG"], pady=8)
        tb.pack(fill="x", padx=20)
        tk.Label(tb, text="🔍 Search by ID:", font=("Arial", 10),
                 bg=self.T["BG"], fg=self.T["TEXT"]).pack(side="left")
        sv = tk.StringVar(value=term)
        se = self._entry(tb, sv, width=26)
        se.pack(side="left", padx=6, ipady=4)
        se.focus()
        se.bind("<Return>", lambda e: self._show_records(sv.get()))
        self._btn(tb, "Search",   lambda: self._show_records(sv.get()),
                  bg=self.T["ACCENT"]).pack(side="left", padx=2)
        self._btn(tb, "Clear",    lambda: self._show_records(""),
                  bg=self.T["GRAY"]).pack(side="left", padx=2)
        self._btn(tb, "➕ Add New", lambda: self._show_form(),
                  bg=self.T["SUCCESS"]).pack(side="right")

        # Table
        tf = self._card(self._content)
        tf.pack(fill="both", expand=True, padx=20, pady=(4,0))
        cols = ("Student ID","Name","Course","Year","Status","Section","Date Added")
        self._tree = ttk.Treeview(tf, columns=cols, show="headings",
                                   selectmode="browse")
        vsb = ttk.Scrollbar(tf, orient="vertical",  command=self._tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)
        self._style_tree()

        for col, w in zip(cols, [105,190,75,55,80,80,105]):
            self._tree.heading(col, text=col,
                               command=lambda c=col: self._sort_tree(c))
            self._tree.column(col, width=w, anchor="center", minwidth=50)

        self._tree.tag_configure("odd",  background=self.T["ROW_ODD"])
        self._tree.tag_configure("even", background=self.T["ROW_EVEN"])

        t = term.lower()
        # Primary search: ID; secondary: name, course, section
        shown = [
            (i, s) for i, s in enumerate(self.students)
            if not t or
               t in s["student_id"].lower() or
               t in s["name"].lower() or
               t in s["course"].lower() or
               t in s.get("section","").lower()
        ]
        for row, (i, s) in enumerate(shown):
            self._tree.insert("", "end", iid=str(i),
                              tags=("odd" if row%2 else "even",),
                              values=(s["student_id"], s["name"], s["course"],
                                      s["year_level"], s.get("status","Regular"),
                                      s.get("section",""), s.get("date_added","")))

        # Action bar
        ab = tk.Frame(self._content, bg=self.T["BG"], pady=7)
        ab.pack(fill="x", padx=20)
        self._btn(ab, "👁 View Details", self._view_details,   bg=self.T["ACCENT"]).pack(side="left", padx=(0,6))
        self._btn(ab, "✏️ Update",       self._update_student, bg=self.T["WARNING"]).pack(side="left", padx=(0,6))
        self._btn(ab, "🗑️ Delete",       self._delete_student, bg=self.T["DANGER"]).pack(side="left")
        tk.Label(ab, text=f"Showing {len(shown)} / {len(self.students)} records",
                 font=("Arial", 9), bg=self.T["BG"], fg=self.T["GRAY"]).pack(side="right")
        self._tree.bind("<Double-1>", lambda e: self._view_details())

    def _sort_tree(self, col: str):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        data = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
        data.sort(reverse=self._sort_rev, key=lambda x: x[0].lower())
        for i, (_, k) in enumerate(data):
            self._tree.move(k, "", i)
            self._tree.item(k, tags=("odd" if i%2 else "even",))

    def _selected_idx(self) -> int | None:
        try:
            sel = self._tree.selection()
            if not sel:
                raise ValueError("Please select a record first.")
            return int(sel[0])
        except ValueError as e:
            messagebox.showwarning("No Selection", str(e))
            return None

    def _view_details(self):
        idx = self._selected_idx()
        if idx is None: return
        s = self.students[idx]

        win = tk.Toplevel(self.root)
        win.title("Student Details")
        win.geometry("490x580")
        win.configure(bg=self.T["CARD"])
        win.resizable(False, False)
        win.grab_set()

        hdr = tk.Frame(win, bg=self.T["ACCENT"], height=66)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="👤  Student Details", font=("Arial", 13, "bold"),
                 bg=self.T["ACCENT"], fg="#ffffff").pack(expand=True)

        body = tk.Frame(win, bg=self.T["CARD"], padx=30, pady=16)
        body.pack(fill="both", expand=True)

        status_colors = {"Regular": self.T["SUCCESS"],
                         "Irregular": self.T["WARNING"],
                         "LOA": self.T["DANGER"]}
        for lbl, val in [
            ("Name",       s["name"]),
            ("Student ID", s["student_id"]),
            ("Course",     s["course"]),
            ("Year Level", s["year_level"]),
            ("Status",     s.get("status","Regular")),
            ("Section",    s.get("section","—")),
            ("Email",      s.get("email","—")),
            ("Contact",    s.get("contact","—")),
            ("Address",    s.get("address","—")),
            ("Date Added", s.get("date_added","—")),
        ]:
            r = tk.Frame(body, bg=self.T["CARD"]); r.pack(fill="x", pady=2)
            tk.Label(r, text=lbl+":", font=("Arial", 9, "bold"),
                     bg=self.T["CARD"], fg=self.T["ACCENT"],
                     width=13, anchor="w").pack(side="left")
            col = status_colors.get(val, self.T["TEXT"]) if lbl == "Status" else self.T["TEXT"]
            tk.Label(r, text=val or "—", font=("Arial", 10),
                     bg=self.T["CARD"], fg=col).pack(side="left")

        ttk.Separator(body).pack(fill="x", pady=8)
        tk.Label(body, text="General Weighted Average",
                 font=("Arial", 10, "bold"),
                 bg=self.T["CARD"], fg=self.T["TEXT"]).pack(anchor="w", pady=(0,4))

        gf = tk.Frame(body, bg=self.T["ROW_ODD"], pady=8, padx=14)
        gf.pack(fill="x")
        for subj, key in self.OVERALL_G:
            gr = tk.Frame(gf, bg=self.T["ROW_ODD"]); gr.pack(fill="x", pady=2)
            tk.Label(gr, text=subj, font=("Arial", 9),
                     bg=self.T["ROW_ODD"], fg=self.T["TEXT"],
                     width=24, anchor="w").pack(side="left")
            val = s.get(key, "0.00")
            try:
                gcol = self.T["SUCCESS"] if float(val) >= 75 else self.T["DANGER"]
            except ValueError:
                gcol = self.T["TEXT"]
            tk.Label(gr, text=val, font=("Arial", 10, "bold"),
                     bg=self.T["ROW_ODD"], fg=gcol).pack(side="left")

        self._btn(body, "  Close  ", win.destroy,
                  bg=self.T["ACCENT"]).pack(pady=12)

    def _update_student(self):
        idx = self._selected_idx()
        if idx is None: return
        pre = dict(self.students[idx])
        pre["_idx"] = idx
        self._show_form(prefill=pre)

    def _delete_student(self):
        try:
            idx = self._selected_idx()
            if idx is None: return
            name = self.students[idx]["name"]
            sid  = self.students[idx]["student_id"]
            self.students.pop(idx)
            self._log(f"Deleted student '{name}' (ID: {sid})")
            messagebox.showinfo("Deleted", f"Record for {name} has been removed.")
            self._show_records()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete record:\n{e}")

    # ═════════════════════════════════════════════════════════════════════
    # COURSES
    # ═════════════════════════════════════════════════════════════════════
    def _show_courses(self):
        self._clear_content()
        self._header(self._content, "📚   Courses")

        tb = tk.Frame(self._content, bg=self.T["BG"], pady=8)
        tb.pack(fill="x", padx=20)
        tk.Label(tb, text=f"{len(self.courses_data)} courses registered",
                 font=("Arial", 10), bg=self.T["BG"],
                 fg=self.T["GRAY"]).pack(side="left")
        self._btn(tb, "➕ Add Course", self._add_course_dialog,
                  bg=self.T["SUCCESS"]).pack(side="right")

        tf = self._card(self._content)
        tf.pack(fill="both", expand=True, padx=20, pady=(4,0))
        cols = ("Code","Course Name","Instructor","Units","Enrolled")
        self._ctree = ttk.Treeview(tf, columns=cols, show="headings",
                                    selectmode="browse")
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._ctree.yview)
        self._ctree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._ctree.pack(fill="both", expand=True)
        self._style_tree()
        for col, w in zip(cols, [80,280,190,60,70]):
            self._ctree.heading(col, text=col)
            self._ctree.column(col, width=w, anchor="center", minwidth=50)
        self._ctree.tag_configure("odd",  background=self.T["ROW_ODD"])
        self._ctree.tag_configure("even", background=self.T["ROW_EVEN"])
        self._refresh_ctree()

        ab = tk.Frame(self._content, bg=self.T["BG"], pady=7)
        ab.pack(fill="x", padx=20)
        self._btn(ab, "✏️ Edit Course",   self._edit_course,   bg=self.T["WARNING"]).pack(side="left", padx=(0,6))
        self._btn(ab, "🗑️ Delete Course", self._delete_course, bg=self.T["DANGER"]).pack(side="left")
        self._ctree.bind("<Double-1>", lambda e: self._edit_course())

    def _refresh_ctree(self):
        self._ctree.delete(*self._ctree.get_children())
        for i, c in enumerate(self.courses_data):
            enrolled = sum(1 for s in self.students if s["course"] == c["code"])
            self._ctree.insert("", "end", iid=str(i),
                               tags=("odd" if i%2 else "even",),
                               values=(c["code"], c["name"],
                                       c["instructor"], c["units"], enrolled))

    def _course_dialog(self, title: str,
                       prefill: dict | None = None,
                       idx: int | None = None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("430x370")
        win.configure(bg=self.T["CARD"])
        win.resizable(False, False)
        win.grab_set()

        hdr = tk.Frame(win, bg=self.T["ACCENT"], height=50)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text=title, font=("Arial", 12, "bold"),
                 bg=self.T["ACCENT"], fg="#ffffff").pack(expand=True)

        body = tk.Frame(win, bg=self.T["CARD"], padx=30, pady=20)
        body.pack(fill="both", expand=True)

        cvars: dict[str, tk.StringVar] = {}
        for lbl, key in [("Course Code *","code"), ("Course Name *","name"),
                          ("Instructor *","instructor"), ("Units *","units")]:
            tk.Label(body, text=lbl, font=("Arial", 9),
                     bg=self.T["CARD"], fg=self.T["TEXT"],
                     anchor="w").pack(fill="x", pady=(8,1))
            var = tk.StringVar(value=str(prefill.get(key,"")) if prefill else "")
            cvars[key] = var
            self._entry(body, var).pack(fill="x", ipady=5)

        err_lbl = tk.Label(body, text="", font=("Arial", 9),
                           bg=self.T["CARD"], fg=self.T["DANGER"],
                           wraplength=360, justify="left")
        err_lbl.pack(anchor="w", pady=(4,0))

        def save():
            try:
                code       = cvars["code"].get().strip().upper()
                name       = cvars["name"].get().strip()
                instructor = cvars["instructor"].get().strip()
                units_raw  = cvars["units"].get().strip()
                if not code:       raise ValueError("Course Code is required.")
                if not name:       raise ValueError("Course Name is required.")
                if not instructor: raise ValueError("Instructor is required.")
                if not units_raw:  raise ValueError("Units is required.")
                if not all(c.isalnum() for c in code):
                    raise ValueError("Course Code must be alphanumeric only.")
                try:
                    units = int(units_raw)
                    if units <= 0: raise ValueError()
                except ValueError:
                    raise ValueError("Units must be a positive whole number.")
                for i2, c in enumerate(self.courses_data):
                    if c["code"] == code and i2 != idx:
                        raise ValueError(f"Course code '{code}' already exists.")
                rec = {"code": code, "name": name,
                       "instructor": instructor, "units": units}
                if idx is not None:
                    self.courses_data[idx] = rec
                    self._log(f"Updated course '{code} — {name}'")
                    messagebox.showinfo("✅ Updated", f"Course '{code}' updated!")
                else:
                    self.courses_data.append(rec)
                    self._log(f"Added course '{code} — {name}'")
                    messagebox.showinfo("✅ Added", f"Course '{code}' added!")
                win.destroy()
                self._show_courses()
            except ValueError as e:
                err_lbl.config(text=f"⚠  {e}")
            except Exception as e:
                messagebox.showerror("❌ Error", str(e))

        bf = tk.Frame(body, bg=self.T["CARD"])
        bf.pack(fill="x", pady=(10,0))
        self._btn(bf, "💾 Save",   save,        bg=self.T["SUCCESS"]).pack(side="left", padx=(0,8))
        self._btn(bf, "❌ Cancel", win.destroy, bg=self.T["DANGER"]).pack(side="left")

    def _add_course_dialog(self):
        self._course_dialog("➕ Add Course")

    def _edit_course(self):
        try:
            sel = self._ctree.selection()
            if not sel:
                raise ValueError("Please select a course to edit.")
            idx = int(sel[0])
            self._course_dialog("✏️ Edit Course",
                                prefill=self.courses_data[idx], idx=idx)
        except ValueError as e:
            messagebox.showwarning("No Selection", str(e))

    def _delete_course(self):
        try:
            sel = self._ctree.selection()
            if not sel:
                raise ValueError("Please select a course to delete.")
            idx  = int(sel[0])
            code = self.courses_data[idx]["code"]
            name = self.courses_data[idx]["name"]
            enrolled = sum(1 for s in self.students if s["course"] == code)
            msg = (f"Delete course '{code} — {name}'?"
                   + (f"\n\n⚠ {enrolled} student(s) are still enrolled in this course."
                      if enrolled else ""))
            if not messagebox.askyesno("⚠ Confirm Delete", msg):
                return
            self.courses_data.pop(idx)
            self._log(f"Deleted course '{code} — {name}'")
            messagebox.showinfo("Deleted", f"Course '{code}' removed.")
            self._show_courses()
        except ValueError as e:
            messagebox.showwarning("No Selection", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ═════════════════════════════════════════════════════════════════════
    # ACTIVITY LOG
    # ═════════════════════════════════════════════════════════════════════
    def _show_activity_log(self):
        self._clear_content()
        self._header(self._content, "📝   Activity Log")

        tb = tk.Frame(self._content, bg=self.T["BG"], pady=8)
        tb.pack(fill="x", padx=20)
        tk.Label(tb, text=f"{len(self.activity_log)} entries logged",
                 font=("Arial", 10), bg=self.T["BG"],
                 fg=self.T["GRAY"]).pack(side="left")
        self._btn(tb, "🗑 Clear Log", self._clear_log,
                  bg=self.T["DANGER"]).pack(side="right")

        tf = self._card(self._content)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        cols = ("#", "Timestamp", "Action")
        lt = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(tf, orient="vertical", command=lt.yview)
        lt.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        lt.pack(fill="both", expand=True)
        self._style_tree()
        for col, w, anchor in [
            ("#", 45, "center"),
            ("Timestamp", 170, "center"),
            ("Action", 500, "center")
        ]:
            lt.heading(col, text=col)
            lt.column(col, width=w, anchor=anchor, minwidth=30)
        lt.tag_configure("odd", background=self.T["ROW_ODD"])
        lt.tag_configure("even", background=self.T["ROW_EVEN"])
        if self.activity_log:
            for i, entry in enumerate(self.activity_log):
                lt.insert("", "end", tags=("odd" if i % 2 else "even",),
                          values=(i + 1, entry["timestamp"], entry["action"]))
        else:
            tk.Label(tf, text="No activity recorded yet.",
                     font=("Arial", 10), bg=self.T["CARD"],
                     fg=self.T["GRAY"]).pack(pady=20)

    def _clear_log(self):
        if messagebox.askyesno("Clear Log",
                               "Clear all activity log entries? This cannot be undone."):
            self.activity_log.clear()
            self._show_activity_log()

    # ═════════════════════════════════════════════════════════════════════
    # SETTINGS
    # ═════════════════════════════════════════════════════════════════════
    def _show_settings(self):
        self._clear_content()
        self._header(self._content, "⚙️   Settings")
        _, inner = self._scrollable(self._content)

        # ── System Info ──
        c2 = self._card(inner); c2.pack(padx=40, pady=24, fill="x")
        tk.Label(c2, text="Appearance", font=("Arial", 12, "bold"),
                 bg=self.T["CARD"], fg=self.T["TEXT"]).pack(
            anchor="w", padx=24, pady=(18,6))
        ttk.Separator(c2).pack(fill="x", padx=20)
        f2 = tk.Frame(c2, bg=self.T["CARD"], padx=28, pady=14); f2.pack(fill="x")
        tk.Label(f2, text="Theme:", font=("Arial", 10),
                 bg=self.T["CARD"], fg=self.T["TEXT"]).pack(side="left", padx=(0,12))
        self._theme_var = tk.StringVar(value=self.theme_name)
        for t in ("light","dark"):
            tk.Radiobutton(f2, text=t.capitalize(), variable=self._theme_var,
                           value=t, bg=self.T["CARD"], fg=self.T["TEXT"],
                           selectcolor=self.T["ACCENT"],
                           activebackground=self.T["CARD"],
                           font=("Arial", 10)).pack(side="left", padx=6)
        self._btn(f2, "Apply", self._apply_theme_setting,
                  bg=self.T["ACCENT"]).pack(side="left", padx=12)

        c4 = self._card(inner); c4.pack(padx=40, pady=(0,28), fill="x")
        tk.Label(c4, text="Change Account Credentials",
                 font=("Arial", 12, "bold"),
                 bg=self.T["CARD"], fg=self.T["TEXT"]).pack(
            anchor="w", padx=24, pady=(18,6))
        ttk.Separator(c4).pack(fill="x", padx=20)
        f4 = tk.Frame(c4, bg=self.T["CARD"], padx=28, pady=14); f4.pack(fill="x")

        tk.Label(f4, text="New Username", font=("Arial", 9),
                 bg=self.T["CARD"], fg=self.T["TEXT"],
                 anchor="w").pack(fill="x", pady=(0,1))
        self._new_user_e = self._entry(f4, None)
        self._new_user_e.pack(fill="x", ipady=5)
        self._new_user_e.insert(0, self.current_user)

        for lbl, attr in [("Current Password *", "_cpw"),
                           ("New Password (leave blank to keep)", "_npw"),
                           ("Confirm New Password",               "_confpw")]:
            tk.Label(f4, text=lbl, font=("Arial", 9),
                     bg=self.T["CARD"], fg=self.T["TEXT"],
                     anchor="w").pack(fill="x", pady=(8,1))
            e = tk.Entry(f4, show="•", font=("Arial", 10),
                         relief="solid", bd=1,
                         bg=self.T["ENTRY_BG"], fg=self.T["ENTRY_FG"],
                         insertbackground=self.T["ENTRY_FG"])
            e.pack(fill="x", ipady=5)
            setattr(self, attr, e)

        self._cred_err = tk.Label(f4, text="", font=("Arial", 9),
                                  bg=self.T["CARD"], fg=self.T["DANGER"],
                                  wraplength=400, justify="left")
        self._cred_err.pack(anchor="w", pady=(4,0))
        self._btn(f4, "Update Credentials", self._change_credentials,
                  bg=self.T["ACCENT"]).pack(anchor="w", pady=(10,0))


    def _apply_theme_setting(self):
        selected = self._theme_var.get()
        if selected == self.theme_name:
            return

        self.theme_name = selected
        self._build_main()
        self._show_settings()


    def _change_credentials(self):
        try:
            new_user = self._new_user_e.get().strip()
            cur      = self._cpw.get().strip()
            new_pw   = self._npw.get().strip()
            conf     = self._confpw.get().strip()

            if not cur:
                raise ValueError("Current password is required.")
            if not new_user:
                raise ValueError("New username cannot be blank.")
            if len(new_user) < 3:
                raise ValueError("Username must be at least 3 characters.")
            if self.users.get(self.current_user) != cur:
                raise PermissionError("Current password is incorrect.")
            if new_pw or conf:
                if len(new_pw) < 6:
                    raise ValueError("New password must be at least 6 characters.")
                if new_pw != conf:
                    raise ValueError("New passwords do not match.")
            if new_user != self.current_user and new_user in self.users:
                raise ValueError(f"Username '{new_user}' is already taken.")

            old_user = self.current_user
            old_pw   = self.users[old_user]
            final_pw = new_pw if new_pw else old_pw

            if new_user != old_user:
                del self.users[old_user]
                self._log(f"Username changed from '{old_user}' to '{new_user}'")
            self.users[new_user] = final_pw
            self.current_user = new_user
            if new_pw:
                self._log("Password updated")

            messagebox.showinfo("✅ Success", "Credentials updated successfully!")
            self._build_main()
            self._show_settings()

        except ValueError as e:
            self._cred_err.config(text=f"⚠  {e}")
        except PermissionError as e:
            self._cred_err.config(text=f"❌  {e}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Unexpected error:\n{e}")



# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    Dashboard(root)
    root.mainloop()
