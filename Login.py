import tkinter as tk
from tkinter import messagebox
import subprocess

# Admin account
admin_user = "admin"
admin_pass = "12345"

# Login function
def login():

    username = username_entry.get()
    password = password_entry.get()

    if username == admin_user and password == admin_pass:

        messagebox.showinfo("Login", "Login Successful!")

        # Open dashboard.py
        subprocess.Popen(["python", "sinarp.py"])

        # Close login window
        window.destroy()

    else:
        messagebox.showerror("Error", "Wrong Username or Password")


# Main Window
window = tk.Tk()
window.title("Login System")
window.geometry("300x220")

title = tk.Label(window, text="Admin Login", font=("Arial", 15))
title.pack(pady=10)

# Username
tk.Label(window, text="Username").pack()
username_entry = tk.Entry(window)
username_entry.pack(pady=5)

# Password
tk.Label(window, text="Password").pack()
password_entry = tk.Entry(window, show="*")
password_entry.pack(pady=5)

# Login Button
login_btn = tk.Button(window, text="Login", command=login)
login_btn.pack(pady=15)

window.mainloop()
