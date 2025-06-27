from tkinter import (
    Tk,
    Canvas,
    Button,
    messagebox,
    Frame,
    Scrollbar,
    Label,
    Toplevel,
    Entry,
    Text,
    WORD,
    StringVar,  # Import StringVar
    filedialog  # Import filedialog for file selection
)
from PIL import Image, ImageTk
from fpdf import FPDF
import os
import mysql.connector
import uuid
import subprocess
import time
from decimal import Decimal, getcontext
import threading
from datetime import datetime
import hashlib  # เพิ่มบรรทัดนี้
import qrcode  # Assuming you are using the qrcode library to generate QR codes


class ProductCard:
    def __init__(
        self, master, product_info, cart, cart_frame, db_connection, parent_catalog
    ):
        self.master = master
        self.product_info = product_info
        self.cart = cart
        self.cart_frame = cart_frame
        self.db_connection = db_connection
        self.parent_catalog = parent_catalog

        # กำหนดเฟรมหลักสำหรับการ์ดสินค้า
        self.card_frame = Frame(
            self.master,
            bg="#FFFFFF",
            relief="ridge",
            borderwidth=2,
            width=1310,
            height=210,
        )
        self.card_frame.grid(sticky="nsew", padx=10, pady=10)
        self.card_frame.grid_propagate(False)  # ป้องกันการย่อขยายเฟรม
        self.card_frame.grid_columnconfigure(1, weight=1)  # ให้ info_frame ขยายได้
        self.card_frame.grid_columnconfigure(2, weight=0)  # action_frame คงที่

        # เฟรมย่อยสำหรับรูปภาพ (ซ้ายสุด)
        image_frame = Frame(self.card_frame, bg="#FFFFFF", width=150)
        image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        # โหลดและแสดงรูปภาพ
        img = Image.open(self.product_info["image_path"])
        img = img.resize((190, 180), Image.Resampling.LANCZOS)
        self.product_image = ImageTk.PhotoImage(img)

        image_label = Label(image_frame, image=self.product_image, bg="#FFFFFF")
        image_label.pack()

        # เฟรมย่อยสำหรับข้อมูลสินค้า (ตรงกลาง)
        info_frame = Frame(self.card_frame, bg="#FFFFFF")
        info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

        # ชื่อสินค้า
        name_label = Label(
            info_frame,
            text=self.product_info["name"],
            font=("Arial", 16, "bold"),
            bg="#FFFFFF",
            anchor="w",
        )
        name_label.pack(anchor="w", pady=2)

        description_label = Label(
            info_frame,
            text=self.product_info["description"],
            font=("Arial", 12),
            fg="#555555",
            bg="#FFFFFF",
            anchor="nw",
            justify="left",
            wraplength=300,  # เพิ่ม justify="left" และ anchor="nw"
        )
        description_label.pack(anchor="w", pady=2)

        # จำนวนสินค้าคงเหลือ
        stock_label = Label(
            info_frame,
            text=f"สินค้าคงเหลือ: {self.product_info['stock']} ชิ้น",
            font=("Arial", 12),
            fg="#B22222",
            bg="#FFFFFF",
            anchor="w",
        )
        stock_label.pack(anchor="w", pady=2)

        # เฟรมย่อยสำหรับ ราคา และ Add to Cart (ด้านขวาสุด)
        action_frame = Frame(self.card_frame, bg="#FFFFFF", width=150)
        action_frame.grid(row=0, column=2, padx=(20, 10), pady=10, sticky="ne")
        action_frame.grid_propagate(False)

        # ราคาสินค้า
        price_label = Label(
            action_frame,
            text=f"{self.product_info['price']:.2f} บาท",
            font=("Arial", 14, "bold"),
            fg="#228B22",
            bg="#FFFFFF",
        )
        price_label.pack(anchor="e", pady=(10, 5))

        # ปุ่ม Add to Cart
        add_to_cart_btn = Button(
            action_frame,
            text="🛒 Add to Cart",
            command=self.add_to_cart,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            padx=10,
            pady=5,
        )
        add_to_cart_btn.pack(anchor="e", pady=(5, 10))

    def setup_fonts(self):
        """Setup fonts for invoice generation"""
        font_files = [
            "THSarabunNew.ttf",
            "THSarabunNew Bold.ttf",
            "THSarabunNew Italic.ttf",
        ]

        # Check if fonts directory exists
        if not os.path.exists("fonts"):
            os.makedirs("fonts")

        # Check if all required fonts exist
        missing_fonts = []
        for font_file in font_files:
            if not os.path.exists(os.path.join("fonts", font_file)):
                missing_fonts.append(font_file)

        if missing_fonts:
            messagebox.showerror(
                "Missing Fonts",
                f"Please download and place the following fonts in the 'fonts' folder:\n"
                + "\n".join(missing_fonts)
                + "\nYou can download them from: https://www.f0nt.com/release/th-sarabun-new/",
            )
            return False
        return True

    def generate_invoice(self, order_details, customer_info, current_datetime):
        """Generate a professional PDF invoice with Thai language support"""

        class THSarabunPDF(FPDF):
            def header(self):
                pass

            def footer(self):
                pass

        # Create PDF with UTF-8 support
        pdf = THSarabunPDF()
        pdf.add_page()

        # Add Thai font
        font_path = os.path.join("fonts", "ANGSA.ttf")
        pdf.add_font("Angsana New", "", font_path, uni=True)
        pdf.add_font(
            "Angsana New", "B", os.path.join("fonts", "ANGSA.ttf"), uni=True
        )
        pdf.add_font(
            "Angsana New", "I", os.path.join("fonts", "ANGSA.ttf"), uni=True
        )

        # Add header
        pdf.set_font("Angsana New", "B", 20)
        pdf.cell(190, 10, "Bansapunk", 0, 1, "C")

        # Add invoice details
        pdf.set_font("Angsana New", "", 12)
        pdf.cell(95, 10, "เลขที่ใบเสร็จ: " + str(order_details["order_number"]), 0, 1)
        pdf.cell(95, 10, "วันที่: " + str(current_datetime), 0, 1)

        # Add separator line
        pdf.line(10, pdf.get_y() + 5, 200, pdf.get_y() + 5)
        pdf.ln(10)

        # Add customer information
        pdf.set_font("Angsana New", "B", 12)
        pdf.cell(190, 10, "ข้อมูลลูกค้า:", 0, 1)
        pdf.set_font("Angsana New", "", 12)

        # Customer name on one line
        name_line = (
            "ชื่อ-นามสกุล: "
            + customer_info["first_name"]
            + " "
            + customer_info["last_name"]
        )
        pdf.cell(190, 10, name_line, 0, 1)

        # Address on one line
        address_line = "Address: " + customer_info["address"]
        pdf.multi_cell(190, 10, address_line, 0, 1)

        # Phone on one line
        phone_line = "เบอร์โทรศัพท์: " + customer_info["telephone"]
        pdf.cell(190, 10, phone_line, 0, 1)

        # Add items table header
        pdf.ln(10)
        pdf.set_font("Angsana New", "B", 12)
        pdf.set_fill_color(200, 220, 255)

        # Table headers
        col_widths = [80, 30, 40, 40]  # Width for each column
        pdf.cell(col_widths[0], 10, "Items", 1, 0, "C", True)
        pdf.cell(col_widths[1], 10, "Amount", 1, 0, "C", True)
        pdf.cell(col_widths[2], 10, "Price", 1, 0, "C", True)
        pdf.cell(col_widths[3], 10, "Total Price", 1, 1, "C", True)

        # Add items
        pdf.set_font("Angsana New", "", 12)
        total = 0
        for item_name, item_data in order_details["items"].items():
            try:
                price = float(item_data["info"]["price"])
                quantity = int(item_data["quantity"])
                item_total = price * quantity
                total += item_total

                # Print item details
                pdf.cell(col_widths[0], 10, str(item_name), 1, 0, "L")
                pdf.cell(col_widths[1], 10, str(quantity), 1, 0, "C")
                pdf.cell(col_widths[2], 10, f"{price:.2f}", 1, 0, "R")
                pdf.cell(col_widths[3], 10, f"{item_total:.2f}", 1, 1, "R")
            except Exception as e:
                print(f"Error processing item {item_name}: {e}")
                continue

        # Add totals
        pdf.ln(5)
        pdf.set_font("Angsana New", "B", 12)

        # Right-aligned totals
        pdf.cell(150, 10, "ราคารวม:", 0, 0, "R")
        pdf.cell(40, 10, f"{total:.2f} บาท", 0, 1, "R")

        # Discount if applicable
        if order_details.get("discount", 0) > 0:
            discount = float(order_details["discount"])
            pdf.cell(150, 10, "ส่วนลด (5%):", 0, 0, "R")
            pdf.cell(40, 10, f"-{discount:.2f} บาท", 0, 1, "R")
            total -= discount

        # Final total
        pdf.set_font("Angsana New", "B", 14)
        pdf.cell(150, 10, "ยอดรวมสุทธิ:", 0, 0, "R")
        pdf.cell(40, 10, f"{total:.2f} บาท", 0, 1, "R")

        # Add footer
        pdf.ln(20)
        pdf.set_font("Angsana New", "I", 10)
        pdf.cell(190, 10, "ขอบคุณที่ใช้บริการ!", 0, 1, "C")
        pdf.cell(190, 10, f"ออกเมื่อ: {current_datetime}", 0, 1, "C")

        # Add notes and contact info
        pdf.set_font("Angsana New", "", 10)
        pdf.cell(190, 5, "หมายเหตุ:", 0, 1, "L")
        pdf.cell(190, 5, "1. กรุณาเก็บใบเสร็จนี้ไว้เป็นหลักฐานการซื้อ", 0, 1, "L")
        pdf.cell(190, 5, "2. สินค้าไม่สามารถคืนหรือเปลี่ยนได้หลังจากได้รับสินค้าแล้ว", 0, 1, "L")
        pdf.cell(190, 5, "3. ใบเสร็จนี้จะสมบูรณ์ต่อเมื่อได้รับการชำระเงินเรียบร้อยแล้ว", 0, 1, "L")

        pdf.ln(5)
        pdf.set_font("Angsana New", "B", 10)
        pdf.cell(190, 5, "ติดต่อเรา:", 0, 1, "L")
        pdf.set_font("Angsana New", "", 10)
        pdf.cell(190, 5, "Bansapunk Shop", 0, 1, "L")
        pdf.cell(190, 5, "โทร: 095-464-5687", 0, 1, "L")
        pdf.cell(190, 5, "Email: bansapunk@gmail.com", 0, 1, "L")

        # Generate filename and save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'invoice_{order_details["order_number"]}_{timestamp}.pdf'

        if not os.path.exists("invoices"):
            os.makedirs("invoices")

        filepath = os.path.join("invoices", filename)

        try:
            pdf.output(filepath, "F")
            os.startfile(filepath)  # เพิ่มบรรทัดนี้เพื่อเปิดไฟล์อัตโนมัติ
            return filepath
        except Exception as e:
            raise Exception(f"Error saving PDF: {str(e)}")

    def show_product_details(self):
        """Show detailed product information"""
        messagebox.showinfo(
            "Product Details",
            f"Name: {self.product_info['name']}\n"
            f"Price: {self.product_info['price']:.2f} บาท\n"
            f"Description: {self.product_info['description']}",
        )

    def add_to_cart(self):
        try:
            self.cart.ensure_connection()  # Ensure connection is active before adding to cart
            # Rest of your existing add_to_cart code...
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item to cart: {e}")

    def add_to_cart(self):
        """Prompt for quantity and add product to cart"""

        def submit_quantity():
            try:
                # Get available stock for the product
                available_stock = self.product_info["stock"]

                # Convert input to integer
                quantity = int(quantity_entry.get())

                # Validate quantity input
                if quantity <= 0:
                    messagebox.showerror(
                        "Invalid Input", "กรุณากรอกจำนวนที่เป็นตัวเลขบวกเท่านั้น."
                    )
                    return

                # Check if requested quantity exceeds available stock
                if quantity > available_stock:
                    messagebox.showerror(
                        "Stock Unavailable",
                        f"ขออภัย มีสินค้า {self.product_info['name']} คงเหลือเพียง {self.product_info['stock']} ชิ้นเท่านั้น",
                    )
                    return

                # Attempt to add item to cart
                if self.cart.add_item(self.product_info, quantity):
                    quantity_window.destroy()
                    self.update_cart_display()
                    messagebox.showinfo(
                        "Cart", f"{self.product_info['name']} ได้ถูกเพิ่มเข้าตะกร้าเรียบร้อยแล้ว"
                    )

            except ValueError:
                # Handle non-numeric input
                messagebox.showerror("Invalid Input", "กรุณากรอกตัวเลขเท่านั้น.")
                quantity_window.focus()

        # Prompt user for quantity
        quantity_window = Toplevel(self.master)
        quantity_window.title("Enter Quantity")
        quantity_window.geometry("400x250")

        # Get available stock
        available_stock = self.cart.get_available_stock(self.product_info["name"])

        # Label with stock information
        label = Label(
            quantity_window,
            text=f"กรอกจำนวนการสั่งซื้อสินค้า\n(มีสินค้าคงเหลือ {self.product_info['stock']} ชิ้น)",
            font=("JasmineUPC", 20, "bold"),
        )
        label.pack(pady=10)

        # Entry for quantity
        quantity_entry = Entry(quantity_window, width=20, font=("Arial", 14))
        quantity_entry.pack(pady=10)

        # Submit button
        submit_btn = Button(
            quantity_window,
            text="ยืนยันจำนวนสินค้า",
            command=submit_quantity,
            bg="green",
            fg="white",
            width=20,
            height=2,
            font=("Arial", 14, "bold"),
        )
        submit_btn.pack(pady=10)

    def update_cart_display(self):
        """Update the cart display frame with quantity edit functionality."""
        # Clear existing cart items
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        # Create a styled cart container
        cart_container = Frame(self.cart_frame, bg="#dd1454", bd=2, relief="ridge")
        cart_container.pack(fill="both", expand=True, padx=1, pady=1)

        cart_label = Label(
            cart_container,
            text="ตะกร้าของคุณ",
            font=("Inter", 20, "bold"),
            bg="#dd1454",
            fg="#FFFFFF",
        )
        cart_label.pack(pady=(20, 10))

        items, total_price, total_quantity, discount = (
            self.cart.get_cart_info()
        )  # Updated this line

        if not items:
            empty_cart_label = Label(
                cart_container,
                text="ตะกร้าสินค้าของคุณว่างเปล่าในตอนนี้",
                font=("Inter", 14),
                bg="#dd1454",
                fg="#FFFFFF",
            )
            empty_cart_label.pack(pady=20)
        else:
            for item_name, data in items.items():
                img = Image.open(data["info"]["image_path"])
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                product_image = ImageTk.PhotoImage(img)
                item_frame = Frame(cart_container, bg="#dd1454", pady=5)
                item_frame.pack(fill="x", pady=5)

                # Product image
                image_label = Label(item_frame, image=product_image, bg="#dd1454")
                image_label.image = product_image
                image_label.pack(side="left", padx=10)

                # Product details label
                details_label = Label(
                    item_frame,
                    text=f"{item_name}\n{data['info']['price']:.2f} บาท",
                    font=("Inter", 12),
                    bg="#dd1454",
                    fg="#FFFFFF",
                    justify="left",
                )
                details_label.pack(side="left", anchor="w", padx=10)

                # Quantity control frame
                quantity_frame = Frame(item_frame, bg="#dd1454")
                quantity_frame.pack(side="left", padx=10)

                # Decrease quantity button
                decrease_button = Button(
                    quantity_frame,
                    text="-",
                    command=lambda i=item_name: self.decrease_cart_item(i),
                    bg="#dd1454",
                    fg="white",
                    font=("Inter", 10),
                    width=2,
                )
                decrease_button.pack(side="left")

                # Quantity Entry
                quantity_entry = Entry(
                    quantity_frame,
                    width=3,
                    font=("Inter", 12),
                    bg="#FFFFFF",
                    fg="#000000",
                    justify="center",
                )
                quantity_entry.insert(0, str(data["quantity"]))
                quantity_entry.pack(side="left", padx=5)

                def update_quantity(event, name=item_name):
                    try:
                        new_quantity = int(quantity_entry.get())
                        if new_quantity <= 0:
                            raise ValueError("Quantity must be greater than zero.")

                        available_stock = self.cart.get_available_stock(name)
                        if new_quantity > available_stock:
                            messagebox.showerror(
                                "Stock Error",
                                f"สินค้ามีอยู่เพียง {available_stock} ชิ้นในสต็อก.",
                            )
                            quantity_entry.delete(0, "end")
                            quantity_entry.insert(0, str(data["quantity"]))
                            return

                        self.cart.items[name]["quantity"] = new_quantity
                        self.update_cart_display()

                    except ValueError:
                        messagebox.showerror("Invalid Input", "กรุณากรอกตัวเลขที่ถูกต้อง.")
                        quantity_entry.delete(0, "end")
                        quantity_entry.insert(0, str(data["quantity"]))

                quantity_entry.bind("<Return>", update_quantity)

                # Increase quantity button
                increase_button = Button(
                    quantity_frame,
                    text="+",
                    command=lambda i=item_name: self.increase_cart_item(i),
                    bg="#4CAF50",
                    fg="white",
                    font=("Inter", 10),
                    width=2,
                )
                increase_button.pack(side="left")

                # Delete button
                delete_button = Button(
                    item_frame,
                    text="Delete",
                    command=lambda i=item_name: self.delete_cart_item(i),
                    bg="#FF6347",
                    fg="white",
                    font=("Inter", 10),
                )
                delete_button.pack(side="right", padx=10)

            # Display discount if applicable
            if discount > 0:
                discount_label = Label(
                    cart_container,
                    text=f"ส่วนลด 5%: {discount:.2f} บาท",
                    font=("Inter", 14, "bold"),
                    bg="#dd1454",
                    fg="#FFFFFF",
                )
                discount_label.pack(pady=5)

            # Show promotion message when close to discount threshold
            if 5 <= total_quantity < 10:
                remaining_items = 10 - total_quantity
                promo_label = Label(
                    cart_container,
                    text=f"ซื้อเพิ่มอีก {remaining_items} ชิ้น รับส่วนลด 5%!",
                    font=("Inter", 12),
                    bg="#dd1454",
                    fg="#FFD700",  # Gold color for promotion
                )
                promo_label.pack(pady=5)

            # Total Price
            total_label = Label(
                cart_container,
                text=f"จำนวนสินค้า: {total_quantity} ชิ้น\nราคาทั้งหมด: {total_price:.2f} บาท",
                font=("Inter", 16, "bold"),
                bg="#dd1454",
                fg="#FFFFFF",
            )
            total_label.pack(pady=10)

            # Confirm button
            confirm_button = Button(
                cart_container,
                text="ยืนยันสินค้า",
                command=self.confirm_order,
                bg="#11d400",
                fg="#FFFFFF",
                font=("Inter", 12),
            )
            confirm_button.pack(pady=20)

    def increase_cart_item(self, item_name):
        """Increase the quantity of a specific item in the cart"""
        if item_name in self.cart.items:
            # Get current cart quantity and available stock
            current_cart_quantity = self.cart.items[item_name]["quantity"]
            available_stock = self.cart.get_available_stock(item_name)

            # Check if we can increase the quantity
            if current_cart_quantity < available_stock and current_cart_quantity < 99:
                self.cart.items[item_name]["quantity"] += 1
                self.update_cart_display()
            else:
                # Show a message if stock limit is reached
                messagebox.showwarning(
                    "Stock Limit",
                    f"Sorry, maximum available stock for {item_name} is {available_stock}.",
                )

    def decrease_cart_item(self, item_name):
        """Decrease the quantity of a specific item in the cart"""
        if item_name in self.cart.items:
            if self.cart.items[item_name]["quantity"] > 1:
                self.cart.items[item_name]["quantity"] -= 1
            else:
                del self.cart.items[item_name]
            self.update_cart_display()

    def delete_cart_item(self, item_name):
        """Delete a specific item from the cart"""
        if item_name in self.cart.items:
            del self.cart.items[item_name]
            self.update_cart_display()
            messagebox.showinfo("Cart", f"{item_name} removed from cart.")

    def save_order_to_database(
        self,
        first_name,
        last_name,
        address,
        telephone,
        total_price,
        total_quantity,
        items,
    ):
        """Save order details to MySQL database"""
        if not self.db_connection:
            messagebox.showerror("Database Error", "No database connection available.")
            return None

        db_cursor = self.db_connection.cursor()

        try:
            # Generate a unique order number
            order_number = str(uuid.uuid4())[:8]  # Use first 8 characters of a UUID

            # Prepare order details string
            order_details = "สินค้า:\n"
            for item, data in items.items():
                order_details += (
                    f"- {item}: {data['quantity']} x {data['info']['price']:.2f} บาท\n"
                )
            order_details += f"\nจำนวนสินค้า: {total_quantity} ชิ้น\n"
            order_details += f"ราคาทั้งหมด: {total_price:.2f} บาท"

            # SQL query to insert order into the product table
            insert_query = """
            INSERT INTO product (
                order_number, 
                first_name, 
                last_name, 
                address, 
                telephone_number, 
                order_details, 
                total_price, 
                total_quantity
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Execute the query
            values = (
                order_number,
                first_name,
                last_name,
                address,
                telephone,
                order_details,
                total_price,
                total_quantity,
            )

            db_cursor.execute(insert_query, values)
            self.db_connection.commit()

            return order_number

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to save order: {err}")
            self.db_connection.rollback()
            return None

        finally:
            db_cursor.close()  # ปิด cursor หลังใช้งานเสร็จ

    def confirm_order(self):
        """Open a window to collect customer information before finalizing the order"""

        def validate_and_submit():
            # Validate first name
            first_name = first_name_entry.get().strip()
            if not first_name:
                messagebox.showerror("Invalid Input", "Please enter your first name.")
                return

            # Validate last name
            last_name = last_name_entry.get().strip()
            if not last_name:
                messagebox.showerror("Invalid Input", "Please enter your last name.")
                return

            # Validate address
            address = address_entry.get("1.0", "end-1c").strip()
            if not address:
                messagebox.showerror("Invalid Input", "Please enter your address.")
                return

            # Validate telephone number (10 digits only)
            telephone = telephone_entry.get().strip()
            if (
                not telephone.isdigit()
                or len(telephone) != 10
                or not telephone.startswith("0")
            ):
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a valid 10-digit phone number starting with '0'.",
                )
                customer_info_window.focus()
                return

            # If all validations pass
            items, total_price, total_quantity, discount = (
                self.cart.get_cart_info()
            )  # Updated this line

            for item, data in items.items():
                if not self.cart.check_stock(item, data["quantity"]):
                    messagebox.showerror(
                        "ไม่มีสินค้าในสต็อก",
                        f"ขออภัย, {item} สินค้าหมดหรือมีปริมาณไม่เพียงพอ",
                    )
                    return

            final_price = total_price

            # Prompt user for confirmation before saving order
            confirmation_message = f"คุณแน่ใจหรือไม่ว่าต้องการส่งคำสั่งซื้อนี้\n\n"
            if discount > 0:
                confirmation_message += f"ราคารวม: {total_price + discount:.2f} บาท\n"
                confirmation_message += f"ส่วนลดสินค้า (5%): -{discount:.2f} บาท\n"
                confirmation_message += f"ยอดรวมสุทธิ: {final_price:.2f} บาท"
            else:
                confirmation_message += f"ยอดที่ต้องจ่าย: {final_price:.2f} บาท"

            # Prompt user for confirmation
            confirm = messagebox.askyesno("ยืนยันการสั่งซื้อสินค้า", confirmation_message)
            if not confirm:
                return

            # Save order to database
            order_number = self.save_order_to_database(
                first_name,
                last_name,
                address,
                telephone,
                total_price,
                total_quantity,
                items,
            )

            if order_number:
                # อัปเดตจำนวนสินค้าในฐานข้อมูล
                self.parent_catalog.update_stock_after_order(items)
                # โหลดสินค้าจากฐานข้อมูลอีกครั้งเพื่อรีเฟรช UI
                self.parent_catalog.load_products()
                self.update_cart_display()

            # Construct order summary
            order_summary = f"Order Details:\n\n"
            order_summary += f"Order Number: {order_number}\n"
            order_summary += f"Customer: {first_name} {last_name}\n"
            order_summary += f"Address: {address}\n"
            order_summary += f"Phone: {telephone}\n\n"
            order_summary += "Items:\n"
            for item, data in items.items():
                order_summary += (
                    f"- {item}: {data['quantity']} x {data['info']['price']:.2f} บาท\n"
                )
            order_summary += f"\nTotal Quantity: {total_quantity}\n"
            order_summary += f"Total Price: {total_price:.2f} บาทห"

            # Close the customer info window
            customer_info_window.destroy()

            # Call show_qr_code_scan and pass total_price
            self.show_qr_code_scan(final_price)

        # Assuming customer_info_window and the input fields are already created
        customer_info_window = Toplevel(self.master)
        customer_info_window.title("Customer Information")
        customer_info_window.geometry("400x600")

        # Add Entry widgets for user inputs with styling
        def create_entry_with_style(parent, label_text):
            # Container frame for better layout control
            entry_frame = Frame(parent, bg="#f4f4f4")
            entry_frame.pack(padx=20, pady=10, fill="x")

            # Label with improved typography
            label = Label(
                entry_frame,
                text=label_text,
                font=("Segoe UI", 12, "bold"),  # Professional font with bold weight
                bg="#f4f4f4",
                fg="#333333",  # Dark gray for readability
                anchor="w",
            )
            label.pack(side="top", fill="x", pady=(0, 5))

            # Entry widget with modern, clean design
            entry = Entry(
                entry_frame,
                font=("Segoe UI", 12),  # Clean, modern font
                relief="flat",  # Flat design for a modern look
                bd=0,  # No border
                highlightthickness=1,  # Thin border when focused
                highlightcolor="#4A90E2",  # Blue highlight color
                highlightbackground="#E0E0E0",  # Light gray border when not focused
                fg="#333333",  # Dark text color
                bg="white",  # Clean white background
                insertbackground="#4A90E2",  # Cursor color
                selectbackground="#4A90E2",  # Selection background color
                selectforeground="white",  # Selection text color
            )
            entry.pack(side="top", fill="x")

            # Subtle bottom border for a refined look
            canvas = Canvas(entry_frame, height=2, bg="#f4f4f4", highlightthickness=0)
            canvas.pack(side="top", fill="x")

            # Animated bottom border
            line = canvas.create_line(0, 1, 0, 1, fill="#4A90E2", width=2)

            def on_focus_in(event):
                """Animate bottom border when entry gets focus"""
                width = entry_frame.winfo_width()
                canvas.coords(line, 0, 1, width, 1)
                entry.configure(highlightthickness=1)

            def on_focus_out(event):
                """Reset bottom border when entry loses focus"""
                canvas.coords(line, 0, 1, 0, 1)
                entry.configure(highlightthickness=0)

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
            return entry

        def create_submit_button(parent, text, command):
            # New, stylish submit button
            button = tk.Button(
                parent,
                text=text,
                font=("Segoe UI", 14, "bold"),
                bg="#11d400",  # Deep blue-gray background
                fg="white",
                activebackground="#34495E",  # Slightly lighter shade for active state
                activeforeground="white",
                relief="flat",  # Smooth, flat appearance
                padx=20,  # Horizontal padding
                pady=10,  # Vertical padding
                command=command,
            )
            button.pack(pady=(20, 10))

            # Add hover effects (simulated with binding)
            def on_enter(e):
                button.config(bg="#34495E")

            def on_leave(e):
                button.config(bg="#2C3E50")

            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

            return button

        title_label = tk.Label(
            customer_info_window,
            text="กรอกข้อมูลลูกค้า",  # ข้อความหัวหน้าต่าง
            font=("Segoe UI", 20, "bold"),  # ขนาดตัวอักษร
            bg="#f4f4f4",  # พื้นหลังให้เหมือนกันกับหน้าต่าง
            fg="#2C3E50",  # สีข้อความเข้มแบบเรียบหรู
            pady=10,  # เว้นระยะห่างด้านบนและล่าง
        )
        title_label.pack(pady=(10, 20))  # จัดวางไว้ด้านบนสุด พร้อม padding
        first_name_entry = create_entry_with_style(customer_info_window, "ชื่อ")
        last_name_entry = create_entry_with_style(customer_info_window, "นามสกุล")
        telephone_entry = create_entry_with_style(customer_info_window, "หมายเลขโทรศัพท์")
        address_frame = Frame(customer_info_window, bg="#f4f4f4")
        address_frame.pack(padx=20, pady=10, fill="x")

        address_label = Label(
            address_frame,
            text="กรอกที่อยู่ในการจัดส่ง",
            font=("Segoe UI", 12, "bold"),
            bg="#f4f4f4",
            fg="#333333",
            anchor="w",
        )
        address_label.pack(side="top", fill="x", pady=(0, 5))

        # Modified address entry with proper configuration
        address_entry = Text(
            address_frame,
            font=("Segoe UI", 12),
            relief="flat",
            bd=0,
            height=4,
            width=30,  # Set a reasonable width
            highlightthickness=1,
            highlightcolor="#4A90E2",
            highlightbackground="#E0E0E0",
            fg="#333333",
            bg="white",
            insertbackground="#4A90E2",
            selectbackground="#4A90E2",
            selectforeground="white",
            wrap=WORD,  # Enable word wrapping
        )
        address_entry.pack(side="top", fill="x")

        # Add character counter
        char_counter_label = Label(
            address_frame,
            text="0/500 ตัวอักษร",
            font=("Segoe UI", 10),
            bg="#f4f4f4",
            fg="#666666",
        )
        char_counter_label.pack(side="top", anchor="e", padx=5)

        def update_char_counter(event=None):
            current_chars = len(address_entry.get("1.0", "end-1c"))
            char_counter_label.config(text=f"{current_chars}/500 ตัวอักษร")

            # Limit text length to 500 characters
            if current_chars > 500:
                address_entry.delete("1.0", "end")
                address_entry.insert("1.0", address_entry.get("1.0", "end-1c")[:500])

        address_entry.bind("<KeyPress>", update_char_counter)
        address_entry.bind("<KeyRelease>", update_char_counter)

        create_submit_button(customer_info_window, "ยืนยัน", validate_and_submit)

    def show_qr_code_scan(self, total_price):
        # Create QR scan window
        qr_window = Toplevel(self.master)
        qr_window.title("QR Code Scan")
        qr_window.geometry("400x800")

        # Load QR code image using PIL (Replace with your QR code image path)
        qr_image = Image.open(
            r"C:\Users\TanachotPC\Desktop\pythonproject\assets\frame2\qr_code.jpg"
        )  # Replace with actual path
        qr_image = qr_image.resize((350, 450))  # Resize image to fit window
        qr_photo = ImageTk.PhotoImage(qr_image)

        # Display QR code image
        qr_label = Label(qr_window, image=qr_photo)
        qr_label.photo = (
            qr_photo  # Keep a reference to the image to prevent garbage collection
        )
        qr_label.pack(pady=(20, 10))  # Padding around the image

        # Display the total price under the QR code
        total_price_label = Label(
            qr_window, text=f"ยอดที่ต้องจ่าย: {total_price:.2f} บาท", font=("Inter", 14)
        )
        total_price_label.pack(pady=(10, 20))  # Padding around the total price label
        # Create frame for slip upload
        upload_frame = Frame(qr_window)
        upload_frame.pack(pady=10)

        # Label to display upload status
        upload_status = StringVar()
        upload_status.set("กรุณาอัปโหลดสลิปการโอนเงิน")

        status_label = Label(upload_frame, textvariable=upload_status, font=("Inter", 12))
        status_label.pack()

        # Function to handle file upload
        def upload_slip():
            file_path = filedialog.askopenfilename(
                title="เลือกไฟล์สลิป",
                filetypes=[("Image Files", "*.jpg *.jpeg *.png"), ("All Files", "*.*")]
            )
            if file_path:
                upload_status.set("อัปโหลดสำเร็จ: " + os.path.basename(file_path))
                upload_slip.file_path = file_path
                confirm_button.config(state="normal")  # Enable the confirm button

                messagebox.showinfo("สำเร็จ", "อัปโหลดสลิปสำเร็จแล้ว!")
                qr_window.deiconify()
            else:
                upload_status.set("ยังไม่ได้อัปโหลดสลิป")
                confirm_button.config(state="disabled")  # Keep the confirm button disabled

        # Upload button
        upload_button = Button(
            upload_frame,
            text="อัปโหลดสลิป",
            command=upload_slip,
            bg="#4CAF50",
            fg="white",
            font=("Inter", 12, "bold")
        )
        upload_button.pack(pady=10)

        # Function for confirming payment
        def confirm_payment():
            qr_window.destroy()  # Close QR code window
            self.show_thank_you_message()  # Display thank you message

        # Button for user to confirm payment
        confirm_button = Button(
            qr_window,
            text="ยืนยันการโอนเงิน",
            command=lambda: (qr_window.destroy(), self.show_thank_you_message()),
            bg="#11d400",
            fg="white",
            font=("Inter", 14, "bold"),
            relief="flat",
            padx=20,
            pady=10,
            state="disabled"
        )
        confirm_button.pack(pady=20)

    def get_order_details_from_db(self, order_number):
        """Fetch order details from the database for the given order number"""
        cursor = self.db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM product WHERE order_number = %s", (order_number,))
        order_data = cursor.fetchone()
        cursor.close()
        return order_data

    def show_thank_you_message(self):
        try:
            # Check if fonts are available
            if not self.setup_fonts():
                return

            billing_window = Toplevel(self.master)
            billing_window.title("Order Billing")
            billing_window.geometry("600x800")
            billing_window.configure(bg="white")

            # Header Section
            header_frame = Frame(billing_window, bg="#f7f7f7", padx=10, pady=10, relief="groove", bd=2)
            header_frame.pack(fill="x", pady=10)

            header_label = Label(
                header_frame,
                text="ใบเสร็จการสั่งซื้อ",
                font=("Arial", 20, "bold"),
                bg="#f7f7f7",
                fg="#333333",
            )
            header_label.pack()

            # Order Information Section
            order_info_frame = Frame(billing_window, bg="white", padx=10, pady=10)
            order_info_frame.pack(fill="x", pady=10)

            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order_number = str(uuid.uuid4())[:8]  # Generate unique order number

            order_info_label = Label(
                order_info_frame,
                text=f"เลขที่คำสั่งซื้อ: {order_number}\nวันที่: {current_datetime}",
                font=("Arial", 12),
                bg="white",
                justify="left",
                anchor="w",
            )
            order_info_label.pack(anchor="w")

            # Item Details Section
            items_frame = Frame(billing_window, bg="white", padx=10, pady=10, relief="groove", bd=2)
            items_frame.pack(fill="both", expand=True, pady=10)

            # Table Header
            header_labels = ["สินค้า", "จำนวน", "ราคา (บาท)"]
            for col, text in enumerate(header_labels):
                label = Label(
                    items_frame,
                    text=text,
                    font=("Arial", 12, "bold"),
                    bg="#e0f7fa",
                    fg="#006064",
                    padx=5,
                    pady=5,
                    relief="ridge",
                )
                label.grid(row=0, column=col, sticky="nsew")

            # Item Details
            items, total_price, total_quantity, discount = self.cart.get_cart_info()
            for row, (item_name, item_data) in enumerate(items.items(), start=1):
                # Column 1: Item Name
                item_label = Label(
                    items_frame,
                    text=item_name,
                    font=("Arial", 12),
                    bg="white",
                    padx=5,
                    pady=5,
                    relief="ridge",
                    anchor="w",
                )
                item_label.grid(row=row, column=0, sticky="nsew")

                # Column 2: Quantity
                quantity_label = Label(
                    items_frame,
                    text=item_data['quantity'],
                    font=("Arial", 12),
                    bg="white",
                    padx=5,
                    pady=5,
                    relief="ridge",
                    anchor="center",
                )
                quantity_label.grid(row=row, column=1, sticky="nsew")

                # Column 3: Price
                price_label = Label(
                    items_frame,
                    text=f"{item_data['info']['price']:.2f}",
                    font=("Arial", 12),
                    bg="white",
                    padx=5,
                    pady=5,
                    relief="ridge",
                    anchor="e",
                )
                price_label.grid(row=row, column=2, sticky="nsew")

            # Adjust column widths
            items_frame.grid_columnconfigure(0, weight=3)
            items_frame.grid_columnconfigure(1, weight=1)
            items_frame.grid_columnconfigure(2, weight=2)

            # Total Section
            totals_frame = Frame(billing_window, bg="white", padx=10, pady=10)
            totals_frame.pack(fill="x", pady=10)

            totals_label = Label(
                totals_frame,
                text=(
                    f"รวมราคา: {total_price + discount:.2f} บาท\n"
                    f"ส่วนลด: -{discount:.2f} บาท\n"
                    f"ราคาสุทธิ: {total_price:.2f} บาท"
                ),
                font=("Arial", 14, "bold"),
                bg="white",
                fg="#333333",
                anchor="e",
                justify="right",
            )
            totals_label.pack(anchor="e")

            # Thank You Section
            thank_you_frame = Frame(billing_window, bg="#e8f5e9", padx=10, pady=10, relief="groove", bd=2)
            thank_you_frame.pack(fill="x", pady=20)

            thank_you_label = Label(
                thank_you_frame,
                text="ขอบคุณที่ใช้บริการของเรา!",
                font=("Arial", 16, "italic"),
                bg="#e8f5e9",
                fg="#2e7d32",
            )
            thank_you_label.pack()

            # Get current cart info
            items, total_price, total_quantity, discount = self.cart.get_cart_info()

            # Get current date and time
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create order details
            order_details = {
                "order_number": str(uuid.uuid4())[:8],
                "items": self.cart.items,
                "total_price": total_price,
                "total_quantity": total_quantity,
                "discount": discount,
            }

            # Get customer info from the database
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT first_name, last_name, address, telephone_number FROM product ORDER BY id DESC LIMIT 1"
            )
            customer_data = cursor.fetchone()
            cursor.close()

            if not customer_data:
                messagebox.showerror("Error", "ไม่พบข้อมูลลูกค้า")
                return

            customer_info = {
                "first_name": customer_data["first_name"],
                "last_name": customer_data["last_name"],
                "address": customer_data["address"],
                "telephone": customer_data["telephone_number"],
            }
            if not items:
                messagebox.showerror("Error", "ตะกร้าสินค้าว่างเปล่า")
                return

            # Generate invoice
            invoice_path = self.generate_invoice(
                order_details, customer_info, current_datetime
            )

            # Show success message
            messagebox.showinfo(
                "บานสะพรั่ง", f"ขอบคุณสำหรับการสั่งซื้อสินค้าของทางร้านโปรดบันทึกใบเสร็จของคุณเพื่อป้องกันการเกิิดปัญหา ขอบคุุณค่ะ"
            )

            # Continue with the rest of your existing show_thank_you_message code...

        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการสร้างใบเสร็จ: {str(e)}")

        finally:
            # Clear the cart after successful order
            self.cart.items.clear()
            self.update_cart_display()


class Cart:
    def __init__(self, db_connection):
        self.items = {}
        self.db_connection = db_connection

    def ensure_connection(self):
        """Ensure database connection is active, reconnect if necessary"""
        try:
            self.db_connection.ping(reconnect=True, attempts=3, delay=1)
        except (mysql.connector.Error, AttributeError):
            self.db_connection = mysql.connector.connect(
                host="localhost", user="root", password="", database="user_db"
            )

    def get_available_stock(self, product_name):
        """Get current available stock for a product"""
        try:
            self.ensure_connection()  # Ensure connection is active
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT stock FROM items WHERE name = %s", (product_name,))
            result = cursor.fetchone()
            cursor.close()
            return result["stock"] if result else 0
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error checking stock: {err}")
            return 0

    def check_stock(self, product_name, requested_quantity):
        """Check if requested quantity is available in stock"""
        try:
            self.ensure_connection()  # Ensure connection is active
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT stock FROM items WHERE name = %s", (product_name,))
            result = cursor.fetchone()
            cursor.close()

            if result is None:
                return False

            return requested_quantity <= result["stock"]
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error checking stock: {err}")
            return False

    def add_item(self, product_info, quantity):
        try:
            self.ensure_connection()  # Ensure connection is active
            # Rest of your existing add_item code...
            if not self.check_stock(product_info["name"], quantity):
                messagebox.showerror(
                    "Stock Unavailable",
                    f"Sorry, only {self.get_available_stock(product_info['name'])} {product_info['name']} are available in stock.",
                )
                return False

            if product_info["name"] in self.items:
                new_quantity = min(
                    self.items[product_info["name"]]["quantity"] + quantity,
                    99,
                    self.get_available_stock(product_info["name"]),
                )
                self.items[product_info["name"]]["quantity"] = new_quantity
            else:
                self.items[product_info["name"]] = {
                    "info": product_info,
                    "quantity": min(quantity, 99),
                }
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding item to cart: {err}")
            return False

    getcontext().prec = 10  # Set precision to 10 decimal places

    def get_cart_info(self):
        """Return cart details: items, total price, total quantity, and discount if applicable"""
        from decimal import Decimal

        total_price = Decimal("0.00")
        total_quantity = 0
        items = self.items

        # Calculate total quantity and initial price
        for item, data in items.items():
            item_price = Decimal(str(data["info"]["price"]))
            item_quantity = Decimal(str(data["quantity"]))
            total_price += item_price * item_quantity
            total_quantity += data["quantity"]

        # Apply 5% discount if total quantity is 10 or more
        discount = Decimal("0.00")
        if total_quantity >= 10:
            discount = (total_price * Decimal("0.05")).quantize(Decimal("0.01"))
            total_price = (total_price - discount).quantize(Decimal("0.01"))

        # Convert back to float for display purposes
        return items, float(total_price), total_quantity, float(discount)


import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
import os
import sys
import uuid


class ProductCatalog:
    def __init__(self, root):
        self.root = root
        self.db_connection = None
        self.db_cursor = None
        self.setup_database_connection()
        self.setup_window()
        self.create_main_layout()

        # Pass self.db_connection when creating Cart
        self.cart = Cart(self.db_connection)  # Updated line

        self.load_products()

    def ensure_connection(self):
        """Ensure database connection is active, reconnect if necessary"""
        try:
            self.db_connection.ping(reconnect=True, attempts=3, delay=1)
        except (mysql.connector.Error, AttributeError):
            self.setup_database_connection()

    def update_stock_after_order(self, items):
        """Update stock in the database after an order is placed."""
        try:
            cursor = self.db_connection.cursor()
            for item_name, data in items.items():
                quantity_to_deduct = data["quantity"]

                cursor.execute(
                    "UPDATE items SET stock = stock - %s WHERE name = %s AND stock >= %s",
                    (quantity_to_deduct, item_name, quantity_to_deduct),
                )
                if cursor.rowcount == 0:
                    messagebox.showerror(
                        "Stock Update Error",
                        f"ไม่สามารถหักจำนวนสินค้า '{item_name}' ออกจากสต็อกได้.",
                    )
                    self.db_connection.rollback()
                    return

            self.db_connection.commit()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"ไม่สามารถอัปเดตสต็อกสินค้าได้: {err}")
            self.db_connection.rollback()

    def setup_database_connection(self):
        """Establish database connection"""
        try:
            if self.db_connection:
                try:
                    self.db_connection.close()
                except:
                    pass

            self.db_connection = mysql.connector.connect(
                host="localhost", user="root", password="", database="user_db"
            )
            self.db_cursor = self.db_connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database Error", f"Failed to connect to database: {err}"
            )

    def setup_window(self):
        """Configure main window settings"""
        self.root.title("Product Catalog")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#FFFFFF")

        # Title label
        title_label = tk.Label(
            self.root,
            text="My Product",
            fg="#dd1454",
            font=("JasmineUPC", 50, "bold"),
            bg=self.root["bg"],  # ตั้งสีพื้นหลังให้เหมือนกับหน้าต่างหลัก
        )
        title_label.place(relx=0.5, rely=0.03, anchor="center")

        subtitle_label = tk.Label(
            self.root,
            text="สินค้าของร้านขายดอกไม้",
            fg="#dd1454",
            font=("JasmineUPC", 30, "bold"),
            bg=self.root["bg"],  # ตั้งสีพื้นหลังให้เหมือนกับหน้าต่างหลัก
            borderwidth=0,
            highlightthickness=0,
        )
        subtitle_label.place(relx=0.5, rely=0.08, anchor="center")

        # Sign Out button
        sign_out_button = tk.Button(
            self.root,
            text="ออกจากระบบ",
            command=self.sign_out,
            font=("Arial", 12, "bold"),
            bg="#FF6347",
            fg="white",
            activebackground="#FF7F7F",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=5,
        )
        sign_out_button.place(relx=0.90, rely=0.03, anchor="ne")

        # Manage Store button
        manage_store_button = tk.Button(
            self.root,
            text="จัดการร้านค้า",
            command=self.open_manage_store,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=5,
        )
        manage_store_button.place(relx=0.99, rely=0.03, anchor="ne")

        refresh_button = tk.Button(
            self.root,
            text="🔄 รีเฟรช",
            command=self.refresh_catalog,
            font=("Arial", 12, "bold"),
            bg="#4169E1",  # Royal Blue
            fg="white",
            activebackground="#1E90FF",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=5,
        )
        refresh_button.place(relx=0.81, rely=0.03, anchor="ne")

        # Hover effects for buttons
        def create_hover_effects(button, enter_bg, leave_bg):
            def on_enter(e):
                button.configure(bg=enter_bg, cursor="hand2")

            def on_leave(e):
                button.configure(bg=leave_bg)

            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        create_hover_effects(sign_out_button, "#FF7F7F", "#FF6347")
        create_hover_effects(manage_store_button, "#45a049", "#4CAF50")
        create_hover_effects(refresh_button, "#1E90FF", "#4CAF50")

    def sign_out(self):
        """Handle sign out and redirect to gui.py"""
        import os
        import sys
        from tkinter import messagebox

        # Confirm sign-out action
        if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
            self.root.destroy()  # Close the current window

            # Redirect to gui.py
            python_executable = sys.executable
            os.execl(python_executable, python_executable, "gui.py")

    def create_main_layout(self):
        """Create main layout with products and cart side by side"""
        # Load background image
        try:
            bg_image_path = r"C:\Users\TanachotPC\Desktop\pythonproject\assets\frame2\product_catalog.jpg"
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize(
                (
                    int(self.root.winfo_screenwidth() * 0.8),
                    int(self.root.winfo_screenheight() * 0.8),
                ),
                Image.Resampling.LANCZOS,
            )
            self.bg_photo = ImageTk.PhotoImage(bg_image)
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.bg_photo = None

        # Main frame for products with background image
        self.products_frame = tk.Frame(self.root, bg="white")
        self.products_frame.place(relx=0, rely=0.1, relwidth=0.7, relheight=0.9)

        # Canvas with background image
        self.canvas = tk.Canvas(self.products_frame, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(
            self.products_frame, orient="vertical", command=self.canvas.yview
        )

        # If background image is loaded, display it
        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.configure(
            bg="#FFFFFF"
        )  # Set a white background with some transparency

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # Create a semi-transparent white frame
        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=int(self.root.winfo_screenwidth() * 0.7) - 20,
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Cart frame
        self.cart_frame = tk.Frame(self.root, bg="#dd1454", width=400)
        self.cart_frame.place(relx=0.7, rely=0.1, relwidth=0.3, relheight=0.9)

    def open_manage_store(self):
        """Open the manageorder.py file"""
        try:
            # เปิดไฟล์ manageorder.py
            subprocess.Popen(["python", "login window.py"])
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to open manageorder.py: {e}")

    def refresh_catalog(self):
        """Refresh the product catalog by reconnecting to database and reloading all products"""
        try:
            # Reconnect to database to ensure fresh connection
            if self.db_connection:
                self.db_connection.close()

            self.setup_database_connection()

            # Clear existing products from display
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Reset cursor and execute fresh query
            self.db_cursor.execute(
                "SELECT name, price, image_path, description, stock FROM items"
            )
            products = self.db_cursor.fetchall()

            # Reload products
            row, col = 0, 0
            for product in products:
                product_with_stock = {
                    "name": product["name"],
                    "price": product["price"],
                    "image_path": product["image_path"],
                    "description": product["description"],
                    "stock": product["stock"],
                }

                product_card = ProductCard(
                    self.scrollable_frame,
                    product_with_stock,
                    self.cart,
                    self.cart_frame,
                    self.db_connection,
                    self,
                )
                product_card.card_frame.grid(
                    row=row, column=col, padx=10, pady=10, sticky="nsew"
                )

                col += 1
                if col >= 1:
                    col = 0
                    row += 1

            # Force update display
            self.scrollable_frame.update()
            self.canvas.update_idletasks()

            # Re-initialize cart display
            self.initialize_cart_display()

            messagebox.showinfo("Success", "คุณได้รีเฟรชหน้าต่างการสั่งซื้อสินค้าเรียบร้อยแล้ว")

        except mysql.connector.Error as db_err:
            messagebox.showerror(
                "Database Error", f"Failed to refresh catalog: {db_err}"
            )
            # Try to reconnect if connection was lost
            self.setup_database_connection()
        except Exception as err:
            messagebox.showerror(
                "Refresh Error", f"An error occurred while refreshing: {err}"
            )

    def load_products(self):
        """โหลดสินค้าและแสดงในรูปแบบการ์ดแนวนอน"""
        try:
            self.ensure_connection()
            self.db_cursor.execute(
                "SELECT name, price, image_path, description, stock FROM items"
            )
            products = self.db_cursor.fetchall()

            # ลบ widget เดิมออก
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # แสดงสินค้าโดยเรียงเป็นแถว
            row, col = 0, 0  # ใช้ตัวแปรควบคุมแถวและคอลัมน์
            for product in products:
                product_with_stock = {
                    "name": product["name"],
                    "price": product["price"],
                    "image_path": product["image_path"],
                    "description": product["description"],
                    "stock": product["stock"],
                }

                product_card = ProductCard(
                    self.scrollable_frame,
                    product_with_stock,
                    self.cart,
                    self.cart_frame,
                    self.db_connection,
                    self,
                )
                product_card.card_frame.grid(
                    row=row, column=col, padx=10, pady=10, sticky="nsew"
                )

                col += 1
                if col >= 1:  # สินค้า 1 ชิ้นต่อแถว
                    col = 0
                    row += 1

                self.initialize_cart_display()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load products: {err}")

    def initialize_cart_display(self):
        """Initialize cart display with an empty cart message and discount information"""
        # Clear existing cart items
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        # Create a styled cart container
        cart_container = tk.Frame(self.cart_frame, bg="#dd1454", bd=2, relief="ridge")
        cart_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Shopping Cart Header
        cart_label = tk.Label(
            cart_container,
            text="ตะกร้าสินค้าของคุณ",
            font=("Inter", 20, "bold"),
            bg="#dd1454",
            fg="#FFFFFF",
        )
        cart_label.pack(pady=(20, 10))

        # Get cart information including discount
        items, total_price, total_quantity, discount = self.cart.get_cart_info()

        if not items:
            # Empty cart message
            empty_cart_label = tk.Label(
                cart_container,
                text="สินค้าของคุณว่างเปล่าในตอนนี้",
                font=("Inter", 14),
                bg="#dd1454",
                fg="#FFFFFF",
            )
            empty_cart_label.pack(pady=20)

            # Zero totals
            total_label = tk.Label(
                cart_container,
                text="จำนวนสินค้า: 0 ชิ้น\nราคาทั้งหมด: 0.00 บาท",
                font=("Inter", 16, "bold"),
                bg="#dd1454",
                fg="#FFFFFF",
            )
            total_label.pack(pady=10)
        else:
            # Display items in cart
            items_frame = tk.Frame(cart_container, bg="#dd1454")
            items_frame.pack(fill="both", expand=True, padx=10, pady=5)

            # Create scrollable frame for items
            canvas = tk.Canvas(items_frame, bg="#dd1454", highlightthickness=0)
            scrollbar = tk.Scrollbar(
                items_frame, orient="vertical", command=canvas.yview
            )
            scrollable_frame = tk.Frame(canvas, bg="#dd1454")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )

            canvas.create_window(
                (0, 0),
                window=scrollable_frame,
                anchor="nw",
                width=canvas.winfo_reqwidth(),
            )
            canvas.configure(yscrollcommand=scrollbar.set)

            # Pack the canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Promotion information
            promo_label = tk.Label(
                cart_container,
                text="🎉 สั่งซื้อ 10 ชิ้นขึ้นไป รับส่วนลด 5% 🎉",
                font=("Inter", 12),
                bg="#dd1454",
                fg="#FFFFFF",
            )
            promo_label.pack(pady=5)

            # Display discount if applicable
            if discount > 0:
                discount_label = tk.Label(
                    cart_container,
                    text=f"ส่วนลด 5%: -{discount:.2f} บาท",
                    font=("Inter", 14, "bold"),
                    bg="#dd1454",
                    fg="#FFD700",  # Gold color for emphasis
                )
                discount_label.pack(pady=5)

            # Separator line
            separator = tk.Frame(cart_container, height=2, bg="#FFFFFF")
            separator.pack(fill="x", padx=20, pady=5)

            # Total information
            totals_frame = tk.Frame(cart_container, bg="#dd1454")
            totals_frame.pack(fill="x", padx=10, pady=5)

            # Display total quantity
            quantity_label = tk.Label(
                totals_frame,
                text=f"จำนวนสินค้า: {total_quantity} ชิ้น",
                font=("Inter", 14),
                bg="#dd1454",
                fg="#FFFFFF",
            )
            quantity_label.pack(pady=2)

            # Display total price
            total_label = tk.Label(
                totals_frame,
                text=f"ราคาทั้งหมด: {total_price:.2f} บาท",
                font=("Inter", 16, "bold"),
                bg="#dd1454",
                fg="#FFFFFF",
            )
            total_label.pack(pady=2)

            # Add checkout button if items exist
            checkout_button = tk.Button(
                cart_container,
                text="ดำเนินการชำระเงิน",
                font=("Inter", 14, "bold"),
                bg="#11d400",  # Green color
                fg="white",
                relief="flat",
                padx=20,
                pady=10,
                command=lambda: (
                    self.show_checkout() if hasattr(self, "show_checkout") else None
                ),
            )
            checkout_button.pack(pady=20)

            # Add hover effect to checkout button
            def on_enter(e):
                checkout_button["bg"] = "#0fb600"

            def on_leave(e):
                checkout_button["bg"] = "#11d400"

            checkout_button.bind("<Enter>", on_enter)
            checkout_button.bind("<Leave>", on_leave)

        # Add cart policy information
        policy_label = tk.Label(
            cart_container,
            text="🛈 ราคาและโปรโมชั่นอาจมีการเปลี่ยนแปลง",
            font=("Inter", 10),
            bg="#dd1454",
            fg="#FFFFFF",
        )
        policy_label.pack(pady=(10, 5))

        # Add current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_label = tk.Label(
            cart_container,
            text=f"Last updated: {current_datetime}",
            font=("Inter", 8),
            bg="#dd1454",
            fg="#FFFFFF",
        )
        date_label.pack(pady=(0, 10))

    def ensure_connection(self):
        """Ensure database connection is active, reconnect if necessary"""
        try:
            # Try to ping the connection
            self.db_connection.ping(reconnect=True, attempts=3, delay=1)
        except (mysql.connector.Error, AttributeError):
            # If ping fails or connection doesn't exist, create new connection
            self.db_connection = mysql.connector.connect(
                host="localhost", user="root", password="", database="user_db"
            )

    def save_order_to_database(
        self,
        first_name,
        last_name,
        address,
        telephone,
        total_price,
        total_quantity,
        items,
    ):
        """Save order details to MySQL database"""
        if not self.db_connection:
            messagebox.showerror("Database Error", "ไม่สามารถเชื่อมต่อกับฐานข้อมูลได้")
            return None

        try:
            # Sanitize and validate address
            sanitized_address = address.strip()
            if len(sanitized_address) > 500:  # Match the UI limit
                sanitized_address = sanitized_address[:500]

            # Generate order number and prepare details
            order_number = str(uuid.uuid4())[:8]

            cursor = self.db_connection.cursor()

            # Use parameterized query to prevent SQL injection
            insert_query = """
            INSERT INTO product (
                order_number, first_name, last_name, address, 
                telephone_number, order_details, total_price, total_quantity
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Prepare order details with proper formatting
            order_details = "สินค้า:\n"
            for item, data in items.items():
                order_details += (
                    f"- {item}: {data['quantity']} x {data['info']['price']:.2f} บาท\n"
                )
            order_details += f"\nจำนวนสินค้า: {total_quantity} ชิ้น\n"
            order_details += f"ราคาทั้งหมด: {total_price:.2f} บาท"

            values = (
                order_number,
                first_name,
                last_name,
                sanitized_address,
                telephone,
                order_details,
                total_price,
                total_quantity,
            )

            cursor.execute(insert_query, values)
            self.db_connection.commit()
            cursor.close()

            return order_number

        except mysql.connector.Error as err:
            self.db_connection.rollback()
            messagebox.showerror("Database Error", f"ไม่สามารถบันทึกคำสั่งซื้อได้: {err}")
            return None

        except Exception as e:
            self.db_connection.rollback()
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการบันทึกคำสั่งซื้อ: {str(e)}")
            return None

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, "db_connection") and self.db_connection:
            self.db_connection.close()


if __name__ == "__main__":
    root = Tk()
    app = ProductCatalog(root)
    root.mainloop()
