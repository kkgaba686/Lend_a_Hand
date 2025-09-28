import requests
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Button
import subprocess
import sys
import os

class LandingPage:
    """
    A tkinter-based landing page application for the Lend a Hand platform.
    Provides the entry point interface with navigation to profile creation.
    """
    
    ASSET_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/landing_page/"

    @staticmethod
    def image_from_url(filename, size=None):
        """
        Fetches and prepares an image from a remote URL for tkinter display.
        
        Args:
            filename (str): Name of the image file to fetch from base URL
            size (tuple, optional): Target dimensions as (width, height) for resizing
            
        Returns:
            ImageTk.PhotoImage: Image object ready for tkinter canvas placement
        """
        url = f"{LandingPage.ASSET_BASE_URL}{filename}"
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        if size:
            image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    @staticmethod
    def open_create_profile():
        """
        Launches the profile creation interface by executing the create_profile.py script.
        Uses the same Python interpreter and navigates to the adjacent directory.
        """
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'create_profile', 
            'create_profile.py'
        )
        subprocess.Popen([sys.executable, script_path])

    def __init__(self):
        """Initializes the main application window and UI components."""
        self.window = Tk()
        self.setup_window()
        self.canvas = self.create_canvas()
        self.setup_ui()
        
    def setup_window(self):
        """Configures the main window properties and dimensions."""
        self.window.geometry("1440x960")
        self.window.configure(bg="#FFFFFF")
        self.window.resizable(False, False)
        
    def create_canvas(self):
        """Creates and places the primary canvas for UI elements."""
        canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=960,
            width=1440,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def setup_ui(self):
        """Constructs the user interface with background image and interactive button."""
        # Background image
        self.image_image_1 = self.image_from_url("image_1.png")
        self.canvas.create_image(720.0, 480.0, image=self.image_image_1)
        
        # Primary action button
        self.button_image_1 = self.image_from_url("button_1.png", size=(564, 109))
        self.button_1 = Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.open_create_profile,
            relief="flat"
        )
        self.button_1.place(x=438.0, y=530.0, width=564.0, height=109.0)

    def run(self):
        """Starts the application's main event loop."""
        self.window.mainloop()

if __name__ == "__main__":
    app = LandingPage()
    app.run()