#ily sir lor
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, date
import random

# ─── DATA STORE ────────────────────────────────────────────────────────────────
DATA_FILE = "sis_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "students": [],
        "courses": [],
        "grades": [],
        "attendance": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── THEME ─────────────────────────────────────────────────────────────────────
COLORS = {
    "bg":        "#0F1117",
    "sidebar":   "#161B22",
    "card":      "#1C2128",
    "accent":    "#2EA043",
    "accent2":   "#388BFD",
    "danger":    "#F85149",
    "warning":   "#D29922",
    "text":      "#E6EDF3",
    "subtext":   "#8B949E",
    "border":    "#30363D",
    "hover":     "#21262D",
    "selected":  "#1F6FEB",
    "header_bg": "#13161C",
}

FONTS = {
    "title":    ("Segoe UI", 22, "bold"),
    "heading":  ("Segoe UI", 14, "bold"),
    "subhead":  ("Segoe UI", 11, "bold"),
    "body":     ("Segoe UI", 10),
    "small":    ("Segoe UI", 9),
    "mono":     ("Consolas", 10),
}

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def next_id(collection):
    if not collection:
        return 1
    return max(item["id"] for item in collection) + 1

def get_grade_letter(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"

def get_grade_color(letter):
    return {"A": COLORS["accent"], "B": COLORS["accent2"],
            "C": COLORS["warning"], "D": COLORS["warning"],
            "F": COLORS["danger"]}.get(letter, COLORS["text"])

# ─── STYLED WIDGETS ────────────────────────────────────────────────────────────
class StyledButton(tk.Button):
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        colors = {
            "primary": (COLORS["accent2"], "#ffffff"),
            "success": (COLORS["accent"],  "#ffffff"),
            "danger":  (COLORS["danger"],  "#ffffff"),
            "ghost":   (COLORS["hover"],   COLORS["text"]),
        }
        bg, fg = colors.get(style, colors["primary"])
        super().__init__(parent, text=text, command=command,
                         bg=bg, fg=fg, activebackground=bg,
                         activeforeground=fg, relief="flat", bd=0,
                         font=FONTS["subhead"], cursor="hand2",
                         padx=14, pady=7, **kwargs)
        self.bind("<Enter>", lambda e: self.config(bg=self._darken(bg)))
        self.bind("<Leave>", lambda e: self.config(bg=bg))

    def _darken(self, hex_color):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        return f"#{max(0,r-20):02x}{max(0,g-20):02x}{max(0,b-20):02x}"

class StyledEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, bg=COLORS["bg"], fg=COLORS["text"],
                         insertbackground=COLORS["text"],
                         relief="flat", bd=0, font=FONTS["body"],
                         highlightthickness=1,
                         highlightbackground=COLORS["border"],
                         highlightcolor=COLORS["accent2"], **kwargs)
        self.placeholder = placeholder
        if placeholder:
            self.insert(0, placeholder)
            self.config(fg=COLORS["subtext"])
            self.bind("<FocusIn>",  self._clear_placeholder)
            self.bind("<FocusOut>", self._restore_placeholder)

    def _clear_placeholder(self, _):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=COLORS["text"])

    def _restore_placeholder(self, _):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=COLORS["subtext"])

    def get_value(self):
        val = self.get()
        return "" if val == self.placeholder else val

class StyledCombo(ttk.Combobox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, font=FONTS["body"], **kwargs)
        self.configure(state="readonly")

# ─── MODAL DIALOG BASE ─────────────────────────────────────────────────────────
class Modal(tk.Toplevel):
    def __init__(self, parent, title, width=480, height=400):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=COLORS["card"])
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - width)  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")

    def field(self, parent, label, row, placeholder=""):
        tk.Label(parent, text=label, bg=COLORS["card"], fg=COLORS["subtext"],
                 font=FONTS["small"]).grid(row=row*2, column=0, sticky="w", pady=(10,2))
        e = StyledEntry(parent, placeholder=placeholder)
        e.grid(row=row*2+1, column=0, sticky="ew", ipady=7)
        return e

    def combo_field(self, parent, label, values, row):
        tk.Label(parent, text=label, bg=COLORS["card"], fg=COLORS["subtext"],
                 font=FONTS["small"]).grid(row=row*2, column=0, sticky="w", pady=(10,2))
        c = StyledCombo(parent, values=values)
        c.grid(row=row*2+1, column=0, sticky="ew", ipady=4)
        return c

