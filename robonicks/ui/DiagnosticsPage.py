import tkinter as tk
from tkinter import font, messagebox

def create_diagnostics_page(root, go_back_callback=None):
    """
    Create and return a diagnostics page frame with motor controls.
    Styled to match the application's teal/turquoise theme.
    """
    
    # Main frame
    frame = tk.Frame(root, bg="#F7F9FC")
    
    # ==============================
    # Header (Teal Theme - Matching Other Screens)
    # ==============================
    header = tk.Frame(frame, bg="#1BC6B4", height=80)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    # Left side - Logo
    left_header = tk.Frame(header, bg="#1BC6B4")
    left_header.pack(side=tk.LEFT, padx=20, fill=tk.Y)
    
    tk.Label(
        left_header, text="🩺 I.V.D",
        font=("Montserrat", 28, "bold"),
        fg="white", bg="#1BC6B4"
    ).pack(anchor='w', pady=(10, 0))
    
    tk.Label(
        left_header, text="Parasite Diagnostic System",
        font=("Montserrat", 10),
        fg="#E8F4F8", bg="#1BC6B4"
    ).pack(anchor='w')
    
    # Right side - Back button
    right_header = tk.Frame(header, bg="#1BC6B4")
    right_header.pack(side=tk.RIGHT, padx=20, fill=tk.Y)
    
    if go_back_callback:
        back_btn = tk.Button(
            right_header, text="← Back to Home",
            command=go_back_callback,
            bg="white", fg="#1BC6B4",
            font=("Montserrat", 11, "bold"),
            bd=0, padx=15, pady=8,
            cursor="hand2",
            relief=tk.FLAT
        )
        back_btn.pack(pady=20)
    
    # ==============================
    # Main Content Area
    # ==============================
    content = tk.Frame(frame, bg="#F7F9FC")
    content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
    
    # Left Panel - Motor Controls
    left_panel = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=1)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # Left Panel Header
    left_header_bar = tk.Frame(left_panel, bg="#1BC6B4", height=35)
    left_header_bar.pack(fill=tk.X)
    left_header_bar.pack_propagate(False)
    
    tk.Label(
        left_header_bar, text="Motor Controls",
        font=("Montserrat", 12, "bold"),
        fg="white", bg="#1BC6B4"
    ).pack(side=tk.LEFT, padx=15, pady=5)
    
    # Motor Control Buttons
    motor_frame = tk.Frame(left_panel, bg="white", padx=20, pady=20)
    motor_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_motor_button(parent, text, icon, color, row):
        """Create a motor control row with label and button"""
        row_frame = tk.Frame(parent, bg="white")
        row_frame.pack(fill=tk.X, pady=10)
        
        label = tk.Label(
            row_frame, text=f"{icon}  {text}",
            font=("Montserrat", 12),
            bg="white", fg="#2C3E50",
            anchor="w"
        )
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        btn = tk.Button(
            row_frame, text="Execute",
            bg=color, fg="white",
            font=("Montserrat", 10, "bold"),
            bd=0, padx=20, pady=5,
            cursor="hand2",
            command=lambda: on_motor_action(text)
        )
        btn.pack(side=tk.RIGHT)
        
        return btn
    
    def on_motor_action(action_name):
        """Handle motor action"""
        messagebox.showinfo("Motor Action", f"{action_name} command sent!")
        print(f"Diagnostics: {action_name} executed")
    
    create_motor_button(motor_frame, "Motor Home", "🏠", "#3498DB", 0)
    create_motor_button(motor_frame, "Motor Move", "⚙️", "#9B59B6", 1)
    create_motor_button(motor_frame, "Blank Read", "📈", "#2ECC71", 2)
    create_motor_button(motor_frame, "Memory Check", "💾", "#E74C3C", 3)
    
    # Right Panel - System Status
    right_panel = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=1)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    # Right Panel Header
    right_header_bar = tk.Frame(right_panel, bg="#1BC6B4", height=35)
    right_header_bar.pack(fill=tk.X)
    right_header_bar.pack_propagate(False)
    
    tk.Label(
        right_header_bar, text="System Status",
        font=("Montserrat", 12, "bold"),
        fg="white", bg="#1BC6B4"
    ).pack(side=tk.LEFT, padx=15, pady=5)
    
    # Status Table
    status_frame = tk.Frame(right_panel, bg="white", padx=20, pady=20)
    status_frame.pack(fill=tk.BOTH, expand=True)
    
    # Table Header
    table_header = tk.Frame(status_frame, bg="#1BC6B4")
    table_header.pack(fill=tk.X)
    
    headers = ["Component", "Status", "Value"]
    for i, h in enumerate(headers):
        tk.Label(
            table_header, text=h,
            font=("Montserrat", 10, "bold"),
            bg="#1BC6B4", fg="white",
            width=15, pady=5
        ).pack(side=tk.LEFT, expand=True)
    
    # Table Rows
    status_data = [
        ("Motor Position", "Ready", "Home"),
        ("Connection", "Active", "COM3"),
        ("Memory", "OK", "85%"),
        ("Temperature", "Normal", "25°C"),
        ("Last Calibration", "Valid", "2024-01-15")
    ]
    
    for component, status, value in status_data:
        row = tk.Frame(status_frame, bg="white", relief=tk.GROOVE, bd=1)
        row.pack(fill=tk.X)
        
        tk.Label(
            row, text=component,
            font=("Montserrat", 10),
            bg="white", fg="#2C3E50",
            width=15, pady=8
        ).pack(side=tk.LEFT, expand=True)
        
        status_color = "#2ECC71" if status in ["Ready", "Active", "OK", "Normal", "Valid"] else "#E74C3C"
        tk.Label(
            row, text=status,
            font=("Montserrat", 10, "bold"),
            bg="white", fg=status_color,
            width=15, pady=8
        ).pack(side=tk.LEFT, expand=True)
        
        tk.Label(
            row, text=value,
            font=("Montserrat", 10),
            bg="white", fg="#7F8C8D",
            width=15, pady=8
        ).pack(side=tk.LEFT, expand=True)
    
    # ==============================
    # Bottom Action Buttons
    # ==============================
    bottom_frame = tk.Frame(frame, bg="#F7F9FC", height=60)
    bottom_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Button(
        bottom_frame, text="▶ Run Full Diagnostics",
        bg="#1BC6B4", fg="white",
        font=("Montserrat", 12, "bold"),
        bd=0, padx=25, pady=10,
        cursor="hand2",
        command=lambda: messagebox.showinfo("Diagnostics", "Running full system diagnostics...")
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        bottom_frame, text="🗑️  Clear Logs",
        bg="#F39C12", fg="white",
        font=("Montserrat", 12, "bold"),
        bd=0, padx=25, pady=10,
        cursor="hand2",
        command=lambda: messagebox.showinfo("Logs", "Logs cleared!")
    ).pack(side=tk.LEFT, padx=5)
    
    # ==============================
    # Footer
    # ==============================
    footer = tk.Frame(frame, bg="#2C3E50", height=30)
    footer.pack(side=tk.BOTTOM, fill=tk.X)
    
    tk.Label(
        footer, text="System Status: Online",
        font=("Montserrat", 9),
        fg="#2ECC71", bg="#2C3E50"
    ).pack(side=tk.RIGHT, padx=20, pady=5)
    
    return frame

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("IVD Diagnostics")
    root.geometry("1100x700")
    root.configure(bg="#F7F9FC")
    
    def go_back():
        print("Going back...")
        root.quit()
    
    page = create_diagnostics_page(root, go_back_callback=go_back)
    page.pack(fill="both", expand=True)
    
    root.mainloop()
