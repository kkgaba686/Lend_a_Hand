from tkinter import Tk, Canvas, Text, Button, messagebox, font
from tkinter import ttk
import requests
from io import BytesIO
from PIL import Image, ImageTk
import datetime
import uuid
import mysql.connector
import os

ASSETS_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/post_task"

connection = mysql.connector.connect(
    host="sql5.freesqldatabase.com",
    user="sql5790057",
    password="G1SxVVhcck",
    database="sql5790057"
)
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Task_information (
        id INT AUTO_INCREMENT PRIMARY KEY,
        unique_task_id VARCHAR(36) UNIQUE,
        unique_user_id VARCHAR(36),
        task_title VARCHAR(255),
        task_requirements_description TEXT,
        estimated_task_duration VARCHAR(255),
        task_date VARCHAR(50)
    )
""")

def image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    image_data = BytesIO(response.content)
    pil_image = Image.open(image_data)
    return ImageTk.PhotoImage(pil_image)

def relative_to_assets(filename: str) -> str:
    from urllib.parse import quote
    return f"{ASSETS_BASE_URL}/{quote(filename)}"

def add_text_placeholder(text_widget, placeholder):
    text_widget.insert("1.0", placeholder)
    text_widget.config(fg="grey")
    text_widget.bind("<FocusIn>", lambda e: clear_text_placeholder(text_widget, placeholder))
    text_widget.bind("<FocusOut>", lambda e: restore_text_placeholder(text_widget, placeholder))

def clear_text_placeholder(text_widget, placeholder):
    if text_widget.get("1.0", "end-1c") == placeholder:
        text_widget.delete("1.0", "end")
        text_widget.config(fg="black")

def restore_text_placeholder(text_widget, placeholder):
    if not text_widget.get("1.0", "end-1c"):
        text_widget.insert("1.0", placeholder)
        text_widget.config(fg="grey")

def get_logged_in_user_id():
    try:
        with open(os.path.join(os.path.dirname(__file__), "../login/session.txt"), "r") as file:
            return file.read().strip()
    except Exception:
        return None

def validate_and_submit():
    title = entry_1.get("1.0", "end-1c").strip()
    description = entry_4.get("1.0", "end-1c").strip()
    hours = entry_2.get("1.0", "end-1c").strip()
    minutes = entry_3.get("1.0", "end-1c").strip()
    preferred_date = date_combobox.get()

    if title == "Task Title (E.g., 'Mowing the lawn')" or not title:
        messagebox.showwarning("Validation", "Please enter a task title.")
        return
    if len(title) < 3:
        messagebox.showwarning("Validation", "Task title must be at least 3 characters.")
        return

    if description == "Task Requirements Description (Be specific - What do you need done? Any particular skills required? Location?)" or not description:
        messagebox.showwarning("Validation", "Please enter a task description.")
        return
    if len(description) < 10:
        messagebox.showwarning("Validation", "Task description must be at least 10 characters.")
        return

    if preferred_date == "Select a date":
        messagebox.showwarning("Validation", "Please select a preferred date.")
        return

    if not hours and not minutes:
        messagebox.showwarning("Validation", "Please enter an estimated task duration.")
        return

    estimated_task_duration = f"{hours}h {minutes}m".strip()
    unique_task_id = str(uuid.uuid4())
    unique_user_id = get_logged_in_user_id()

    if not unique_user_id:
        messagebox.showerror("Error", "No user session found. Please log in again.")
        return

    query = """
        INSERT INTO Task_information (
            unique_task_id,
            unique_user_id,
            task_title,
            task_requirements_description,
            estimated_task_duration,
            task_date
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (unique_task_id, unique_user_id, title, description, estimated_task_duration, preferred_date))
    connection.commit()

    messagebox.showinfo("Success", f"One hand, coming right up!\nYour unique task ID is: {unique_task_id}")

# --- GUI setup ---
window = Tk()
window.geometry("411x823")
window.configure(bg="#FFFFFF")
canvas = Canvas(window, bg="#FFFFFF", height=823, width=411, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

canvas.create_rectangle(0.0, 63.0, 411.0, 823.0, fill="#FFE347", outline="")

image_image_1 = image_from_url(relative_to_assets("image_1.png"))
image_image_2 = image_from_url(relative_to_assets("image_2.png"))
image_image_3 = image_from_url(relative_to_assets("image_3.png"))
image_image_4 = image_from_url(relative_to_assets("image_4.png"))
image_image_5 = image_from_url(relative_to_assets("image_5.png"))
image_image_6 = image_from_url(relative_to_assets("image_6.png"))
image_image_7 = image_from_url(relative_to_assets("image_7.png"))

entry_image_1 = image_from_url(relative_to_assets("entry_1.png"))
entry_image_2 = image_from_url(relative_to_assets("entry_2.png"))
entry_image_3 = image_from_url(relative_to_assets("entry_3.png"))
entry_image_4 = image_from_url(relative_to_assets("entry_4.png"))

button_image_1 = image_from_url(relative_to_assets("button_1.png"))

window.image_refs = [
    image_image_1, image_image_2, image_image_3, image_image_4,
    image_image_5, image_image_6, image_image_7,
    entry_image_1, entry_image_2, entry_image_3, entry_image_4,
    button_image_1
]

canvas.create_image(205.0, 802.0, image=image_image_1)
canvas.create_image(205.0, 31.0, image=image_image_2)
canvas.create_image(204.0, 370.0, image=image_image_3)
canvas.create_image(131.0, 127.0, image=image_image_4)
canvas.create_image(190.0, 163.0, image=image_image_5)
canvas.create_image(180.0, 612.0, image=image_image_6)
canvas.create_image(348.0, 612.0, image=image_image_7)

ENTRY_FONT = ("Arial", 12)

canvas.create_image(205.5, 215.0, image=entry_image_1)
entry_1 = Text(window, bd=0, bg="#D9D9D9", font=ENTRY_FONT, wrap="word", padx=10, pady=10, height=2)
entry_1.place(x=60.0, y=190.0, width=291.0, height=48.0)
add_text_placeholder(entry_1, "Task Title (E.g., 'Mowing the lawn')")

canvas.create_image(101.0, 613.0, image=entry_image_2)
entry_2 = Text(window, bd=0, bg="#D9D9D9", font=ENTRY_FONT, padx=10, pady=10, height=2)
entry_2.place(x=61.0, y=588.0, width=80.0, height=48.0)

canvas.create_image(262.0, 613.0, image=entry_image_3)
entry_3 = Text(window, bd=0, bg="#D9D9D9", font=ENTRY_FONT, padx=10, pady=10, height=2)
entry_3.place(x=222.0, y=588.0, width=80.0, height=48.0)

canvas.create_image(205.5, 413.0, image=entry_image_4)
entry_4 = Text(window, bd=0, bg="#D9D9D9", font=ENTRY_FONT, wrap="word", padx=10, pady=10)
entry_4.place(x=65.0, y=258.0, width=281.0, height=308.0)
add_text_placeholder(entry_4, "Task Requirements Description (Be specific - What do you need done? Any particular skills required? Location?)")

today = datetime.date.today()
days = [(today + datetime.timedelta(days=i)).strftime("%d %b %Y") for i in range(30)]

date_combobox = ttk.Combobox(window, values=days, font=ENTRY_FONT, state="readonly", width=26)
date_combobox.place(x=80, y=665)
date_combobox.set("Select a date")

button_1 = Button(
    window,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=validate_and_submit,
    relief="flat"
)
button_1.place(x=16.0, y=700.0, width=380.0, height=75.0)

window.resizable(False, False)
window.mainloop()

cursor.close()
connection.close()
