from tkinter import Tk, Canvas, Entry, Text, Button, messagebox, font
import requests
from io import BytesIO
from PIL import Image, ImageTk
import mysql.connector
from urllib.parse import quote
import re
import uuid
import os
import subprocess
import sys

ASSETS_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/create_profile"

def image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    image_data = BytesIO(response.content)
    pil_image = Image.open(image_data)
    return ImageTk.PhotoImage(pil_image)

def relative_to_assets(filename: str) -> str:
    encoded_filename = quote(filename)
    return f"{ASSETS_BASE_URL}/{encoded_filename}"

def add_placeholder(entry_widget, placeholder, is_password=False):
    entry_widget.insert(0, placeholder)
    entry_widget.config(fg='grey')
    if is_password:
        entry_widget.config(show='')

    def on_focus_in(event):
        if entry_widget.get() == placeholder:
            entry_widget.delete(0, 'end')
            entry_widget.config(fg='black')
            if is_password:
                entry_widget.config(show='*')

    def on_focus_out(event):
        if not entry_widget.get():
            entry_widget.insert(0, placeholder)
            entry_widget.config(fg='grey')
            if is_password:
                entry_widget.config(show='')

    entry_widget.bind("<FocusIn>", on_focus_in)
    entry_widget.bind("<FocusOut>", on_focus_out)

def add_text_placeholder(text_widget, placeholder):
    text_widget.insert("1.0", placeholder)
    text_widget.config(fg='grey')

    def on_focus_in(event):
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", "end")
            text_widget.config(fg='black')

    def on_focus_out(event):
        if not text_widget.get("1.0", "end-1c"):
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg='grey')

    text_widget.bind("<FocusIn>", on_focus_in)
    text_widget.bind("<FocusOut>", on_focus_out)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def submit_to_db():
    name = entry_1.get().strip()
    email = entry_2.get().strip()
    biography = entry_5.get("1.0", "end-1c").strip()
    password = entry_3.get()
    confirm_password = entry_4.get()

    placeholders = {
        "Full Name (e.g., Krish Gaba)": name,
        "Email (e.g., example@domain.com)": email,
        "Biography - How do you want to Lend a Hand? - at least 10 characters long": biography,
        "Password": password,
        "Confirm Password": confirm_password
    }

    for placeholder_text, value in placeholders.items():
        if not value or value == placeholder_text:
            messagebox.showwarning("Warning", f"Please fill in the field: {placeholder_text}")
            return

    if len(name) < 3 or len(name) > 255:
        messagebox.showwarning("Warning", "Name must be between 3 and 255 characters.")
        return

    if not is_valid_email(email):
        messagebox.showwarning("Warning", "Please enter a valid email address.")
        return

    if len(biography) < 10:
        messagebox.showwarning("Warning", "Biography must be at least 10 characters.")
        return

    if len(password) < 6:
        messagebox.showwarning("Warning", "Password must be at least 6 characters long.")
        return

    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    unique_user_id = str(uuid.uuid4())

    try:
        connection = mysql.connector.connect(
            host="sql5.freesqldatabase.com",
            user="sql5794100",
            password="BmzWGi52RK",
            database="sql5794100",
            port=3306
        )
        cursor = connection.cursor()
        try:
            cursor.execute("ALTER TABLE User_information ADD COLUMN unique_user_id VARCHAR(36) UNIQUE")
        except mysql.connector.Error as err:
            if err.errno in (1060, 1146):
                pass
            else:
                raise
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS User_information (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_user_id VARCHAR(36) UNIQUE,
                name VARCHAR(255),
                email VARCHAR(255),
                biography TEXT,
                password VARCHAR(255)
            )
        """)
        query = """
            INSERT INTO User_information (unique_user_id, name, email, biography, password)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (unique_user_id, name, email, biography, password))
        connection.commit()
        messagebox.showinfo("Success", f"Welcome to Lend a Hand, {name}!\nYour User ID:\n{unique_user_id}")
        cursor.close()
        connection.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"An error occurred:\n{e}")

def open_login():
    # Assumes login.py is one directory up, inside 'login' folder
    login_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "login", "login.py"))
    if os.path.exists(login_path):
        subprocess.Popen([sys.executable, login_path])
    else:
        messagebox.showerror("Error", f"Could not find login.py at:\n{login_path}")

window = Tk()
window.geometry("1440x960")
window.configure(bg="#FFFFFF")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=960,
    width=1440,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

image_image_1 = image_from_url(relative_to_assets("image_1.png"))
button_image_1 = image_from_url(relative_to_assets("button_1.png"))
button_image_2 = image_from_url(relative_to_assets("button_2.png"))
entry_image_1 = image_from_url(relative_to_assets("entry_1.png"))
entry_image_2 = image_from_url(relative_to_assets("entry_2.png"))
entry_image_3 = image_from_url(relative_to_assets("entry_3.png"))
entry_image_4 = image_from_url(relative_to_assets("entry_4.png"))
entry_image_5 = image_from_url(relative_to_assets("entry_5.png"))

window.image_image_1 = image_image_1
window.button_image_1 = button_image_1
window.button_image_2 = button_image_2
window.entry_image_1 = entry_image_1
window.entry_image_2 = entry_image_2
window.entry_image_3 = entry_image_3
window.entry_image_4 = entry_image_4
window.entry_image_5 = entry_image_5

canvas.create_image(720.0, 480.0, image=image_image_1)

button_1 = Button(
    window,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=submit_to_db,
    relief="flat"
)
button_1.place(x=78.0, y=750.0, width=380.0, height=75.0)

button_2 = Button(
    window,
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=open_login,
    relief="flat"
)
button_2.place(x=85.0, y=838.0, width=326.0, height=25.0)

entry_font = font.Font(family="Arial", size=14)
text_font = font.Font(family="Arial", size=14)

canvas.create_image(280.0, 265.0, image=entry_image_1)
entry_1 = Entry(window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, font=entry_font)
entry_1.place(x=105.0, y=240.0, width=350.0, height=48.0)
add_placeholder(entry_1, "Full Name (e.g., Krish Gaba)")

canvas.create_image(280.0, 355.0, image=entry_image_2)
entry_2 = Entry(window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, font=entry_font)
entry_2.place(x=105.0, y=330.0, width=350.0, height=48.0)
add_placeholder(entry_2, "Email (e.g., example@domain.com)")

canvas.create_image(280.0, 485.0, image=entry_image_5)
entry_5 = Text(window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, font=text_font)
entry_5.place(x=110.0, y=420.0, width=340.0, height=128.0)
add_text_placeholder(entry_5, "Biography - How do you want to Lend a Hand? - at least 10 characters long")

canvas.create_image(280.0, 600.0, image=entry_image_3)
entry_3 = Entry(window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, show="", font=entry_font)
entry_3.place(x=105.0, y=575.0, width=350.0, height=48.0)
add_placeholder(entry_3, "Password", is_password=True)

canvas.create_image(280.0, 680.0, image=entry_image_4)
entry_4 = Entry(window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, show="", font=entry_font)
entry_4.place(x=105.0, y=655.0, width=350.0, height=48.0)
add_placeholder(entry_4, "Confirm Password", is_password=True)

window.resizable(False, False)
window.mainloop()
