import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Admin Login")
        self.root.geometry("400x400")
        self.root.configure(bg='#130f10')
        
        # Create the login form UI
        self.create_login_form()
    
    def create_login_form(self):
        # Title label
        title_label = tk.Label(self.root, text="จัดการหลังบ้าน", font=("Inter", 24, "bold"), bg="#130f10", fg="white")
        title_label.pack(pady=(40, 10))
        
        # Username
        tk.Label(self.root, text="Username:", font=("Inter", 12), bg="#130f10", fg="white").pack(pady=5)
        self.username_entry = tk.Entry(self.root, font=("Inter", 12), bg="#FFFFFF", fg="black", bd=0, insertbackground="white")
        self.username_entry.pack(pady=10, ipadx=10, ipady=5)
        
        # Password
        tk.Label(self.root, text="Password:", font=("Inter", 12), bg="#130f10", fg="white").pack(pady=5)
        self.password_entry = tk.Entry(self.root, font=("Inter", 12), bg="#FFFFFF", fg="black", bd=0, show="*", insertbackground="white")
        self.password_entry.pack(pady=10, ipadx=10, ipady=5)
        
        # Login Button
        login_button = tk.Button(
            self.root, text="Login", command=self.login, bg="#848c5b", fg="white", font=("Inter", 12, "bold"), padx=15, pady=5
        )
        login_button.pack(pady=20)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Simulate a simple authentication process
        if username == "admin" and password == "admin123":  # Replace with your own authentication logic
            self.on_login_success()  # Trigger on successful login
            self.root.destroy()
        else:
            messagebox.showerror("Login Error", "Invalid username or password. Please try again.")

def open_admin_order_management():
    """Open the manageorder.py file"""
    try:
        # Launch manageorder.py using subprocess
        subprocess.Popen(["python", "managestore.py"])
    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to open managestore.py: {e}")

def open_login_window():
    """Open the login window first"""
    login_root = tk.Tk()
    login_window = LoginWindow(login_root, on_login_success=open_admin_order_management)
    login_root.mainloop()

if __name__ == "__main__":
    open_login_window()
