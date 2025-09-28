# -*- coding: utf-8 -*-
import requests
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Canvas, Frame, Label, Scrollbar, Entry, messagebox, StringVar, Button, ttk, Text, Toplevel
import tkinter.font as tkFont
import mysql.connector
from urllib.parse import quote
from functools import partial
from datetime import datetime, date
from tkcalendar import DateEntry
import re
import unicodedata
import os

# Configuration constants
ASSETS_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/view_task/"
DB_CONFIG = {
    'host': "sql5.freesqldatabase.com",
    'user': "sql5800183",
    'password': "M1cRUDEctC",
    'database': "sql5800183",
    'port': 3306
}

# Session management functions
def get_current_user_id():
    """Get current logged-in user ID from session file"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        session_file = os.path.join(parent_dir, "login", "session.txt")
        
        with open(session_file, 'r') as f:
            user_id = f.read().strip()
        return user_id
    except Exception as e:
        print(f"Error reading session: {e}")
        return None

def get_user_balance(user_id):
    """Get current balance for a user"""
    try:
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT Balance FROM User_information WHERE unique_user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result['Balance'] if result and 'Balance' in result else 0
    except Exception as e:
        print(f"Error getting user balance: {e}")
        return 0

# Database connection helper
def db_connect():
    return mysql.connector.connect(**DB_CONFIG)

def ensure_tables_updated():
    """Ensure database has required columns for task management"""
    try:
        conn = db_connect()
        cursor = conn.cursor()
        
        # Add Balance column if missing
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_information' AND COLUMN_NAME = 'Balance'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE User_information ADD COLUMN Balance INT DEFAULT 0")
        
        # Add task assignment and completion columns if missing
        columns_to_add = [
            ('unique_worker_id', "ALTER TABLE Task_information ADD COLUMN unique_worker_id VARCHAR(255)"),
            ('task_completion_worker', "ALTER TABLE Task_information ADD COLUMN task_completion_worker BOOLEAN DEFAULT FALSE"),
            ('task_completion_poster', "ALTER TABLE Task_information ADD COLUMN task_completion_poster BOOLEAN DEFAULT FALSE")
        ]
        
        for col_name, alter_sql in columns_to_add:
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Task_information' AND COLUMN_NAME = '{col_name}'")
            if not cursor.fetchone():
                cursor.execute(alter_sql)
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Table update warning: {e}")

def fetch_tasks(filter_type="all", current_user_id=None):
    """Fetch tasks based on filter type and current user"""
    try:
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        
        base_query = """
            SELECT
                t.task_title,
                t.task_requirements_description,
                t.estimated_task_duration,
                DATE(t.task_date) AS task_date,
                t.unique_task_id,
                t.unique_worker_id,
                t.task_completion_worker,
                t.task_completion_poster,
                u.name,
                t.unique_user_id as poster_id
            FROM Task_information AS t
            LEFT JOIN User_information AS u
                ON t.unique_user_id = u.unique_user_id
        """
        
        where_clause = ""
        params = []
        
        if filter_type == "my_tasks" and current_user_id:
            where_clause = " WHERE t.unique_user_id = %s"
            params = [current_user_id]
        elif filter_type == "accepted_tasks" and current_user_id:
            where_clause = " WHERE t.unique_worker_id = %s"
            params = [current_user_id]
        elif filter_type == "available_tasks" and current_user_id:
            where_clause = " WHERE (t.unique_worker_id IS NULL OR t.unique_worker_id = '') AND t.unique_user_id != %s"
            params = [current_user_id]
        
        query = base_query + where_clause + " ORDER BY t.task_date DESC;"
        cursor.execute(query, params)
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()

        # Normalize task data
        for task in tasks:
            if not task.get("name"):
                task["name"] = "Unknown User"
            if not task.get("task_title"):
                task["task_title"] = "Untitled Task"

            # Handle date formatting
            task_date = task.get("task_date")
            if isinstance(task_date, (datetime, date)):
                task["task_date"] = task_date.date() if isinstance(task_date, datetime) else task_date
            else:
                try:
                    if task_date is None:
                        task["task_date"] = None
                    else:
                        task["task_date"] = datetime.strptime(str(task_date), "%Y-%m-%d").date()
                except Exception:
                    task["task_date"] = None

            # Handle duration formatting
            if task.get("estimated_task_duration") is None:
                task["estimated_task_duration"] = ""
            else:
                task["estimated_task_duration"] = str(task["estimated_task_duration"])
                
            # Ensure boolean fields are properly set
            task["task_completion_worker"] = bool(task.get("task_completion_worker"))
            task["task_completion_poster"] = bool(task.get("task_completion_poster"))
            
        return tasks

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Could not fetch tasks.\nError: {e}")
        return []

def assign_task_to_worker(task_id, worker_id):
    """Assign a task to a worker"""
    try:
        conn = db_connect()
        cursor = conn.cursor()
        query = "UPDATE Task_information SET unique_worker_id = %s WHERE unique_task_id = %s"
        cursor.execute(query, (worker_id, task_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not assign task.\nError: {e}")
        return False

def unassign_task(task_id):
    """Remove worker assignment from a task"""
    try:
        conn = db_connect()
        cursor = conn.cursor()
        query = "UPDATE Task_information SET unique_worker_id = NULL WHERE unique_task_id = %s"
        cursor.execute(query, (task_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not unassign task.\nError: {e}")
        return False

def approve_task_completion(task_id, user_type, current_user_id):
    """Approve task completion and process payment if both parties agree"""
    try:
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        
        # Get task details for permission checking
        cursor.execute("SELECT * FROM Task_information WHERE unique_task_id = %s", (task_id,))
        task = cursor.fetchone()
        
        if not task:
            return False, "Task not found"
        
        # Verify user has permission to approve
        if user_type == "worker" and task['unique_worker_id'] != current_user_id:
            return False, "Only the assigned worker can approve completion"
        elif user_type == "poster" and task['unique_user_id'] != current_user_id:
            return False, "Only the task poster can approve completion"
        
        # Update completion status
        if user_type == "worker":
            query = "UPDATE Task_information SET task_completion_worker = TRUE WHERE unique_task_id = %s"
        else:
            query = "UPDATE Task_information SET task_completion_poster = TRUE WHERE unique_task_id = %s"
        
        cursor.execute(query, (task_id,))
        conn.commit()
        
        # Check if both parties approved
        cursor.execute("SELECT task_completion_worker, task_completion_poster FROM Task_information WHERE unique_task_id = %s", (task_id,))
        updated_task = cursor.fetchone()
        
        if updated_task['task_completion_worker'] and updated_task['task_completion_poster']:
            # Process payment - 1 time currency per hour
            duration_minutes = parse_duration_to_minutes(task['estimated_task_duration'])
            time_currency = max(1, duration_minutes // 60)
            
            # Update balances
            cursor.execute("UPDATE User_information SET Balance = Balance + %s WHERE unique_user_id = %s", 
                          (time_currency, task['unique_worker_id']))
            cursor.execute("UPDATE User_information SET Balance = Balance - %s WHERE unique_user_id = %s", 
                          (time_currency, task['unique_user_id']))
            conn.commit()
            
            cursor.close()
            conn.close()
            return True, f"Payment processed! {time_currency} time currency transferred."
        
        cursor.close()
        conn.close()
        return True, "Approval recorded. Waiting for other party to approve."
        
    except Exception as e:
        return False, f"Error: {str(e)}"

# Comment/communication system functions
def ensure_communication_table_exists():
    """Create communication log table if it doesn't exist"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS Communication_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        unique_task_id VARCHAR(255) NOT NULL,
        unique_user_id VARCHAR(255),
        comment_text TEXT NOT NULL,
        created_at DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(create_sql)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

