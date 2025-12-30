import tkinter as tk

from .base_screen import Screen

class MachineReady(Screen):
    def __init__(self, root):
        super().__init__(root)
        self.build()

    def build(self):

        tk.Label(
            self.frame, text="Machine Ready!",
            font=("Montserrat", 32, "bold"),
            fg="#1BC6B4", bg="#F7F9FC"
        ).pack(pady=80)

        tk.Button(
            self.frame, text="Go Home",
            bg="#3AC7F1", fg="white",
            font=("Montserrat", 16, "bold"),
            command=self.go_home,
            bd=0, relief=tk.FLAT, height=2, width=20
        ).pack()

    def go_home(self):
        from .home_screen import HomeMenu 
        self.destroy()
        HomeMenu(self.root, setup_complete=True)
