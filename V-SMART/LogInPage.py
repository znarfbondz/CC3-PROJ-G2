from DASHBOARD import Dashboard
import os
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from PIL import Image, ImageTk, ImageDraw  # Added ImageDraw
except ImportError:
    raise SystemExit("Please install Pillow first: pip install pillow >_<")

# ----------Details--------------
APP_TITLE = "V-SMART: Valenzuela Student Management and Records Technology"
WINDOW_W, WINDOW_H = 1100, 650
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "Screenshot 2026-05-11 231939.png")
LOGO_PATH = os.path.join(BASE_DIR, "download.png")
WHITE_PANEL = "white"
BUTTON_BG = "#359bfc"
TEXT_COLOR = "#0f172a"
USERS = {
    "admin": "admin",
    "user": "1234"
}
C_DEEP = "#050d1f"
C_NAVY = "#0a1628"
C_PANEL = "#0e1e38"
C_ACCENT = "#1e6bff"
C_GLOW = "#3d8bff"
C_GOLD = "#f0c040"
C_WHITE = "#f0f6ff"
C_MUTED = "#7a90b0"
C_INPUT_BG = "#0c1830"
C_INPUT_BD = "#1e3a5f"
C_INPUT_FOC = "#1e6bff"
C_BTN_HVR = "#1457e0"

FONT_TITLE = ("Georgia", 22, "bold")
FONT_SUB = ("Georgia", 9)
FONT_LABEL = ("Courier New", 9, "bold")
FONT_INPUT = ("Courier New", 11)
FONT_BTN = ("Georgia", 11, "bold")
FONT_SMALL = ("Courier New", 8)
#--------DATABASE---------
import sqlite3
import os
 
DB = "enrollment.db"
 
 
# ── Setup ─────────────────────────────────────────────────────────────────────
 
def init():
    con = sqlite3.connect(DB)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            student_id      TEXT PRIMARY KEY,
            last_name       TEXT NOT NULL,
            first_name      TEXT NOT NULL,
            year_level      TEXT NOT NULL,
            section         TEXT NOT NULL,
            email           TEXT,
            address         TEXT,
            contact_number  TEXT
        );
 
        CREATE TABLE IF NOT EXISTS grades (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            subject     TEXT NOT NULL,
            grade       REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );
    """)
    con.commit()
    con.close()
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
 
def pause():
    input("\n  Press Enter to continue...")
 
def clear():
    os.system("cls" if os.name == "nt" else "clear")
 
def ask(prompt, required=True):
    while True:
        val = input(f"  {prompt}: ").strip()
        if val or not required:
            return val
        print("  This field is required.")
 
def divider():
    print("  " + "─" * 54)
 
 
# ── Student operations ────────────────────────────────────────────────────────
 
def add_student():
    clear()
    print("  ┌─ ADD NEW STUDENT ─────────────────────────────┐\n")
    sid    = ask("Student ID (e.g. 2024-0001)")
    lname  = ask("Last Name")
    fname  = ask("First Name")
    year   = ask("Year Level (e.g. 1, 2, 3, 4)")
    sec    = ask("Section (e.g. BSCS-1A)")
    email  = ask("Email", required=False)
    addr   = ask("Address", required=False)
    phone  = ask("Contact Number", required=False)
 
    con = sqlite3.connect(DB)
    try:
        con.execute("""
            INSERT INTO students
              (student_id, last_name, first_name, year_level,
               section, email, address, contact_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (sid, lname, fname, year, sec, email, addr, phone))
        con.commit()
        print(f"\n  Student {lname}, {fname} [{sid}] enrolled successfully.")
    except sqlite3.IntegrityError:
        print(f"\n  Student ID {sid} already exists.")
    con.close()
    pause()
 
 
