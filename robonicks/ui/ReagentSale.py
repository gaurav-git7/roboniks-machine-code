"""
Reagent Management Page - Improved UI with Teal Theme
Matches the styling of other screens (ReadSample, Stock, History)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
import random

def create_reagent_page(root, go_back_callback=None):
    """Create reagent management page with improved UI"""
    
    COLORS = {
        'primary': '#1BC6B4',
        'secondary': '#3AC7F1',
        'accent': '#2E8B57',
        'danger': '#E74C3C',
        'warning': '#F39C12',
        'success': '#27AE60',
        'light': '#F7F9FC',
        'white': '#FFFFFF',
        'dark': '#2C3E50',
        'gray': '#95A5A6'
    }
    
    frame = tk.Frame(root, bg=COLORS['light'])
    
    def fetch_current_stock():
        """Fetch current stock from backend API"""
        try:
            import requests
            response = requests.get("http://127.0.0.1:8001/ops/current-stock", timeout=2)
            if response.ok:
                data = response.json()
                return data.get("total_remaining", 0), len(data.get("items", []))
        except:
            pass
        return 0, 0
    
    # Get live stock data
    remaining_tests, active_reagents = fetch_current_stock()
    
    # Header (Teal - matching other screens)
    header = tk.Frame(frame, bg=COLORS['primary'], height=80)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    left_header = tk.Frame(header, bg=COLORS['primary'])
    left_header.pack(side=tk.LEFT, padx=30, fill=tk.Y)
    
    tk.Label(left_header, text="🧪 I.V.D", font=("Montserrat", 28, "bold"),
            fg="white", bg=COLORS['primary']).pack(anchor='w', pady=(10, 0))
    tk.Label(left_header, text="Reagent Management System", font=("Montserrat", 12),
            fg="#E8F4F8", bg=COLORS['primary']).pack(anchor='w')
    
    right_header = tk.Frame(header, bg=COLORS['primary'])
    right_header.pack(side=tk.RIGHT, padx=30, fill=tk.Y)
    
    if go_back_callback:
        tk.Button(right_header, text="← Back to Home", command=go_back_callback,
                 bg=COLORS['secondary'], fg="white", font=("Montserrat", 11, "bold"),
                 bd=0, padx=20, pady=8, cursor="hand2",
                 activebackground=COLORS['accent']).pack(pady=20)
    
    # Main content area
    content = tk.Frame(frame, bg=COLORS['light'])
    content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
    
    # Stats Cards Row
    cards_frame = tk.Frame(content, bg=COLORS['light'])
    cards_frame.pack(fill=tk.X, pady=(0, 15))
    
    def create_card(parent, title, value, color):
        card = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        inner = tk.Frame(card, bg="white", padx=20, pady=15)
        inner.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(inner, text=title, font=("Montserrat", 10), bg="white", fg=COLORS['gray']).pack(anchor='w')
        tk.Label(inner, text=str(value), font=("Montserrat", 28, "bold"), bg="white", fg=color).pack(anchor='w')
        
        # Color accent bar
        accent = tk.Frame(card, bg=color, height=4)
        accent.pack(side=tk.BOTTOM, fill=tk.X)
    
    create_card(cards_frame, "Remaining Tests", remaining_tests, COLORS['warning'])
    create_card(cards_frame, "Active Batches", active_reagents, COLORS['success'])
    create_card(cards_frame, "Tests per Pack", "50", COLORS['secondary'])
    create_card(cards_frame, "Status", "Active" if remaining_tests > 0 else "Empty", 
                COLORS['success'] if remaining_tests > 0 else COLORS['danger'])
    
    # Two Column Layout
    columns = tk.Frame(content, bg=COLORS['light'])
    columns.pack(fill=tk.BOTH, expand=True)
    
    # Left Panel - Control
    left_panel = tk.Frame(columns, bg="white", relief=tk.RAISED, bd=1)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # Left panel header
    left_header_bar = tk.Frame(left_panel, bg=COLORS['primary'], height=45)
    left_header_bar.pack(fill=tk.X)
    left_header_bar.pack_propagate(False)
    tk.Label(left_header_bar, text="⚙️ Reagent Control", font=("Montserrat", 14, "bold"),
            fg="white", bg=COLORS['primary']).pack(side=tk.LEFT, padx=20, pady=10)
    
    control_content = tk.Frame(left_panel, bg="white", padx=30, pady=25)
    control_content.pack(fill=tk.BOTH, expand=True)
    
    # Purchase Button
    purchase_btn = tk.Button(control_content, text="🛒 Purchase Reagent",
                            bg=COLORS['secondary'], fg="white",
                            font=("Montserrat", 13, "bold"), bd=0,
                            padx=30, pady=15, cursor="hand2",
                            command=lambda: messagebox.showinfo("Purchase", "Opening purchase portal..."))
    purchase_btn.pack(fill=tk.X, pady=(0, 20))
    
    # OTP Section
    otp_frame = tk.LabelFrame(control_content, text=" OTP Verification ", 
                              font=("Montserrat", 11, "bold"), bg="white",
                              fg=COLORS['dark'], padx=15, pady=15)
    otp_frame.pack(fill=tk.X, pady=(0, 20))
    
    otp_row = tk.Frame(otp_frame, bg="white")
    otp_row.pack(fill=tk.X)
    
    tk.Label(otp_row, text="Enter OTP:", font=("Montserrat", 11), bg="white", fg=COLORS['dark']).pack(side=tk.LEFT)
    
    otp_entry = tk.Entry(otp_row, font=("Montserrat", 12), width=12, relief=tk.SOLID, bd=1)
    otp_entry.pack(side=tk.LEFT, padx=10)
    
    def verify_otp():
        if otp_entry.get() == "123456":
            messagebox.showinfo("Success", "OTP Verified!")
        else:
            messagebox.showerror("Error", "Invalid OTP. Demo OTP: 123456")
    
    tk.Button(otp_row, text="Verify", bg=COLORS['success'], fg="white",
             font=("Montserrat", 10, "bold"), bd=0, padx=15, pady=5,
             cursor="hand2", command=verify_otp).pack(side=tk.LEFT)
    
    # Load Reagent Section
    load_frame = tk.LabelFrame(control_content, text=" Load Reagent ", 
                               font=("Montserrat", 11, "bold"), bg="white",
                               fg=COLORS['dark'], padx=15, pady=15)
    load_frame.pack(fill=tk.X, pady=(0, 20))
    
    box_row = tk.Frame(load_frame, bg="white")
    box_row.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(box_row, text="No. of Boxes:", font=("Montserrat", 11), bg="white", fg=COLORS['dark']).pack(side=tk.LEFT)
    
    box_var = tk.StringVar(value="1")
    box_combo = ttk.Combobox(box_row, textvariable=box_var, values=["1", "2", "3", "4", "5"],
                            font=("Montserrat", 11), state="readonly", width=8)
    box_combo.pack(side=tk.LEFT, padx=10)
    
    def load_reagent():
        import requests
        batch_num = random.randint(100, 999)
        qr_string = f"D0001-BATCH{batch_num}-PACK{box_var.get()}"
        
        try:
            response = requests.post(
                "http://127.0.0.1:8001/ops/scan-qr",
                params={"qr_string": qr_string},
                timeout=5
            )
            
            if response.ok:
                data = response.json()
                messagebox.showinfo(
                    "Reagent Loaded",
                    f"✅ Added {data.get('added_tests', 50)} tests\n"
                    f"Batch: {data.get('batch', 'N/A')}\n"
                    f"Total remaining: {data.get('total_remaining', 'N/A')}"
                )
            else:
                messagebox.showerror("Error", f"Failed: {response.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Backend not running (port 8001)")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    load_btn = tk.Button(load_frame, text="⚡ Load Reagent",
                        bg=COLORS['danger'], fg="white",
                        font=("Montserrat", 14, "bold"), bd=0,
                        padx=30, pady=15, cursor="hand2",
                        command=load_reagent)
    load_btn.pack(fill=tk.X)
    
    # Right Panel - Info
    right_panel = tk.Frame(columns, bg="white", relief=tk.RAISED, bd=1)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    # Right panel header
    right_header_bar = tk.Frame(right_panel, bg=COLORS['primary'], height=45)
    right_header_bar.pack(fill=tk.X)
    right_header_bar.pack_propagate(False)
    tk.Label(right_header_bar, text="📊 Usage Information", font=("Montserrat", 14, "bold"),
            fg="white", bg=COLORS['primary']).pack(side=tk.LEFT, padx=20, pady=10)
    
    info_content = tk.Frame(right_panel, bg="white", padx=30, pady=25)
    info_content.pack(fill=tk.BOTH, expand=True)
    
    # Info rows
    info_data = [
        ("Daily Average", "~12 tests/day"),
        ("Weekly Estimate", "~84 tests"),
        ("Days Until Empty", f"~{max(1, remaining_tests // 12)} days" if remaining_tests > 0 else "N/A"),
        ("Last Loaded", "Today"),
        ("Batch Expires", "2025-06-30"),
    ]
    
    for label, value in info_data:
        row = tk.Frame(info_content, bg="white")
        row.pack(fill=tk.X, pady=8)
        
        tk.Label(row, text=label + ":", font=("Montserrat", 12, "bold"),
                bg="white", fg=COLORS['dark'], width=15, anchor='w').pack(side=tk.LEFT)
        tk.Label(row, text=value, font=("Montserrat", 12),
                bg="white", fg=COLORS['gray']).pack(side=tk.LEFT)
    
    # Status box
    status_color = "#D5F5E3" if remaining_tests > 10 else "#FADBD8"
    status_text_color = COLORS['success'] if remaining_tests > 10 else COLORS['danger']
    status_msg = "✓ Stock Level: Good" if remaining_tests > 10 else "⚠ Low Stock - Reorder Soon"
    
    status_box = tk.Frame(info_content, bg=status_color, padx=20, pady=15)
    status_box.pack(fill=tk.X, pady=20)
    
    tk.Label(status_box, text=status_msg, font=("Montserrat", 12, "bold"),
            bg=status_color, fg=status_text_color).pack()
    
    # Footer
    footer = tk.Frame(frame, bg=COLORS['dark'], height=35)
    footer.pack(side=tk.BOTTOM, fill=tk.X)
    
    from datetime import datetime
    tk.Label(footer, text=f"System Ready | Last Update: {datetime.now().strftime('%I:%M %p')}", 
            font=("Montserrat", 10), fg=COLORS['gray'], bg=COLORS['dark']).pack(side=tk.RIGHT, padx=20, pady=8)
    
    return frame