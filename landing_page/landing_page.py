import requests
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Button
import subprocess
import sys
import os

ASSET_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/landing_page/"

def image_from_url(filename, size=None):
    url = f"{ASSET_BASE_URL}{filename}"
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    if size:
        image = image.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(image)

def open_create_profile():
    # Path to create_profile.py one directory up in create_profile folder
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'create_profile', 'create_profile.py')
    # Use the same python executable to run the script
    subprocess.Popen([sys.executable, script_path])

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

image_image_1 = image_from_url("image_1.png")
canvas.create_image(720.0, 480.0, image=image_image_1)

button_image_1 = image_from_url("button_1.png", size=(564, 109))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=open_create_profile,
    relief="flat"
)
button_1.place(x=438.0, y=530.0, width=564.0, height=109.0)

window.resizable(False, False)
window.mainloop()
