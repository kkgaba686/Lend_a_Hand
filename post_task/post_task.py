from tkinter import Tk, Canvas, Text, Button, messagebox, font
from tkinter import ttk
import requests
from io import BytesIO
from PIL import Image, ImageTk
import datetime
import uuid
import mysql.connector
import os

class PostTaskApp:
    """Main application class for posting tasks to the Lend a Hand platform."""
    
    ASSETS_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/post_task"
    
    def __init__(self):
        """Initialize the application with database connection and GUI setup."""
        self.setup_database()
        self.setup_gui()
        self.load_images()
        self.create_widgets()
        self.setup_event_handlers()
        
    def setup_database(self):
        """Establish database connection and ensure required tables/columns exist."""
        self.connection = mysql.connector.connect(
            host="sql5.freesqldatabase.com",
            user="sql5800183",
            password="M1cRUDEctC",
            database="sql5800183"
        )
        self.cursor = self.connection.cursor()
        
        # Create Task_information table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Task_information (
                unique_task_id VARCHAR(255) PRIMARY KEY,
                unique_user_id VARCHAR(255),
                task_title TEXT,
                task_requirements_description TEXT,
                estimated_task_duration VARCHAR(50)
            )
        """)
        self.connection.commit()
        
        # Add task_date column if missing
        self.cursor.execute("SHOW COLUMNS FROM Task_information LIKE 'task_date'")
        if not self.cursor.fetchone():
            self.cursor.execute("ALTER TABLE Task_information ADD COLUMN task_date VARCHAR(50)")
            self.connection.commit()

    def setup_gui(self):
        """Initialize the main application window and canvas."""
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
        self.canvas.create_rectangle(0.0, 63.0, 411.0, 823.0, fill="#FFE347", outline="")

    def load_images(self):
        """Load all required images from remote assets repository."""
        self.images = {}
        image_files = [
            "image_1.png", "image_2.png", "image_3.png", "image_4.png",
            "image_5.png", "image_6.png", "image_7.png",
            "entry_1.png", "entry_2.png", "entry_3.png", "entry_4.png",
            "button_1.png"
        ]
        
        for img_file in image_files:
            self.images[img_file] = self.image_from_url(self.relative_to_assets(img_file))
        
        # Store references to prevent garbage collection
        self.window.image_refs = list(self.images.values())

    def create_widgets(self):
        """Create and position all GUI widgets (text entries, buttons, combobox)."""
        # Background images
        self.canvas.create_image(205.0, 802.0, image=self.images["image_1.png"])
        self.canvas.create_image(205.0, 31.0, image=self.images["image_2.png"])
        self.canvas.create_image(204.0, 370.0, image=self.images["image_3.png"])
        self.canvas.create_image(131.0, 127.0, image=self.images["image_4.png"])
        self.canvas.create_image(190.0, 163.0, image=self.images["image_5.png"])
        self.canvas.create_image(180.0, 612.0, image=self.images["image_6.png"])
        self.canvas.create_image(348.0, 612.0, image=self.images["image_7.png"])
        
        # Text entry fields with placeholder support
        self.ENTRY_FONT = ("Arial", 12)
        self.create_text_entries()
        self.create_date_selector()
        self.create_submit_button()

    def create_text_entries(self):
        """Create and configure text entry widgets with placeholder functionality."""
        # Task title entry
        self.canvas.create_image(205.5, 215.0, image=self.images["entry_1.png"])
        self.entry_1 = Text(
            self.window, bd=0, bg="#D9D9D9", font=self.ENTRY_FONT, 
            wrap="word", padx=10, pady=10, height=2
        )
        self.entry_1.place(x=60.0, y=190.0, width=291.0, height=48.0)
        self.add_text_placeholder(self.entry_1, "Task Title (E.g., 'Mowing the lawn')")
        
        # Hours entry
        self.canvas.create_image(101.0, 613.0, image=self.images["entry_2.png"])
        self.entry_2 = Text(
            self.window, bd=0, bg="#D9D9D9", font=self.ENTRY_FONT, 
            padx=10, pady=10, height=2
        )
        self.entry_2.place(x=61.0, y=588.0, width=80.0, height=48.0)
        
        # Minutes entry
        self.canvas.create_image(262.0, 613.0, image=self.images["entry_3.png"])
        self.entry_3 = Text(
            self.window, bd=0, bg="#D9D9D9", font=self.ENTRY_FONT, 
            padx=10, pady=10, height=2
        )
        self.entry_3.place(x=222.0, y=588.0, width=80.0, height=48.0)
        
        # Task description entry
        self.canvas.create_image(205.5, 413.0, image=self.images["entry_4.png"])
        self.entry_4 = Text(
            self.window, bd=0, bg="#D9D9D9", font=self.ENTRY_FONT, 
            wrap="word", padx=10, pady=10
        )
        self.entry_4.place(x=65.0, y=258.0, width=281.0, height=308.0)
        self.add_text_placeholder(
            self.entry_4, 
            "Task Requirements Description (Be specific - What do you need done? Any particular skills required? Location?)"
        )

    def create_date_selector(self):
        """Create date selection combobox with next 30 days as options."""
        today = datetime.date.today()
        days = [(today + datetime.timedelta(days=i)).strftime("%d %b %Y") for i in range(30)]
        
        self.date_combobox = ttk.Combobox(
            self.window, values=days, font=self.ENTRY_FONT, 
            state="readonly", width=26
        )
        self.date_combobox.place(x=80, y=665)
        self.date_combobox.set("Select a date")

    def create_submit_button(self):
        """Create the main submission button."""
        self.button_1 = Button(
            self.window,
            image=self.images["button_1.png"],
            borderwidth=0,
            highlightthickness=0,
            command=self.validate_and_submit,
            relief="flat"
        )
        self.button_1.place(x=16.0, y=700.0, width=380.0, height=75.0)

    def setup_event_handlers(self):
        """Configure window properties and event handlers."""
        self.window.resizable(False, False)

    def run(self):
        """Start the main application loop."""
        self.window.mainloop()
        self.cleanup()

    def cleanup(self):
        """Clean up resources when application closes."""
        self.cursor.close()
        self.connection.close()

    @staticmethod
    def image_from_url(url):
        """Download and convert image from URL to Tkinter-compatible format."""
        response = requests.get(url)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        pil_image = Image.open(image_data)
        return ImageTk.PhotoImage(pil_image)

    @staticmethod
    def relative_to_assets(filename: str) -> str:
        """Generate full URL for asset file."""
        from urllib.parse import quote
        return f"{PostTaskApp.ASSETS_BASE_URL}/{quote(filename)}"

    def add_text_placeholder(self, text_widget, placeholder):
        """Add placeholder text to text widget with focus handlers."""
        text_widget.insert("1.0", placeholder)
        text_widget.config(fg="grey")
        text_widget.bind("<FocusIn>", lambda e: self.clear_text_placeholder(text_widget, placeholder))
        text_widget.bind("<FocusOut>", lambda e: self.restore_text_placeholder(text_widget, placeholder))

    @staticmethod
    def clear_text_placeholder(text_widget, placeholder):
        """Clear placeholder text when widget gains focus."""
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", "end")
            text_widget.config(fg="black")

    @staticmethod
    def restore_text_placeholder(text_widget, placeholder):
        """Restore placeholder text if widget is empty and loses focus."""
        if not text_widget.get("1.0", "end-1c"):
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg="grey")

    @staticmethod
    def get_logged_in_user_id():
        """Retrieve current user ID from session file."""
        try:
            file_path = os.path.join(os.path.dirname(__file__), "../login/session.txt")
            with open(file_path, "r") as file:
                return file.read().strip()
        except Exception:
            return None

    def validate_and_submit(self):
        """Validate form data and submit task to database."""
        # Extract and sanitize input values
        title = self.entry_1.get("1.0", "end-1c").strip()
        description = self.entry_4.get("1.0", "end-1c").strip()
        hours = self.entry_2.get("1.0", "end-1c").strip()
        minutes = self.entry_3.get("1.0", "end-1c").strip()
        preferred_date = self.date_combobox.get()

        # Validate task title
        if title == "Task Title (E.g., 'Mowing the lawn')" or not title:
            messagebox.showwarning("Validation", "Please enter a task title.")
            return
        if len(title) < 3:
            messagebox.showwarning("Validation", "Task title must be at least 3 characters.")
            return

        # Validate task description
        if description == "Task Requirements Description (Be specific - What do you need done? Any particular skills required? Location?)" or not description:
            messagebox.showwarning("Validation", "Please enter a task description.")
            return
        if len(description) < 10:
            messagebox.showwarning("Validation", "Task description must be at least 10 characters.")
            return

        # Validate date selection
        if preferred_date == "Select a date":
            messagebox.showwarning("Validation", "Please select a preferred date.")
            return

        # Validate duration input
        if not hours and not minutes:
            messagebox.showwarning("Validation", "Please enter an estimated task duration.")
            return

        # Prepare data for database insertion
        estimated_task_duration = f"{hours}h {minutes}m".strip()
        unique_task_id = str(uuid.uuid4())
        unique_user_id = self.get_logged_in_user_id()

        if not unique_user_id:
            messagebox.showerror("Error", "No user session found. Please log in again.")
            return

        # Insert task into database
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
        self.cursor.execute(query, (unique_task_id, unique_user_id, title, description, estimated_task_duration, preferred_date))
        self.connection.commit()

        messagebox.showinfo("Success", f"One hand, coming right up!\nYour unique task ID is: {unique_task_id}")


def main():
    """Main entry point for the Post Task application."""
    app = PostTaskApp()
    app.run()

if __name__ == "__main__":
    main()