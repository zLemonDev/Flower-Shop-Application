
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox, Toplevel
import subprocess
import mysql.connector
from PIL import Image, ImageTk

# เชื่อมต่อกับฐานข้อมูล MySQL
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # ปรับตามผู้ใช้ MySQL ของคุณ
            password="",  # ปรับตามรหัสผ่าน MySQL ของคุณ
            database="user_db"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

# ฟังก์ชันตรวจสอบผู้ใช้
def check_user():
    username = entry_1.get()
    password = entry_2.get()
    
    if not username or not password:
        messagebox.showwarning("Input Error", "Please fill out both fields.")
        return

    connection = connect_to_database()
    if connection is None:
        return
    
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    connection.close()

    if result:
        messagebox.showinfo("Login Success", "Welcome, " + username + "!")
        window.destroy()
        product()

    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\TanadolBook\Desktop\Flower_Shop\assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("1920x1080")
window.configure(bg = "#FFFFFF")


canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 1080,
    width = 1920,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)
background_image_path = r"C:\Users\TanadolBook\Desktop\Flower_Shop\assets\frame0\backround_image.jpg"
print("Background image path:", background_image_path)
canvas.place(x = 0, y = 0)
image_image_1 = ImageTk.PhotoImage(Image.open(background_image_path))
    
image_1 = canvas.create_image(
    960.0,
    540.0,
    image=image_image_1
)


cardimage_path = r"C:\Users\TanadolBook\Desktop\Flower_Shop\assets\frame0\image_2.png"
image_image_2 = ImageTk.PhotoImage(Image.open(cardimage_path))
image_2 = canvas.create_image(
    1436.0,
    525.0,
    image=image_image_2
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=check_user,
    relief="flat"
)
button_1.place(
    x=1378.0,
    y=763.0,
    width=179.60401916503906,
    height=60.0
)

button_image_hover_1 = PhotoImage(
    file=relative_to_assets("button_hover_1.png"))

def button_1_hover(e):
    button_1.config(
        image=button_image_hover_1
    )
def button_1_leave(e):
    button_1.config(
        image=button_image_1
    )

button_1.bind('<Enter>', button_1_hover)
button_1.bind('<Leave>', button_1_leave)

def open_register():
    try:
        subprocess.Popen(["python", "register.py"])  # รัน register.py
        window.destroy()  # ปิดหน้าต่างหลัก
    except FileNotFoundError:
        messagebox.showerror("Error", "register.py not found.")

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=open_register,  # เชื่อมฟังก์ชันนี้กับปุ่ม
    relief="flat"
)
button_2.place(
    x=1614.0,
    y=176.0,
    width=166.0,
    height=60.0
)

button_image_hover_2 = PhotoImage(
    file=relative_to_assets("button_hover_2.png"))

def button_2_hover(e):
    button_2.config(
        image=button_image_hover_2
    )
def button_2_leave(e):
    button_2.config(
        image=button_image_2
    )

button_2.bind('<Enter>', button_2_hover)
button_2.bind('<Leave>', button_2_leave)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    1471.0,
    617.0,
    image=entry_image_1
)
def on_enter(e):
    entry_1.delete(0, 'end')

def on_leave(e):
    if entry_1.get() == "":
        entry_1.insert(0, "Username")
entry_1 = Entry(
    bd=4,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Itim Regular", 20)  # กำหนด font และขนาด (เช่น Arial ขนาด 14)
)
entry_1.insert(0,'Username')
entry_1.bind('<FocusIn>', on_enter)
entry_1.bind('<FocusOut>', on_leave)
entry_1.place(
    x=1212.0,
    y=454.0,
    width=518.0,
    height=54.0
)
entry_2 = Entry(
    bd=4,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Itim Regular", 20),  # กำหนด font และขนาด
    show="*"  # ใช้ "*" เพื่อแสดงรหัสผ่านในรูปแบบสัญลักษณ์
)

# ฟังก์ชัน placeholder สำหรับ Password
def on_enter_password(e):
    if entry_2.get() == "Password":
        entry_2.delete(0, 'end')
        entry_2.config(show="*")  # เปิดการแสดงรหัสผ่านเป็น *

def on_leave_password(e):
    if entry_2.get() == "":
        entry_2.insert(0, "Password")
        entry_2.config(show="")  # ลบการแสดงรหัสผ่านเพื่อให้เห็นคำว่า Password

entry_2.insert(0, 'Password')
entry_2.bind('<FocusIn>', on_enter_password)
entry_2.bind('<FocusOut>', on_leave_password)
entry_2.place(
    x=1212.0,
    y=589.0,
    width=518.0,
    height=54.0
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    1471.0,
    482.0,
    image=entry_image_2
)
image_image_3 = PhotoImage(
    file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    1171.0,
    484.0,
    image=image_image_3
)

image_image_4 = PhotoImage(
    file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    1171.0,
    621.0,
    image=image_image_4
)

# Function to display image in full window
def display_full_window_image():
    # Create a new top-level window (a new window)
    full_window = Toplevel(window)
    full_window.geometry("1920x1080")  # Set the size of the new window (full screen)
    
    # Open the image to be displayed
    image_path = r"C:\Users\TanadolBook\Desktop\Flower_Shop\assets\frame0\author.jpg"  # Update this path to your image
    img = Image.open(image_path)
    
    # Resize the image to fit the full screen using the updated method
    img = img.resize((1920, 1080), Image.Resampling.LANCZOS)  # Updated resampling method
    
    # Convert the image to PhotoImage for Tkinter
    full_window_image = ImageTk.PhotoImage(img)
    
    # Create a canvas to display the image
    canvas_full_window = Canvas(full_window, width=1920, height=1080)
    canvas_full_window.pack()
    
    # Display the image on the canvas
    canvas_full_window.create_image(960, 540, image=full_window_image)
    
    # Keep a reference to the image to prevent it from being garbage collected
    full_window.mainloop()

# Add "Author" text button at the top-left
author_button = Button(
    window,
    text="ผู้จัดทำ",  # Button text
    font=("Arial", 18, "bold"),  # Adjust font style and size
    command=display_full_window_image,  # Function to call when the button is pressed
    relief="flat",  # Flat appearance
    bg="#FFFFFF",  # Green background for the button
    fg="black",  # White text color
)

# Position the "Author" button at the top left
author_button.place(x=20, y=20, width=150, height=50)  # Adjust the size and position as needed

def product():
    try:
        subprocess.Popen(["python", "product.py"])  # รัน register.py
    except FileNotFoundError:
        messagebox.showerror("Error", "product.py not found.")
window.resizable(False, False)
window.mainloop()
