from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox
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
            database="user_db"  # ชื่อฐานข้อมูล
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

# ฟังก์ชันลงทะเบียนผู้ใช้
def register_user():
    username = entry_3.get()
    password = entry_1.get()
    password_again = entry_2.get()  # เพิ่มตัวแปรสำหรับ Confirm Password
    email = entry_4.get()

    # ตรวจสอบว่ามีช่องไหนว่างหรือไม่
    if not username or not email or not password or not password_again:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return

    # ตรวจสอบว่า Password กับ Confirm Password ตรงกันหรือไม่
    if password != password_again:
        messagebox.showwarning("Password Error", "Passwords do not match.")
        return
    
    # ตรวจสอบว่าอีเมลเป็น @gmail.com หรือไม่
    if not email.endswith('@gmail.com'):
        messagebox.showwarning("Email Error", "Email must be a valid Gmail address.")
        return

    # เชื่อมต่อกับฐานข้อมูล
    connection = connect_to_database()
    if connection is None:
        return
    
    cursor = connection.cursor()

    # ตรวจสอบว่าอีเมลหรือชื่อผู้ใช้ซ้ำหรือไม่
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    result = cursor.fetchone()

    if result:
        messagebox.showerror("Registration Failed", "Username or Email already exists.")
        connection.close()
        return

    # บันทึกข้อมูลผู้ใช้ใหม่
    query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, password, email))
    connection.commit()
    connection.close()

    messagebox.showinfo("Registration Successful", "You have successfully registered!")
    open_main()  # เปิดหน้าต่างหลักหลังจากสมัครสมาชิก

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\TanadolBook\Desktop\Flower_Shop\assets\frame1\background.jpg")


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

background_image_path = r"C:\Users\TanadolBook\Desktop\Flower_Shop\assets\frame1\background.jpg"
print("Background image path:", background_image_path)
canvas.place(x = 0, y = 0)
image_image_1 = ImageTk.PhotoImage(Image.open(background_image_path))
    
image_1 = canvas.create_image(
    960.0,
    540.0,
    image=image_image_1
)

card_register = r"C:\Users\TanadolBook\Desktop\Flower_Shop\assets\frame1\image_2.png"
print("Background image path:", card_register)
canvas.place(x = 0, y = 0)
image_image_2 = ImageTk.PhotoImage(Image.open(card_register))
image_2 = canvas.create_image(
    1436.0,
    525.0,
    image=image_image_2
)

button_image_1 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=register_user,  # เชื่อมฟังก์ชันการลงทะเบียน
    relief="flat"
)
button_1.place(
    x=1360.0,
    y=803.0,
    width=179.60401916503906,
    height=60.0
)

button_image_hover_1 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\button_hover_1.png"))

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

def open_main():
    try:
        subprocess.Popen(["python", "gui.py"])  # รัน register.py
        window.destroy()  # ปิดหน้าต่างหลัก
    except FileNotFoundError:
        messagebox.showerror("Error", "gui.py not found.")
button_image_2 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=open_main,  # เชื่อมฟังก์ชันนี้กับปุ่ม
    relief="flat"
)
button_2.place(
    x=1614.0,
    y=176.0,
    width=166.0,
    height=60.0
)

button_image_hover_2 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\button_hover_2.png"))

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

def on_enter(e, entry, placeholder_text):
    entry.delete(0, 'end')  # ลบ placeholder เมื่อเริ่มพิมพ์

def on_leave(e, entry, placeholder_text):
    if entry.get() == "":
        entry.insert(0, placeholder_text)  # หากช่องว่าง กลับไปแสดง placeholder
entry_image_1 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\entry_1.png"))
entry_bg_1 = canvas.create_image(
    1471.0,
    627.0,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Itim Regular", 20)
)
entry_1.insert(0, "Password")  # ตั้งค่า placeholder เป็น "Username"
entry_1.bind('<FocusIn>', lambda e: on_enter(e, entry_1, "Password"))
entry_1.bind('<FocusOut>', lambda e: on_leave(e, entry_1, "Password"))
entry_1.place(
    x=1212.0,
    y=599.0,
    width=518.0,
    height=54.0
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\entry_2.png"))
entry_bg_2 = canvas.create_image(
    1473.0,
    730.0,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Itim Regular", 20)
)
entry_2.insert(0, "Confirm Password")  # ตั้งค่า placeholder เป็น "Username"
entry_2.bind('<FocusIn>', lambda e: on_enter(e, entry_2, "Confirm Password"))
entry_2.bind('<FocusOut>', lambda e: on_leave(e, entry_2, "Confirm Password"))
entry_2.place(
    x=1214.0,
    y=702.0,
    width=518.0,
    height=54.0
)

entry_image_3 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\entry_3.png"))
entry_bg_3 = canvas.create_image(
    1471.0,
    522.0,
    image=entry_image_3
)
entry_3 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Itim Regular", 20)  # กำหนด font และขนาด (เช่น Arial ขนาด 14)
)
entry_3.insert(0, "Username")  # ตั้งค่า placeholder เป็น "Username"
entry_3.bind('<FocusIn>', lambda e: on_enter(e, entry_3, "Username"))
entry_3.bind('<FocusOut>', lambda e: on_leave(e, entry_3, "Username"))
entry_3.place(x=1212.0, y=599.0, width=518.0, height=54.0)
entry_3.place(
    x=1212.0,
    y=494.0,
    width=518.0,
    height=54.0
)

entry_image_4 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\entry_4.png"))
entry_bg_4 = canvas.create_image(
    1471.0,
    412.0,
    image=entry_image_4
)
entry_4 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Itim Regular", 20)  # กำหนด font และขนาด (เช่น Arial ขนาด 14)
)
entry_4.insert(0, "Gmail")  # ตั้งค่า placeholder เป็น "Username"
entry_4.bind('<FocusIn>', lambda e: on_enter(e, entry_4, "Gmail"))
entry_4.bind('<FocusOut>', lambda e: on_leave(e, entry_4, "Gmail"))
entry_4.place(
    x=1212.0,
    y=384.0,
    width=518.0,
    height=54.0
)

image_image_3 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\image_3.png"))
image_3 = canvas.create_image(
    1171.0,
    524.0,
    image=image_image_3
)

image_image_4 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\image_4.png"))
image_4 = canvas.create_image(
    1171.0,
    631.0,
    image=image_image_4
)

image_image_5 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\image_5.png"))
image_5 = canvas.create_image(
    1173.0,
    734.0,
    image=image_image_5
)

image_image_6 = PhotoImage(
    file=relative_to_assets("C:\\Users\\TanadolBook\\Desktop\\Flower_Shop\\assets\\frame1\\image_6.png"))
image_6 = canvas.create_image(
    1173.0,
    414.0,
    image=image_image_6
)
window.resizable(False, False)
window.mainloop()