# ─── STUDENT MODAL ─────────────────────────────────────────────────────────────
class StudentModal(Modal):
    def __init__(self, parent, student=None):
        super().__init__(parent, "Add Student" if not student else "Edit Student", 420, 460)
        self.student = student
        frame = tk.Frame(self, bg=COLORS["card"], padx=30, pady=20)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Student Information", bg=COLORS["card"],
                 fg=COLORS["text"], font=FONTS["heading"]).grid(row=0, column=0, sticky="w", pady=(0,10))

        self.fname  = self.field(frame, "First Name",    1, "e.g. Juan")
        self.lname  = self.field(frame, "Last Name",     2, "e.g. Dela Cruz")
        self.email  = self.field(frame, "Email",         3, "student@school.edu")
        self.course = self.field(frame, "Program/Course",4, "e.g. BS Computer Science")
        self.year   = self.combo_field(frame, "Year Level",
                                       ["1st Year","2nd Year","3rd Year","4th Year"], 5)

        if student:
            self.fname.delete(0,tk.END);  self.fname.insert(0, student["first_name"])
            self.lname.delete(0,tk.END);  self.lname.insert(0, student["last_name"])
            self.email.delete(0,tk.END);  self.email.insert(0, student["email"])
            self.course.delete(0,tk.END); self.course.insert(0, student["program"])
            self.year.set(student["year_level"])
        else:
            self.year.set("1st Year")

        bf = tk.Frame(frame, bg=COLORS["card"])
        bf.grid(row=12, column=0, sticky="e", pady=(20,0))
        StyledButton(bf, "Cancel", self.destroy, "ghost").pack(side="left", padx=(0,8))
        StyledButton(bf, "Save",   self._save,   "success").pack(side="left")

    def _save(self):
        fn = self.fname.get_value() if hasattr(self.fname,'get_value') else self.fname.get()
        ln = self.lname.get_value() if hasattr(self.lname,'get_value') else self.lname.get()
        em = self.email.get_value() if hasattr(self.email,'get_value') else self.email.get()
        pr = self.course.get_value() if hasattr(self.course,'get_value') else self.course.get()
        yr = self.year.get()
        if not fn or not ln:
            messagebox.showerror("Validation", "First and last name are required.", parent=self)
            return
        self.result = {"first_name": fn, "last_name": ln,
                       "email": em, "program": pr, "year_level": yr}
        self.destroy()

# ─── COURSE MODAL ──────────────────────────────────────────────────────────────
class CourseModal(Modal):
    def __init__(self, parent, course=None):
        super().__init__(parent, "Add Course" if not course else "Edit Course", 420, 340)
        frame = tk.Frame(self, bg=COLORS["card"], padx=30, pady=20)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Course Details", bg=COLORS["card"],
                 fg=COLORS["text"], font=FONTS["heading"]).grid(row=0, column=0, sticky="w", pady=(0,10))

        self.code    = self.field(frame, "Course Code", 1, "e.g. CS101")
        self.name    = self.field(frame, "Course Name", 2, "e.g. Introduction to Computing")
        self.teacher = self.field(frame, "Instructor",  3, "e.g. Prof. Santos")
        self.units   = self.combo_field(frame, "Units", ["1","2","3","4","5","6"], 4)

        if course:
            self.code.delete(0,tk.END);    self.code.insert(0, course["code"])
            self.name.delete(0,tk.END);    self.name.insert(0, course["name"])
            self.teacher.delete(0,tk.END); self.teacher.insert(0, course["instructor"])
            self.units.set(str(course["units"]))
        else:
            self.units.set("3")

        bf = tk.Frame(frame, bg=COLORS["card"])
        bf.grid(row=10, column=0, sticky="e", pady=(20,0))
        StyledButton(bf, "Cancel", self.destroy, "ghost").pack(side="left", padx=(0,8))
        StyledButton(bf, "Save",   self._save,   "success").pack(side="left")

    def _save(self):
        def gv(w): return w.get_value() if hasattr(w,'get_value') else w.get()
        code = gv(self.code); name = gv(self.name); instr = gv(self.teacher)
        if not code or not name:
            messagebox.showerror("Validation", "Code and name are required.", parent=self)
            return
        self.result = {"code": code, "name": name,
                       "instructor": instr, "units": int(self.units.get())}
        self.destroy()