def fetch_comments_for_task(unique_task_id):
    """Get all comments for a specific task"""
    try:
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT c.id, c.unique_task_id, c.unique_user_id, c.comment_text, c.created_at, u.name
            FROM Communication_log c
            LEFT JOIN User_information u ON c.unique_user_id = u.unique_user_id
            WHERE c.unique_task_id = %s
            ORDER BY c.created_at ASC
        """
        cursor.execute(query, (str(unique_task_id),))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for row in rows:
            if not row.get('name'):
                row['name'] = 'Unknown User'
            if not row.get('created_at'):
                row['created_at'] = datetime.now()
        return rows
    except Exception as e:
        print("fetch_comments_for_task error:", e)
        return []

def insert_comment(unique_task_id, unique_user_id, comment_text):
    """Add a new comment to the communication log"""
    if comment_text is None or not str(comment_text).strip():
        return False
    try:
        ensure_communication_table_exists()
        conn = db_connect()
        cursor = conn.cursor()
        query = "INSERT INTO Communication_log (unique_task_id, unique_user_id, comment_text, created_at) VALUES (%s, %s, %s, %s)"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(query, (str(unique_task_id), unique_user_id, comment_text.strip(), now))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not save comment.\nError: {e}")
        return False

def fetch_all_users():
    """Get all users for comment dropdown"""
    try:
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT unique_user_id, name FROM User_information ORDER BY name ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows if rows else []
    except Exception:
        return []

def parse_duration_to_minutes(duration_str):
    """Convert duration string to minutes"""
    if duration_str is None:
        return 0
    duration_str = str(duration_str).lower().strip()

    if re.fullmatch(r'\d+', duration_str):
        return int(duration_str)

    # Parse hours and minutes
    h_match = re.search(r'(\d+)\s*h(?:ou)?', duration_str)
    m_match = re.search(r'(\d+)\s*m(?:in)?', duration_str)
    hours = int(h_match.group(1)) if h_match else 0
    minutes = int(m_match.group(1)) if m_match else 0

    # Fallback for simple number parsing
    if hours == 0 and minutes == 0:
        num_match = re.search(r'(\d+)', duration_str)
        if num_match:
            minutes = int(num_match.group(1))

    return hours * 60 + minutes

def normalize_str(text):
    """Normalize string for comparison"""
    if text is None:
        return ""
    text = str(text)
    return unicodedata.normalize("NFKD", text).casefold()

# Main application class
class TaskViewerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Lend a Hand")
        self.master.geometry("411x823")
        self.master.resizable(False, False)

        # Initialize database and user session
        ensure_tables_updated()
        self.current_user_id = get_current_user_id()
        self.current_balance = get_user_balance(self.current_user_id) if self.current_user_id else 0
        
        # Task data and UI state
        self.all_tasks = fetch_tasks("all", self.current_user_id)
        self.image_references = {}
        self.current_filter = "all"

        self.setup_fonts()

        # Main application frames
        self.main_view_frame = Frame(self.master)
        self.detail_view_frame = Frame(self.master, bg="#FFFFFF")

        self.setup_main_view()
        self.main_view_frame.pack(fill="both", expand=True)

    def setup_fonts(self):
        """Define application fonts"""
        self.font_task_title = tkFont.Font(family="Arial", size=14, weight="bold")
        self.font_task_body = tkFont.Font(family="Arial", size=12)
        self.font_task_small = tkFont.Font(family="Arial", size=10)
        self.font_task_date = tkFont.Font(family="Arial", size=12, weight="bold")
        self.font_detail_title = tkFont.Font(family="Arial", size=18, weight="bold")
        self.font_detail_header = tkFont.Font(family="Arial", size=14, weight="bold")

    def _load_image(self, filename, key):
        """Load image from assets URL"""
        try:
            url = f"{ASSETS_BASE_URL}{quote(filename)}"
            response = requests.get(url, timeout=6)
            response.raise_for_status()
            img_data = Image.open(BytesIO(response.content))
            photo_img = ImageTk.PhotoImage(img_data)
            self.image_references[key] = photo_img
            return photo_img
        except Exception:
            return None

    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, r, **kwargs):
        """Create rounded rectangle shape on canvas"""
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1,
            x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2,
            x1, y2 - r, x1, y1 + r, x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def setup_main_view(self):
        """Setup main task listing view"""
        canvas = Canvas(self.main_view_frame, bg="#FFFFFF", height=823, width=411, bd=0, highlightthickness=0, relief="ridge")
        canvas.pack(fill="both", expand=True)
        canvas.create_rectangle(0, 63, 411, 823, fill="#FFE347", outline="")

        # Load and place UI assets
        asset_placements = {
            "image_2.png": (205, 31), "image_4.png": (196, 130),
            "image_5.png": (163, 166), "entry_1.png": (185, 215),
            "image_3.png": (204, 590),
            "image_6.png": (358, 214), "image_1.png": (205, 802)
        }
        for filename, (x, y) in asset_placements.items():
            img = self._load_image(filename, filename)
            if img:
                canvas.create_image(x, y, image=img)

        # Display user balance
        balance_text = f"Balance: {self.current_balance}"
        canvas.create_text(350, 80, text=balance_text, font=("Arial", 12, "bold"), fill="#000000")

        # Search functionality
        self.search_var = StringVar()
        self.search_var.trace_add("write", lambda *a: self._apply_filters())

        search_entry = Entry(self.main_view_frame, textvariable=self.search_var, font=("Arial", 14), bd=0, relief="flat", bg="#D9D9D9")
        canvas.create_window(185, 215, window=search_entry, width=230, height=40)
        search_entry.bind("<Return>", lambda e: self._apply_filters())

        # Tasks container with scrolling
        self.container_canvas = Canvas(self.main_view_frame, bg="#D9D9D9", width=370, height=520, bd=0, highlightthickness=0)
        self._create_rounded_rectangle(self.container_canvas, 2, 2, 368, 518, r=20, fill="#D9D9D9", outline="#CCCCCC")
        canvas.create_window(205, 260, window=self.container_canvas, anchor="n")

        self.container_inner_frame = Frame(self.container_canvas, bg="#D9D9D9")
        self.container_canvas.create_window(0, 0, window=self.container_inner_frame, anchor="nw", width=370, height=520)

        self._setup_filter_controls(self.container_inner_frame)

        # Scrollable task list area
        task_scroll_container = Frame(self.container_inner_frame, bg="#D9D9D9")
        task_scroll_container.pack(fill="both", expand=True)

        self.task_canvas = Canvas(task_scroll_container, bg="#D9D9D9", highlightthickness=0)
        scrollbar = Scrollbar(task_scroll_container, orient="vertical", command=self.task_canvas.yview)
        self.scrollable_frame = Frame(self.task_canvas, bg="#D9D9D9")

        self.scrollable_frame.bind("<Configure>", lambda e: self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all")))

        def _on_mousewheel(event):
            self.task_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.task_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.task_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=350)
        self.task_canvas.configure(yscrollcommand=scrollbar.set)

        self.task_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._populate_task_list(self.all_tasks)

    def _setup_filter_controls(self, parent_frame):
        """Setup task filtering controls"""
        filter_frame = Frame(parent_frame, bg="#D9D9D9", pady=10)
        filter_frame.pack(fill="x", padx=5, pady=(5, 10))

        # Task type filter radio buttons
        filter_label = Label(filter_frame, text="Show:", bg="#D9D9D9")
        filter_label.grid(row=0, column=0, padx=(5, 2), sticky="w")
        
        self.filter_var = StringVar(value="all")
        filter_options = [
            ("All Tasks", "all"),
            ("My Tasks", "my_tasks"), 
            ("Accepted Tasks", "accepted_tasks"),
            ("Available Tasks", "available_tasks")
        ]
        
        for i, (text, value) in enumerate(filter_options):
            rb = ttk.Radiobutton(filter_frame, text=text, variable=self.filter_var, 
                               value=value, command=self._on_filter_change)
            rb.grid(row=0, column=i+1, padx=5, sticky="w")

        # Date and duration filters
        date_frame = Frame(filter_frame, bg="#D9D9D9")
        date_frame.grid(row=1, column=0, columnspan=5, sticky="w", pady=(10, 0))

        Label(date_frame, text="From:", bg="#D9D9D9").grid(row=0, column=0, padx=(5, 2))
        self.start_date_entry = DateEntry(date_frame, width=10, borderwidth=2, date_pattern='y-mm-dd', state="readonly")
        self.start_date_entry.grid(row=0, column=1, padx=(0, 5))
        self.start_date_entry.set_date(date.today())
        self.start_date_entry.delete(0, "end")

        Label(date_frame, text="To:", bg="#D9D9D9").grid(row=0, column=2, padx=(5, 2))
        self.end_date_entry = DateEntry(date_frame, width=10, borderwidth=2, date_pattern='y-mm-dd', state="readonly")
        self.end_date_entry.grid(row=0, column=3, padx=(0, 5))
        self.end_date_entry.set_date(date.today())
        self.end_date_entry.delete(0, "end")

        Label(date_frame, text="Duration:", bg="#D9D9D9").grid(row=0, column=4, pady=(0, 0), sticky="e", padx=(10, 2))
        self.duration_var = StringVar()
        duration_options = ["Any Duration", "Under 1 hour", "1 - 3 hours", "Over 3 hours"]
        duration_combo = ttk.Combobox(date_frame, textvariable=self.duration_var, values=duration_options, state="readonly", width=15)
        duration_combo.set("Any Duration")
        duration_combo.grid(row=0, column=5, sticky="w", pady=(0, 0))

        self.duration_var.trace_add("write", lambda *a: self._apply_filters())

        apply_button = Button(date_frame, text="Apply Filters", command=self._apply_filters, relief="flat", bg="#FEBF00", activebackground="#E0A800")
        apply_button.grid(row=0, column=6, padx=(10, 0), sticky="w")

    def _on_filter_change(self):
        """Handle task filter changes"""
        self.current_filter = self.filter_var.get()
        self.all_tasks = fetch_tasks(self.current_filter, self.current_user_id)
        self._apply_filters()

    def _apply_filters(self, *args):
        """Apply search and filter criteria to task list"""
        filtered = list(self.all_tasks)
        raw_search = (self.search_var.get() or "").strip()
        search_term = normalize_str(raw_search)

        # Search filter
        if search_term:
            def matches_search(task):
                for key in ('task_title', 'task_requirements_description', 'name', 'unique_task_id'):
                    if search_term in normalize_str(task.get(key, "")):
                        return True
                # Date search
                task_date = task.get('task_date')
                if task_date:
                    try:
                        if isinstance(task_date, date):
                            date_str = task_date.strftime('%d %b %Y')
                        else:
                            date_str = str(task_date)
                    except Exception:
                        date_str = str(task_date)
                    if search_term in normalize_str(date_str):
                        return True
                return False

            filtered = [task for task in filtered if matches_search(task)]

        # Date range filter
        start_text = (self.start_date_entry.get() or "").strip()
        end_text = (self.end_date_entry.get() or "").strip()

        start_date_val = None
        end_date_val = None
        try:
            if start_text:
                start_date_val = datetime.strptime(start_text, "%Y-%m-%d").date()
        except Exception:
            start_date_val = None

        try:
            if end_text:
                end_date_val = datetime.strptime(end_text, "%Y-%m-%d").date()
        except Exception:
            end_date_val = None

        if start_date_val or end_date_val:
            temp_filtered = []
            for task in filtered:
                task_date_obj = task.get('task_date')
                if not task_date_obj:
                    continue
                if start_date_val and task_date_obj < start_date_val:
                    continue
                if end_date_val and task_date_obj > end_date_val:
                    continue
                temp_filtered.append(task)
            filtered = temp_filtered

        # Duration filter
        duration_choice = (self.duration_var.get() or "Any Duration")
        if duration_choice != "Any Duration":
            if duration_choice == "Under 1 hour":
                filtered = [task for task in filtered if parse_duration_to_minutes(task.get('estimated_task_duration')) < 60]
            elif duration_choice == "1 - 3 hours":
                filtered = [task for task in filtered if 60 <= parse_duration_to_minutes(task.get('estimated_task_duration')) <= 180]
            elif duration_choice == "Over 3 hours":
                filtered = [task for task in filtered if parse_duration_to_minutes(task.get('estimated_task_duration')) > 180]

        self._populate_task_list(filtered)

    def _truncate_text(self, text, max_length):
        """Truncate long text with ellipsis"""
        if not isinstance(text, str):
            return ""
        return (text[:max_length - 3].strip() + "...") if len(text) > max_length else text

    def _populate_task_list(self, tasks_to_display):
        """Display tasks in the scrollable list"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        colors = ["#FFFFFF", "#FFFEE0"]  # Alternating row colors

        if not tasks_to_display:
            Label(self.scrollable_frame, text="No tasks match your filters.", font=self.font_task_body, bg="#D9D9D9").pack(pady=20)
            return

        # Create task cards for each task
        for i, task in enumerate(tasks_to_display):
            bg_color = colors[i % 2]
            outer_frame = Frame(self.scrollable_frame, bg="#D9D9D9")
            outer_frame.pack(pady=6, fill="x")

            task_canvas = Canvas(outer_frame, bg="#D9D9D9", highlightthickness=0, width=350, height=125)
            task_canvas.pack(fill="x")

            self._create_rounded_rectangle(task_canvas, 2, 2, 348, 123, r=25, outline="#CCCCCC", fill=bg_color)

            content_frame = Frame(task_canvas, bg=bg_color)
            task_canvas.create_window(5, 5, window=content_frame, anchor="nw", width=338, height=113)

            # Task header with title and status
            top_frame = Frame(content_frame, bg=bg_color)
            top_frame.pack(fill="x", padx=10, pady=(5, 0))
            top_frame.grid_columnconfigure(0, weight=1)

            # Status indicator
            status_text = ""
            if task.get('task_completion_worker') and task.get('task_completion_poster'):
                status_text = " ✓ Completed"
            elif task.get('task_completion_worker') or task.get('task_completion_poster'):
                status_text = " ⏳ Pending Approval"
            elif task.get('unique_worker_id'):
                status_text = " 👤 Assigned"
            
            title_text = task.get('task_title', 'No Title')
            if status_text:
                title_text += status_text

            Label(top_frame, text=title_text, font=self.font_task_title, bg=bg_color, anchor="w").grid(row=0, column=0, sticky="w")

            # Date and duration
            task_date = task.get('task_date')
            date_str = "No Date"
            if isinstance(task_date, date):
                date_str = task_date.strftime('%d %b %Y')
            else:
                try:
                    date_str = datetime.strptime(str(task_date), '%Y-%m-%d').strftime('%d %b %Y')
                except Exception:
                    date_str = str(task_date) if task_date else "No Date"

            duration_date_text = f"{task.get('estimated_task_duration', '')}\n{date_str}"
            Label(top_frame, text=duration_date_text, font=self.font_task_date, bg=bg_color, justify="right").grid(row=0, column=1, sticky="e", padx=(10, 0))

            # Task details
            Label(content_frame, text=f"By: {task.get('name', 'N/A')}", font=self.font_task_body, bg=bg_color, anchor="w").pack(fill="x", padx=10, pady=2)

            truncated_desc = self._truncate_text(task.get('task_requirements_description', ''), 75)
            desc_label = Label(content_frame, text=truncated_desc, font=self.font_task_body, wraplength=310, bg=bg_color, justify="left", anchor="nw")
            desc_label.pack(fill="x", padx=10, pady=2)

            Label(content_frame, text=f"ID: {task.get('unique_task_id', '')}", font=self.font_task_small, fg="grey", bg=bg_color, anchor="w").pack(fill="x", padx=10, pady=(0, 5))

            # Make entire task card clickable
            click_handler = partial(self.show_task_detail, task)
            to_bind = [task_canvas, content_frame, top_frame, desc_label]
            to_bind += top_frame.winfo_children()
            to_bind += content_frame.winfo_children()
            for widget in to_bind:
                try:
                    widget.bind("<Button-1>", click_handler)
                except Exception:
                    pass

    def show_task_detail(self, task_data, event=None):
        """Show detailed view of a specific task"""
        self.main_view_frame.pack_forget()
        for widget in self.detail_view_frame.winfo_children():
            widget.destroy()
        self.detail_view_frame.pack(fill="both", expand=True)

        # Back button
        back_button = Button(self.detail_view_frame, text="< Back to All Tasks", command=self.show_main_view, relief="flat", font=("Arial", 12), fg="#007BFF", bg="#FFFFFF")
        back_button.pack(anchor="w", padx=20, pady=(20, 15))

        content_frame = Frame(self.detail_view_frame, bg="#FFFFFF")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Task information display
        Label(content_frame, text=task_data.get('task_title'), font=self.font_detail_title, bg="#FFFFFF", wraplength=340, justify="left").pack(anchor="w", pady=(0, 5))
        Label(content_frame, text=f"Posted by: {task_data.get('name')}", font=self.font_task_body, bg="#FFFFFF").pack(anchor="w")

        task_date = task_data.get('task_date')
        date_str = "No Date"
        if isinstance(task_date, date):
            date_str = task_date.strftime('%d %B %Y')
        else:
            try:
                date_str = datetime.strptime(str(task_date), '%Y-%m-%d').strftime('%d %B %Y')
            except Exception:
                date_str = str(task_date) if task_date else "No Date"

        Label(content_frame, text=f"{task_data.get('estimated_task_duration')} - {date_str}", font=self.font_detail_header, bg="#FFFFFF").pack(anchor="w", pady=10)
        Label(content_frame, text="Requirements:", font=self.font_task_body, bg="#FFFFFF", justify="left").pack(anchor="w", pady=(10, 2))
        Label(content_frame, text=task_data.get('task_requirements_description'), font=self.font_task_body, bg="#FFFFFF", wraplength=330, justify="left").pack(anchor="w")
        Label(content_frame, text=f"ID: {task_data.get('unique_task_id')}", font=self.font_task_small, fg="grey", bg="#FFFFFF").pack(anchor="w", pady=10)

        # Task management buttons
        button_frame = Frame(content_frame, bg="#FFFFFF")
        button_frame.pack(fill="x", pady=10)
        
        # Determine user's relationship to task
        is_poster = task_data.get('poster_id') == self.current_user_id
        is_worker = task_data.get('unique_worker_id') == self.current_user_id
        is_assigned = task_data.get('unique_worker_id') is not None and task_data.get('unique_worker_id') != ''
        is_available = not is_assigned and not is_poster
        
        # Completion status
        worker_completed = task_data.get('task_completion_worker', False)
        poster_completed = task_data.get('task_completion_poster', False)
        both_completed = worker_completed and poster_completed
        
        # Status display
        if both_completed:
            status_label = Label(button_frame, text="✓ Task Completed and Paid", font=("Arial", 12, "bold"), fg="green", bg="#FFFFFF")
            status_label.pack(pady=5)
        elif worker_completed or poster_completed:
            status_label = Label(button_frame, text="⏳ Waiting for completion approval", font=("Arial", 10), fg="orange", bg="#FFFFFF")
            status_label.pack(pady=5)
        
        # Action buttons based on user role and task status
        if is_available:
            accept_btn = Button(button_frame, text="Accept This Task", 
                              command=lambda: self.accept_task(task_data),
                              bg="#4CAF50", fg="white", font=("Arial", 10))
            accept_btn.pack(pady=5)
        
        elif is_worker and not both_completed:
            if not worker_completed:
                complete_btn = Button(button_frame, text="Mark as Complete", 
                                    command=lambda: self.approve_completion(task_data, "worker"),
                                    bg="#2196F3", fg="white", font=("Arial", 10))
                complete_btn.pack(pady=5)
            
            unassign_btn = Button(button_frame, text="Unassign from Task", 
                                command=lambda: self.unassign_task(task_data),
                                bg="#FF9800", fg="white", font=("Arial", 10))
            unassign_btn.pack(pady=5)
        
        elif is_poster and not both_completed:
            if not poster_completed and is_assigned:
                approve_btn = Button(button_frame, text="Approve Completion", 
                                   command=lambda: self.approve_completion(task_data, "poster"),
                                   bg="#2196F3", fg="white", font=("Arial", 10))
                approve_btn.pack(pady=5)

        # Comments section
        Frame(content_frame, height=2, bg="#EEEEEE").pack(fill="x", pady=20)
        Label(content_frame, text="--- Conversation ---", font=self.font_task_body, fg="grey", bg="#FFFFFF").pack()

        comment_btn = Button(content_frame, text="Feeling chatty? Add a comment.", command=partial(self.open_comments_window, task_data), relief="flat", bg="#FEBF00", activebackground="#E0A800")
        comment_btn.pack(pady=10)

        Label(content_frame, text="(Click the button to view and add comments)", font=self.font_task_small, fg="grey", bg="#FFFFFF").pack()

    def accept_task(self, task_data):
        """Accept an available task"""
        if not self.current_user_id:
            messagebox.showerror("Error", "You must be logged in to accept a task.")
            return
        
        if assign_task_to_worker(task_data['unique_task_id'], self.current_user_id):
            messagebox.showinfo("Success", "You have accepted this task!")
            self.show_main_view()  # Refresh view

    def unassign_task(self, task_data):
        """Unassign from a task"""
        if messagebox.askyesno("Confirm", "Are you sure you want to unassign yourself from this task?"):
            if unassign_task(task_data['unique_task_id']):
                messagebox.showinfo("Success", "You have been unassigned from this task.")
                self.show_main_view()  # Refresh view

    def approve_completion(self, task_data, user_type):
        """Approve task completion"""
        success, message = approve_task_completion(
            task_data['unique_task_id'], 
            user_type, 
            self.current_user_id
        )
        
        if success:
            messagebox.showinfo("Success", message)
            # Update balance display
            self.current_balance = get_user_balance(self.current_user_id)
            self.show_main_view()  # Refresh view
        else:
            messagebox.showerror("Error", message)

    def open_comments_window(self, task_data):
        """Open comments/communication window for a task"""
        unique_task_id = task_data.get('unique_task_id')
        if not unique_task_id:
            messagebox.showerror("Error", "This task has no ID and cannot be commented on.")
            return

        win = Toplevel(self.master)
        win.title("Conversation")
        win.geometry("380x520")

        Label(win, text=task_data.get('task_title'), font=self.font_detail_header).pack(anchor='w', padx=10, pady=(10, 5))
        Label(win, text=f"Task ID: {unique_task_id}", font=self.font_task_small, fg='grey').pack(anchor='w', padx=10)

        # Comments display area
        comments_container = Frame(win)
        comments_container.pack(fill='both', expand=True, padx=10, pady=10)

        canvas = Canvas(comments_container, highlightthickness=0)
        scrollbar = Scrollbar(comments_container, orient='vertical', command=canvas.yview)
        inner = Frame(canvas)

        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=inner, anchor='nw', width=340)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        def load_comments():
            """Load and display comments for this task"""
            for widget in inner.winfo_children():
                widget.destroy()
            comments = fetch_comments_for_task(unique_task_id)
            if not comments:
                Label(inner, text='No comments yet. Be the first to comment!', font=self.font_task_body, fg='grey').pack(pady=10)
                return
            for comment in comments:
                name = comment.get('name') or 'Unknown User'
                created_at = comment.get('created_at')
                if isinstance(created_at, datetime):
                    time_str = created_at.strftime('%d %b %Y %H:%M')
                else:
                    try:
                        time_str = datetime.strptime(str(created_at), '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y %H:%M')
                    except Exception:
                        time_str = str(created_at)
                header = Frame(inner)
                header.pack(fill='x', pady=(8, 0))
                Label(header, text=f"{name}", font=self.font_task_title, anchor='w').pack(side='left')
                Label(header, text=time_str, font=self.font_task_small, fg='grey').pack(side='right')
                Label(inner, text=comment.get('comment_text'), wraplength=320, justify='left', font=self.font_task_body).pack(anchor='w', pady=(0, 8))

        load_comments()

        # Comment input area
        bottom = Frame(win)
        bottom.pack(fill='x', padx=10, pady=8)

        users = fetch_all_users()
        user_map = {f"{user['name']} ({user['unique_user_id']})": user['unique_user_id'] for user in users}
        user_list = list(user_map.keys())
        user_var = StringVar()
        if user_list:
            user_var.set(user_list[0])
        else:
            user_list = ['Anonymous']
            user_var.set('Anonymous')

        Label(bottom, text='Comment as:', font=self.font_task_small).pack(anchor='w')
        user_combo = ttk.Combobox(bottom, values=user_list, textvariable=user_var, state='readonly')
        user_combo.pack(fill='x')

        Label(bottom, text='Your comment:', font=self.font_task_small).pack(anchor='w', pady=(8, 0))
        comment_text = Text(bottom, height=4)
        comment_text.pack(fill='x')

        def submit_comment():
            """Submit a new comment"""
            text = comment_text.get('1.0', 'end').strip()
            selected = user_var.get()
            user_id = None
            if selected and selected in user_map:
                user_id = user_map[selected]
            elif selected == 'Anonymous':
                user_id = None
            else:
                user_id = None

            if not text:
                messagebox.showwarning('Empty', 'Please write a comment before submitting.')
                return

            success = insert_comment(unique_task_id, user_id, text)
            if success:
                comment_text.delete('1.0', 'end')
                load_comments()
                canvas.yview_moveto(1.0)  # Scroll to bottom

        submit_btn = Button(bottom, text='Post comment', command=submit_comment, bg='#007BFF', fg='white')
        submit_btn.pack(pady=(8, 0), anchor='e')

    def show_main_view(self):
        """Return to main task list view"""
        self.detail_view_frame.pack_forget()
        # Refresh data
        self.all_tasks = fetch_tasks(self.current_filter, self.current_user_id)
        self.current_balance = get_user_balance(self.current_user_id) if self.current_user_id else 0
        
        # Rebuild main view to reflect changes
        for widget in self.main_view_frame.winfo_children():
            widget.destroy()
        self.setup_main_view()
        
        self.main_view_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskViewerApp(root)
    root.mainloop()