import requests
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Entry, Button, StringVar, messagebox
import tkinter.font as tkFont
import mysql.connector

ASSETS_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/login/"

def image_from_url(filename):
    url = f"{ASSETS_BASE_URL}{filename}"
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return ImageTk.PhotoImage(image)

def add_placeholder(entry, placeholder_text, is_password=False):
    entry.insert(0, placeholder_text)
    entry.config(fg='grey', show='')

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, "end")
            entry.config(fg='black')
            if is_password:
                entry.config(show='*')

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder_text)
            entry.config(fg='grey')
            if is_password:
                entry.config(show='')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def login_user():
    email_input = entry_1.get().strip()
    password_input_email = entry_2.get().strip()
    user_id_input = entry_3.get().strip()
    password_input_uid = entry_4.get().strip()

    if email_input == "" and user_id_input == "":
        messagebox.showwarning("Input Error", "Please enter either Email or Unique User ID.")
        return

    try:
        conn = mysql.connector.connect(
            host="sql5.freesqldatabase.com",
            user="sql5790057",
            password="G1SxVVhcck",
            database="sql5790057",
            port=3306
        )
        cursor = conn.cursor()

        query = """
            SELECT name FROM User_information 
            WHERE (email = %s AND password = %s)
               OR (unique_user_id = %s AND password = %s)
            LIMIT 1
        """
        cursor.execute(query, (email_input, password_input_email, user_id_input, password_input_uid))
        result = cursor.fetchone()

        if result:
            name = result[0]
            messagebox.showinfo("Login Success", f"Welcome, {name}.")
        else:
            messagebox.showerror("Login Failed", "Incorrect credentials. Please try again.")

        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"An error occurred:\n{e}")

# --- GUI ---
window = Tk()
window.geometry("411x823")
window.configure(bg="#FFFFFF")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=823,
    width=411,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

canvas.create_rectangle(0.0, 230.0, 411.0, 823.0, fill="#FFE347", outline="")

font_style = tkFont.Font(family="Arial", size=14)

image_image_1 = image_from_url("image_1.png")
image_1 = canvas.create_image(205.0, 116.0, image=image_image_1)

image_image_2 = image_from_url("image_2.png")
image_2 = canvas.create_image(205.0, 802.0, image=image_image_2)

image_image_3 = image_from_url("image_3.png")
image_3 = canvas.create_image(205.0, 31.0, image=image_image_3)

image_image_4 = image_from_url("image_4.png")
image_4 = canvas.create_image(204.0, 454.0, image=image_image_4)

button_image_1 = image_from_url("button_1.png")
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=login_user,
    relief="flat"
)
button_1.place(x=16.0, y=681.0, width=380.0, height=75.0)

canvas.create_rectangle(
    36.460784729942134,
    253.6444091796875,
    372.26978081203197,
    654.2305119613333,
    fill="#FAFAFA",
    outline=""
)

image_image_5 = image_from_url("image_5.png")
image_5 = canvas.create_image(158.0, 291.0, image=image_image_5)

entry_image_1 = image_from_url("entry_1.png")
entry_bg_1 = canvas.create_image(205.5, 378.0, image=entry_image_1)
entry_1 = Entry(bd=0, bg="#D9D9D9", fg="#000716", justify="center", font=font_style)
entry_1.place(x=60.0, y=353.0, width=291.0, height=48.0)
add_placeholder(entry_1, "Email (e.g., example@domain.com)")

entry_image_2 = image_from_url("entry_2.png")
entry_bg_2 = canvas.create_image(205.5, 446.0, image=entry_image_2)
entry_2 = Entry(bd=0, bg="#D9D9D9", fg="#000716", justify="center", font=font_style)
entry_2.place(x=60.0, y=421.0, width=291.0, height=48.0)
add_placeholder(entry_2, "Password", is_password=True)

entry_image_3 = image_from_url("entry_3.png")
entry_bg_3 = canvas.create_image(205.5, 545.0, image=entry_image_3)
entry_3 = Entry(bd=0, bg="#D9D9D9", fg="#000716", justify="center", font=font_style)
entry_3.place(x=60.0, y=520.0, width=291.0, height=48.0)
add_placeholder(entry_3, "Assigned Unique User ID")

entry_image_4 = image_from_url("entry_4.png")
entry_bg_4 = canvas.create_image(205.5, 613.0, image=entry_image_4)
entry_4 = Entry(bd=0, bg="#D9D9D9", fg="#000716", justify="center", font=font_style)
entry_4.place(x=60.0, y=588.0, width=291.0, height=48.0)
add_placeholder(entry_4, "Password", is_password=True)

image_image_6 = image_from_url("image_6.png")
image_6 = canvas.create_image(204.0, 495.0, image=image_image_6)

image_image_7 = image_from_url("image_7.png")
image_7 = canvas.create_image(312.5294189453125, 322.22021484375, image=image_image_7)

image_image_8 = image_from_url("image_8.png")
image_8 = canvas.create_image(175.0, 328.0, image=image_image_8)

window.resizable(False, False)
window.mainloop()