# ─── GRADE MODAL ───────────────────────────────────────────────────────────────
class GradeModal(Modal):
    def __init__(self, parent, students, courses, grade=None):
        super().__init__(parent, "Record Grade", 420, 360)
        self.students = students
        self.courses  = courses
        frame = tk.Frame(self, bg=COLORS["card"], padx=30, pady=20)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Grade Entry", bg=COLORS["card"],
                 fg=COLORS["text"], font=FONTS["heading"]).grid(row=0, column=0, sticky="w", pady=(0,10))

        snames = [f"{s['first_name']} {s['last_name']} (ID:{s['id']})" for s in students]
        cnames = [f"{c['code']} - {c['name']}" for c in courses]

        self.student_cb = self.combo_field(frame, "Student", snames, 1)
        self.course_cb  = self.combo_field(frame, "Course",  cnames, 2)
        self.score_e    = self.field(frame, "Score (0-100)", 3, "e.g. 88")
        self.sem_cb     = self.combo_field(frame, "Semester",
                                           ["1st Sem AY 2024-25","2nd Sem AY 2024-25",
                                            "1st Sem AY 2025-26","2nd Sem AY 2025-26"], 4)
        self.sem_cb.set("1st Sem AY 2025-26")

        bf = tk.Frame(frame, bg=COLORS["card"])
        bf.grid(row=10, column=0, sticky="e", pady=(20,0))
        StyledButton(bf, "Cancel", self.destroy, "ghost").pack(side="left", padx=(0,8))
        StyledButton(bf, "Save",   self._save,   "success").pack(side="left")

    def _save(self):
        si = self.student_cb.current()
        ci = self.course_cb.current()
        def gv(w): return w.get_value() if hasattr(w,'get_value') else w.get()
        score_str = gv(self.score_e)
        if si < 0 or ci < 0 or not score_str:
            messagebox.showerror("Validation", "All fields are required.", parent=self)
            return
        try:
            score = float(score_str)
            if not (0 <= score <= 100): raise ValueError
        except ValueError:
            messagebox.showerror("Validation", "Score must be 0–100.", parent=self)
            return
        self.result = {
            "student_id": self.students[si]["id"],
            "course_id":  self.courses[ci]["id"],
            "score": score,
            "semester": self.sem_cb.get(),
            "date": date.today().isoformat()
        }
        self.destroy()

# ─── ATTENDANCE MODAL ──────────────────────────────────────────────────────────
class AttendanceModal(Modal):
    def __init__(self, parent, students, courses):
        super().__init__(parent, "Record Attendance", 460, 420)
        self.students = students
        self.courses  = courses
        frame = tk.Frame(self, bg=COLORS["card"], padx=30, pady=20)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Attendance Entry", bg=COLORS["card"],
                 fg=COLORS["text"], font=FONTS["heading"]).grid(row=0, column=0, sticky="w", pady=(0,10))

        snames = [f"{s['first_name']} {s['last_name']} (ID:{s['id']})" for s in students]
        cnames = [f"{c['code']} - {c['name']}" for c in courses]

        self.student_cb = self.combo_field(frame, "Student", snames, 1)
        self.course_cb  = self.combo_field(frame, "Course",  cnames, 2)
        self.date_e     = self.field(frame, "Date (YYYY-MM-DD)", 3,
                                     date.today().isoformat())
        self.status_cb  = self.combo_field(frame, "Status",
                                           ["Present","Absent","Late","Excused"], 4)
        self.status_cb.set("Present")

        bf = tk.Frame(frame, bg=COLORS["card"])
        bf.grid(row=10, column=0, sticky="e", pady=(20,0))
        StyledButton(bf, "Cancel", self.destroy, "ghost").pack(side="left", padx=(0,8))
        StyledButton(bf, "Save",   self._save,   "success").pack(side="left")

    def _save(self):
        si = self.student_cb.current()
        ci = self.course_cb.current()
        def gv(w): return w.get_value() if hasattr(w,'get_value') else w.get()
        dt = gv(self.date_e) or date.today().isoformat()
        if si < 0 or ci < 0:
            messagebox.showerror("Validation", "Student and course are required.", parent=self)
            return
        self.result = {
            "student_id": self.students[si]["id"],
            "course_id":  self.courses[ci]["id"],
            "date": dt,
            "status": self.status_cb.get()
        }
        self.destroy()

