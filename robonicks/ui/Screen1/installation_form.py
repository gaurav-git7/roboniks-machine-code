import tkinter as tk
from tkinter import messagebox
# import requests  <-- Lazy loaded in methods

from .base_screen import Screen
from .machine_ready import MachineReady

API_BASE = "http://127.0.0.1:8000"
Local_api="http://127.0.0.1:8001"
class InstallationForm(Screen):
    def __init__(self, root):
        super().__init__(root)
        
        # Check if already activated
        if self.check_activation():
            self.show_activated_page()
            return

        self.dist_name = tk.StringVar()
        self.dist_code = tk.StringVar()
        self.dist_otp = tk.StringVar()

        self.user_name = tk.StringVar()
        self.user_addr1 = tk.StringVar()
        self.user_addr2 = tk.StringVar()
        self.user_addr3 = tk.StringVar()
        self.user_addr4 = tk.StringVar()
        self.user_pin = tk.StringVar()
        self.user_mobile = tk.StringVar()
        self.user_email = tk.StringVar()
        self.machine_id = None
        self.lab_id_from_server = None

        self.build()
    
    def check_activation(self):
        """Check if machine is already activated"""
        try:
            import requests
            response = requests.get(f"{Local_api}/activation/check", timeout=2)
            if response.ok:
                return response.json().get("activated", False)
        except:
            pass
        return False
    
    def show_activated_page(self):
        """Show activated status page with back button"""
        # Clear frame
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.frame, bg="#1BC6B4", height=80)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="I.V.D",
            font=("Montserrat", 36, "bold"),
            fg="white", bg="#1BC6B4"
        ).pack(side=tk.LEFT, padx=30)
        
        # Main content
        content = tk.Frame(self.frame, bg="white")
        content.pack(fill=tk.BOTH, expand=True)
        
        # Centered container
        center_frame = tk.Frame(content, bg="white")
        center_frame.place(relx=0.5, rely=0.4, anchor="center")
        
        # Success icon
        tk.Label(
            center_frame, text="✅",
            font=("Arial", 72),
            bg="white"
        ).pack(pady=(0, 20))
        
        # Activated message
        tk.Label(
            center_frame, text="Machine Activated",
            font=("Montserrat", 28, "bold"),
            bg="white", fg="#27AE60"
        ).pack(pady=(0, 10))
        
        tk.Label(
            center_frame, text="This machine is already activated and ready to use.",
            font=("Montserrat", 14),
            bg="white", fg="#7F8C8D"
        ).pack(pady=(0, 30))
        
        # Back to Dashboard button
        def go_to_dashboard():
            from .home_screen import HomeMenu
            for widget in self.root.winfo_children():
                widget.destroy()
            HomeMenu(self.root, setup_complete=True)
        
        back_btn = tk.Button(
            center_frame, text="← Back to Dashboard",
            font=("Montserrat", 14, "bold"),
            bg="#1BC6B4", fg="white",
            activebackground="#17A99A",
            bd=0, padx=40, pady=15,
            cursor="hand2",
            command=go_to_dashboard
        )
        back_btn.pack()

    def field(self, parent, label, var, required=True, state="normal"):
        txt = label + (" *" if required else "")
        tk.Label(
            parent, text=txt,
            font=("Montserrat", 12), bg="white",
            anchor="w"
        ).pack(fill=tk.X, pady=(10, 2))

        entry = tk.Entry(
            parent, font=("Montserrat", 12),
            textvariable=var,
            state=state,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground="#B9C4D0"
        )
        entry.pack(fill=tk.X, ipady=6, padx=2, pady=(0, 10))
        return entry

    def build(self):

        header = tk.Frame(self.frame, bg="#1BC6B4", height=80)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="I.V.D",
            font=("Montserrat", 36, "bold"),
            fg="white", bg="#1BC6B4"
        ).pack(side=tk.LEFT, padx=30)

        container = tk.Frame(self.frame, bg="#F7F9FC")
        container.pack(expand=True, fill=tk.BOTH, padx=30, pady=20)

        left_card = tk.Frame(container, bg="white", bd=0, relief=tk.FLAT)
        left_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=20)

        tk.Label(
            left_card, text="Distributor Details",
            bg="#D2FBF5", fg="#222",
            font=("Montserrat", 16, "bold")
        ).pack(fill=tk.X, pady=(0, 20))

        self.field(left_card, "Distributor Name", self.dist_name)
        self.field(left_card, "Distributor Code", self.dist_code)

        tk.Button(
            left_card, text="Get OTP",
            bg="#3AC7F1", fg="white",
            font=("Montserrat", 12, "bold"),
            command=self.get_otp,
            bd=0, relief=tk.FLAT,
            height=2
        ).pack(fill=tk.X, pady=10)

        self.field(left_card, "Enter OTP", self.dist_otp)

        tk.Button(
            left_card, text="Verify OTP",
            bg="#3AC7F1", fg="white",
            font=("Montserrat", 12, "bold"),
            command=self.verify_otp,
            bd=0, relief=tk.FLAT,
            height=2
        ).pack(fill=tk.X)

        tk.Button(
            left_card, text="Submit Distributor",
            bg="#1BC6B4", fg="white",
            font=("Montserrat", 14, "bold"),
            command=self.submit_distributor,
            bd=0, relief=tk.FLAT,
            height=2
        ).pack(fill=tk.X, pady=20)

        self.user_frame = tk.Frame(container, bg="white", bd=0, relief=tk.FLAT)
        self.user_frame.pack_forget()

        tk.Label(
            self.user_frame, text="User Details",
            bg="#D2FBF5", fg="#222",
            font=("Montserrat", 16, "bold")
        ).pack(fill=tk.X, pady=(0, 20))

        self.user_entries = [
            self.field(self.user_frame, "Username", self.user_name, state="disabled"),
            self.field(self.user_frame, "Address Line 1", self.user_addr1, state="disabled"),
            self.field(self.user_frame, "Address Line 2", self.user_addr2, required=False, state="disabled"),
            self.field(self.user_frame, "Address Line 3", self.user_addr3, required=False, state="disabled"),
            self.field(self.user_frame, "Pincode (6 digits)", self.user_pin, state="disabled"),
            self.field(self.user_frame, "Mobile (10 digits)", self.user_mobile, state="disabled"),
            self.field(self.user_frame, "Email", self.user_email, state="disabled")
        ]

        self.user_submit_btn = tk.Button(
            self.user_frame, text="Submit User",
            bg="#1BC6B4", fg="white",
            font=("Montserrat", 14, "bold"),
            bd=0, relief=tk.FLAT, state="disabled",
            command=self.submit_user
        )
        self.user_submit_btn.pack(fill=tk.X, pady=20)

    def get_otp(self):
        name = self.dist_name.get().strip()
        code = self.dist_code.get().strip()

        if not name or not code:
            messagebox.showwarning("Missing", "Enter Name & Code.")
            return

        try:
            import requests
            r = requests.post(
                f"{API_BASE}/otp/generate-otp",
                json={"name": name, "code": code}
            )
            if r.status_code == 200:
                messagebox.showinfo("OTP Sent", "OTP sent to distributor email.")
            else:
                messagebox.showerror("Error", r.json().get("detail"))
        except Exception as e:
            messagebox.showerror("Network Error", str(e))

    def verify_otp(self):
        code = self.dist_code.get().strip()
        otp = self.dist_otp.get().strip()

        if len(otp) != 6:
            messagebox.showwarning("Invalid", "OTP must be 6 digits.")
            return

        try:
            import requests
            r = requests.post(
                f"{API_BASE}/otp/verify-post",
                json={"code": code, "otp": otp}
            )
            if r.status_code == 200:
                messagebox.showinfo("Verified", "OTP Verified Successfully!")
                self.show_user_form()
            else:
                messagebox.showerror("Error", r.json().get("detail"))

        except Exception as e:
            messagebox.showerror("Network Error", str(e))

    def show_user_form(self):
        self.user_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=20)
        for entry in self.user_entries:
            entry.config(state="normal")
        self.user_submit_btn.config(state="normal")

    def submit_distributor(self):
        if not self.dist_name.get() or not self.dist_code.get() or not self.dist_otp.get():
            messagebox.showwarning("Missing", "Complete Distributor section first.")
            return
        messagebox.showinfo("Saved", "Distributor Details Accepted.")
    def submit_user(self):
        # Validate
        if not self.user_name.get() or not self.user_mobile.get():
           messagebox.showwarning("Missing", "Please fill user details.")
           return

        # ==============================
        # 1. API CALL TO SAVE USER DATA
        # ==============================
        try:
            import requests
            payload = {
                "name": self.user_name.get(),
                "address1": self.user_addr1.get(),
                "address2": self.user_addr2.get(),
                "address3": self.user_addr3.get(),
                "address4":"",
                "pin": self.user_pin.get(),
                "mobile": self.user_mobile.get(),
                "email": self.user_email.get(),
                "code": self.dist_code.get(),
                "machine_id":self.machine_id
            }

            r = requests.post(f"{API_BASE}/labs/crt", json=payload)

            if r.status_code != 200:
               messagebox.showerror("Error", r.json().get("detail", "Server error"))
               return
            
            # ✅ Capture machine_id from Cloud
            cloud_data = r.json()
            if "machine_id" in cloud_data:
                self.machine_id = cloud_data["machine_id"]
            else:
                self.machine_id = "UNKNOWN" # Fallback

        except Exception as e:
            messagebox.showerror("Network Error", str(e))
            return

        # ==============================
        # 2. SAVE LOCAL ACTIVATION
        # ==============================
        try:
            # requests is already imported in this scope if we reached here from above, 
            # but for safety/clarity in separate blocks:
            import requests
            activation_payload={
                "machine_id": self.machine_id,
                "dist_code":self.dist_code.get(),
                "dist_name": self.dist_name.get()
            }
            r=requests.post(
                f"{Local_api}/activation/activate",
                json=activation_payload
            )
            if r.status_code!=200:
                messagebox.showerror("Activation Error",r.json().get("detail","Local activation failed"))
                return
            
            # ✅ Do not expect machine_id back from Local API (it just returns success)
            # self.machine_id = r.json()["machine_id"] <--- REMOVED

        except Exception as e:
            messagebox.showerror("Local Server Error",str(e))

        messagebox.showinfo("Success", "User Details Saved!")

        self.destroy()
        MachineReady(self.root)

    