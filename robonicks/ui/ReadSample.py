import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random
import math
from utils.memory_manager import MemoryManager

# Add sibling path if needed, but no backend path required
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
robonicks_dir = os.path.dirname(os.path.dirname(current_dir))
if robonicks_dir not in sys.path:
    sys.path.append(robonicks_dir)


class ReadSamplePage(tk.Frame):
    def __init__(self, root, go_back_callback=None):
        super().__init__(root)
        self.root = root
        self.go_back_callback = go_back_callback
        
        # Initialize Services
        from services.test_result_service import TestResultService
        self.test_result_service = TestResultService()
        
        self.COLORS = {
            'primary': '#1BC6B4',      # Teal
            'secondary': '#3AC7F1',    # Light Blue
            'accent': '#2E8B57',       # Sea Green
            'danger': '#E74C3C',       # Red
            'warning': '#F39C12',      # Orange
            'success': '#27AE60',      # Green
            'light': '#F7F9FC',        # Light Gray
            'white': '#FFFFFF',
            'dark': '#2C3E50',         # Dark Gray
            'gray': '#95A5A6'          # Medium Gray
        }
        
        self.build_ui()
        self.pack(fill='both', expand=True)
    
    def _fetch_current_stock(self):
        """Fetch current stock from backend API"""
        try:
            import requests
            response = requests.get("http://127.0.0.1:8001/ops/current-stock", timeout=2)
            if response.ok:
                return response.json().get("total_remaining", 0)
        except:
            pass
        return 0
    
    def build_ui(self):
        # Main container
        main_container = tk.Frame(self, bg=self.COLORS['light'])
        main_container.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(main_container, bg=self.COLORS['primary'], height=80)
        header.pack(fill='x', pady=(0, 20))
        
        # Title
        title_frame = tk.Frame(header, bg=self.COLORS['primary'])
        title_frame.pack(side='left', padx=30, fill='y')
        
        tk.Label(
            title_frame,
            text="🔬 I.V.D",
            font=("Montserrat", 28, "bold"),
            fg="white",
            bg=self.COLORS['primary']
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="Parasite Diagnostic System",
            font=("Montserrat", 12),
            fg="#E8F4F8",
            bg=self.COLORS['primary']
        ).pack(anchor='w', pady=(5, 0))
        
        # Back button
        if self.go_back_callback:
            back_btn = tk.Button(
                header,
                text="← Back to Home",
                font=("Montserrat", 11, "bold"),
                bg=self.COLORS['secondary'],
                fg="white",
                activebackground=self.COLORS['accent'],
                bd=0,
                relief=tk.FLAT,
                padx=20,
                pady=8,
                cursor="hand2",
                command=self.go_back
            )
            back_btn.pack(side='right', padx=30)
        
        # Main content area
        content = tk.Frame(main_container, bg=self.COLORS['light'])
        content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Sample Input
        left_panel = tk.Frame(content, bg='white', relief=tk.RAISED, bd=2)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Left panel header
        left_header = tk.Frame(left_panel, bg=self.COLORS['primary'], height=40)
        left_header.pack(fill='x')
        
        tk.Label(
            left_header,
            text="Sample Processing",
            font=("Montserrat", 14, "bold"),
            fg="white",
            bg=self.COLORS['primary']
        ).pack(side='left', padx=15)
        
        # ID section
        id_frame = tk.Frame(left_panel, bg='white', padx=20, pady=20)
        id_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(
            id_frame,
            text="ID:",
            font=("Montserrat", 12, "bold"),
            bg='white',
            fg=self.COLORS['dark']
        ).pack(anchor='w')
        
        # ID input options
        id_options_frame = tk.Frame(id_frame, bg='white')
        id_options_frame.pack(fill='x', pady=(10, 0))
        
        # Barcode/auto selection
        self.id_method = tk.StringVar(value="auto")
        
        barcode_radio = tk.Radiobutton(
            id_options_frame,
            text="Barcode",
            variable=self.id_method,
            value="barcode",
            bg='white',
            font=("Montserrat", 10)
        )
        barcode_radio.pack(side='left', padx=(0, 20))
        
        auto_radio = tk.Radiobutton(
            id_options_frame,
            text="Auto-generate",
            variable=self.id_method,
            value="auto",
            bg='white',
            font=("Montserrat", 10)
        )
        auto_radio.pack(side='left')
        
        # ID input field
        id_input_frame = tk.Frame(id_frame, bg='white')
        id_input_frame.pack(fill='x', pady=(10, 0))
        
        self.id_var = tk.StringVar()
        id_entry = tk.Entry(
            id_input_frame,
            textvariable=self.id_var,
            font=("Montserrat", 11),
            width=30,
            relief=tk.SOLID,
            bd=1
        )
        id_entry.pack(side='left', padx=(0, 10))
        
        # Generate button
        gen_btn = tk.Button(
            id_input_frame,
            text="Generate ID",
            command=self.generate_id,
            bg=self.COLORS['secondary'],
            fg="white",
            font=("Montserrat", 10),
            padx=15,
            pady=5
        )
        gen_btn.pack(side='left')
        
        # Current date
        date_frame = tk.Frame(id_frame, bg='white')
        date_frame.pack(fill='x', pady=(20, 0))
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        tk.Label(
            date_frame,
            text="Current Date:",
            font=("Montserrat", 11, "bold"),
            bg='white',
            fg=self.COLORS['dark']
        ).pack(side='left', padx=(0, 10))
        
        date_label = tk.Label(
            date_frame,
            textvariable=self.date_var,
            font=("Montserrat", 11),
            bg='white',
            fg=self.COLORS['dark']
        )
        date_label.pack(side='left')
        
        # Cuvette instructions
        instructions_frame = tk.Frame(left_panel, bg='white', padx=20, pady=20)
        instructions_frame.pack(fill='x', pady=(10, 0))
        
        # Step 1
        step1_frame = tk.Frame(instructions_frame, bg='white')
        step1_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            step1_frame,
            text="1. Remove cuvette if present & press Enter",
            font=("Montserrat", 11),
            bg='white',
            fg=self.COLORS['dark']
        ).pack(side='left', padx=(0, 15))
        
        step1_btn = tk.Button(
            step1_frame,
            text="Enter",
            command=self.remove_cuvette,
            bg=self.COLORS['warning'],
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=20,
            pady=6
        )
        step1_btn.pack(side='right')
        
        # Step 2
        step2_frame = tk.Frame(instructions_frame, bg='white')
        step2_frame.pack(fill='x')
        
        tk.Label(
            step2_frame,
            text="2. Insert cuvette & press Enter",
            font=("Montserrat", 11),
            bg='white',
            fg=self.COLORS['dark']
        ).pack(side='left', padx=(0, 15))
        
        step2_btn = tk.Button(
            step2_frame,
            text="Enter",
            command=self.insert_cuvette,
            bg=self.COLORS['success'],
            fg="white",
            font=("Montserrat", 10, "bold"),
            padx=20,
            pady=6
        )
        step2_btn.pack(side='right')
        
        # Right panel - Results and Chart
        right_panel = tk.Frame(content, bg='white', relief=tk.RAISED, bd=2)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Right panel header
        right_header = tk.Frame(right_panel, bg=self.COLORS['primary'], height=40)
        right_header.pack(fill='x')
        
        tk.Label(
            right_header,
            text="Analysis Results",
            font=("Montserrat", 14, "bold"),
            fg="white",
            bg=self.COLORS['primary']
        ).pack(side='left', padx=15)
        
        # Results table
        results_frame = tk.Frame(right_panel, bg='white', padx=20, pady=20)
        results_frame.pack(fill='both', expand=True)
        
        # Table header
        table_header = tk.Frame(results_frame, bg=self.COLORS['secondary'])
        table_header.pack(fill='x')
        
        tk.Label(
            table_header,
            text="ID",
            font=("Montserrat", 12, "bold"),
            fg="white",
            bg=self.COLORS['secondary'],
            width=15
        ).pack(side='left', padx=1)
        
        tk.Label(
            table_header,
            text="Result",
            font=("Montserrat", 12, "bold"),
            fg="white",
            bg=self.COLORS['secondary'],
            width=15
        ).pack(side='left', padx=1)
        
        tk.Label(
            table_header,
            text="Time",
            font=("Montserrat", 12, "bold"),
            fg="white",
            bg=self.COLORS['secondary'],
            width=15
        ).pack(side='left', padx=1)
        
        # Parasite count table entries
        # We need to access these later to update them
        self.result_vars = {}
        
        parasite_rows = [
            ("No. of Parasite", "count_total"),
            ("> 2000", "count_2000"),
            ("> 200", "count_200"),
            ("> 20", "count_20"),
            ("< 5", "count_5")
        ]
        
        for i, (label_text, key) in enumerate(parasite_rows):
            row_frame = tk.Frame(results_frame, bg='white' if i % 2 == 0 else self.COLORS['light'])
            row_frame.pack(fill='x', pady=1)
            
            tk.Label(
                row_frame,
                text=label_text,
                font=("Montserrat", 11),
                bg=row_frame.cget('bg'),
                fg=self.COLORS['dark'],
                width=15
            ).pack(side='left', padx=1)
            
            # Result entry (The number count)
            res_var = tk.StringVar(value="")
            self.result_vars[key] = res_var
            
            result_entry = tk.Entry(
                row_frame,
                textvariable=res_var,
                font=("Montserrat", 11),
                width=15,
                relief=tk.SOLID,
                bd=1
            )
            result_entry.pack(side='left', padx=1)
            
            # Time entry (placeholder for now)
            time_var = tk.StringVar(value="" if i==0 else ("secs" if i == 2 else ""))
            time_entry = tk.Entry(
                row_frame,
                textvariable=time_var,
                font=("Montserrat", 11),
                width=15,
                relief=tk.SOLID,
                bd=1
            )
            time_entry.pack(side='left', padx=1)
        
        # Chart frame
        chart_frame = tk.Frame(right_panel, bg='white', padx=20, pady=20)
        chart_frame.pack(fill='both', expand=True)
        
        # Chart title
        tk.Label(
            chart_frame,
            text="AD3 Count vs Time",
            font=("Montserrat", 13, "bold"),
            bg='white',
            fg=self.COLORS['dark']
        ).pack(anchor='w')
        
        # Create chart using Canvas instead of Matplotlib
        self.chart_canvas = tk.Canvas(chart_frame, bg='white', highlightthickness=0)
        self.chart_canvas.pack(fill='both', expand=True, pady=(10, 0))
        self.chart_canvas.bind('<Configure>', self.draw_chart) # Redraw on resize
        
        # Initial chart data
        self.chart_data = {
             'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
             'y': [0] * 12 # Start empty
        }
        
        # Current stock display
        stock_frame = tk.Frame(main_container, bg=self.COLORS['dark'], height=40)
        stock_frame.pack(side='bottom', fill='x')
        
        # Fetch current stock from API
        initial_stock = self._fetch_current_stock()
        self.stock_var = tk.StringVar(value=f"Current stock: {initial_stock}")
        stock_label = tk.Label(
            stock_frame,
            textvariable=self.stock_var,
            font=("Montserrat", 11, "bold"),
            fg="white",
            bg=self.COLORS['dark']
        )
        stock_label.pack(side='right', padx=30)
        
        # Action buttons
        action_frame = tk.Frame(main_container, bg=self.COLORS['light'], pady=20)
        action_frame.pack(side='bottom', fill='x')
        
        # Start analysis button
        start_btn = tk.Button(
            action_frame,
            text="▶ Start Analysis",
            command=self.start_analysis,
            bg=self.COLORS['success'],
            fg="white",
            font=("Montserrat", 12, "bold"),
            padx=30,
            pady=10,
            relief=tk.RAISED,
            bd=2
        )
        start_btn.pack(side='left', padx=(30, 10))
        
        # Clear button
        clear_btn = tk.Button(
            action_frame,
            text="🗑️ Clear All",
            command=self.clear_all,
            bg=self.COLORS['danger'],
            fg="white",
            font=("Montserrat", 12, "bold"),
            padx=30,
            pady=10,
            relief=tk.RAISED,
            bd=2
        )
        clear_btn.pack(side='left', padx=10)
        
        # Save results button
        save_btn = tk.Button(
            action_frame,
            text="💾 Save Results",
            command=self.save_results,
            bg=self.COLORS['secondary'],
            fg="white",
            font=("Montserrat", 12, "bold"),
            padx=30,
            pady=10,
            relief=tk.RAISED,
            bd=2
        )
    
        # Initialize canvas objects once
        self.init_canvas_objects()

    def init_canvas_objects(self):
        """Create canvas objects once for recycling"""
        # Axes
        self.chart_canvas.create_line(0,0,0,0, fill="#7F8C8D", width=2, tags="axis_y")
        self.chart_canvas.create_line(0,0,0,0, fill="#7F8C8D", width=2, tags="axis_x")
        
        # Grid & Labels (Fixed count: 6 Y-steps, 7 X-steps)
        for i in range(6):
            self.chart_canvas.create_line(0,0,0,0, fill="#ECF0F1", dash=(4, 4), tags=f"grid_y_{i}")
            self.chart_canvas.create_text(0,0, text="", anchor="e", font=("Montserrat", 8), fill="#7F8C8D", tags=f"label_y_{i}")
            
        for i in range(7): # 0, 2, 4... 12
            self.chart_canvas.create_text(0,0, text="", anchor="n", font=("Montserrat", 8), fill="#7F8C8D", tags=f"label_x_{i}")

        # Data Objects (Max 12 points)
        for i in range(12):
            # Point
            self.chart_canvas.create_oval(0,0,0,0, fill="#3498DB", outline="white", tags=f"point_{i}", state="hidden")
            # Value Label
            self.chart_canvas.create_text(0,0, text="", font=("Montserrat", 8), fill="#3498DB", tags=f"val_{i}", state="hidden")

        # Line & Area
        self.chart_canvas.create_line(0,0,0,0, fill="#3498DB", width=2, smooth=True, tags="data_line", state="hidden")
        self.chart_canvas.create_polygon(0,0,0,0, fill="#D6EAF8", outline="", smooth=True, tags="data_area", state="hidden")

    def draw_chart(self, event=None):
        """Update chart object coordinates (No delete)"""
        w = self.chart_canvas.winfo_width()
        h = self.chart_canvas.winfo_height()
        
        # Margins
        margin_left = 40
        margin_bottom = 30
        margin_top = 20
        margin_right = 20
        
        graph_w = w - margin_left - margin_right
        graph_h = h - margin_bottom - margin_top
        
        if graph_w <= 0 or graph_h <= 0: return

        # Update Axes
        self.chart_canvas.coords("axis_y", margin_left, margin_top, margin_left, h - margin_bottom)
        self.chart_canvas.coords("axis_x", margin_left, h - margin_bottom, w - margin_right, h - margin_bottom)
        
        # Update Grid & Y-Labels
        # Determine logical Y max
        data_max = max(self.chart_data['y']) if self.chart_data['y'] else 0
        max_y = max(80, data_max + 10)
        
        steps = 5
        for i in range(steps + 1):
            val = int((max_y / steps) * i)
            y_pos = h - margin_bottom - (val / max_y) * graph_h
            
            self.chart_canvas.coords(f"grid_y_{i}", margin_left, y_pos, w - margin_right, y_pos)
            self.chart_canvas.coords(f"label_y_{i}", margin_left - 5, y_pos)
            self.chart_canvas.itemconfigure(f"label_y_{i}", text=str(val))

        # Update X-Labels
        max_x = 12
        for idx, i in enumerate(range(0, max_x + 1, 2)):
            x_pos = margin_left + (i / max_x) * graph_w
            self.chart_canvas.coords(f"label_x_{idx}", x_pos, h - margin_bottom + 15)
            self.chart_canvas.itemconfigure(f"label_x_{idx}", text=str(i))
            
        # Draw Data Line & Area
        if not self.chart_data['x']: 
            self.chart_canvas.itemconfigure("data_line", state="hidden")
            self.chart_canvas.itemconfigure("data_area", state="hidden")
            return
        
        points = []
        for i, (x_val, y_val) in enumerate(zip(self.chart_data['x'], self.chart_data['y'])):
            x = margin_left + (x_val / max_x) * graph_w
            y = h - margin_bottom - (y_val / max_y) * graph_h
            points.extend([x, y])
            
            # Update points
            self.chart_canvas.coords(f"point_{i}", x-3, y-3, x+3, y+3)
            self.chart_canvas.itemconfigure(f"point_{i}", state="normal")
            
            # Update value labels (every 2nd point)
            if x_val % 2 == 0:
                self.chart_canvas.coords(f"val_{i}", x, y - 10)
                self.chart_canvas.itemconfigure(f"val_{i}", text=str(y_val), state="normal")
            else:
                self.chart_canvas.itemconfigure(f"val_{i}", state="hidden")

        if len(points) >= 4:
            self.chart_canvas.coords("data_line", *points)
            self.chart_canvas.itemconfigure("data_line", state="normal")
            
            # Area
            fill_points = points.copy()
            fill_points.extend([points[-2], h - margin_bottom])
            fill_points.extend([points[0], h - margin_bottom])
            self.chart_canvas.coords("data_area", *fill_points)
            self.chart_canvas.itemconfigure("data_area", state="normal")

    def generate_id(self):
        """Generate a sample ID"""
        if self.id_method.get() == "auto":
            sample_id = f"SMP-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            self.id_var.set(sample_id)
            messagebox.showinfo("ID Generated", f"Generated Sample ID: {sample_id}")
        else:
            messagebox.showinfo("Barcode Mode", "Please scan barcode or enter ID manually")
    
    def remove_cuvette(self):
        """Handle remove cuvette action"""
        self.date_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        messagebox.showinfo("Step 1", "Cuvette removal confirmed. Please insert new cuvette.")
    
    def insert_cuvette(self):
        """Handle insert cuvette action"""
        self.date_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        messagebox.showinfo("Step 2", "Cuvette inserted. Ready for analysis.")
    
    def start_analysis(self):
        """Start the analysis process"""
        if not self.id_var.get():
            messagebox.showwarning("Missing ID", "Please enter or generate a Sample ID first.")
            return
        
        # Simulate analysis
        messagebox.showinfo("Analysis Started", 
                          f"Starting analysis for Sample ID: {self.id_var.get()}\n"
                          "Please wait...")
        
        # Simulate results after delay
        self.after(2000, self.simulate_results)
    
    def simulate_results(self):
        """Simulate realistic analysis results and save to DB"""
        
        # 1. Generate Logical Random Data
        # We simulate "Reading" particles
        
        # Categories: >2000 (Very High), >200 (High), >20 (Med), <5 (Noise/Low)
        # To make it realistic, we'll choose a "Scenario" first
        scenario = random.choice(["negative", "positive_low", "positive_high"])
        
        if scenario == "negative":
            c_2000 = 0
            c_200 = random.randint(0, 5)
            c_20 = random.randint(0, 20)
            c_5 = random.randint(5, 50)
            total_parasites = 0 # Clinically negative
            species = None
            result_val = "Negative"
            abnormal_flag = "N"
            
        elif scenario == "positive_low":
            c_2000 = 0
            c_200 = random.randint(5, 30)
            c_20 = random.randint(30, 100)
            c_5 = random.randint(50, 150)
            total_parasites = c_2000 + c_200 + c_20 # Count relevant ones
            species = random.choice(["Plasmodium vivax", "Plasmodium falciparum"])
            result_val = "Positive"
            abnormal_flag = "A"
            
        else: # positive_high
            c_2000 = random.randint(5, 50)
            c_200 = random.randint(50, 200)
            c_20 = random.randint(100, 300)
            c_5 = random.randint(100, 500)
            total_parasites = c_2000 + c_200 + c_20
            species = "Plasmodium falciparum" # Usually associated with high counts
            result_val = "Positive"
            abnormal_flag = "A"

        # 2. Update UI Variables
        self.result_vars["count_2000"].set(str(c_2000))
        self.result_vars["count_200"].set(str(c_200))
        self.result_vars["count_20"].set(str(c_20))
        self.result_vars["count_5"].set(str(c_5))
        self.result_vars["count_total"].set(str(total_parasites))
        
        # 3. Update Chart Data
        # Generate a curve that generally rises
        points = []
        current = 0
        for _ in range(12):
            step = random.randint(0, max(5, int(total_parasites / 10)))
            current += step
            points.append(current)
            
        # Normalize to last point near total for visual consistency
        if points[-1] > 0 and total_parasites > 0:
            scale = total_parasites / points[-1]
            points = [int(p * scale) * (random.uniform(0.8, 1.2)) for p in points]
        
        self.chart_data['y'] = points
        self.draw_chart()
        
        # 4. Prepare Data for Database
        sample_id = self.id_var.get()
        
        # We leave patient data blank as requested
        patient_data = {
            'patient_id': '', # Blank
            'first_name': '',
            'last_name': '',
            'dob': '',
            'gender': '',
            'phone': ''
        }
        
        # Primary Result Data
        result_data = {
            'test_code': 'PARASITE',
            'loinc_code': '850.1', # Imaginary LOINC for this example
            'result_value': result_val,
            'result_unit': 'count/uL',
            'reference_range': 'Negative',
            'abnormal_flag': abnormal_flag,
            'result_status': 'F', # Final
            'parasite_detected': (result_val == "Positive"),
            'parasite_species': species,
            'parasite_count': total_parasites,
            'microscopy_findings': f"Automated analysis: {c_2000} (>2000), {c_200} (>200)",
            'order_number': sample_id,
            'ordering_provider': 'System',
            'operator_id': 'Admin',
            'sample_collected_at': datetime.now()
        }
        
        # Additional Detailed Observations (Rows in OBX / Result records)
        observations = [
            {
                'test_code': 'CNT_2000',
                'test_name': 'Count > 2000',
                'value': str(c_2000),
                'unit': 'count',
                'reference_range': '0',
                'abnormal_flag': 'H' if c_2000 > 0 else 'N'
            },
            {
                'test_code': 'CNT_200',
                'test_name': 'Count > 200',
                'value': str(c_200),
                'unit': 'count'
            },
            {
                'test_code': 'CNT_20',
                'test_name': 'Count > 20',
                'value': str(c_20),
                'unit': 'count'
            }
        ]
        
        # 5. Save to Database (Which generates HL7/ASTM)
        print(f"Saving result for {sample_id}...")
        try:
            result_id = self.test_result_service.save_test_result(
                sample_id=sample_id,
                test_name="Malaria Parasite Detection",
                result_data=result_data,
                patient_data=patient_data,
                observations=observations,
                device_id="ROBO_DEV_01"
            )
            
            if result_id:
                print(f"Successfully saved Result ID: {result_id}")
                messagebox.showinfo("Analysis Complete", 
                                  f"Analysis completed for Sample ID: {sample_id}\n"
                                  f"Result: {result_val}\n"
                                  f"Data saved to database with protocols.")
            else:
                messagebox.showerror("Save Error", "Failed to save results to database.")
                
        except Exception as e:
            print(f"Exception saving result: {e}")
            messagebox.showerror("System Error", f"Error saving content: {e}")

        # Update stock via backend API (Lightweight - no local logic)
        try:
            import requests
            sample_id = self.id_var.get()
            
            response = requests.post(
                "http://127.0.0.1:8001/ops/run-test",
                params={"sample_id": sample_id},
                timeout=5
            )
            
            if response.ok:
                data = response.json()
                remaining = data.get("remaining_stock", "N/A")
                self.stock_var.set(f"Current stock: {remaining}")
                print(f"Stock updated via API: {remaining} remaining")
            else:
                print(f"API Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("Backend not available - stock not updated")
        except Exception as e:
            print(f"Stock update error: {e}")
    
    def save_results(self):
        """Manual save (Already handled in simulate, but just in case)"""
        # Since we auto-save in simulate_results, this can be just a confirmation
        if not self.id_var.get():
             messagebox.showwarning("No Data", "No analysis results to save.")
             return
             
        messagebox.showinfo("Info", "Results are automatically saved after analysis.")
        
    def clear_all(self):
        """Clear all input fields"""
        self.id_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Clear result vars
        for var in self.result_vars.values():
            var.set("")
        
        # Reset chart to initial state
        self.chart_data = {
            'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'y': [0] * 12
        }
        self.draw_chart()
        
        messagebox.showinfo("Cleared", "All fields have been cleared.")
    
    def go_back(self):
        """Go back to home menu"""
        # Clean up matplot (if any)
        if hasattr(self, 'fig'):
             try:
                 import matplotlib.pyplot as plt
                 plt.close(self.fig)
             except ImportError:
                 pass
        
        self.destroy()
        MemoryManager.full_cleanup()
        
        if self.go_back_callback:
            self.go_back_callback()
    
    # Static method used in ReadSample demo at bottom, ignore for now
    
if __name__ == "__main__":
    # minimal dummy for standalone testing
    root = tk.Tk()
    app = ReadSamplePage(root) # This will fail if DB not found in standalone
    root.mainloop()