# ─── MAIN APPLICATION ──────────────────────────────────────────────────────────
class SISApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Information System")
        self.geometry("1200x720")
        self.minsize(1000, 650)
        self.configure(bg=COLORS["bg"])
        self.data = load_data()
        self._seed_demo_data()
        self._build_ui()

    def _seed_demo_data(self):
        if not self.data["students"]:
            demo_students = [
                {"id":1,"first_name":"Maria","last_name":"Santos","email":"msantos@sis.edu",
                 "program":"BS Computer Science","year_level":"3rd Year"},
                {"id":2,"first_name":"Juan","last_name":"Dela Cruz","email":"jdelacruz@sis.edu",
                 "program":"BS Information Technology","year_level":"2nd Year"},
                {"id":3,"first_name":"Ana","last_name":"Reyes","email":"areyes@sis.edu",
                 "program":"BS Computer Science","year_level":"1st Year"},
            ]
            demo_courses = [
                {"id":1,"code":"CS101","name":"Introduction to Computing","instructor":"Prof. Garcia","units":3},
                {"id":2,"code":"CS201","name":"Data Structures","instructor":"Prof. Lim","units":3},
                {"id":3,"code":"MATH10","name":"College Algebra","instructor":"Prof. Cruz","units":4},
            ]
            demo_grades = [
                {"id":1,"student_id":1,"course_id":1,"score":92,"semester":"1st Sem AY 2025-26","date":"2025-10-01"},
                {"id":2,"student_id":1,"course_id":2,"score":85,"semester":"1st Sem AY 2025-26","date":"2025-10-01"},
                {"id":3,"student_id":2,"course_id":1,"score":78,"semester":"1st Sem AY 2025-26","date":"2025-10-01"},
                {"id":4,"student_id":3,"course_id":3,"score":65,"semester":"1st Sem AY 2025-26","date":"2025-10-01"},
            ]
            demo_att = []
            statuses = ["Present","Present","Present","Late","Absent"]
            for s in demo_students:
                for c in demo_courses[:2]:
                    for day in range(1, 6):
                        demo_att.append({"id": len(demo_att)+1,
                                          "student_id": s["id"], "course_id": c["id"],
                                          "date": f"2025-10-0{day}",
                                          "status": random.choice(statuses)})
            self.data = {"students": demo_students, "courses": demo_courses,
                         "grades": demo_grades, "attendance": demo_att}
            save_data(self.data)

    # ── UI SKELETON ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["header_bg"], height=56)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🎓  Student Information System BY Group 3", bg=COLORS["header_bg"],
                 fg=COLORS["text"], font=FONTS["title"]).pack(side="left", padx=24)
        tk.Label(hdr, text=f"v1.0  •  {date.today().strftime('%B %d, %Y')}",
                 bg=COLORS["header_bg"], fg=COLORS["subtext"],
                 font=FONTS["small"]).pack(side="right", padx=24)

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(body, bg=COLORS["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.current_page = tk.StringVar(value="dashboard")
        nav_items = [
            ("📊", "Dashboard",   "dashboard"),
            ("👤", "Students",    "students"),
            ("📚", "Courses",     "courses"),
            ("📝", "Grades",      "grades"),
            ("📅", "Attendance",  "attendance"),
        ]
        tk.Label(self.sidebar, text="NAVIGATION", bg=COLORS["sidebar"],
                 fg=COLORS["subtext"], font=FONTS["small"]).pack(pady=(20,8), padx=16, anchor="w")

        self.nav_btns = {}
        for icon, label, page in nav_items:
            btn = self._nav_btn(icon, label, page)
            self.nav_btns[page] = btn

        # Main content
        self.content = tk.Frame(body, bg=COLORS["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {}
        self._show_page("dashboard")

    def _nav_btn(self, icon, label, page):
        f = tk.Frame(self.sidebar, bg=COLORS["sidebar"], cursor="hand2")
        f.pack(fill="x", padx=8, pady=2)
        lbl = tk.Label(f, text=f"  {icon}  {label}", bg=COLORS["sidebar"],
                       fg=COLORS["text"], font=FONTS["body"], anchor="w",
                       padx=8, pady=10)
        lbl.pack(fill="x")

        def click(e=None):
            self._show_page(page)
        def enter(e): f.config(bg=COLORS["hover"]); lbl.config(bg=COLORS["hover"])
        def leave(e):
            if self.current_page.get() != page:
                f.config(bg=COLORS["sidebar"]); lbl.config(bg=COLORS["sidebar"])

        for w in (f, lbl):
            w.bind("<Button-1>", click)
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
        return (f, lbl)

    def _set_nav_active(self, page):
        for pg, (f, lbl) in self.nav_btns.items():
            if pg == page:
                f.config(bg=COLORS["selected"]); lbl.config(bg=COLORS["selected"])
            else:
                f.config(bg=COLORS["sidebar"]); lbl.config(bg=COLORS["sidebar"])

    def _show_page(self, page):
        self.current_page.set(page)
        self._set_nav_active(page)
        for w in self.content.winfo_children():
            w.destroy()
        getattr(self, f"_page_{page}")()

    # ── DASHBOARD ────────────────────────────────────────────────────────────
    def _page_dashboard(self):
        p = tk.Frame(self.content, bg=COLORS["bg"], padx=30, pady=24)
        p.pack(fill="both", expand=True)

        tk.Label(p, text="Dashboard", bg=COLORS["bg"],
                 fg=COLORS["text"], font=FONTS["title"]).pack(anchor="w")
        tk.Label(p, text="Overview of your institution", bg=COLORS["bg"],
                 fg=COLORS["subtext"], font=FONTS["body"]).pack(anchor="w", pady=(2,20))

        # Stat cards
        stats_frame = tk.Frame(p, bg=COLORS["bg"])
        stats_frame.pack(fill="x")

        def att_rate():
            if not self.data["attendance"]: return 0
            present = sum(1 for a in self.data["attendance"] if a["status"]=="Present")
            return round(present/len(self.data["attendance"])*100)

        def avg_grade():
            if not self.data["grades"]: return 0
            return round(sum(g["score"] for g in self.data["grades"])/len(self.data["grades"]),1)

        cards = [
            ("👤", "Students",       str(len(self.data["students"])), COLORS["accent2"]),
            ("📚", "Courses",        str(len(self.data["courses"])),  COLORS["accent"]),
            ("📝", "Grade Records",  str(len(self.data["grades"])),   COLORS["warning"]),
            ("📅", "Attendance Rate",f"{att_rate()}%",                COLORS["accent"]),
            ("🎯", "Average Grade",  f"{avg_grade()}",                COLORS["accent2"]),
        ]
        for i, (icon, title, val, color) in enumerate(cards):
            c = tk.Frame(stats_frame, bg=COLORS["card"], padx=20, pady=16,
                         highlightthickness=1, highlightbackground=COLORS["border"])
            c.grid(row=0, column=i, padx=(0,12), sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)
            tk.Label(c, text=icon, bg=COLORS["card"], fg=color, font=("Segoe UI",22)).pack(anchor="w")
            tk.Label(c, text=val, bg=COLORS["card"], fg=color,
                     font=("Segoe UI",26,"bold")).pack(anchor="w")
            tk.Label(c, text=title, bg=COLORS["card"], fg=COLORS["subtext"],
                     font=FONTS["small"]).pack(anchor="w")

        # Recent activity
        tk.Label(p, text="Recent Students", bg=COLORS["bg"],
                 fg=COLORS["text"], font=FONTS["heading"]).pack(anchor="w", pady=(28,10))
        self._mini_table(p, ["Name","Program","Year","Email"],
                         [[f"{s['first_name']} {s['last_name']}",s["program"],
                           s["year_level"],s["email"]]
                          for s in self.data["students"][-5:]])

        tk.Label(p, text="Recent Grades", bg=COLORS["bg"],
                 fg=COLORS["text"], font=FONTS["heading"]).pack(anchor="w", pady=(20,10))
        rows = []
        for g in self.data["grades"][-5:]:
            st = next((s for s in self.data["students"] if s["id"]==g["student_id"]), None)
            co = next((c for c in self.data["courses"]  if c["id"]==g["course_id"]),  None)
            if st and co:
                ltr = get_grade_letter(g["score"])
                rows.append([f"{st['first_name']} {st['last_name']}",
                              co["code"], str(g["score"]), ltr, g["semester"]])
        self._mini_table(p, ["Student","Course","Score","Grade","Semester"], rows)

    def _mini_table(self, parent, headers, rows):
        frame = tk.Frame(parent, bg=COLORS["card"],
                         highlightthickness=1, highlightbackground=COLORS["border"])
        frame.pack(fill="x")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Mini.Treeview", background=COLORS["card"],
                        foreground=COLORS["text"], fieldbackground=COLORS["card"],
                        rowheight=30, font=FONTS["body"], borderwidth=0)
        style.configure("Mini.Treeview.Heading", background=COLORS["hover"],
                        foreground=COLORS["subtext"], font=FONTS["small"], relief="flat")
        style.map("Mini.Treeview", background=[("selected", COLORS["selected"])])
        tv = ttk.Treeview(frame, columns=headers, show="headings",
                          style="Mini.Treeview", height=min(len(rows),5))
        for h in headers:
            tv.heading(h, text=h)
            tv.column(h, width=150, anchor="w")
        for row in rows:
            tv.insert("", "end", values=row)
        tv.pack(fill="x")

    # ── STUDENTS PAGE ─────────────────────────────────────────────────────────
    def _page_students(self):
        p = tk.Frame(self.content, bg=COLORS["bg"], padx=30, pady=24)
        p.pack(fill="both", expand=True)

        hf = tk.Frame(p, bg=COLORS["bg"])
        hf.pack(fill="x", pady=(0,16))
        tk.Label(hf, text="Students", bg=COLORS["bg"],
                 fg=COLORS["text"], font=FONTS["title"]).pack(side="left")
        StyledButton(hf, "+ Add Student", self._add_student, "success").pack(side="right")

        # Search
        sf = tk.Frame(p, bg=COLORS["bg"])
        sf.pack(fill="x", pady=(0,10))
        self.student_search = StyledEntry(sf, placeholder="Search students...")
        self.student_search.pack(side="left", ipady=7, ipadx=10)
        self.student_search.bind("<KeyRelease>", lambda e: self._refresh_students())

        # Table
        style = ttk.Style()
        style.configure("Main.Treeview", background=COLORS["card"],
                        foreground=COLORS["text"], fieldbackground=COLORS["card"],
                        rowheight=34, font=FONTS["body"], borderwidth=0)
        style.configure("Main.Treeview.Heading", background=COLORS["hover"],
                        foreground=COLORS["subtext"], font=FONTS["subhead"], relief="flat")
        style.map("Main.Treeview", background=[("selected", COLORS["selected"])])

        cols = ["ID","First Name","Last Name","Program","Year","Email"]
        tf = tk.Frame(p, bg=COLORS["card"],
                      highlightthickness=1, highlightbackground=COLORS["border"])
        tf.pack(fill="both", expand=True)
        self.stv = ttk.Treeview(tf, columns=cols, show="headings", style="Main.Treeview")
        widths = [50,120,120,220,100,200]
        for col, w in zip(cols, widths):
            self.stv.heading(col, text=col)
            self.stv.column(col, width=w, anchor="w")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.stv.yview)
        self.stv.configure(yscrollcommand=sb.set)
        self.stv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Actions
        af = tk.Frame(p, bg=COLORS["bg"])
        af.pack(fill="x", pady=(10,0))
        StyledButton(af, "✏ Edit",   self._edit_student,   "primary").pack(side="left", padx=(0,8))
        StyledButton(af, "🗑 Delete", self._delete_student, "danger").pack(side="left")

        self._refresh_students()

    def _refresh_students(self):
        q = ""
        if hasattr(self, "student_search"):
            v = self.student_search.get()
            if v != "Search students...": q = v.lower()
        self.stv.delete(*self.stv.get_children())
        for s in self.data["students"]:
            if q and q not in f"{s['first_name']} {s['last_name']} {s['email']} {s['program']}".lower():
                continue
            self.stv.insert("", "end", iid=str(s["id"]),
                            values=[s["id"],s["first_name"],s["last_name"],
                                    s["program"],s["year_level"],s["email"]])

    def _add_student(self):
        m = StudentModal(self)
        self.wait_window(m)
        if m.result:
            m.result["id"] = next_id(self.data["students"])
            self.data["students"].append(m.result)
            save_data(self.data)
            self._refresh_students()

    def _edit_student(self):
        sel = self.stv.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a student first."); return
        sid = int(sel[0])
        student = next((s for s in self.data["students"] if s["id"]==sid), None)
        m = StudentModal(self, student)
        self.wait_window(m)
        if m.result:
            student.update(m.result)
            save_data(self.data)
            self._refresh_students()

    def _delete_student(self):
        sel = self.stv.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a student first."); return
        sid = int(sel[0])
        if messagebox.askyesno("Confirm", "Delete this student? This will also remove their grades and attendance."):
            self.data["students"]  = [s for s in self.data["students"]  if s["id"]!=sid]
            self.data["grades"]    = [g for g in self.data["grades"]    if g["student_id"]!=sid]
            self.data["attendance"]= [a for a in self.data["attendance"] if a["student_id"]!=sid]
            save_data(self.data)
            self._refresh_students()

    # ── COURSES PAGE ──────────────────────────────────────────────────────────
    def _page_courses(self):
        p = tk.Frame(self.content, bg=COLORS["bg"], padx=30, pady=24)
        p.pack(fill="both", expand=True)

        hf = tk.Frame(p, bg=COLORS["bg"])
        hf.pack(fill="x", pady=(0,16))
        tk.Label(hf, text="Courses", bg=COLORS["bg"],
                 fg=COLORS["text"], font=FONTS["title"]).pack(side="left")
        StyledButton(hf, "+ Add Course", self._add_course, "success").pack(side="right")

        style = ttk.Style()
        style.configure("Main.Treeview", background=COLORS["card"],
                        foreground=COLORS["text"], fieldbackground=COLORS["card"],
                        rowheight=34, font=FONTS["body"])
        style.configure("Main.Treeview.Heading", background=COLORS["hover"],
                        foreground=COLORS["subtext"], font=FONTS["subhead"], relief="flat")
        style.map("Main.Treeview", background=[("selected", COLORS["selected"])])

        cols = ["ID","Code","Course Name","Instructor","Units"]
        tf = tk.Frame(p, bg=COLORS["card"],
                      highlightthickness=1, highlightbackground=COLORS["border"])
        tf.pack(fill="both", expand=True)
        self.ctv = ttk.Treeview(tf, columns=cols, show="headings", style="Main.Treeview")
        for col, w in zip(cols,[50,100,300,200,60]):
            self.ctv.heading(col, text=col)
            self.ctv.column(col, width=w, anchor="w")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.ctv.yview)
        self.ctv.configure(yscrollcommand=sb.set)
        self.ctv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        af = tk.Frame(p, bg=COLORS["bg"])
        af.pack(fill="x", pady=(10,0))
        StyledButton(af, "✏ Edit",   self._edit_course,   "primary").pack(side="left", padx=(0,8))
        StyledButton(af, "🗑 Delete", self._delete_course, "danger").pack(side="left")

        self._refresh_courses()

    def _refresh_courses(self):
        self.ctv.delete(*self.ctv.get_children())
        for c in self.data["courses"]:
            self.ctv.insert("", "end", iid=str(c["id"]),
                            values=[c["id"],c["code"],c["name"],c["instructor"],c["units"]])

    def _add_course(self):
        m = CourseModal(self)
        self.wait_window(m)
        if m.result:
            m.result["id"] = next_id(self.data["courses"])
            self.data["courses"].append(m.result)
            save_data(self.data)
            self._refresh_courses()

    def _edit_course(self):
        sel = self.ctv.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a course first."); return
        cid = int(sel[0])
        course = next((c for c in self.data["courses"] if c["id"]==cid), None)
        m = CourseModal(self, course)
        self.wait_window(m)
        if m.result:
            course.update(m.result)
            save_data(self.data)
            self._refresh_courses()

    def _delete_course(self):
        sel = self.ctv.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a course first."); return
        cid = int(sel[0])
        if messagebox.askyesno("Confirm", "Delete this course?"):
            self.data["courses"]    = [c for c in self.data["courses"]    if c["id"]!=cid]
            self.data["grades"]     = [g for g in self.data["grades"]     if g["course_id"]!=cid]
            self.data["attendance"] = [a for a in self.data["attendance"]  if a["course_id"]!=cid]
            save_data(self.data)
            self._refresh_courses()

    # ── GRADES PAGE ───────────────────────────────────────────────────────────
    def _page_grades(self):
        p = tk.Frame(self.content, bg=COLORS["bg"], padx=30, pady=24)
        p.pack(fill="both", expand=True)

        hf = tk.Frame(p, bg=COLORS["bg"])
        hf.pack(fill="x", pady=(0,16))
        tk.Label(hf, text="Grades", bg=COLORS["bg"],
                 fg=COLORS["text"], font=FONTS["title"]).pack(side="left")
        StyledButton(hf, "+ Record Grade", self._add_grade, "success").pack(side="right")

        # Summary cards
        if self.data["grades"]:
            sf = tk.Frame(p, bg=COLORS["bg"])
            sf.pack(fill="x", pady=(0,16))
            avg = sum(g["score"] for g in self.data["grades"]) / len(self.data["grades"])
            passing = sum(1 for g in self.data["grades"] if g["score"]>=75)
            cards = [
                ("Average", f"{avg:.1f}", COLORS["accent2"]),
                ("Passing",  str(passing), COLORS["accent"]),
                ("Failing",  str(len(self.data["grades"])-passing), COLORS["danger"]),
            ]
            for i,(lbl,val,col) in enumerate(cards):
                c = tk.Frame(sf, bg=COLORS["card"], padx=16, pady=12,
                             highlightthickness=1, highlightbackground=COLORS["border"])
                c.grid(row=0, column=i, padx=(0,12))
                tk.Label(c, text=val, bg=COLORS["card"], fg=col,
                         font=("Segoe UI",20,"bold")).pack()
                tk.Label(c, text=lbl, bg=COLORS["card"], fg=COLORS["subtext"],
                         font=FONTS["small"]).pack()

        cols = ["ID","Student","Course","Score","Grade","Semester","Date"]
        tf = tk.Frame(p, bg=COLORS["card"],
                      highlightthickness=1, highlightbackground=COLORS["border"])
        tf.pack(fill="both", expand=True)
        self.gtv = ttk.Treeview(tf, columns=cols, show="headings", style="Main.Treeview")
        for col, w in zip(cols,[40,180,150,60,60,180,100]):
            self.gtv.heading(col, text=col)
            self.gtv.column(col, width=w, anchor="w")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.gtv.yview)
        self.gtv.configure(yscrollcommand=sb.set)
        self.gtv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        af = tk.Frame(p, bg=COLORS["bg"])
        af.pack(fill="x", pady=(10,0))
        StyledButton(af, "🗑 Delete", self._delete_grade, "danger").pack(side="left")

        self._refresh_grades()

    def _refresh_grades(self):
        self.gtv.delete(*self.gtv.get_children())
        for g in self.data["grades"]:
            st = next((s for s in self.data["students"] if s["id"]==g["student_id"]), None)
            co = next((c for c in self.data["courses"]  if c["id"]==g["course_id"]),  None)
            if st and co:
                ltr = get_grade_letter(g["score"])
                self.gtv.insert("", "end", iid=str(g["id"]),
                                values=[g["id"],
                                        f"{st['first_name']} {st['last_name']}",
                                        co["code"], g["score"], ltr,
                                        g["semester"], g["date"]])

    def _add_grade(self):
        if not self.data["students"]:
            messagebox.showinfo("No Students", "Add students first."); return
        if not self.data["courses"]:
            messagebox.showinfo("No Courses", "Add courses first."); return
        m = GradeModal(self, self.data["students"], self.data["courses"])
        self.wait_window(m)
        if m.result:
            m.result["id"] = next_id(self.data["grades"])
            self.data["grades"].append(m.result)
            save_data(self.data)
            self._page_grades()

    def _delete_grade(self):
        sel = self.gtv.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a grade record first."); return
        gid = int(sel[0])
        if messagebox.askyesno("Confirm", "Delete this grade record?"):
            self.data["grades"] = [g for g in self.data["grades"] if g["id"]!=gid]
            save_data(self.data)
            self._page_grades()

    # ── ATTENDANCE PAGE ───────────────────────────────────────────────────────
    def _page_attendance(self):
        p = tk.Frame(self.content, bg=COLORS["bg"], padx=30, pady=24)
        p.pack(fill="both", expand=True)

        hf = tk.Frame(p, bg=COLORS["bg"])
        hf.pack(fill="x", pady=(0,16))
        tk.Label(hf, text="Attendance", bg=COLORS["bg"],
                 fg=COLORS["text"], font=FONTS["title"]).pack(side="left")
        StyledButton(hf, "+ Record Attendance", self._add_attendance, "success").pack(side="right")

        # Summary
        if self.data["attendance"]:
            sf = tk.Frame(p, bg=COLORS["bg"])
            sf.pack(fill="x", pady=(0,16))
            counts = {"Present":0,"Absent":0,"Late":0,"Excused":0}
            for a in self.data["attendance"]:
                counts[a["status"]] = counts.get(a["status"],0)+1
            colors_map = {"Present":COLORS["accent"],"Absent":COLORS["danger"],
                          "Late":COLORS["warning"],"Excused":COLORS["accent2"]}
            for i,(status,count) in enumerate(counts.items()):
                c = tk.Frame(sf, bg=COLORS["card"], padx=16, pady=12,
                             highlightthickness=1, highlightbackground=COLORS["border"])
                c.grid(row=0, column=i, padx=(0,12))
                tk.Label(c, text=str(count), bg=COLORS["card"],
                         fg=colors_map.get(status,COLORS["text"]),
                         font=("Segoe UI",20,"bold")).pack()
                tk.Label(c, text=status, bg=COLORS["card"], fg=COLORS["subtext"],
                         font=FONTS["small"]).pack()

        cols = ["ID","Student","Course","Date","Status"]
        tf = tk.Frame(p, bg=COLORS["card"],
                      highlightthickness=1, highlightbackground=COLORS["border"])
        tf.pack(fill="both", expand=True)
        self.atv = ttk.Treeview(tf, columns=cols, show="headings", style="Main.Treeview")
        for col, w in zip(cols,[40,200,160,120,100]):
            self.atv.heading(col, text=col)
            self.atv.column(col, width=w, anchor="w")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.atv.yview)
        self.atv.configure(yscrollcommand=sb.set)
        self.atv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        af = tk.Frame(p, bg=COLORS["bg"])
        af.pack(fill="x", pady=(10,0))
        StyledButton(af, "🗑 Delete", self._delete_attendance, "danger").pack(side="left")

        self._refresh_attendance()

    def _refresh_attendance(self):
        self.atv.delete(*self.atv.get_children())
        status_colors = {"Present":COLORS["accent"],"Absent":COLORS["danger"],
                         "Late":COLORS["warning"],"Excused":COLORS["accent2"]}
        for a in sorted(self.data["attendance"], key=lambda x: x["date"], reverse=True):
            st = next((s for s in self.data["students"] if s["id"]==a["student_id"]), None)
            co = next((c for c in self.data["courses"]  if c["id"]==a["course_id"]),  None)
            if st and co:
                self.atv.insert("", "end", iid=str(a["id"]),
                                values=[a["id"],
                                        f"{st['first_name']} {st['last_name']}",
                                        co["code"], a["date"], a["status"]])

    def _add_attendance(self):
        if not self.data["students"]:
            messagebox.showinfo("No Students", "Add students first."); return
        if not self.data["courses"]:
            messagebox.showinfo("No Courses", "Add courses first."); return
        m = AttendanceModal(self, self.data["students"], self.data["courses"])
        self.wait_window(m)
        if m.result:
            m.result["id"] = next_id(self.data["attendance"])
            self.data["attendance"].append(m.result)
            save_data(self.data)
            self._page_attendance()

    def _delete_attendance(self):
        sel = self.atv.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a record first."); return
        aid = int(sel[0])
        if messagebox.askyesno("Confirm", "Delete this attendance record?"):
            self.data["attendance"] = [a for a in self.data["attendance"] if a["id"]!=aid]
            save_data(self.data)
            self._page_attendance()

# ─── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SISApp()
    app.mainloop()