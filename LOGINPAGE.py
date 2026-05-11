import os #for interacting with the operating system ig
import tkinter as tk #short cut lanbg
from tkinter import ttk, messagebox #ttk for better widgets at messagebox pop up windows

try:
   from PIL import Image, ImageTk #image to open, imagetk display images in tk label, iamgefilter applies filter
except ImportError:
    raise SystemExit("Please install Pillow first: pip install pillow >_<")

#----------Details--------------
APP_TITLE = "V-SMART: Valenzuela Student Management and Records Technology"
WINDOW_W, WINDOW_H = 1100, 650
BG_PATH = "C:\\CC3-IMAGES\\Screenshot 2026-05-11 231939.png"
WHITE_PANEL = "white"
BUTTON_BG = "#359bfc"
TEXT_COLOR = "#0f172a"
USERS = {
    "admin" : "admin",
    "user" : "1234"
}

#------------LOGINPAGE------------
class LoginPage(tk.Tk):
    def __init__(self): #runs automatically kahit d tinawag
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.minsize(900, 560)
        self.configure(bg="#0f172a")

        #bg loading system
        self._bg_src = None
        self._bg_img = None
        self._load_background()

        #canvas
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0) #creates canva widget
        self.canvas.pack(fill="both", expand=True) #stretch, grow when window iz resizwd

        #to update bg later
        self.bg_item = self.canvas.create_image(0, 0, anchor="nw")

        #login card
        self.card = self._build_card(self.canvas)
        self.card_window = self.canvas.create_window(
        WINDOW_W // 2, WINDOW_H // 2,
        window=self.card, anchor="center"
        )
        #RESIZE AND ENTER KEYS
        self.bind("<Configure>", self._on_resize) #adjusts accordingly
        self.bind("<Return>", lambda _e: self._handle_login()) #when user enters enter run login
  
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
        self.canvas.coords(self.card_window, w // 2, h // 2)
   
    #------card------
    def _build_card(self, parent):
        card = tk.Frame(
            parent,
            bg=WHITE_PANEL,
            highlightthickness=1,
            width = 30,
            height = 10,
            highlightbackground=WHITE_PANEL,
        )
        # ---------- LOGO (TOP) ----------
        LOGO_PATH = "C:\\CC3-IMAGES\\download.jpg"

        if os.path.exists(LOGO_PATH):
            logo_img = Image.open(LOGO_PATH).resize((80,80), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)

            logo_label = tk.Label(card, image=self.logo_photo)
            logo_label.image = self.logo_photo  
            logo_label.pack(side="top", pady=(0, 10))
        else:
            tk.Label(card, text="NO IMAGE", bg=WHITE_PANEL).pack(pady=(0, 12))

        card.configure(padx=100, pady=100)
        tk.Label(
            card, text="V-SMART",
            bg=WHITE_PANEL, fg='#010245',
            font=("Times New Roman", 11, "bold"),
        ).pack()
        tk.Label(
            card, text="Valenzuela Student Management and Records Technology",
            bg=WHITE_PANEL, fg='#010245',
            font=("Tmes New Roman", 16, "bold"),
        ).pack(pady=(2, 18))

        tk.Label(
            card, text="Please log in to access the system",
            bg=WHITE_PANEL, fg='#010245',
            font=("Tmes New Roman", 10),
        ).pack(pady=(0, 14))
        

        # ---------- INPUTS ----------
        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()

        tk.Label(card, text="Username", bg=WHITE_PANEL, fg=TEXT_COLOR).pack(anchor='w')
        tk.Entry(card, textvariable=self.user_var, width=40).pack(padx = 5, pady=10)

        tk.Label(card, text="Password", bg=WHITE_PANEL, fg=TEXT_COLOR).pack(anchor="w")
        tk.Entry(card, textvariable=self.pass_var, show="*",width=40).pack(padx = 5, pady=10)

        # ---------- BUTTON ----------
        tk.Button(
            card,
            text="Login",
            bg=BUTTON_BG,
            width = 10,
            height = 2,
            fg="white",
            command=self._handle_login
        ).pack(pady=50)
        return card

        #------LOGIN------
    def _handle_login(self):
        u = self.user_var.get().strip()
        p = self.pass_var.get().strip()

        if USERS.get(u) == p:
            messagebox.showinfo("Success", "Login successful!")
        else:
            messagebox.showerror("Error", "Invalid credentials")

           
        




LoginPage().mainloop()