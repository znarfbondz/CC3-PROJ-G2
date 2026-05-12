from Dashboard import Dashboard
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
BG_PATH = "C:\\Users\\abelx\\Downloads\\Screenshot_2026-05-11_231939.png"
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

        # Start slide-in animation after window is drawn
        self.after(100, self._slide_in_card)

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
        LOGO_PATH = "C:\\Users\\abelx\\Downloads\\download.jpg"
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
        tk.Label(card, text="DepEd Valenzuela City Division  ·  2026",
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
    def _slide_in_card(self):
        target_y = self.winfo_height() // 2
        start_y = -200
        steps = 28

        def step(current_y, i):
            if i > steps:
                return
            t = i / steps
            # Ease out cubic
            ease = 1 - (1 - t) ** 3
            new_y = int(start_y + (target_y - start_y) * ease)
            if self.card_window:
                self.canvas.coords(self.card_window, self.winfo_width() // 2, new_y)
            if i < steps:
                self.after(16, lambda: step(new_y, i + 1))

        step(start_y, 1)

    # ───── Login logic ─────
    def _handle_login(self):
        u = self.user_var.get().strip()
        p = self.pass_var.get().strip()

        if not u or not p:
            self._shake_card()
            messagebox.showwarning("Missing Fields", "Please enter both username and password.")
            return

        if USERS.get(u) == p:
            self._btn.config(text="✓  ACCESS GRANTED", bg="#16a34a")
            self.after(700, lambda: self._open_dashboard(u))  # ← calls dashboard
        else:
            self._btn.config(text="✗  INVALID", bg="#dc2626")
            self.after(1200, lambda: self._btn.config(text="LOG  IN  →", bg="#1e6bff"))
            self._shake_card()
            messagebox.showerror("Access Denied", "Invalid username or password.")

    def _shake_card(self):
        if not self.card_window:
            return
        cx = self.winfo_width() // 2
        cy = self.winfo_height() // 2
        offsets = [10, -10, 8, -8, 5, -5, 2, -2, 0]

        def step(i=0):
            if i < len(offsets):
                self.canvas.coords(self.card_window, cx + offsets[i], cy)
                self.after(40, lambda: step(i + 1))

        step()

    def _open_dashboard(self, username):
        self.withdraw()  # Hide login window
        dashboard_root = tk.Tk()  #  NEW ROOT for dashboard
        Dashboard(dashboard_root)  #  Pass NEW root + username
        dashboard_root.mainloop()
        self.deiconify()

    def _on_logout(self):
            self.deiconify()  # bring login back
            self._btn.config(text="LOG  IN  →", bg="#1e6bff")
            self.user_var.set("")
            self.pass_var.set("")

LoginPage().mainloop()