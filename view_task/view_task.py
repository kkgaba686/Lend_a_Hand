import requests
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Text
from urllib.parse import quote

ASSETS_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/view_task/"

def image_from_url(filename):
    url = f"{ASSETS_BASE_URL}{quote(filename)}"
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return ImageTk.PhotoImage(image)

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

canvas.create_rectangle(0.0, 63.0, 411.0, 823.0, fill="#FFE347", outline="")

image_image_1 = image_from_url("image_1.png")
image_1 = canvas.create_image(205.0, 802.0, image=image_image_1)

image_image_2 = image_from_url("image_2.png")
image_2 = canvas.create_image(205.0, 31.0, image=image_image_2)

image_image_3 = image_from_url("image_3.png")
image_3 = canvas.create_image(204.0, 422.0, image=image_image_3)

entry_image_1 = image_from_url("entry_1.png")
entry_bg_1 = canvas.create_image(185.0, 215.0, image=entry_image_1)
entry_1 = Text(
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(x=60.0, y=190.0, width=250.0, height=48.0)

entry_image_2 = image_from_url("entry_2.png")
entry_bg_2 = canvas.create_image(205.5, 541.0, image=entry_image_2)
entry_2 = Text(
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_2.place(x=65.0, y=344.0, width=281.0, height=392.0)

image_image_4 = image_from_url("image_4.png")
image_4 = canvas.create_image(196.0, 130.0, image=image_image_4)

image_image_5 = image_from_url("image_5.png")
image_5 = canvas.create_image(163.0, 166.0, image=image_image_5)

image_image_6 = image_from_url("image_6.png")
image_6 = canvas.create_image(358.0, 214.0, image=image_image_6)

window.resizable(False, False)
window.mainloop()
