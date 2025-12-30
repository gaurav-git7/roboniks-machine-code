import tkinter as tk
from utils.local_db import LocalDB
from ui.Screen1.home_screen import HomeMenu
from ui.Screen1.installation_form import InstallationForm

class App:
    def __init__(self):
        root = tk.Tk()
        root.title("I.V.D System")
        root.geometry("1100x730")
        root.configure(bg="#F7F9FC")

        db = LocalDB()

        if db.is_activated():
            # This works now
            HomeMenu(root, setup_complete=True)
            
        else:
            InstallationForm(root)
             
        root.mainloop()

if __name__ == "__main__":
    App()