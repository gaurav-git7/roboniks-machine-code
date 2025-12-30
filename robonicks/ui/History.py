# history_screen_full.py
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import requests
import math
import io 
import os
import csv
from datetime import datetime
import importlib
from utils.memory_manager import MemoryManager

# -----------------------------
# Configuration - adjust to your environment
# -----------------------------
API_BASE_URL = "http://127.0.0.1:8001"  # Backend runs on port 8001
HISTORY_ENDPOINT = "/ops/consumption"   # Consumption history endpoint

# -----------------------------
# Helper: default data shape
# -----------------------------
def empty_month_row(month_name):
    return {
        "month": month_name,
        "positive": 0,
        "negative": 0,
        "high_time": "",
        "low_time": ""
    }

# -----------------------------
# Data Class for Memory Optimization
# -----------------------------
class HistoryRecord:
    __slots__ = ['month', 'positive', 'negative', 'high_time', 'low_time']
    
    def __init__(self, month, positive, negative, high_time="", low_time=""):
        self.month = month
        self.positive = positive
        self.negative = negative
        self.high_time = high_time
        self.low_time = low_time

# -----------------------------
# HistoryScreen
# -----------------------------
class HistoryScreen(tk.Frame):
    def __init__(self, root, go_back_callback):
        super().__init__(root)
        self.root = root
        self.go_back_callback = go_back_callback
        
        # Configure frame
        self.configure(bg="white")
        self.pack(fill="both", expand=True)
        
        # UI state
        self.selected_summary = tk.StringVar(value="Monthly")
        self.selected_month = tk.StringVar(value="JANUARY")
        self.selected_year = tk.StringVar(value=str(datetime.now().year))

        # year range till 2050
        self.YEAR_OPTIONS = [str(y) for y in range(2020, 2051)]
        self.MONTH_OPTIONS = [
            "JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE",
            "JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"
        ]

        # Table / pagination state
        self.page_size = tk.IntVar(value=6)
        self.current_page = 1
        self.data = []            # full dataset returned from API (list of dicts)
        self.display_rows = []    # rows shown on current page

        # build UI
        self.build_ui()
        # initial fetch
        self.fetch_and_render()

    # -------------------------
    # UI construction
    # -------------------------
    def build_ui(self):
        # Header
        header = tk.Frame(self, bg="#1BC6B4", height=90)
        header.pack(fill="x", pady=(0, 20))
        
        # Title with icon
        title_frame = tk.Frame(header, bg="#1BC6B4")
        title_frame.pack(side="left", padx=30, fill="y")
        
        tk.Label(
            title_frame, 
            text="📊",
            font=("Arial", 28),
            fg="white", 
            bg="#1BC6B4"
        ).pack(side="left")
        
        tk.Label(
            title_frame,
            text="History & Analytics",
            font=("Montserrat", 28, "bold"),
            fg="white",
            bg="#1BC6B4"
        ).pack(side="left", padx=(10, 0))
        
        # Back button
        back_btn = tk.Button(
            header,
            text="← Back to Home",
            font=("Montserrat", 11, "bold"),
            bg="#3AC7F1",
            fg="white",
            activebackground="#32B4DB",
            bd=0,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.go_back
        )
        back_btn.pack(side="right", padx=30)

        # Main container
        main_container = tk.Frame(self, bg="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Control Panel
        control_panel = tk.Frame(main_container, bg="#F7F9FC", relief=tk.RAISED, bd=1)
        control_panel.pack(fill="x", pady=(0, 20))
        
        # Mode selection with icons
        mode_frame = tk.Frame(control_panel, bg="#F7F9FC", padx=15, pady=10)
        mode_frame.pack(side="left", fill="y")
        
        tk.Label(
            mode_frame,
            text="📅 View Mode:",
            font=("Montserrat", 11, "bold"),
            bg="#F7F9FC",
            fg="#2C3E50"
        ).pack(side="left", padx=(0, 10))
        
        tk.Radiobutton(
            mode_frame, 
            text="📅 Monthly", 
            variable=self.selected_summary, 
            value="Monthly", 
            command=self.on_mode_change, 
            bg="#F7F9FC",
            font=("Montserrat", 10),
            activebackground="#F7F9FC"
        ).pack(side="left", padx=(0, 15))
        
        tk.Radiobutton(
            mode_frame, 
            text="📊 Yearly", 
            variable=self.selected_summary, 
            value="Yearly", 
            command=self.on_mode_change, 
            bg="#F7F9FC",
            font=("Montserrat", 10),
            activebackground="#F7F9FC"
        ).pack(side="left")

        # Filter frame
        filter_frame = tk.Frame(control_panel, bg="#F7F9FC", padx=15, pady=10)
        filter_frame.pack(side="left", fill="y")
        
        tk.Label(
            filter_frame,
            text="🗓️ Month:",
            font=("Montserrat", 11),
            bg="#F7F9FC",
            fg="#2C3E50"
        ).pack(side="left", padx=(0, 5))
        
        self.month_combo = ttk.Combobox(
            filter_frame, 
            values=self.MONTH_OPTIONS, 
            textvariable=self.selected_month, 
            state="readonly", 
            width=14,
            font=("Montserrat", 10)
        )
        self.month_combo.pack(side="left", padx=(0, 15))
        self.month_combo.bind("<<ComboboxSelected>>", lambda e: self.on_input_change())
        
        tk.Label(
            filter_frame,
            text="📅 Year:",
            font=("Montserrat", 11),
            bg="#F7F9FC",
            fg="#2C3E50"
        ).pack(side="left", padx=(0, 5))
        
        self.year_combo = ttk.Combobox(
            filter_frame, 
            values=self.YEAR_OPTIONS, 
            textvariable=self.selected_year, 
            state="readonly", 
            width=8,
            font=("Montserrat", 10)
        )
        self.year_combo.pack(side="left")
        self.year_combo.bind("<<ComboboxSelected>>", lambda e: self.on_input_change())

        # Action buttons frame
        action_frame = tk.Frame(control_panel, bg="#F7F9FC", padx=15, pady=10)
        action_frame.pack(side="right")
        
        # Fetch button
        fetch_btn = tk.Button(
            action_frame,
            text="🔍 Fetch Data",
            bg="#3498DB",
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=15,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            command=self.fetch_and_render
        )
        fetch_btn.pack(side="left", padx=(0, 10))

        # Memory Cleanup Button
        cleanup_btn = tk.Button(
            action_frame,
            text="🧹 Free Memory",
            bg="#E67E22",
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=15,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            command=self.manual_cleanup
        )
        cleanup_btn.pack(side="left", padx=(0, 10))

        # Export buttons
        # Export Buttons
        tk.Button(
            action_frame,
            text="📊 Export Excel",
            bg="#2ECC71",
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=15,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            command=self.export_excel
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            action_frame,
            text="📄 Export PDF",
            bg="#E74C3C",
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=15,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            command=self.save_pdf
        ).pack(side="left", padx=(0, 10))

        # Page size selector
        tk.Label(
            action_frame,
            text="📄 Rows/page:",
            font=("Montserrat", 10),
            bg="#F7F9FC",
            fg="#2C3E50"
        ).pack(side="left", padx=(0, 5))
        
        page_size_menu = ttk.Combobox(
            action_frame, 
            textvariable=self.page_size, 
            values=[6, 8, 10, 12, 24], 
            width=4, 
            state="readonly",
            font=("Montserrat", 10)
        )
        page_size_menu.pack(side="left")
        page_size_menu.bind("<<ComboboxSelected>>", lambda e: self.on_page_size_change())

        # Main content area
        content_frame = tk.Frame(main_container, bg="white")
        content_frame.pack(fill="both", expand=True)

        # Left side - Table (70% width)
        table_container = tk.Frame(content_frame, bg="white", relief=tk.SOLID, bd=1)
        table_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Table header
        table_header = tk.Frame(table_container, bg="#3498DB", height=40)
        table_header.pack(fill="x")
        
        tk.Label(
            table_header,
            text="📋 Test Results History",
            font=("Montserrat", 14, "bold"),
            fg="white",
            bg="#3498DB"
        ).pack(side="left", padx=15)

        # Scrollable table area
        table_inner = tk.Frame(table_container, bg="white")
        table_inner.pack(fill="both", expand=True, padx=1, pady=1)

        # Create canvas with scrollbar
        self.table_canvas = tk.Canvas(table_inner, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_inner, orient="vertical", command=self.table_canvas.yview)
        self.scrollable_frame = tk.Frame(self.table_canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
        )

        self.table_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.table_canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.table_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel for scrolling
        self.table_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Right side - Chart (30% width)
        chart_container = tk.Frame(content_frame, bg="white", relief=tk.SOLID, bd=1, width=350)
        chart_container.pack(side="right", fill="both", expand=False)
        chart_container.pack_propagate(False)

        # Chart header
        chart_header = tk.Frame(chart_container, bg="#9B59B6", height=40)
        chart_header.pack(fill="x")
        
        tk.Label(
            chart_header,
            text="📈 Analytics Chart",
            font=("Montserrat", 14, "bold"),
            fg="white",
            bg="#9B59B6"
        ).pack(side="left", padx=15)

        # Chart area
        self.chart_canvas = tk.Canvas(chart_container, bg="white", highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.chart_canvas.bind("<Configure>", lambda e: self.render_chart())

        # Chart controls
        chart_controls = tk.Frame(chart_container, bg="white", pady=10)
        chart_controls.pack(fill="x", padx=10)
        
        refresh_btn = tk.Button(
            chart_controls,
            text="🔄 Refresh Chart",
            bg="#FF9800",
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=15,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            command=self.render_chart
        )
        refresh_btn.pack()

        # Pagination controls at bottom
        pagination_frame = tk.Frame(main_container, bg="white", pady=10)
        pagination_frame.pack(fill="x")

        prev_btn = tk.Button(
            pagination_frame,
            text="◀ Previous",
            bg="#95A5A6",
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=15,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            command=self.prev_page
        )
        prev_btn.pack(side="left", padx=(0, 10))

        next_btn = tk.Button(
            pagination_frame,
            text="Next ▶",
            bg="#95A5A6",
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=15,
            pady=6,
            relief=tk.RAISED,
            bd=2,
            command=self.next_page
        )
        next_btn.pack(side="left")

        self.page_info_lbl = tk.Label(
            pagination_frame,
            text="Page 0 of 0",
            font=("Montserrat", 11, "bold"),
            bg="white",
            fg="#2C3E50"
        )
        self.page_info_lbl.pack(side="left", padx=20)

        # Status bar at bottom
        status_bar = tk.Frame(self, bg="#2C3E50", height=30)
        status_bar.pack(side="bottom", fill="x")
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready",
            font=("Montserrat", 9),
            fg="#95A5A6",
            bg="#2C3E50"
        )
        self.status_label.pack(side="left", padx=20)

        # initial UI state
        self.on_mode_change()

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling for table"""
        self.table_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # -------------------------
    # Input change handlers
    # -------------------------
    def on_mode_change(self):
        mode = self.selected_summary.get()
        if mode == "Monthly":
            self.month_combo.config(state="readonly")
            self.year_combo.config(state="readonly")
        else:
            # Yearly only
            self.month_combo.config(state="disabled")
            self.year_combo.config(state="readonly")
        
        self.update_status(f"Mode changed to {mode}")

    def on_input_change(self):
        self.current_page = 1
        self.update_status("Filters updated")

    def on_page_size_change(self):
        self.current_page = 1
        self.render_table()
        self.update_status(f"Page size changed to {self.page_size.get()}")

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        # Clear after 3 seconds
        self.after(3000, lambda: self.status_label.config(text="Ready"))

    def manual_cleanup(self):
        """Trigger manual memory cleanup"""
        self.update_status("Cleaning up memory...")
        before = MemoryManager.get_ram_usage()
        MemoryManager.full_cleanup()
        after = MemoryManager.get_ram_usage()
        freed = before - after
        msg = f"Memory Cleaned! Freed: {freed:.1f} MB (Total: {after:.1f} MB)"
        self.update_status(msg)
        messagebox.showinfo("Memory Cleanup", msg)

    # -------------------------
    # Data fetch & parse
    # -------------------------
    def fetch_and_render(self):
        mode = self.selected_summary.get()
        params = {"mode": mode, "year": self.selected_year.get()}
        if mode == "Monthly":
            params["month"] = self.selected_month.get()

        self.update_status("Fetching data from server...")

        try:
            url = API_BASE_URL.rstrip("/") + HISTORY_ENDPOINT
            # requests is light enough to prompt-import if needed, but we keep it
            # implementation note: if requests was heavy we'd lazy import it too
            resp = requests.get(url, params=params, timeout=3) # Short timeout
            resp.raise_for_status()
            payload = resp.json()
            # parse into our canonical rows
            rows = self.parse_api_response(payload, mode)
            self.data = rows
            self.current_page = 1
            self.render_table()
            self.render_chart()
            self.update_status(f"Successfully fetched {len(rows)} records")
            messagebox.showinfo("Success", f"Fetched {len(rows)} rows from server")
        except requests.RequestException as e:
            self.update_status("Failed to fetch data (Mock Data Used)")
            # Fallback mock data for testing
            import random
            mock_data = []
            if mode == "Monthly":
                # Create mock records
                mock_data = []
                for m in self.MONTH_OPTIONS:
                    rec = HistoryRecord(m, random.randint(10, 100), random.randint(5, 50))
                    mock_data.append(rec)
            else:
                mock_data = []
                for y in range(2020, 2025):
                    rec = HistoryRecord(str(y), random.randint(10, 100), random.randint(5, 50))
                    mock_data.append(rec)
            
            self.data = mock_data
            self.render_table()
            self.render_chart()

    def parse_api_response(self, payload, mode):
        # ... logic reused ...
        if not isinstance(payload, list):
            if isinstance(payload, dict) and "data" in payload:
                payload = payload["data"]
            else:
                return []

        canonical = []
        for item in payload:
            month = item.get("month") or item.get("name") or str(item.get("id"))
            # specific optimization: use slotted class
            rec = HistoryRecord(
                month=str(month),
                positive=int(item.get("positive", 0)),
                negative=int(item.get("negative", 0)),
                high_time=item.get("high_time", ""),
                low_time=item.get("low_time", "")
            )
            canonical.append(rec)
        return canonical

    # -------------------------
    # Table rendering & pagination
    # -------------------------
    def render_table(self):
        # Clear previous rows
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        # Create table headers
        header_frame = tk.Frame(self.scrollable_frame, bg="#3498DB")
        header_frame.pack(fill="x", pady=(0, 2))

        headers = ["Month", "Positive Tests", "Negative Tests", "Peak Time", "Off-Peak Time"]
        for i, h in enumerate(headers):
            lbl = tk.Label(
                header_frame,
                text=h,
                font=("Montserrat", 11, "bold"),
                fg="white",
                bg="#3498DB",
                width=20,
                height=2,
                relief=tk.FLAT
            )
            lbl.pack(side="left", padx=1, fill="x", expand=True)

        total = len(self.data)
        size = int(self.page_size.get())
        total_pages = max(1, math.ceil(total / size))
        if self.current_page > total_pages:
            self.current_page = total_pages

        start = (self.current_page - 1) * size
        end = start + size
        page_rows = self.data[start:end]
        
        colors = ["#FFFFFF", "#F7F9FC"]
        for idx, row in enumerate(page_rows):
            row_color = colors[idx % 2]
            row_frame = tk.Frame(self.scrollable_frame, bg=row_color, height=35)
            row_frame.pack(fill="x", pady=1)

            # Columns - Access attributes from slotted object
            cols = [row.month, str(row.positive), str(row.negative), row.high_time, row.low_time]
            col_colors = ["#2C3E50", "#27AE60", "#E74C3C", "#2C3E50", "#2C3E50"]
            
            for i, val in enumerate(cols):
                 tk.Label(
                    row_frame, text=val, font=("Montserrat", 10),
                    bg=row_color, fg=col_colors[i], width=20, anchor="center"
                 ).pack(side="left", fill="both", expand=True)

        self.page_info_lbl.config(text=f"Page {self.current_page} of {total_pages}")
        self.update_status(f"Displaying {len(page_rows)} of {total} records")

    def next_page(self):
        if self.current_page * int(self.page_size.get()) < len(self.data):
            self.current_page += 1
            self.render_table()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_table()

    # -------------------------
    # Chart rendering (Canvas impl)
    # -------------------------
    def init_chart_objects(self):
        """Create chart objects (12 bars max)"""
        # Axes
        self.chart_canvas.create_line(0,0,0,0, fill="gray", tags="axis_y")
        self.chart_canvas.create_line(0,0,0,0, fill="gray", tags="axis_x")
        
        # Max 12 bars supported
        for i in range(12):
            # Pos Bar
            self.chart_canvas.create_rectangle(0,0,0,0, fill="#27AE60", outline="", tags=f"p_bar_{i}", state="hidden")
            # Neg Bar
            self.chart_canvas.create_rectangle(0,0,0,0, fill="#E74C3C", outline="", tags=f"n_bar_{i}", state="hidden")
            # Label
            self.chart_canvas.create_text(0,0, text="", font=("Arial", 8), tags=f"lbl_{i}", state="hidden")

    def render_chart(self):
        """Draw bar chart on canvas (Recycling)"""
        # Ensure objects exist (lazy init if not called in __init__)
        if not self.chart_canvas.find_withtag("axis_y"):
            self.init_chart_objects()

        if not self.data:
            # Hide all
            for i in range(12):
                 self.chart_canvas.itemconfigure(f"p_bar_{i}", state="hidden")
                 self.chart_canvas.itemconfigure(f"n_bar_{i}", state="hidden")
                 self.chart_canvas.itemconfigure(f"lbl_{i}", state="hidden")
            return

        w = self.chart_canvas.winfo_width()
        h = self.chart_canvas.winfo_height()
        if w <= 1 or h <= 1: return

        margin_left = 40
        margin_bottom = 30
        graph_w = w - margin_left - 20
        graph_h = h - margin_bottom - 20

        # Update Axes
        self.chart_canvas.coords("axis_y", margin_left, 20, margin_left, h-margin_bottom)
        self.chart_canvas.coords("axis_x", margin_left, h-margin_bottom, w-20, h-margin_bottom)

        # Find max value
        max_val = 0
        for r in self.data:
            max_val = max(max_val, r.positive, r.negative)
        if max_val == 0: max_val = 10

        # Draw Bars
        display_data = self.data[:12]
        bar_count = len(display_data)
        
        # If no bars, hide everything
        if bar_count == 0:
            for i in range(12):
                 self.chart_canvas.itemconfigure(f"p_bar_{i}", state="hidden")
                 self.chart_canvas.itemconfigure(f"n_bar_{i}", state="hidden")
                 self.chart_canvas.itemconfigure(f"lbl_{i}", state="hidden")
            return
        
        bar_width = (graph_w / bar_count) * 0.4
        spacing = (graph_w / bar_count)
        
        for i in range(12):
            if i < bar_count:
                row = display_data[i]
                x_center = margin_left + (i * spacing) + (spacing/2)
                
                # Positive Bar
                pos_h = (row.positive / max_val) * graph_h
                if pos_h > 0:
                    x1 = x_center - bar_width
                    y1 = h - margin_bottom - pos_h
                    x2 = x_center
                    y2 = h - margin_bottom
                    self.chart_canvas.coords(f"p_bar_{i}", x1, y1, x2, y2)
                    self.chart_canvas.itemconfigure(f"p_bar_{i}", state="normal")
                else:
                    self.chart_canvas.itemconfigure(f"p_bar_{i}", state="hidden")
                
                # Negative Bar
                neg_h = (row.negative / max_val) * graph_h
                if neg_h > 0:
                    x1 = x_center
                    y1 = h - margin_bottom - neg_h
                    x2 = x_center + bar_width
                    y2 = h - margin_bottom
                    self.chart_canvas.coords(f"n_bar_{i}", x1, y1, x2, y2)
                    self.chart_canvas.itemconfigure(f"n_bar_{i}", state="normal")
                else:
                    self.chart_canvas.itemconfigure(f"n_bar_{i}", state="hidden")
                
                # Label
                label = row.month[:3]
                self.chart_canvas.coords(f"lbl_{i}", x_center, h-margin_bottom+10)
                self.chart_canvas.itemconfigure(f"lbl_{i}", text=label, state="normal")
            else:
                # Hide unused bars
                self.chart_canvas.itemconfigure(f"p_bar_{i}", state="hidden")
                self.chart_canvas.itemconfigure(f"n_bar_{i}", state="hidden")
                self.chart_canvas.itemconfigure(f"lbl_{i}", state="hidden")

    # -------------------------
    # Exports
    # -------------------------
    def export_excel(self):
        if not self.data:
            messagebox.showwarning("No Data", "No data to export")
            return
        
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path: return

        self.update_status("Exporting to Excel (loading openpyxl)...")
        self.after(100, lambda: self._do_export_excel(path))

    def _do_export_excel(self, path):
        try:
            import openpyxl
            # optimizing: use write_only=True (Stream writing)
            wb = openpyxl.Workbook(write_only=True)
            ws = wb.create_sheet()
            ws.append(["Month", "Positive", "Negative", "Peak Time", "Off-Peak"])
            
            for r in self.data:
                # If using __slots__ object, access attributes, if dict access keys
                if hasattr(r, 'month'):
                     ws.append([r.month, r.positive, r.negative, r.high_time, r.low_time])
                else:
                     ws.append([r["month"], r["positive"], r["negative"], r.get("high_time",""), r.get("low_time","")])
            
            wb.save(path)
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            MemoryManager.cleanup_heavy_modules()
            self.update_status("Export finished & Memory cleaned")

    def save_pdf(self):
        if not self.data: return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not path: return

        self.update_status("Exporting to PDF (loading ReportLab)...")
        self.after(100, lambda: self._do_save_pdf(path))

    def _do_save_pdf(self, path):
        try:
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.pagesizes import A4
            
            c = pdf_canvas.Canvas(path, pagesize=A4)
            width, height = A4
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height-50, "History Report")
            c.setFont("Helvetica", 10)
            
            y = height - 100
            for r in self.data:
                # Optimized access
                line = f"{r.month}: +{r.positive} / -{r.negative}"
                c.drawString(50, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50
            
            c.save()
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            MemoryManager.cleanup_heavy_modules()
            self.update_status("Export finished & Memory cleaned")

    def destroy(self):
        super().destroy()
        MemoryManager.full_cleanup()

    def go_back(self):
        self.destroy()
        if self.go_back_callback:
            self.go_back_callback()