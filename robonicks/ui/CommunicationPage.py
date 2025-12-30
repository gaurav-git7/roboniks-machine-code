import tkinter as tk
from tkinter import font, messagebox

def create_communication_page(root, go_back_callback=None):
    """
    Create and return a communication settings page frame.
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
        left_header, text="📡 I.V.D",
        font=("Montserrat", 28, "bold"),
        fg="white", bg="#1BC6B4"
    ).pack(anchor='w', pady=(10, 0))
    
    tk.Label(
        left_header, text="Communication Settings",
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
    
    # Import DB for settings persistence
    from utils.minimal_db import MinimalDB
    db = MinimalDB()
    
    # Left Panel - Timeline Selection
    left_panel = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=1)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # Left Panel Header
    left_header_bar = tk.Frame(left_panel, bg="#1BC6B4", height=35)
    left_header_bar.pack(fill=tk.X)
    left_header_bar.pack_propagate(False)
    
    tk.Label(
        left_header_bar, text="Timeline Selection",
        font=("Montserrat", 12, "bold"),
        fg="white", bg="#1BC6B4"
    ).pack(side=tk.LEFT, padx=15, pady=5)
    
    # Timeline Options
    timeline_frame = tk.Frame(left_panel, bg="white", padx=30, pady=30)
    timeline_frame.pack(fill=tk.BOTH, expand=True)
    
    timeline_var = tk.StringVar(value=db.get_setting("sync_timeline", "morning_to_morning"))
    
    def on_timeline_change():
        db.set_setting("sync_timeline", timeline_var.get())
        messagebox.showinfo("Saved", f"Timeline set to: {timeline_var.get().replace('_', ' ').title()}")
    
    tk.Label(
        timeline_frame, text="Select when to sync data:",
        font=("Montserrat", 11),
        bg="white", fg="#7F8C8D"
    ).pack(anchor="w", pady=(0, 20))
    
    tk.Radiobutton(
        timeline_frame, text="⏱️  Morning to Morning (24 hours)",
        variable=timeline_var, value="morning_to_morning",
        font=("Montserrat", 12), bg="white", fg="#2C3E50",
        activebackground="white", command=on_timeline_change,
        indicatoron=1, selectcolor="#1BC6B4",
        padx=10, pady=10
    ).pack(anchor="w", pady=5)
    
    tk.Radiobutton(
        timeline_frame, text="🌙  Upto 12 Midnight (Same day)",
        variable=timeline_var, value="upto_midnight",
        font=("Montserrat", 12), bg="white", fg="#2C3E50",
        activebackground="white", command=on_timeline_change,
        indicatoron=1, selectcolor="#1BC6B4",
        padx=10, pady=10
    ).pack(anchor="w", pady=5)
    
    # Right Panel - Protocol Selection
    right_panel = tk.Frame(content, bg="white", relief=tk.RIDGE, bd=1)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    # Right Panel Header
    right_header_bar = tk.Frame(right_panel, bg="#1BC6B4", height=35)
    right_header_bar.pack(fill=tk.X)
    right_header_bar.pack_propagate(False)
    
    tk.Label(
        right_header_bar, text="Protocol Selection",
        font=("Montserrat", 12, "bold"),
        fg="white", bg="#1BC6B4"
    ).pack(side=tk.LEFT, padx=15, pady=5)
    
    # Protocol Options
    protocol_frame = tk.Frame(right_panel, bg="white", padx=30, pady=30)
    protocol_frame.pack(fill=tk.BOTH, expand=True)
    
    protocol_var = tk.StringVar(value=db.get_setting("default_protocol", "HL7"))
    
    def on_protocol_change():
        db.set_setting("default_protocol", protocol_var.get())
        messagebox.showinfo("Saved", f"Protocol set to: IVD {protocol_var.get()}")
    
    tk.Label(
        protocol_frame, text="Select message protocol:",
        font=("Montserrat", 11),
        bg="white", fg="#7F8C8D"
    ).pack(anchor="w", pady=(0, 20))
    
    tk.Radiobutton(
        protocol_frame, text="📋  IVD ASTM (ASTM E1394)",
        variable=protocol_var, value="ASTM",
        font=("Montserrat", 12), bg="white", fg="#2C3E50",
        activebackground="white", command=on_protocol_change,
        indicatoron=1, selectcolor="#1BC6B4",
        padx=10, pady=10
    ).pack(anchor="w", pady=5)
    
    tk.Radiobutton(
        protocol_frame, text="📋  IVD HL7 (HL7 v2.5)",
        variable=protocol_var, value="HL7",
        font=("Montserrat", 12), bg="white", fg="#2C3E50",
        activebackground="white", command=on_protocol_change,
        indicatoron=1, selectcolor="#1BC6B4",
        padx=10, pady=10
    ).pack(anchor="w", pady=5)
    
    # ==============================
    # Bottom Action Buttons
    # ==============================
    bottom_frame = tk.Frame(frame, bg="#F7F9FC", height=60)
    bottom_frame.pack(fill=tk.X, padx=20, pady=10)
    
    def on_wait_request():
        messagebox.showinfo("LIS Mode", "Waiting for LIS request...\n\nThis feature will listen for incoming messages from the Laboratory Information System.")
    
    tk.Button(
        bottom_frame, text="▶ Wait For Request",
        bg="#E74C3C", fg="white",
        font=("Montserrat", 12, "bold"),
        bd=0, padx=25, pady=10,
        cursor="hand2",
        command=on_wait_request
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        bottom_frame, text="🔄  Reset to Defaults",
        bg="#F39C12", fg="white",
        font=("Montserrat", 12, "bold"),
        bd=0, padx=25, pady=10,
        cursor="hand2",
        command=lambda: [
            timeline_var.set("morning_to_morning"),
            protocol_var.set("HL7"),
            db.set_setting("sync_timeline", "morning_to_morning"),
            db.set_setting("default_protocol", "HL7"),
            messagebox.showinfo("Reset", "Settings reset to defaults!")
        ]
    ).pack(side=tk.LEFT, padx=5)
    
    # ==============================
    # Footer
    # ==============================
    footer = tk.Frame(frame, bg="#2C3E50", height=30)
    footer.pack(side=tk.BOTTOM, fill=tk.X)
    
    current_protocol = db.get_setting("default_protocol", "HL7")
    current_timeline = db.get_setting("sync_timeline", "morning_to_morning").replace("_", " ").title()
    
    tk.Label(
        footer, text=f"Current: {current_protocol} | Timeline: {current_timeline}",
        font=("Montserrat", 9),
        fg="#95A5A6", bg="#2C3E50"
    ).pack(side=tk.RIGHT, padx=20, pady=5)
    
    return frame

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("IVD Communications")
    root.geometry("1100x700")
    root.configure(bg="#F7F9FC")
    
    def go_back():
        print("Going back...")
        root.quit()
    
    page = create_communication_page(root, go_back_callback=go_back)
    page.pack(fill="both", expand=True)
    
    root.mainloop()