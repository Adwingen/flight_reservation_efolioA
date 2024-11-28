# main.py

from controller.app_controller import AppController
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Flight Booking System")
    app = AppController(root)
    root.mainloop()
