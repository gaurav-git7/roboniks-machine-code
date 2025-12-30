import tkinter as tk
from tkinter import messagebox
# from .installation_form import InstallationForm  <-- Moved to lazy import
from .base_screen import Screen
from utils.activation_manager import ActivationManager

class HomeMenu(Screen):
    def __init__(self, root, setup_complete=False):
        super().__init__(root)
        self.activation_manager = ActivationManager()
        # Store module references to avoid repeated imports
        self.module_classes = {}
        self.build()

    def build(self):
        # Configure main frame
        self.frame.configure(bg="#F7F9FC")
        
        # Header
        header = tk.Frame(self.frame, bg="#1BC6B4", height=80)
        header.pack(fill=tk.X)
        
        # Left side - Title
        left_header = tk.Frame(header, bg="#1BC6B4")
        left_header.pack(side=tk.LEFT, padx=30, fill=tk.Y)
        
        tk.Label(
            left_header, text="I.V.D",
            font=("Montserrat", 36, "bold"),
            fg="white", bg="#1BC6B4"
        ).pack(anchor='w')
        
        tk.Label(
            left_header, text="Clinical Diagnostics System",
            font=("Montserrat", 12),
            fg="#E8F4F8",
            bg="#1BC6B4"
        ).pack(anchor='w', pady=(5, 0))
        
        # Right side - Status
        right_header = tk.Frame(header, bg="#1BC6B4")
        right_header.pack(side=tk.RIGHT, padx=30, fill=tk.Y)
        
        # Check activation status
        is_activated = self.activation_manager.is_activated()
        status_text = "ACTIVATED" if is_activated else "SETUP REQUIRED"
        status_color = "#27AE60" if is_activated else "#E74C3C"
        
        status_label = tk.Label(
            right_header,
            text=f"Status: {status_text}",
            font=("Montserrat", 11, "bold"),
            fg="white",
            bg=status_color,
            padx=15,
            pady=8,
            relief=tk.RAISED,
            bd=2
        )
        status_label.pack(anchor='e')
        
        # Main content container
        container = tk.Frame(self.frame, bg="#F7F9FC")
        container.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
        
        # Dashboard grid
        dashboard_frame = tk.Frame(container, bg="#F7F9FC")
        dashboard_frame.pack(expand=True, fill=tk.BOTH)
        
        # Define modules
        modules = [
            {
                "name": "Installations",
                "icon": "⚙️",
                "description": "System Setup & Activation",
                "color": "#3498DB",
                "state": "disabled" if is_activated else "normal",
                "handler": self.open_installations
            },
            {
                "name": "Reagent",
                "icon": "🧪",
                "description": "Reagent Management",
                "color": "#9B59B6",
                "state": "normal",
                "handler": self.open_reagent
            },
            {
                "name": "Diagnostics",
                "description": "Diagnostic Tools",
                "icon": "🩺",
                "color": "#E74C3C",
                "state": "normal",
                "handler": self.open_diagnostics
            },
            {
                "name": "Utilities",
                "icon": "🛠️",
                "description": "System Utilities",
                "color": "#F39C12",
                "state": "normal",
                "handler": self.open_utilities
            },
            {
                "name": "Stock",
                "icon": "📦",
                "description": "Inventory Management",
                "color": "#2ECC71",
                "state": "normal",
                "handler": self.open_stock
            },
            {
                "name": "History",
                "icon": "📊",
                "description": "Records & History",
                "color": "#16A085",
                "state": "normal",
                "handler": self.open_history
            },
            {
                "name": "Communications",
                "icon": "📡",
                "description": "Network & Communication",
                "color": "#2980B9",
                "state": "normal",
                "handler": self.open_communications
            },
            {
                "name": "Read Sample",
                "icon": "🔬",
                "description": "Sample Analysis",
                "color": "#8E44AD",
                "state": "normal",
                "handler": self.open_read_sample
            }
        ]
        
        # Create module buttons - 4x2 grid
        r, c = 0, 0
        for module in modules:
            # Module container
            module_frame = tk.Frame(
                dashboard_frame,
                bg="white",
                relief=tk.RAISED,
                bd=2
            )
            module_frame.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
            module_frame.grid_propagate(False)
            module_frame.config(width=220, height=160)
            
            # Make grid expand
            dashboard_frame.grid_rowconfigure(r, weight=1)
            dashboard_frame.grid_columnconfigure(c, weight=1)
            
            # Module icon
            icon_label = tk.Label(
                module_frame,
                text=module["icon"],
                font=("Arial", 28),
                bg="white",
                fg=module["color"]
            )
            icon_label.pack(pady=(15, 5))
            
            # Module name
            name_label = tk.Label(
                module_frame,
                text=module["name"],
                font=("Montserrat", 14, "bold"),
                bg="white",
                fg="#2C3E50"
            )
            name_label.pack()
            
            # Module description
            desc_label = tk.Label(
                module_frame,
                text=module["description"],
                font=("Montserrat", 9),
                bg="white",
                fg="#7F8C8D"
            )
            desc_label.pack(pady=(5, 10))
            
            # Module button
            btn = tk.Button(
                module_frame,
                text="Open",
                command=module["handler"],
                bg=module["color"],
                fg="white",
                font=("Montserrat", 10, "bold"),
                padx=25,
                pady=8,
                relief=tk.RAISED,
                bd=2,
                state=module["state"]
            )
            btn.pack(pady=(0, 15))
            
            c += 1
            if c == 4:  # 4 columns per row
                r += 1
                c = 0
        
        # Footer
        footer = tk.Frame(self.frame, bg="#2C3E50", height=40)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(
            footer,
            text="I.V.D System v1.0 | © 2024 Clinical Diagnostics",
            font=("Montserrat", 9),
            fg="#95A5A6",
            bg="#2C3E50"
        ).pack(side=tk.LEFT, padx=30)
        
        # Refresh button
        refresh_btn = tk.Button(
            footer,
            text="🔄 Refresh",
            command=self.refresh_status,
            font=("Montserrat", 9),
            bg="#2C3E50",
            fg="#95A5A6",
            bd=0,
            relief=tk.FLAT,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.RIGHT, padx=30)

    def open_installations(self):
        """Open installations module"""
        is_activated = self.activation_manager.is_activated()
        if is_activated:
            messagebox.showinfo(
                "Already Activated",
                "System is already activated. No setup required."
            )
            return
        
        # Clear the entire window first
        for widget in self.root.winfo_children():
            widget.destroy()
        from .installation_form import InstallationForm
        InstallationForm(self.root)

    def open_history(self):
        """Open history module"""
        try:
            from ui.History import HistoryScreen
            # Clear the entire window first
            for widget in self.root.winfo_children():
                widget.destroy()
            HistoryScreen(self.root, go_back_callback=self.go_back_home)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Could not load History module: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening History: {e}")

    def open_stock(self):
        """Open stock module"""
        try:
            from ui.Stock import IVDStockPage
            # Clear the entire window first
            for widget in self.root.winfo_children():
                widget.destroy()
            IVDStockPage(self.root, go_back_callback=self.go_back_home)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Could not load Stock module: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening Stock: {e}")

    def open_read_sample(self):
        """Open read sample module"""
        try:
            from ui.ReadSample import ReadSamplePage
            # Clear the entire window first
            for widget in self.root.winfo_children():
                widget.destroy()
            ReadSamplePage(self.root, go_back_callback=self.go_back_home)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Could not load Read Sample module: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening Read Sample: {e}")

    def open_communications(self):
        """Open communications module"""
        try:
            from ui.CommunicationPage import create_communication_page  # Fixed: Assuming class name
            # Clear the entire window first
            for widget in self.root.winfo_children():
                widget.destroy()
            comm_page = create_communication_page(self.root, go_back_callback=self.go_back_home)
            comm_page.pack(fill="both",expand=True)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Could not load Communications module: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening Communications: {e}")
    
        
    def open_reagent(self):
        """Open reagent module - to be implemented"""
        try:
            from ui.ReagentSale import create_reagent_page
            
            for widget in self.root.winfo_children():
                widget.destroy()
            reagent_page= create_reagent_page(
                self.root,
                go_back_callback=self.go_back_home
            )
            reagent_page.pack(fill="both",expand=True)
        except ImportError as e:
            messagebox.showerror("Module Error",f"Could not load Reagent module:{e}")
        except Exception as e:
            messagebox.showerror("Error",f"Error opening Reagent: {e}")

    def open_diagnostics(self):
        """Open diagnostics module"""
        try:
            from ui.DiagnosticsPage import create_diagnostics_page
            # Clear the entire window first
            for widget in self.root.winfo_children():
                widget.destroy()
            diag_page = create_diagnostics_page(self.root, go_back_callback=self.go_back_home)
            diag_page.pack(fill="both", expand=True)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Could not load Diagnostics module: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening Diagnostics: {e}")

    def open_utilities(self):
        """Open utilities module"""
        try:
            from ui.Utilities import UtilitiesPage
            # Clear the entire window first
            for widget in self.root.winfo_children():
                widget.destroy()
            UtilitiesPage(self.root, go_back_callback=self.go_back_home)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Could not load Utilities module: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening Utilities: {e}")

    def show_coming_soon(self, module_name):
        """Show coming soon message for unimplemented modules"""
        messagebox.showinfo(
            "Coming Soon",
            f"The '{module_name}' module is under development."
        )

    def go_back_home(self):
        """Callback to go back to home menu"""
        # Clear everything
        for widget in self.root.winfo_children():
            widget.destroy()
        # Create new HomeMenu instance
        HomeMenu(self.root)

    def refresh_status(self):
        """Refresh the activation status"""
        is_activated = self.activation_manager.is_activated()
        
        # Clear and rebuild the UI
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.build()
        
        status = "activated" if is_activated else "not activated"
        messagebox.showinfo(
            "Status Refreshed",
            f"System status: {status}"
        )