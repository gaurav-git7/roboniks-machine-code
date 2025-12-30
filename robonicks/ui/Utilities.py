import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class UtilitiesPage(tk.Frame):
    def __init__(self, root, go_back_callback=None):
        super().__init__(root)
        self.root = root
        self.go_back_callback = go_back_callback
        self.configure(bg='#F7F9FC')  # Light background
        
        # Color scheme that matches your app
        self.COLORS = {
            'primary': '#1BC6B4',      # Teal/Cyan
            'secondary': '#3AC7F1',    # Light Blue
            'accent': '#2E8B57',       # Sea Green
            'danger': '#E74C3C',       # Soft Red
            'warning': '#F39C12',      # Orange
            'success': '#27AE60',      # Green
            'light': '#F7F9FC',        # Light Gray
            'white': '#FFFFFF',
            'dark': '#2C3E50',         # Dark Gray
            'gray': '#95A5A6',         # Medium Gray
            'dropdown_bg': '#F0F0F0'   # Dropdown background
        }
        
        # Configuration storage
        self.config = self.load_config()
        
        self.build_ui()
        self.pack(fill='both', expand=True)
    
    def load_config(self):
        """Load utilities configuration from file"""
        config_path = os.path.join('config', 'utilities_config.json')
        default_config = {
            'interface': 'USB',
            'protocol': 'HL7',
            'communication': 'Internal',
            'id': 'Auto Seq'
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save utilities configuration to file"""
        config_path = os.path.join('config', 'utilities_config.json')
        
        try:
            os.makedirs('config', exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def build_ui(self):
        # Main container
        main_container = tk.Frame(self, bg=self.COLORS['light'])
        main_container.pack(fill='both', expand=True)
        
        # Header Section
        header = tk.Frame(main_container, bg=self.COLORS['primary'], height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        
        # Title with icon
        title_frame = tk.Frame(header, bg=self.COLORS['primary'])
        title_frame.pack(side='left', padx=30, fill='y')
        
        tk.Label(
            title_frame,
            text="🛠️ I.V.D",
            font=("Montserrat", 28, "bold"),
            fg="white",
            bg=self.COLORS['primary']
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="System Utilities Configuration",
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
                activeforeground="white",
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
        
        # Configuration card
        config_card = tk.Frame(content, bg='white', relief=tk.RAISED, bd=2)
        config_card.pack(fill='both', expand=True)
        
        # Card header
        card_header = tk.Frame(config_card, bg=self.COLORS['primary'], height=40)
        card_header.pack(fill='x')
        
        tk.Label(
            card_header,
            text="Configuration Settings",
            font=("Montserrat", 14, "bold"),
            fg="white",
            bg=self.COLORS['primary']
        ).pack(side='left', padx=15)
        
        # Dropdowns container
        dropdowns_frame = tk.Frame(config_card, bg='white', padx=40, pady=30)
        dropdowns_frame.pack(fill='both', expand=True)
        
        # Configure grid for 2x2 layout
        for i in range(2):
            dropdowns_frame.grid_rowconfigure(i, weight=1)
            dropdowns_frame.grid_columnconfigure(i, weight=1)
        
        # Create dropdown sections
        self.create_dropdown_section(
            dropdowns_frame, 
            "Interface", 
            ['USB', 'LAN', 'Serial'],
            self.config['interface'],
            0, 0,
            'interface'
        )
        
        self.create_dropdown_section(
            dropdowns_frame, 
            "Protocol", 
            ['HL7', 'ASTM'],
            self.config['protocol'],
            0, 1,
            'protocol'
        )
        
        self.create_dropdown_section(
            dropdowns_frame, 
            "Communication", 
            ['Internal', 'External'],
            self.config['communication'],
            1, 0,
            'communication'
        )
        
        self.create_dropdown_section(
            dropdowns_frame, 
            "ID", 
            ['Auto Seq', 'Barcode'],
            self.config['id'],
            1, 1,
            'id'
        )
        
        # Bottom buttons container
        bottom_frame = tk.Frame(config_card, bg='white', pady=20)
        bottom_frame.pack(fill='x', padx=40)
        
        # Save button
        save_btn = tk.Button(
            bottom_frame,
            text="💾 Save Configuration",
            font=("Montserrat", 12, "bold"),
            bg=self.COLORS['success'],
            fg="white",
            activebackground=self.COLORS['accent'],
            activeforeground="white",
            bd=0,
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2',
            command=self.save_config
        )
        save_btn.pack(side='left', padx=(0, 10))
        
        # Reset button
        reset_btn = tk.Button(
            bottom_frame,
            text="🔄 Reset to Default",
            font=("Montserrat", 12, "bold"),
            bg=self.COLORS['warning'],
            fg="white",
            activebackground="#E67E22",
            activeforeground="white",
            bd=0,
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2',
            command=self.reset_config
        )
        reset_btn.pack(side='left')
    
    def create_dropdown_section(self, parent, label, options, default_value, row, col, config_key):
        """Create a styled dropdown section"""
        section_frame = tk.Frame(parent, bg='white')
        section_frame.grid(row=row, column=col, padx=20, pady=20, sticky='nsew')
        
        # Label
        label_widget = tk.Label(
            section_frame,
            text=label,
            font=("Montserrat", 13, "bold"),
            bg='white',
            fg=self.COLORS['dark']
        )
        label_widget.pack(anchor='w', pady=(0, 10))
        
        # Dropdown container with border - fixed height
        dropdown_container = tk.Frame(
            section_frame,
            bg=self.COLORS['secondary'],
            relief=tk.SOLID,
            bd=2,
            height=50
        )
        dropdown_container.pack(fill='x')
        dropdown_container.pack_propagate(False)  # Maintain fixed height
        
        # Inner frame
        dropdown_frame = tk.Frame(dropdown_container, bg='white')
        dropdown_frame.place(relx=0, rely=0, relwidth=1, relheight=1, x=2, y=2, width=-4, height=-4)
        
        # Current selection display
        selection_frame = tk.Frame(dropdown_frame, bg='white', cursor='hand2')
        selection_frame.pack(fill='both', expand=True, padx=15)
        
        selection_label = tk.Label(
            selection_frame,
            text=default_value,
            font=("Montserrat", 12),
            bg='white',
            fg=self.COLORS['dark'],
            anchor='w'
        )
        selection_label.pack(side='left', fill='both', expand=True)
        
        arrow_label = tk.Label(
            selection_frame,
            text="▼",
            font=("Arial", 10),
            bg='white',
            fg=self.COLORS['secondary']
        )
        arrow_label.pack(side='right')
        
        # Create overlay menu frame (Using Toplevel to float above everything)
        menu_frame = None
        menu_visible = [False]
        
        def toggle_menu(event=None):
            nonlocal menu_frame
            
            if menu_visible[0]:
                # Hide menu
                if menu_frame:
                    menu_frame.destroy()
                    menu_frame = None
                arrow_label.config(text="▼")
                menu_visible[0] = False
                
                # Unbind global click
                self.unbind_all('<Button-1>')
            else:
                # Show menu - create as Toplevel to ensure it's on top of everything
                menu_frame = tk.Toplevel(self)
                menu_frame.overrideredirect(True) # Remove window decorations
                
                # Calculate absolute position
                # Get the absolute coordinates of the dropdown container on the screen
                x = dropdown_container.winfo_rootx()
                y = dropdown_container.winfo_rooty() + dropdown_container.winfo_height()
                width = dropdown_container.winfo_width()
                
                menu_frame.geometry(f"{width}x{len(options)*45}+{x}+{y}")
                menu_frame.configure(bg='white', relief=tk.SOLID, bd=1)
                
                # Create option buttons
                for option in options:
                    option_btn = tk.Button(
                        menu_frame,
                        text=option,
                        font=("Montserrat", 11),
                        bg=self.COLORS['light'],
                        fg=self.COLORS['dark'],
                        activebackground=self.COLORS['secondary'],
                        activeforeground='white',
                        bd=0,
                        relief=tk.FLAT,
                        anchor='w',
                        padx=15,
                        pady=8,
                        cursor='hand2',
                        command=lambda opt=option: select_option(opt)
                    )
                    option_btn.pack(fill='x', pady=0)
                    
                    # Hover effect
                    option_btn.bind('<Enter>', lambda e, btn=option_btn: btn.config(bg=self.COLORS['secondary'], fg='white'))
                    option_btn.bind('<Leave>', lambda e, btn=option_btn: btn.config(bg=self.COLORS['light'], fg=self.COLORS['dark']))
                
                arrow_label.config(text="▲")
                menu_visible[0] = True
                
                # Bind clicking outside to close
                # Since it's a Toplevel, we can bind FocusOut or just click on root
                def close_on_click(e):
                    # Check if click is inside the menu window
                    try:
                        if menu_frame and e.widget.winfo_toplevel() != menu_frame:
                             # Also allow clicking on the dropdown button itself without double-toggling
                             # (The toggle logic handles the button click, this handles specific outside clicks)
                             
                             # Simple check: if widget is not part of our dropdown components
                             if e.widget not in [selection_frame, selection_label, arrow_label]:
                                toggle_menu()
                    except Exception:
                        pass # Widget might be destroyed
                
                # Use 'after' to avoid immediate triggering from the current click
                self.after(100, lambda: self.bind_all('<Button-1>', close_on_click))

        
        def select_option(option):
            selection_label.config(text=option)
            self.config[config_key] = option
            toggle_menu()
        
        # Bind click events
        selection_frame.bind('<Button-1>', toggle_menu)
        selection_label.bind('<Button-1>', toggle_menu)
        arrow_label.bind('<Button-1>', toggle_menu)
    
    def reset_config(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Reset Configuration", "Are you sure you want to reset all settings to default values?"):
            self.config = {
                'interface': 'USB',
                'protocol': 'HL7',
                'communication': 'Internal',
                'id': 'Auto Seq'
            }
            # Rebuild UI to reflect changes
            for widget in self.winfo_children():
                widget.destroy()
            self.build_ui()
            messagebox.showinfo("Success", "Configuration reset to default values!")
    
    def go_back(self):
        """Handle back button click"""
        if self.go_back_callback:
            self.go_back_callback()


# Test the page standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Utilities")
    root.geometry("1024x768")
    
    def go_back():
        print("Going back...")
        root.quit()
    
    page = UtilitiesPage(root, go_back_callback=go_back)
    root.mainloop()