def view_all():
    clear()
    print("  ┌─ ALL ENROLLED STUDENTS ───────────────────────┐\n")
    con = sqlite3.connect(DB)
    rows = con.execute("""
        SELECT s.student_id, s.last_name, s.first_name,
               s.year_level, s.section,
               ROUND(AVG(g.grade), 2) AS avg_grade
        FROM students s
        LEFT JOIN grades g ON s.student_id = g.student_id
        GROUP BY s.student_id
        ORDER BY s.last_name, s.first_name
    """).fetchall()
    con.close()
 
    if not rows:
        print("  No students enrolled yet.")
    else:
        print(f"  {'ID':<12} {'Last Name':<15} {'First Name':<14} "
              f"{'Yr':<4} {'Section':<10} {'Avg'}")
        divider()
        for r in rows:
            avg = f"{r[5]:.2f}" if r[5] is not None else "N/A"
            print(f"  {r[0]:<12} {r[1]:<15} {r[2]:<14} "
                  f"{r[3]:<4} {r[4]:<10} {avg}")
    pause()
 
 
def view_student():
    clear()
    print("  ┌─ VIEW STUDENT PROFILE ────────────────────────┐\n")
    sid = ask("Enter Student ID")
 
    con = sqlite3.connect(DB)
    s = con.execute("SELECT * FROM students WHERE student_id = ?", (sid,)).fetchone()
    g = con.execute(
        "SELECT subject, grade FROM grades WHERE student_id = ? ORDER BY subject",
        (sid,)).fetchall()
    avg = con.execute(
        "SELECT ROUND(AVG(grade), 2) FROM grades WHERE student_id = ?",
        (sid,)).fetchone()[0]
    con.close()
 
    if not s:
        print(f"\n  Student {sid} not found.")
    else:
        print(f"""
  Student ID    : {s[0]}
  Name          : {s[1]}, {s[2]}
  Year Level    : {s[3]}
  Section       : {s[4]}
  Email         : {s[5] or '—'}
  Address       : {s[6] or '—'}
  Contact No.   : {s[7] or '—'}""")
        divider()
        if g:
            for subject, grade in g:
                print(f"  {subject:<20} {grade:.2f}")
            divider()
            print(f"  {'Average Grade':<20} {avg:.2f}")
        else:
            print("  No grades on record.")
    pause()
 
 
def update_student():
    clear()
    print("  ┌─ UPDATE STUDENT ──────────────────────────────┐\n")
    sid = ask("Enter Student ID to update")
 
    con = sqlite3.connect(DB)
    s = con.execute("SELECT * FROM students WHERE student_id = ?", (sid,)).fetchone()
    con.close()
 
    if not s:
        print(f"\n  Student {sid} not found.")
        pause()
        return
 
    print(f"\n  Updating: {s[1]}, {s[2]} — leave blank to keep current value.\n")
    fields = {}
    mapping = {
        "last_name":      f"Last Name       [{s[1]}]",
        "first_name":     f"First Name      [{s[2]}]",
        "year_level":     f"Year Level      [{s[3]}]",
        "section":        f"Section         [{s[4]}]",
        "email":          f"Email           [{s[5] or ''}]",
        "address":        f"Address         [{s[6] or ''}]",
        "contact_number": f"Contact Number  [{s[7] or ''}]",
    }
    for col, label in mapping.items():
        val = ask(label, required=False)
        if val:
            fields[col] = val
 
    if fields:
        setters = ", ".join(f"{k} = ?" for k in fields)
        con = sqlite3.connect(DB)
        con.execute(f"UPDATE students SET {setters} WHERE student_id = ?",
                    (*fields.values(), sid))
        con.commit()
        con.close()
        print(f"\n  Student {sid} updated successfully.")
    else:
        print("\n  No changes made.")
    pause()
 
 
