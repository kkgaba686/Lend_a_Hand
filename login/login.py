"""
Login Application for Lend a Hand Platform
GUI-based authentication system supporting email and user ID login methods.
"""

import requests
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Entry, Button, StringVar, messagebox
import tkinter.font as tkFont
import mysql.connector

class LoginApplication:
    """Main application class handling user authentication and GUI management."""
    
    def __init__(self):
        """Initialize the application window and UI components."""
        self.setup_gui()
    
    def setup_gui(self):
        """Configure the main window, canvas, and all visual elements."""
        self.window = Tk()
        self.window.geometry("411x823")
        self.window.configure(bg="#FFFFFF")

        self.canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=823,
            width=411,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        self.canvas.create_rectangle(0.0, 230.0, 411.0, 823.0, fill="#FFE347", outline="")

        font_style = tkFont.Font(family="Arial", size=14)

        # Load and position decorative images
        image_image_1 = self.image_from_url("image_1.png")
        self.canvas.create_image(205.0, 116.0, image=image_image_1)

        image_image_2 = self.image_from_url("image_2.png")
        self.canvas.create_image(205.0, 802.0, image=image_image_2)

        image_image_3 = self.image_from_url("image_3.png")
        self.canvas.create_image(205.0, 31.0, image=image_image_3)

        image_image_4 = self.image_from_url("image_4.png")
        self.canvas.create_image(204.0, 454.0, image=image_image_4)

        # Login submission button
        button_image_1 = self.image_from_url("button_1.png")
        self.button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.login_user,
            relief="flat"
        )
        self.button_1.place(x=16.0, y=681.0, width=380.0, height=75.0)

        # Form container background
        self.canvas.create_rectangle(
            36.460784729942134,
            253.6444091796875,
            372.26978081203197,
            654.2305119613333,
            fill="#FAFAFA",
            outline=""
        )

        # Form header image
        image_image_5 = self.image_from_url("image_5.png")
        self.canvas.create_image(158.0, 291.0, image=image_image_5)

        # Email input field
        entry_image_1 = self.image_from_url("entry_1.png")
        self.canvas.create_image(205.5, 378.0, image=entry_image_1)
        self.entry_1 = Entry(bd=0, bg="#D9D9D9", fg="#000716", justify="center", font=font_style)
        self.entry_1.place(x=60.0, y=353.0, width=291.0, height=48.0)
        self.add_placeholder(self.entry_1, "Email (e.g., example@domain.com)")

        # Password field for email login
        entry_image_2 = self.image_from_url("entry_2.png")
        self.canvas.create_image(205.5, 446.0, image=entry_image_2)
        self.entry_2 = Entry(bd=0, bg="#D9D9D9", fg="#000716", justify="center", font=font_style)
        self.entry_2.place(x=60.0, y=421.0, width=291.0, height=48.0)
        self.add_placeholder(self.entry_2, "Password", is_password=True)

        # User ID input field
        entry_image_3 = self.image_from_url("entry_3.png")
        self.canvas.create_image(205.5, 545.0, image=entry_image_3)
        self.entry_3 = Entry(bd=0, bg="#D9D9D9", fg="#000716", justify="center", font=font_style)
        self.entry_3.place(x=60.0, y=520.0, width=291.0, height=48.0)
        self.add_placeholder(self.entry_3, "Assigned Unique User ID")

        # Password field for user ID login
        entry_image_4 = self.image_from_url("entry_4.png")
        self.canvas.create_image(205.5, 613.0, image=entry_image_4)
        self.entry_4 = Entry(bd=0, bg="#D9D9D9", fg="#000716", justify="center", font=font_style)
        self.entry_4.place(x=60.0, y=588.0, width=291.0, height=48.0)
        self.add_placeholder(self.entry_4, "Password", is_password=True)

        # Additional UI elements
        image_image_6 = self.image_from_url("image_6.png")
        self.canvas.create_image(204.0, 495.0, image=image_image_6)

        image_image_7 = self.image_from_url("image_7.png")
        self.canvas.create_image(312.5294189453125, 322.22021484375, image=image_image_7)

        image_image_8 = self.image_from_url("image_8.png")
        self.canvas.create_image(175.0, 328.0, image=image_image_8)

        self.window.resizable(False, False)
        self.window.mainloop()

    def image_from_url(self, filename):
        """
        Load image from remote URL and convert for Tkinter use.
        
        Args:
            filename: Image file name from assets repository
            
        Returns:
            ImageTk.PhotoImage: Tkinter-compatible image object
        """
        ASSETS_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/login/"
        url = f"{ASSETS_BASE_URL}{filename}"
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        return ImageTk.PhotoImage(image)

    def add_placeholder(self, entry, placeholder_text, is_password=False):
        """
        Add hint text to input fields that clears on focus.
        
        Args:
            entry: Tkinter Entry widget to enhance
            placeholder_text: Hint text to display when field is empty
            is_password: Whether field should mask input characters
        """
        entry.insert(0, placeholder_text)
        entry.config(fg='grey', show='')

        def on_focus_in(event):
            """Clear placeholder text when user selects the field"""
            if entry.get() == placeholder_text:
                entry.delete(0, "end")
                entry.config(fg='black')
                if is_password:
                    entry.config(show='*')

        def on_focus_out(event):
            """Restore placeholder if field remains empty"""
            if entry.get() == "":
                entry.insert(0, placeholder_text)
                entry.config(fg='grey')
                if is_password:
                    entry.config(show='')

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def login_user(self):
        """
        Authenticate user credentials against database records.
        
        Supports dual login methods: email/password or user ID/password.
        Saves successful login session to file for persistence.
        """
        # Retrieve and clean user inputs
        email_input = self.entry_1.get().strip()
        password_input_email = self.entry_2.get().strip()
        user_id_input = self.entry_3.get().strip()
        password_input_uid = self.entry_4.get().strip()

        # Validate at least one login method is provided
        if email_input == "" and user_id_input == "":
            messagebox.showwarning("Input Error", "Please enter either Email or Unique User ID.")
            return

        try:
            # Establish database connection
            conn = mysql.connector.connect(
                host="sql5.freesqldatabase.com",
                user="sql5800183",
                password="M1cRUDEctC",
                database="sql5800183",
                port=3306
            )
            cursor = conn.cursor()

            # Query for email or user ID authentication
            query = """
                SELECT name, unique_user_id FROM User_information 
                WHERE (email = %s AND password = %s)
                   OR (unique_user_id = %s AND password = %s)
                LIMIT 1
            """
            cursor.execute(query, (email_input, password_input_email, user_id_input, password_input_uid))
            result = cursor.fetchone()

            if result:
                # Successful authentication
                name, unique_id = result
                with open("session.txt", "w") as f:
                    f.write(unique_id)
                messagebox.showinfo("Login Success", f"Welcome, {name}.")
            else:
                messagebox.showerror("Login Failed", "Incorrect credentials. Please try again.")

            cursor.close()
            conn.close()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"An error occurred:\n{e}")


# Start the application
if __name__ == "__main__":
    app = LoginApplication()