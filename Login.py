import tkinter as tk
from tkinter import messagebox # ask kay sir if pwede to
import subprocess
import sys

# Login function
def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        messagebox.showwarning("Warning", "Fill all fields")
        return

    try:
        with open("accounts.txt", "r") as file: # ask kay sir if pwede to
            accounts = file.readlines()
    except FileNotFoundError:
        messagebox.showerror("Error", "No accounts found!")
        return


    for acc in accounts:
        parts = acc.strip().split(",")

        if len(parts) != 2:
            continue

        user, passw = parts

        if username == user and password == passw:
            messagebox.showinfo("Login", "Login Successful!")
            subprocess.Popen([sys.executable, "sinarp.py"])
            window.destroy()
            return

    messagebox.showerror("Error", "Wrong Username or Password")

def register():
    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        messagebox.showwarning("Warning", "Fill all fields")
        return

    # check duplicates
    try:
        with open("accounts.txt", "r") as file:
            for line in file:
                data = line.strip().split(",")
                if len(data) == 2:
                    user, _ = data
                    if user == username:
                        messagebox.showerror("Error", "User already exists!")
                        return
    except FileNotFoundError:
        pass

    # save account
    with open("accounts.txt", "a") as file:
        file.write(f"{username},{password}\n")

    messagebox.showinfo("Success", "Account Created!")

# Main Window
window = tk.Tk()
window.title("Login System")
window.geometry("400x500")


title = tk.Label(window, text="SIS SECURE LOG IN", font=("Arial", 15))
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

# Register Button
register_btn = tk.Button(window, text="Register", command=register)
register_btn.pack(pady=5)

window.mainloop()