def delete_student():
    clear()
    print("  ┌─ DELETE STUDENT ──────────────────────────────┐\n")
    sid = ask("Enter Student ID to delete")
 
    con = sqlite3.connect(DB)
    s = con.execute("SELECT last_name, first_name FROM students WHERE student_id = ?",
                    (sid,)).fetchone()
    if not s:
        print(f"\n  Student {sid} not found.")
        con.close()
        pause()
        return
 
    confirm = ask(f"Delete {s[0]}, {s[1]}? Type YES to confirm")
    if confirm.upper() == "YES":
        con.execute("DELETE FROM grades  WHERE student_id = ?", (sid,))
        con.execute("DELETE FROM students WHERE student_id = ?", (sid,))
        con.commit()
        print(f"\n  Student {sid} deleted.")
    else:
        print("\n  Cancelled.")
    con.close()
    pause()
 
 
# ── Grade operations ──────────────────────────────────────────────────────────
 
def manage_grades():
    clear()
    print("  ┌─ MANAGE GRADES ───────────────────────────────┐\n")
    sid = ask("Enter Student ID")
 
    con = sqlite3.connect(DB)
    s = con.execute("SELECT last_name, first_name FROM students WHERE student_id = ?",
                    (sid,)).fetchone()
    if not s:
        print(f"\n  Student {sid} not found.")
        con.close()
        pause()
        return
 
    print(f"\n  Student: {s[0]}, {s[1]}\n")
    print("  [1] Add / update a subject grade")
    print("  [2] Delete a subject grade")
    print("  [3] View all grades")
    choice = ask("Choice")
 
    if choice == "1":
        subject = ask("Subject name")
        while True:
            raw = ask("Grade (0–100)")
            try:
                grade = float(raw)
                if 0 <= grade <= 100:
                    break
                print("  Enter a number between 0 and 100.")
            except ValueError:
                print("  Invalid number.")
        # Upsert: update if exists, insert if not
        exists = con.execute(
            "SELECT id FROM grades WHERE student_id = ? AND subject = ?",
            (sid, subject)).fetchone()
        if exists:
            con.execute("UPDATE grades SET grade = ? WHERE student_id = ? AND subject = ?",
                        (grade, sid, subject))
            print(f"\n  Updated {subject}: {grade}")
        else:
            con.execute("INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)",
                        (sid, subject, grade))
            print(f"\n  Added {subject}: {grade}")
        con.commit()
 
        avg = con.execute(
            "SELECT ROUND(AVG(grade), 2) FROM grades WHERE student_id = ?",
            (sid,)).fetchone()[0]
        print(f"  New average grade: {avg:.2f}")
 
    elif choice == "2":
        subject = ask("Subject to delete")
        con.execute("DELETE FROM grades WHERE student_id = ? AND subject = ?",
                    (sid, subject))
        con.commit()
        print(f"\n  Removed {subject} grade.")
 
    elif choice == "3":
        rows = con.execute(
            "SELECT subject, grade FROM grades WHERE student_id = ? ORDER BY subject",
            (sid,)).fetchall()
        avg = con.execute(
            "SELECT ROUND(AVG(grade), 2) FROM grades WHERE student_id = ?",
            (sid,)).fetchone()[0]
        if rows:
            print()
            divider()
            for row in rows:
                print(f"  {row[0]:<20} {row[1]:.2f}")
            divider()
            print(f"  {'Average':<20} {avg:.2f}")
        else:
            print("\n  No grades on record.")
 
    con.close()
    pause()
 
 
# ── Main menu ─────────────────────────────────────────────────────────────────
 
def menu():
    init()
    while True:
        clear()
        print("  ╔══════════════════════════════════════════════╗")
        print("  ║       STUDENT ENROLLMENT DATABASE            ║")
        print("  ╠══════════════════════════════════════════════╣")
        print("  ║  [1]  Add new student                        ║")
        print("  ║  [2]  View all students                      ║")
        print("  ║  [3]  View student profile                   ║")
        print("  ║  [4]  Update student info                    ║")
        print("  ║  [5]  Manage grades                          ║")
        print("  ║  [6]  Delete student                         ║")
        print("  ║  [0]  Exit                                   ║")
        print("  ╚══════════════════════════════════════════════╝")
 
        choice = ask("Choose an option")
 
        if   choice == "1": add_student()
        elif choice == "2": view_all()
        elif choice == "3": view_student()
        elif choice == "4": update_student()
        elif choice == "5": manage_grades()
        elif choice == "6": delete_student()
        elif choice == "0":
            print("\n  Goodbye!\n")
            break
        else:
            print("\n  Invalid option.")
            pause()
 
 
