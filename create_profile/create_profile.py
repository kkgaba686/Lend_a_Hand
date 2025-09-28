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

class ProfileCreator:
    """Main application class for creating user profiles in the Lend a Hand system."""
    
    @staticmethod
    def image_from_url(url):
        """
        Fetch and convert an image from a URL to a Tkinter-compatible format.
        
        Args:
            url (str): The URL of the image to load
            
        Returns:
            ImageTk.PhotoImage: The loaded image ready for Tkinter use
        """
        response = requests.get(url)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        pil_image = Image.open(image_data)
        return ImageTk.PhotoImage(pil_image)

    @staticmethod
    def relative_to_assets(filename: str) -> str:
        """
        Generate full URL for assets stored in the GitHub repository.
        
        Args:
            filename (str): Name of the asset file
            
        Returns:
            str: Complete URL to the asset file
        """
        encoded_filename = quote(filename)
        return f"{ASSETS_BASE_URL}/{encoded_filename}"

    @staticmethod
    def add_placeholder(entry_widget, placeholder, is_password=False):
        """
        Add placeholder text functionality to an Entry widget.
        
        Args:
            entry_widget (Entry): The Entry widget to add placeholder to
            placeholder (str): The placeholder text to display
            is_password (bool): Whether this is a password field
        """
        entry_widget.insert(0, placeholder)
        entry_widget.config(fg='grey')
        if is_password:
            entry_widget.config(show='')

        def on_focus_in(event):
            """Clear placeholder text when widget gains focus."""
            if entry_widget.get() == placeholder:
                entry_widget.delete(0, 'end')
                entry_widget.config(fg='black')
                if is_password:
                    entry_widget.config(show='*')

        def on_focus_out(event):
            """Restore placeholder text when widget loses focus and is empty."""
            if not entry_widget.get():
                entry_widget.insert(0, placeholder)
                entry_widget.config(fg='grey')
                if is_password:
                    entry_widget.config(show='')

        entry_widget.bind("<FocusIn>", on_focus_in)
        entry_widget.bind("<FocusOut>", on_focus_out)

    @staticmethod
    def add_text_placeholder(text_widget, placeholder):
        """
        Add placeholder text functionality to a Text widget.
        
        Args:
            text_widget (Text): The Text widget to add placeholder to
            placeholder (str): The placeholder text to display
        """
        text_widget.insert("1.0", placeholder)
        text_widget.config(fg='grey')

        def on_focus_in(event):
            """Clear placeholder text when widget gains focus."""
            if text_widget.get("1.0", "end-1c") == placeholder:
                text_widget.delete("1.0", "end")
                text_widget.config(fg='black')

        def on_focus_out(event):
            """Restore placeholder text when widget loses focus and is empty."""
            if not text_widget.get("1.0", "end-1c"):
                text_widget.insert("1.0", placeholder)
                text_widget.config(fg='grey')

        text_widget.bind("<FocusIn>", on_focus_in)
        text_widget.bind("<FocusOut>", on_focus_out)

    @staticmethod
    def is_valid_email(email):
        """
        Validate email format using regular expression.
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if email format is valid, False otherwise
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def __init__(self):
        """Initialize the profile creation window and UI components."""
        self.window = Tk()
        self.setup_window()
        self.setup_canvas()
        self.load_assets()
        self.create_ui_elements()
        self.setup_event_handlers()
        
    def submit_to_db(self):
        """Handle form submission with validation and database insertion."""
        # Retrieve and clean form data
        name = self.entry_1.get().strip()
        email = self.entry_2.get().strip()
        biography = self.entry_5.get("1.0", "end-1c").strip()
        password = self.entry_3.get()
        confirm_password = self.entry_4.get()

        # Define placeholder texts for validation
        placeholders = {
            "Full Name (e.g., Krish Gaba)": name,
            "Email (e.g., example@domain.com)": email,
            "Biography - How do you want to Lend a Hand? - at least 10 characters long": biography,
            "Password": password,
            "Confirm Password": confirm_password
        }

        # Validate that all fields are filled
        for placeholder_text, value in placeholders.items():
            if not value or value == placeholder_text:
                messagebox.showwarning("Warning", f"Please fill in the field: {placeholder_text}")
                return

        # Validate name length
        if len(name) < 3 or len(name) > 255:
            messagebox.showwarning("Warning", "Name must be between 3 and 255 characters.")
            return

        # Validate email format
        if not self.is_valid_email(email):
            messagebox.showwarning("Warning", "Please enter a valid email address.")
            return

        # Validate biography length
        if len(biography) < 10:
            messagebox.showwarning("Warning", "Biography must be at least 10 characters.")
            return

        # Validate password length
        if len(password) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters long.")
            return

        # Validate password match
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Generate unique user identifier
        unique_user_id = str(uuid.uuid4())

        # Database operations
        try:
            connection = mysql.connector.connect(
                host="sql5.freesqldatabase.com",
                user="sql5800183",
                password="M1cRUDEctC",
                database="sql5800183",
                port=3306
            )
            cursor = connection.cursor()
            
            # Ensure unique_user_id column exists
            try:
                cursor.execute("ALTER TABLE User_information ADD COLUMN unique_user_id VARCHAR(36) UNIQUE")
            except mysql.connector.Error as err:
                # Ignore errors if column already exists or table doesn't exist
                if err.errno in (1060, 1146):
                    pass
                else:
                    raise
            
            # Create table if it doesn't exist
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
            
            # Insert new user record
            query = """
                INSERT INTO User_information (unique_user_id, name, email, biography, password)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (unique_user_id, name, email, biography, password))
            connection.commit()
            
            # Success message with user ID
            messagebox.showinfo("Success", f"Welcome to Lend a Hand, {name}!\nYour User ID:\n{unique_user_id}")
            
            cursor.close()
            connection.close()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"An error occurred:\n{e}")

    def open_login(self):
        """Open the login window by executing the login.py script."""
        login_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "login", "login.py"))
        if os.path.exists(login_path):
            subprocess.Popen([sys.executable, login_path])
        else:
            messagebox.showerror("Error", f"Could not find login.py at:\n{login_path}")

    def setup_window(self):
        """Configure the main application window properties."""
        self.window.geometry("1440x960")
        self.window.configure(bg="#FFFFFF")
        self.window.resizable(False, False)

    def setup_canvas(self):
        """Create and configure the main canvas for the application."""
        self.canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=960,
            width=1440,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

    def load_assets(self):
        """Load all required images from remote assets repository."""
        self.image_image_1 = ProfileCreator.image_from_url(ProfileCreator.relative_to_assets("image_1.png"))
        self.button_image_1 = ProfileCreator.image_from_url(ProfileCreator.relative_to_assets("button_1.png"))
        self.button_image_2 = ProfileCreator.image_from_url(ProfileCreator.relative_to_assets("button_2.png"))
        self.entry_image_1 = ProfileCreator.image_from_url(ProfileCreator.relative_to_assets("entry_1.png"))
        self.entry_image_2 = ProfileCreator.image_from_url(ProfileCreator.relative_to_assets("entry_2.png"))
        self.entry_image_3 = ProfileCreator.image_from_url(ProfileCreator.relative_to_assets("entry_3.png"))
        self.entry_image_4 = ProfileCreator.image_from_url(ProfileCreator.relative_to_assets("entry_4.png"))
        self.entry_image_5 = ProfileCreator.image_from_url(ProfileCreator.relative_to_assets("entry_5.png"))

        # Store images as window attributes to prevent garbage collection
        self.window.image_image_1 = self.image_image_1
        self.window.button_image_1 = self.button_image_1
        self.window.button_image_2 = self.button_image_2
        self.window.entry_image_1 = self.entry_image_1
        self.window.entry_image_2 = self.entry_image_2
        self.window.entry_image_3 = self.entry_image_3
        self.window.entry_image_4 = self.entry_image_4
        self.window.entry_image_5 = self.entry_image_5

    def create_ui_elements(self):
        """Create and position all UI elements on the canvas."""
        # Background image
        self.canvas.create_image(720.0, 480.0, image=self.image_image_1)

        # Submit button
        self.button_1 = Button(
            self.window,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.submit_to_db,
            relief="flat"
        )
        self.button_1.place(x=78.0, y=750.0, width=380.0, height=75.0)

        # Login redirect button
        self.button_2 = Button(
            self.window,
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.open_login,
            relief="flat"
        )
        self.button_2.place(x=85.0, y=838.0, width=326.0, height=25.0)

        # Configure fonts for form elements
        entry_font = font.Font(family="Arial", size=14)
        text_font = font.Font(family="Arial", size=14)

        # Name entry field
        self.canvas.create_image(280.0, 265.0, image=self.entry_image_1)
        self.entry_1 = Entry(self.window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, font=entry_font)
        self.entry_1.place(x=105.0, y=240.0, width=350.0, height=48.0)
        ProfileCreator.add_placeholder(self.entry_1, "Full Name (e.g., Krish Gaba)")

        # Email entry field
        self.canvas.create_image(280.0, 355.0, image=self.entry_image_2)
        self.entry_2 = Entry(self.window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, font=entry_font)
        self.entry_2.place(x=105.0, y=330.0, width=350.0, height=48.0)
        ProfileCreator.add_placeholder(self.entry_2, "Email (e.g., example@domain.com)")

        # Biography text area
        self.canvas.create_image(280.0, 485.0, image=self.entry_image_5)
        self.entry_5 = Text(self.window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, font=text_font)
        self.entry_5.place(x=110.0, y=420.0, width=340.0, height=128.0)
        ProfileCreator.add_text_placeholder(self.entry_5, "Biography - How do you want to Lend a Hand? - at least 10 characters long")

        # Password entry field
        self.canvas.create_image(280.0, 600.0, image=self.entry_image_3)
        self.entry_3 = Entry(self.window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, show="", font=entry_font)
        self.entry_3.place(x=105.0, y=575.0, width=350.0, height=48.0)
        ProfileCreator.add_placeholder(self.entry_3, "Password", is_password=True)

        # Password confirmation field
        self.canvas.create_image(280.0, 680.0, image=self.entry_image_4)
        self.entry_4 = Entry(self.window, bd=0, bg="#D9D9D9", fg="grey", highlightthickness=0, show="", font=entry_font)
        self.entry_4.place(x=105.0, y=655.0, width=350.0, height=48.0)
        ProfileCreator.add_placeholder(self.entry_4, "Confirm Password", is_password=True)

    def setup_event_handlers(self):
        """Set up any additional event handlers if needed."""
        # Currently handled within placeholder functions
        pass

    def run(self):
        """Start the main application event loop."""
        self.window.mainloop()

# Application entry point
if __name__ == "__main__":
    app = ProfileCreator()
    app.run()