import tkinter as tk

class Screen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root, bg="#F7F9FC")
        self.frame.pack(fill="both", expand=True)

    def destroy(self):
        self.frame.destroy()