if __name__ == "_main_":
    menu()

# ------------LOGINPAGE------------
class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.minsize(900, 560)
        self.configure(bg="#0f172a")

        # bg loading system
        self._bg_src = None
        self._bg_img = None
        self._load_background()

        # canvas
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # to update bg later
        self.bg_item = self.canvas.create_image(0, 0, anchor="nw")

        # Create the card (FIXED)
        self.card_window = None
        self._build_card()  # Actually build and place the card

        # Animation variables
        self._card_y = -200  # Start above the window

        # RESIZE AND ENTER KEYS
        self.bind("<Configure>", self._on_resize)
        self.bind("<Return>", lambda _e: self._handle_login())

       
    # ---------- Background ----------
    def _load_background(self):
        if os.path.exists(BG_PATH):
            self._bg_src = Image.open(BG_PATH).convert("RGB")
        else:
            self._bg_src = Image.new("RGB", (WINDOW_W, WINDOW_H), "#3a4a6b")

    def _render_background(self, w, h):
        img = self._bg_src.resize((w, h), Image.LANCZOS)
        self._bg_img = ImageTk.PhotoImage(img)
        self.canvas.itemconfigure(self.bg_item, image=self._bg_img)

    def _on_resize(self, event):
        if event.widget is not self:
            return
        w, h = max(event.width, 1), max(event.height, 1)
        self._render_background(w, h)
        if self.card_window:
            self.canvas.coords(self.card_window, w // 2, h // 2)

    # ───── Card building ─────
    def _build_card(self):
        card = tk.Frame(self.canvas, bg=C_PANEL,
                        highlightthickness=1, highlightbackground=C_INPUT_BD,
                        padx=48, pady=36)

        # ── Top accent bar ──
        accent_bar = tk.Frame(card, bg=C_ACCENT, height=3)
        accent_bar.pack(fill="x", padx=0, pady=(0, 24))

        # ── Logo ──
        if os.path.exists(LOGO_PATH):
            try:
                raw = Image.open(LOGO_PATH).resize((72, 72), Image.LANCZOS)
                # Circular crop
                mask = Image.new("L", (72, 72), 0)
                d = ImageDraw.Draw(mask)  # Now ImageDraw is imported
                d.ellipse((0, 0, 72, 72), fill=255)
                raw.putalpha(mask)
                self._logo_photo = ImageTk.PhotoImage(raw)
                lbl = tk.Label(card, image=self._logo_photo, bg=C_PANEL)
                lbl.pack()
            except Exception as e:
                print(f"Logo error: {e}")
                self._fallback_logo(card)
        else:
            self._fallback_logo(card)

        # ── Title ──
        tk.Label(card, text="V-SMART", bg=C_PANEL, fg=C_GOLD,
                 font=FONT_TITLE).pack(pady=(10, 0))

        tk.Label(card,
                 text="Valenzuela Student Management and Records Technology",
                 bg=C_PANEL, fg=C_MUTED, font=FONT_SUB,
                 wraplength=340, justify="center").pack(pady=(2, 4))

        # ── Divider ──
        div = tk.Frame(card, bg=C_INPUT_BD, height=1)
        div.pack(fill="x", pady=(6, 18))

        tk.Label(card, text="SECURE LOGIN", bg=C_PANEL, fg=C_ACCENT,
                 font=FONT_SMALL).pack(pady=(0, 14))

        # ── Username and Password ──
        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        self._user_entry = self._build_field(card, "USERNAME", self.user_var, show=None)
        self._pass_entry = self._build_field(card, "PASSWORD", self.pass_var, show="●")

        # ── Login Button ──
        self._build_button(card)

        # ── Footer ──
        tk.Label(card, text="Valenzuela Information Technology Society  ·  2026",
                 bg=C_PANEL, fg=C_MUTED, font=FONT_SMALL).pack(pady=(16, 0))

        # Place the card on canvas (initially above screen for animation)
        self.card_window = self.canvas.create_window(
            WINDOW_W // 2, -200,  # Start above the window
            window=card, anchor="center"
        )

    def _fallback_logo(self, parent):
        tk.Label(parent, text="⬡", bg=C_PANEL, fg=C_ACCENT,
                 font=("Arial", 36)).pack()

    def _build_field(self, parent, label_text, var, show=None):
        container = tk.Frame(parent, bg=C_PANEL)
        container.pack(fill="x", pady=(0, 12))

        tk.Label(container, text=label_text, bg=C_PANEL, fg=C_MUTED,
                 font=FONT_LABEL, anchor="w").pack(fill="x")

        frame = tk.Frame(container, bg=C_INPUT_BG,
                         highlightthickness=1, highlightbackground=C_INPUT_BD)
        frame.pack(fill="x", pady=(3, 0))

        entry = tk.Entry(frame, textvariable=var,
                         bg=C_INPUT_BG, fg=C_WHITE,
                         insertbackground=C_GLOW,
                         relief="flat", font=FONT_INPUT,
                         show=show or "",
                         bd=8, width=32)
        entry.pack(fill="x")

        # Focus glow effect
        entry.bind("<FocusIn>", lambda e, f=frame: f.configure(highlightbackground=C_INPUT_FOC))
        entry.bind("<FocusOut>", lambda e, f=frame: f.configure(highlightbackground=C_INPUT_BD))
        return entry

    def _build_button(self, parent):
        self._btn_frame = tk.Frame(parent, bg=C_ACCENT,
                                   highlightthickness=0)
        self._btn_frame.pack(fill="x", pady=(8, 0))

        self._btn = tk.Button(
            self._btn_frame,
            text="LOG  IN  →",
            bg=C_ACCENT, fg=C_WHITE,
            activebackground=C_BTN_HVR, activeforeground=C_WHITE,
            relief="flat", font=FONT_BTN,
            bd=0, padx=20, pady=12,
            cursor="hand2",
            command=self._handle_login
        )
        self._btn.pack(fill="x")

        self._btn.bind("<Enter>", lambda e: self._btn.config(bg=C_BTN_HVR))
        self._btn.bind("<Leave>", lambda e: self._btn.config(bg=C_ACCENT))

    # ───── Slide-in animation (FIXED) ─────
   

    # ───── Login logic ─────
    def _handle_login(self):
        u = self.user_var.get().strip()
        p = self.pass_var.get().strip()

        if not u or not p:
            messagebox.showwarning("Missing Fields", "Please enter both username and password.")
            return

        if USERS.get(u) == p:
            self._btn.config(text="✓  ACCESS GRANTED", bg="#16a34a")
            self.after(700, lambda: self._open_dashboard(u))  # ← calls dashboard
        else:
            self._btn.config(text="✗  INVALID", bg="#dc2626")
            self.after(1200, lambda: self._btn.config(text="LOG  IN  →", bg="#1e6bff"))
            messagebox.showerror("Access Denied", "Invalid username or password.")



    def _open_dashboard(self, username):
        self.withdraw()  # Hide login window
        dashboard_root = tk.Toplevel(self)
        dashboard_root.protocol(
            "WM_DELETE_WINDOW",
            lambda: (dashboard_root.destroy(), self._on_logout())
        )
        Dashboard(dashboard_root, username, on_logout=self._on_logout, users=USERS)

    def _on_logout(self):
        self.deiconify()  # bring login back
        if self._btn:
            self._btn.config(text="LOG  IN  →", bg="#1e6bff")
        self.user_var.set("")
        self.pass_var.set("")

LoginPage().mainloop()
