# -*- coding: utf-8 -*-
import requests
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Canvas, Frame, Label, Scrollbar, Entry, messagebox, StringVar, Button, ttk
import tkinter.font as tkFont
import mysql.connector
from urllib.parse import quote
from functools import partial
from datetime import datetime, date
from tkcalendar import DateEntry  # Requires: pip install tkcalendar
import re

# --- ASSETS AND DATABASE CONFIGURATION ---
ASSETS_BASE_URL = "https://raw.githubusercontent.com/kkgaba686/Lend_a_Hand/main/assets/view_task/"
DB_CONFIG = {
    'host': "sql5.freesqldatabase.com",
    'user': "sql5794100",
    'password': "BmzWGi52RK",
    'database': "sql5794100",
    'port': 3306
}


# --- DATABASE HELPER ---
def fetch_tasks():
    """Fetches all tasks from the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                t.task_title, t.task_requirements_description,
                t.estimated_task_duration, t.task_date,
                t.unique_task_id, u.name
            FROM Task_information AS t
            JOIN User_information AS u ON t.unique_user_id = u.unique_user_id
            ORDER BY t.task_date ASC;
        """
        cursor.execute(query)
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        return tasks
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Could not fetch tasks.\nError: {e}")
        return []


# --- MAIN APPLICATION CLASS ---
class TaskViewerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Lend a Hand")
        self.master.geometry("411x823")
        self.master.resizable(False, False)

        self.all_tasks = fetch_tasks()
        self.image_references = {}

        self.setup_fonts()

        self.main_view_frame = Frame(self.master)
        self.detail_view_frame = Frame(self.master, bg="#FFFFFF")

        self.setup_main_view()
        self.main_view_frame.pack(fill="both", expand=True)

    def setup_fonts(self):
        self.font_task_title = tkFont.Font(family="Arial", size=14, weight="bold")
        self.font_task_body = tkFont.Font(family="Arial", size=12)
        self.font_task_small = tkFont.Font(family="Arial", size=10)
        self.font_task_date = tkFont.Font(family="Arial", size=12, weight="bold")
        self.font_detail_title = tkFont.Font(family="Arial", size=18, weight="bold")
        self.font_detail_header = tkFont.Font(family="Arial", size=14, weight="bold")

    def _load_image(self, filename, key):
        try:
            url = f"{ASSETS_BASE_URL}{quote(filename)}"
            response = requests.get(url)
            response.raise_for_status()
            img_data = Image.open(BytesIO(response.content))
            photo_img = ImageTk.PhotoImage(img_data)
            self.image_references[key] = photo_img
            return photo_img
        except requests.exceptions.RequestException:
            return None

    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1,
            x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2,
            x1, y2 - r, x1, y1 + r, x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def setup_main_view(self):
        canvas = Canvas(self.main_view_frame, bg="#FFFFFF", height=823, width=411, bd=0, highlightthickness=0, relief="ridge")
        canvas.pack(fill="both", expand=True)
        canvas.create_rectangle(0, 63, 411, 823, fill="#FFE347", outline="")

        asset_placements = {
            "image_2.png": (205, 31), "image_4.png": (196, 130),
            "image_5.png": (163, 166), "entry_1.png": (185, 215),
            "image_3.png": (204, 590),  # Main grey container
            "image_6.png": (358, 214), "image_1.png": (205, 802)
        }
        for filename, (x, y) in asset_placements.items():
            img = self._load_image(filename, filename)
            if img:
                canvas.create_image(x, y, image=img)

        self.search_var = StringVar()
        self.search_var.trace_add("write", self._apply_filters)
        search_entry = Entry(self.main_view_frame, textvariable=self.search_var, font=("Arial", 14), bd=0, relief="flat", bg="#D9D9D9")
        canvas.create_window(185, 215, window=search_entry, width=230, height=40)

        # Adjusted height to stop at start of nav bar
        self.container_canvas = Canvas(self.main_view_frame, bg="#D9D9D9", width=370, height=520, bd=0, highlightthickness=0)
        self._create_rounded_rectangle(self.container_canvas, 2, 2, 368, 518, r=20, fill="#D9D9D9", outline="#CCCCCC")
        canvas.create_window(205, 260, window=self.container_canvas, anchor="n")

        self.container_inner_frame = Frame(self.container_canvas, bg="#D9D9D9")
        self.container_canvas.create_window(0, 0, window=self.container_inner_frame, anchor="nw", width=370, height=520)

        self._setup_filter_controls(self.container_inner_frame)

        task_scroll_container = Frame(self.container_inner_frame, bg="#D9D9D9")
        task_scroll_container.pack(fill="both", expand=True)

        task_canvas = Canvas(task_scroll_container, bg="#D9D9D9", highlightthickness=0)
        scrollbar = Scrollbar(task_scroll_container, orient="vertical", command=task_canvas.yview)
        self.scrollable_frame = Frame(task_canvas, bg="#D9D9D9")

        self.scrollable_frame.bind(
            "<Configure>", lambda e: task_canvas.configure(scrollregion=task_canvas.bbox("all"))
        )
        self.master.bind_all("<MouseWheel>", lambda e: task_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        task_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=350)
        task_canvas.configure(yscrollcommand=scrollbar.set)

        task_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._populate_task_list(self.all_tasks)

    def _setup_filter_controls(self, parent_frame):
        filter_frame = Frame(parent_frame, bg="#D9D9D9", pady=10)
        filter_frame.pack(fill="x", padx=5, pady=(5, 10))

        Label(filter_frame, text="From:", bg="#D9D9D9").grid(row=0, column=0, padx=(5, 2))
        self.start_date_entry = DateEntry(filter_frame, width=10, borderwidth=2, date_pattern='y-mm-dd', state="readonly")
        self.start_date_entry.grid(row=0, column=1, padx=(0, 5))
        self.start_date_entry.delete(0, "end")

        Label(filter_frame, text="To:", bg="#D9D9D9").grid(row=0, column=2, padx=(5, 2))
        self.end_date_entry = DateEntry(filter_frame, width=10, borderwidth=2, date_pattern='y-mm-dd', state="readonly")
        self.end_date_entry.grid(row=0, column=3, padx=(0, 5))
        self.end_date_entry.delete(0, "end")

        Label(filter_frame, text="Duration:", bg="#D9D9D9").grid(row=1, column=0, pady=(5, 0), sticky="e")
        self.duration_var = StringVar()
        duration_options = ["Any Duration", "Under 1 hour", "1 - 3 hours", "Over 3 hours"]
        duration_combo = ttk.Combobox(filter_frame, textvariable=self.duration_var, values=duration_options, state="readonly", width=15)
        duration_combo.set("Any Duration")
        duration_combo.grid(row=1, column=1, columnspan=2, sticky="w", pady=(5, 0))

        apply_button = Button(filter_frame, text="Apply", command=self._apply_filters, relief="flat", bg="#FEBF00", activebackground="#E0A800")
        apply_button.grid(row=0, column=4, rowspan=2, padx=(5, 0), sticky="nsew")

    def _parse_duration_to_minutes(self, duration_str):
        hours, minutes = 0, 0
        if not isinstance(duration_str, str):
            return 0
        h_match = re.search(r'(\d+)\s*h', duration_str)
        m_match = re.search(r'(\d+)\s*m', duration_str)
        if h_match:
            hours = int(h_match.group(1))
        if m_match:
            minutes = int(m_match.group(1))
        return (hours * 60) + minutes

    def _apply_filters(self, *args):
        filtered = self.all_tasks
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [
                t for t in filtered
                if search_term in str(t.get('task_title', '')).lower()
                or search_term in str(t.get('task_requirements_description', '')).lower()
                or search_term in str(t.get('name', '')).lower()
            ]

        try:
            start_date_val = self.start_date_entry.get_date()
        except (ValueError, TypeError):
            start_date_val = None
        try:
            end_date_val = self.end_date_entry.get_date()
        except (ValueError, TypeError):
            end_date_val = None

        if start_date_val or end_date_val:
            temp_filtered = []
            for t in filtered:
                task_date_val = t.get('task_date')
                if not task_date_val:
                    continue
                task_date_obj = None
                if isinstance(task_date_val, date):
                    task_date_obj = task_date_val
                elif isinstance(task_date_val, str):
                    try:
                        task_date_obj = datetime.strptime(task_date_val, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        continue
                else:
                    continue
                if start_date_val and task_date_obj < start_date_val:
                    continue
                if end_date_val and task_date_obj > end_date_val:
                    continue
                temp_filtered.append(t)
            filtered = temp_filtered

        duration_choice = self.duration_var.get()
        if duration_choice != "Any Duration":
            if duration_choice == "Under 1 hour":
                filtered = [t for t in filtered if self._parse_duration_to_minutes(t.get('estimated_task_duration')) < 60]
            elif duration_choice == "1 - 3 hours":
                filtered = [t for t in filtered if 60 <= self._parse_duration_to_minutes(t.get('estimated_task_duration')) <= 180]
            elif duration_choice == "Over 3 hours":
                filtered = [t for t in filtered if self._parse_duration_to_minutes(t.get('estimated_task_duration')) > 180]

        self._populate_task_list(filtered)

    def _truncate_text(self, text, max_length):
        if not isinstance(text, str):
            return ""
        return (text[:max_length - 3].strip() + "...") if len(text) > max_length else text

    def _populate_task_list(self, tasks_to_display):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        colors = ["#FFFFFF", "#FFFEE0"]

        if not tasks_to_display:
            Label(self.scrollable_frame, text="No tasks match your filters.", font=self.font_task_body, bg="#D9D9D9").pack(pady=20)
            return

        for i, task in enumerate(tasks_to_display):
            bg_color = colors[i % 2]
            outer_frame = Frame(self.scrollable_frame, bg="#D9D9D9")
            outer_frame.pack(pady=6, fill="x")

            task_canvas = Canvas(outer_frame, bg="#D9D9D9", highlightthickness=0, width=350, height=125)
            task_canvas.pack(fill="x")

            self._create_rounded_rectangle(task_canvas, 2, 2, 348, 123, r=25, outline="#CCCCCC", fill=bg_color)

            content_frame = Frame(task_canvas, bg=bg_color)
            task_canvas.create_window(5, 5, window=content_frame, anchor="nw", width=338, height=113)

            top_frame = Frame(content_frame, bg=bg_color)
            top_frame.pack(fill="x", padx=10, pady=(5, 0))
            top_frame.grid_columnconfigure(0, weight=1)

            Label(top_frame, text=task.get('task_title', 'No Title'), font=self.font_task_title, bg=bg_color, anchor="w").grid(row=0, column=0, sticky="w")

            task_date = task.get('task_date')
            date_str = str(task_date) if task_date else "No Date"
            if hasattr(task_date, 'strftime'):
                date_str = task_date.strftime('%d %b %Y')
            else:
                try:
                    date_str = datetime.strptime(str(task_date), '%Y-%m-%d').strftime('%d %b %Y')
                except (ValueError, TypeError):
                    pass

            duration_date_text = f"{task.get('estimated_task_duration', '')}\n{date_str}"
            Label(top_frame, text=duration_date_text, font=self.font_task_date, bg=bg_color, justify="right").grid(row=0, column=1, sticky="e", padx=(10, 0))

            Label(content_frame, text=f"By: {task.get('name', 'N/A')}", font=self.font_task_body, bg=bg_color, anchor="w").pack(fill="x", padx=10, pady=2)

            truncated_desc = self._truncate_text(task.get('task_requirements_description', ''), 75)
            desc_label = Label(content_frame, text=truncated_desc, font=self.font_task_body, wraplength=310, bg=bg_color, justify="left", anchor="nw")
            desc_label.pack(fill="x", padx=10, pady=2)

            Label(content_frame, text=f"ID: {task.get('unique_task_id', '')}", font=self.font_task_small, fg="grey", bg=bg_color, anchor="w").pack(fill="x", padx=10, pady=(0, 5))

            click_handler = partial(self.show_task_detail, task)
            for widget in [task_canvas, content_frame, top_frame, desc_label] + top_frame.winfo_children() + content_frame.winfo_children():
                widget.bind("<Button-1>", click_handler)

    def show_task_detail(self, task_data, event=None):
        self.main_view_frame.pack_forget()
        for widget in self.detail_view_frame.winfo_children():
            widget.destroy()
        self.detail_view_frame.pack(fill="both", expand=True)

        back_button = Button(self.detail_view_frame, text="< Back to All Tasks", command=self.show_main_view, relief="flat", font=("Arial", 12), fg="#007BFF", bg="#FFFFFF")
        back_button.pack(anchor="w", padx=20, pady=(20, 15))

        content_frame = Frame(self.detail_view_frame, bg="#FFFFFF")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        Label(content_frame, text=task_data.get('task_title'), font=self.font_detail_title, bg="#FFFFFF", wraplength=340, justify="left").pack(anchor="w", pady=(0, 5))
        Label(content_frame, text=f"Posted by: {task_data.get('name')}", font=self.font_task_body, bg="#FFFFFF").pack(anchor="w")

        task_date = task_data.get('task_date')
        date_str = str(task_date)
        if hasattr(task_date, 'strftime'):
            date_str = task_date.strftime('%d %B %Y')
        else:
            try:
                date_str = datetime.strptime(str(task_date), '%Y-%m-%d').strftime('%d %B %Y')
            except (ValueError, TypeError):
                pass

        Label(content_frame, text=f"{task_data.get('estimated_task_duration')} - {date_str}", font=self.font_detail_header, bg="#FFFFFF").pack(anchor="w", pady=10)
        Label(content_frame, text="Requirements:", font=self.font_task_body, bg="#FFFFFF", justify="left").pack(anchor="w", pady=(10, 2))
        Label(content_frame, text=task_data.get('task_requirements_description'), font=self.font_task_body, bg="#FFFFFF", wraplength=330, justify="left").pack(anchor="w")
        Label(content_frame, text=f"ID: {task_data.get('unique_task_id')}", font=self.font_task_small, fg="grey", bg="#FFFFFF").pack(anchor="w", pady=10)

        Frame(content_frame, height=2, bg="#EEEEEE").pack(fill="x", pady=20)
        Label(content_frame, text="--- Commenting system will be here ---", font=self.font_task_body, fg="grey", bg="#FFFFFF").pack()

    def show_main_view(self):
        self.detail_view_frame.pack_forget()
        self.main_view_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskViewerApp(root)
    root.mainloop()
