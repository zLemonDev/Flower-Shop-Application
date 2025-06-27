import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from ttkbootstrap import Style
from tkinter import filedialog

class AdminOrderManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin - Store Order Management")
        self.root.geometry("1800x800")
        
        # Use ttkbootstrap for a modern, professional look
        style = Style(theme='cosmo')
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg='#140c13')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            self.main_frame, 
            text="Store Order Management", 
            font=("Inter", 24, "bold"), 
            bg='#140c13', 
            fg='white'
        )
        title_label.pack(pady=(20, 10))
        
        # Create Treeview with custom styling
        self.create_order_table()
        
        # Buttons frame
        self.create_action_buttons()
        
        # Connect to database and load orders
        self.connect_to_database()
        
    def connect_to_database(self):
        """Establish database connection and load orders"""
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="user_db"
            )
            self.db_cursor = self.db_connection.cursor(dictionary=True)
            self.load_orders()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            
    def create_order_table(self):
        """Create a professional-looking order table"""
        # Table Frame
        table_frame = tk.Frame(self.main_frame, bg='#140c13')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        tree_scrolly = ttk.Scrollbar(table_frame)
        tree_scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scrollx = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        tree_scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.order_tree = ttk.Treeview(
            table_frame, 
            columns=( 
                "Order Number", "First Name", "Last Name", 
                "Address", "Telephone", "Total Price", 
                "Total Quantity", "Order Date"
            ), 
            show='headings',
            yscrollcommand=tree_scrolly.set,
            xscrollcommand=tree_scrollx.set
        )
        
        # Column configuration
        column_widths = [100, 100, 100, 200, 120, 100, 100, 150]
        column_names = [
            "Order Number", "First Name", "Last Name", 
            "Address", "Telephone", "Total Price", 
            "Total Quantity", "Order Date"
        ]
        
        for i, (col, width) in enumerate(zip(self.order_tree['columns'], column_widths)):
            self.order_tree.heading(col, text=column_names[i], anchor=tk.CENTER)
            self.order_tree.column(col, width=width, anchor=tk.CENTER)
        
        self.order_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        tree_scrolly.config(command=self.order_tree.yview)
        tree_scrollx.config(command=self.order_tree.xview)
        
        # Row color configuration
        self.order_tree.tag_configure('oddrow', background='#2c3e50', foreground='white')
        self.order_tree.tag_configure('evenrow', background='#34495e', foreground='white')

        # Total Price and Quantity Labels
        self.total_label = tk.Label(
            self.main_frame, 
            text="Total: Price - 0.00 บาท | Quantity - 0", 
            font=("Inter", 14, "bold"), 
            bg='#140c13', 
            fg='white'
        )
        self.total_label.pack(pady=(10, 20))
        
    def load_orders(self):
        """Load orders from database with error handling"""
        try:
            # Clear existing items
            for i in self.order_tree.get_children():
                self.order_tree.delete(i)

            # Fetch orders
            self.db_cursor.execute("""
                SELECT 
                    order_number, 
                    first_name, 
                    last_name, 
                    address, 
                    telephone_number, 
                    total_price, 
                    total_quantity,
                    created_at
                FROM product
                ORDER BY created_at DESC
            """)

            orders = self.db_cursor.fetchall()
            total_price = 0
            total_quantity = 0

            # Populate treeview
            for index, order in enumerate(orders):
                tag = 'oddrow' if index % 2 == 0 else 'evenrow'
                self.order_tree.insert('', 'end', values=(
                    order['order_number'],
                    order['first_name'],
                    order['last_name'],
                    order['address'],
                    order['telephone_number'],
                    f"{order['total_price']:,} บาท",
                    order['total_quantity'],
                    order['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                ), tags=(tag,))

                # Calculate totals
                total_price += order['total_price']
                total_quantity += order['total_quantity']

            # Update total label
            self.total_label.config(
                text=f"ยอดรวมทั้งหมด - {total_price:,.2f} บาท | จำนวนดอกไม้ทั้งหมด - {total_quantity:,.2f} ชิ้น"
            )

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load orders: {err}")
            
    def create_action_buttons(self):
        """Create action buttons for order management"""
        button_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # View Order Details Button
        view_details_btn = tk.Button(
            button_frame, 
            text="View Order Details", 
            command=self.view_order_details,
            bg='#3498db', 
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        view_details_btn.pack(side=tk.LEFT, padx=10)
        
        # Refresh Orders Button
        refresh_btn = tk.Button(
            button_frame, 
            text="Refresh Orders", 
            command=self.load_orders,
            bg='#2ecc71', 
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # Delete Order Button
        delete_btn = tk.Button(
            button_frame, 
            text="Delete Order", 
            command=self.delete_order,
            bg='#e74c3c', 
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        delete_btn.pack(side=tk.LEFT, padx=10)

        # Delete Product Button
        delete_product_btn = tk.Button(
            button_frame, 
            text="Manage Products", 
            command=self.delete_product,
            bg='#e74c3c', 
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        delete_product_btn.pack(side=tk.LEFT, padx=10)

        # View Order Totals Button (Add this new button)
        view_totals_btn = tk.Button(
            button_frame, 
            text="View Order Totals", 
            command=self.view_order_totals,
            bg='#9b59b6', 
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        view_totals_btn.pack(side=tk.LEFT, padx=10)

    def view_order_totals(self):
        """Display a window to select date and view order totals"""
        totals_window = tk.Toplevel(self.root)
        totals_window.title("View Order Totals")
        totals_window.geometry("800x700")
        totals_window.configure(bg='#2c3e50')

        # Title
        title_label = tk.Label(
            totals_window,
            text="View Order Totals by Period",
            font=("Inter", 18, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=(20, 30))

        # Period Selection Frame
        period_frame = tk.Frame(totals_window, bg='#2c3e50')
        period_frame.pack(fill=tk.X, padx=20)

        # Period Type Selection
        period_var = tk.StringVar(value="daily")
        
        period_label = tk.Label(
            period_frame,
            text="Select Period Type:",
            font=("Inter", 12),
            bg='#2c3e50',
            fg='white'
        )
        period_label.pack(pady=(0, 10))

        # Radio buttons for period selection
        daily_radio = ttk.Radiobutton(
            period_frame,
            text="Daily",
            variable=period_var,
            value="daily"
        )
        daily_radio.pack(side=tk.LEFT, padx=10)

        monthly_radio = ttk.Radiobutton(
            period_frame,
            text="Monthly",
            variable=period_var,
            value="monthly"
        )
        monthly_radio.pack(side=tk.LEFT, padx=10)

        yearly_radio = ttk.Radiobutton(
            period_frame,
            text="Yearly",
            variable=period_var,
            value="yearly"
        )
        yearly_radio.pack(side=tk.LEFT, padx=10)

        # Date Selection Frame
        date_frame = tk.Frame(totals_window, bg='#2c3e50')
        date_frame.pack(fill=tk.X, padx=20, pady=20)

        # Get current date
        current_date = datetime.now()

        # Year Selection
        year_label = tk.Label(
            date_frame,
            text="Year:",
            font=("Inter", 12),
            bg='#2c3e50',
            fg='white'
        )
        year_label.grid(row=0, column=0, padx=5, pady=5)

        year_var = tk.StringVar(value=str(current_date.year))
        year_spinbox = ttk.Spinbox(
            date_frame,
            from_=2020,
            to=2030,
            textvariable=year_var,
            width=10
        )
        year_spinbox.grid(row=0, column=1, padx=5, pady=5)

        # Month Selection
        month_label = tk.Label(
            date_frame,
            text="Month:",
            font=("Inter", 12),
            bg='#2c3e50',
            fg='white'
        )
        month_label.grid(row=1, column=0, padx=5, pady=5)

        month_var = tk.StringVar(value=f"{current_date.month:02d}")
        month_spinbox = ttk.Spinbox(
            date_frame,
            from_=1,
            to=12,
            format="%02.0f",
            textvariable=month_var,
            width=10
        )
        month_spinbox.grid(row=1, column=1, padx=5, pady=5)

        # Day Selection
        day_label = tk.Label(
            date_frame,
            text="Day:",
            font=("Inter", 12),
            bg='#2c3e50',
            fg='white'
        )
        day_label.grid(row=2, column=0, padx=5, pady=5)

        day_var = tk.StringVar(value=f"{current_date.day:02d}")
        day_spinbox = ttk.Spinbox(
            date_frame,
            from_=1,
            to=31,
            format="%02.0f",
            textvariable=day_var,
            width=10
        )
        day_spinbox.grid(row=2, column=1, padx=5, pady=5)

        # Results Frame
        results_frame = tk.Frame(totals_window, bg='#34495e')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create Treeview for results
        columns = ("Description", "Value")
        results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        for col in columns:
            results_tree.heading(col, text=col)
            results_tree.column(col, width=300)
        
        results_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        def update_date_fields(*args):
            """Enable/disable date fields based on period selection"""
            period = period_var.get()
            
            if period == "yearly":
                month_spinbox.config(state='disabled')
                day_spinbox.config(state='disabled')
            elif period == "monthly":
                month_spinbox.config(state='normal')
                day_spinbox.config(state='disabled')
            else:  # daily
                month_spinbox.config(state='normal')
                day_spinbox.config(state='normal')

        # Bind the period selection to update date fields
        period_var.trace('w', update_date_fields)

        def fetch_totals():
            """Fetch and display order totals based on selected period"""
            period = period_var.get()
            year = year_var.get()
            month = month_var.get()
            day = day_var.get()

            try:
                # Clear existing items
                for item in results_tree.get_children():
                    results_tree.delete(item)

                # Build query based on period type
                if period == "yearly":
                    query = """
                        SELECT 
                            COUNT(*) as order_count,
                            SUM(total_price) as total_sales,
                            SUM(total_quantity) as total_items,
                            YEAR(created_at) as period,
                            MIN(created_at) as start_date,
                            MAX(created_at) as end_date
                        FROM product 
                        WHERE YEAR(created_at) = %s
                        GROUP BY YEAR(created_at)
                    """
                    params = (year,)
                    period_text = f"Year {year}"
                
                elif period == "monthly":
                    query = """
                        SELECT 
                            COUNT(*) as order_count,
                            SUM(total_price) as total_sales,
                            SUM(total_quantity) as total_items,
                            MONTH(created_at) as period,
                            MIN(created_at) as start_date,
                            MAX(created_at) as end_date
                        FROM product 
                        WHERE YEAR(created_at) = %s 
                        AND MONTH(created_at) = %s
                        GROUP BY YEAR(created_at), MONTH(created_at)
                    """
                    params = (year, month)
                    period_text = f"Month {month}, {year}"
                
                else:  # daily
                    query = """
                        SELECT 
                            COUNT(*) as order_count,
                            SUM(total_price) as total_sales,
                            SUM(total_quantity) as total_items,
                            DAY(created_at) as period,
                            MIN(created_at) as start_date,
                            MAX(created_at) as end_date
                        FROM product 
                        WHERE DATE(created_at) = %s
                    """
                    params = (f"{year}-{month}-{day}",)
                    period_text = f"Date: {year}-{month}-{day}"

                self.db_cursor.execute(query, params)
                totals = self.db_cursor.fetchone()

                if totals and totals['order_count'] > 0:
                    # Display period
                    results_tree.insert('', 'end', values=('Period', period_text))
                    
                    # Display date range
                    date_range = f"From {totals['start_date']} to {totals['end_date']}"
                    results_tree.insert('', 'end', values=('Date Range', date_range))
                    
                    # Display totals
                    results_tree.insert('', 'end', values=('Total Orders', f"{totals['order_count']:,}"))
                    results_tree.insert('', 'end', values=('Total Sales', f"{totals['total_sales']:,.2f} บาท"))
                    results_tree.insert('', 'end', values=('Total Items Sold', f"{totals['total_items']:,}"))

                    # Calculate and display averages
                    avg_order = totals['total_sales'] / totals['order_count']
                    results_tree.insert('', 'end', values=('Average Order Value', f"{avg_order:,.2f} บาท"))
                    
                    if totals['total_items'] > 0:
                        avg_item_price = totals['total_sales'] / totals['total_items']
                        results_tree.insert('', 'end', values=('Average Item Price', f"{avg_item_price:,.2f} บาท"))
                else:
                    results_tree.insert('', 'end', values=('No Data', f"No orders found for {period_text}"))

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to fetch totals: {err}")

        # View Totals Button
        view_button = tk.Button(
            totals_window,
            text="View Totals",
            command=fetch_totals,
            bg='#3498db',
            fg='white',
            font=("Inter", 12, "bold"),
            padx=20,
            pady=10
        )
        view_button.pack(pady=20)

        # Initial update of date fields
        update_date_fields()


    def delete_product(self):
        """Create and display the 'Manage Products' window with delete and add product sections"""
        manage_window = tk.Toplevel(self.root)
        manage_window.title("Product Management")
        manage_window.geometry("1100x700")
        manage_window.configure(bg='#2c3e50')


        # Main Frame to split into two sections
        main_frame = tk.Frame(manage_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create two columns
        left_frame = tk.Frame(main_frame, bg='#2c3e50', width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        right_frame = tk.Frame(main_frame, bg='#130f10', width=500)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Left Side: Product List (Delete/Edit)
        list_title = tk.Label(
            left_frame,
            text="Existing Products",
            font=("Inter", 20, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        list_title.pack(pady=(20, 10))

        # Create Product Table Frame
        table_frame = tk.Frame(left_frame, bg='#2c3e50')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollbars
        tree_scrolly = ttk.Scrollbar(table_frame)
        tree_scrolly.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scrollx = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        tree_scrollx.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview for Products
        product_tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Price", "Description"),
            show='headings',
            selectmode='browse',
            yscrollcommand=tree_scrolly.set,
            xscrollcommand=tree_scrollx.set
        )

        # Column configuration
        product_tree.heading("ID", text="Product ID")
        product_tree.heading("Name", text="Product Name")
        product_tree.heading("Price", text="Price")
        product_tree.heading("Description", text="Description")

        product_tree.column("ID", width=100, anchor=tk.CENTER)
        product_tree.column("Name", width=200, anchor=tk.CENTER)
        product_tree.column("Price", width=100, anchor=tk.CENTER)
        product_tree.column("Description", width=250, anchor=tk.CENTER)

        product_tree.pack(fill=tk.BOTH, expand=True)

        # Configure scrollbars
        tree_scrolly.config(command=product_tree.yview)
        tree_scrollx.config(command=product_tree.xview)

        # Fetch and populate products
        try:
            self.db_cursor.execute("SELECT id, name, price, description FROM items")
            products = self.db_cursor.fetchall()

            for product in products:
                product_tree.insert('', 'end', values=(
                    product['id'],
                    product['name'],
                    f"{product['price']:.2f} บาท",
                    product['description']
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch products: {err}")

        # Button Frame for Product List
        list_button_frame = tk.Frame(left_frame, bg='#2c3e50')
        list_button_frame.pack(pady=10)

        # Delete Button
        delete_button = tk.Button(
            list_button_frame,
            text="Delete Selected Products",
            command=lambda tree=product_tree: self.delete_selected_products(tree),
            bg='#e74c3c',
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        delete_button.pack(side=tk.LEFT, padx=10)

        # Edit Button
        edit_button = tk.Button(
            list_button_frame,
            text="Edit Selected Product",
            command=lambda: self.edit_product(product_tree),
            bg='#3498db',
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        edit_button.pack(side=tk.LEFT, padx=10)

        # Right Side: Add New Product
        add_title = tk.Label(
            right_frame,
            text="Add New Product",
            font=("Inter", 20, "bold"),
            bg='#130f10',
            fg='white'
        )
        add_title.pack(pady=(20, 10))

        # Input fields for new product
        self.create_product_input_fields(right_frame, product_tree, manage_window)

    def create_product_input_fields(self, frame, product_tree, manage_window):
        """Helper method to create input fields for adding new products."""
        # Product Name
        name_label = tk.Label(frame, text="Product Name:", font=("Inter", 12), bg='#130f10', fg='white')
        name_label.pack(fill='x', padx=20, pady=5)
        name_entry = ttk.Entry(frame, font=("Inter", 12))
        name_entry.pack(fill='x', padx=20, pady=5)

        # Price
        price_label = tk.Label(frame, text="ราคา (บาท):", font=("Inter", 12), bg='#130f10', fg='white')
        price_label.pack(fill='x', padx=20, pady=5)
        price_entry = ttk.Entry(frame, font=("Inter", 12))
        price_entry.pack(fill='x', padx=20, pady=5)

        # Description
        desc_label = tk.Label(frame, text="Description:", font=("Inter", 12), bg='#130f10', fg='white')
        desc_label.pack(fill='x', padx=20, pady=5)
        desc_entry = ttk.Entry(frame, font=("Inter", 12))
        desc_entry.pack(fill='x', padx=20, pady=5)

        # Image Path
        image_path_var = tk.StringVar()
        image_label = tk.Label(frame, text="Image Path:", font=("Inter", 12), bg='#130f10', fg='white')
        image_label.pack(fill='x', padx=20, pady=5)
        image_path_display = ttk.Entry(frame, textvariable=image_path_var, state='readonly', font=("Inter", 12))
        image_path_display.pack(fill='x', padx=20, pady=5)

        # Choose Image Button
        choose_image_btn = tk.Button(
            frame,
            text="Choose Image",
            command=lambda: self.choose_image(image_path_var, manage_window),  # ส่ง image_path_var เป็น argument
            bg='#3498db',
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        choose_image_btn.pack(fill='x', padx=20, pady=5)

        manage_window.transient(self.root)
        manage_window.focus_set()

        # Add Product Button
        add_product_btn = tk.Button(
            frame,
            text="Add Product",
            command=lambda: self.submit_product(
                name_entry.get().strip(),
                price_entry.get().strip(),
                desc_entry.get().strip(),
                image_path_var.get(),
                self.db_cursor,
                product_tree
            ),
            bg='#2ecc71',
            fg='white',
            font=("Inter", 12, "bold"),
            padx=15,
            pady=5
        )
        add_product_btn.pack(pady=20)

    def populate_product_tree(self, product_tree):
        """Fetch and populate products in the Treeview"""
        try:
            self.db_cursor.execute("SELECT id, name, price, description FROM items")
            products = self.db_cursor.fetchall()

            for product in products:
                product_tree.insert('', 'end', values=(
                    product['id'], 
                    product['name'], 
                    f"{product['price']:.2f} บาท", 
                    product['description']
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch products: {err}")

    def delete_selected_products(self, product_tree):
        """Delete selected products from the database and Treeview"""
        selected_items = product_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select at least one product to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected products?")
        if not confirm:
            return

        try:
            for item in selected_items:
                product_id = product_tree.item(item)['values'][0]
                self.db_cursor.execute("DELETE FROM items WHERE id = %s", (product_id,))
                self.db_connection.commit()
                product_tree.delete(item)

            messagebox.showinfo("Success", "Selected products deleted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete products: {err}")

    def edit_product(self, product_tree):
        """Open a window to edit the selected product"""
        selected_item = product_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a product to edit.")
            return

        # Get selected product details
        product_id = product_tree.item(selected_item)['values'][0]
        
        try:
            # Fetch full product details
            self.db_cursor.execute("SELECT * FROM items WHERE id = %s", (product_id,))
            product = self.db_cursor.fetchone()

            if not product:
                messagebox.showerror("Error", "Product not found.")
                return

            # Create the edit window
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Edit Product - {product['name']}")
            edit_window.geometry("500x700")
            edit_window.configure(bg='#130f10')

            # Open Edit Product Window
            self.open_edit_product_window(product, product_tree, edit_window)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch product details: {err}")

    def open_edit_product_window(self, product, product_tree, edit_window):

        # Title
        title_label = tk.Label(
            edit_window,
            text="Edit Product",
            font=("Inter", 18, "bold"),
            bg='#130f10',
            fg='white'
        )
        title_label.pack(pady=(20, 10))

        # Name Entry
        name_entry = self.create_entry_with_label(edit_window, "ชื่อสินค้า:", product['name'])

        # Price Entry
        price_entry = self.create_entry_with_label(edit_window, "รราคา (บาท):", str(product['price']))

        # Stock Entry
        stock_entry = self.create_entry_with_label(edit_window, "จำนวนสินค้า:", str(product['stock']))

        # Description Entry
        desc_entry = self.create_entry_with_label(edit_window, "รายละเอียดสินค้า:", product['description'])

        # Image Path
        image_path_var = tk.StringVar(value=product['image_path'])
        self.create_image_selector(edit_window, image_path_var, edit_window)

        # Save Button
        def save_changes():
            """Save edited product details to database"""
            try:
                new_name = name_entry.get().strip()
                new_price = price_entry.get().strip()
                new_stock = stock_entry.get().strip()
                new_desc = desc_entry.get().strip()
                new_image_path = image_path_var.get()

                if not new_name or not new_price or not new_stock or not new_desc or not new_image_path:
                    messagebox.showwarning("Input Error", "Please fill in all fields.")
                    return

                new_price = float(new_price)
                new_stock = int(new_stock)

                # Update the product in the database, including the stock
                self.db_cursor.execute(
                    """
                    UPDATE items 
                    SET name = %s, price = %s, stock = %s, description = %s, image_path = %s 
                    WHERE id = %s
                    """, 
                    (new_name, new_price, new_stock, new_desc, new_image_path, product['id'])
                )
                self.db_connection.commit()

                # Update the product in the treeview
                selected_item_index = product_tree.selection()[0]
                product_tree.item(selected_item_index, values=(
                    product['id'], new_name, f"{new_price:.2f} บาท", new_desc, new_stock
                ))

                messagebox.showinfo("Success", "Product updated successfully!")
                edit_window.destroy()

            except ValueError:
                messagebox.showerror("Input Error", "Invalid price or stock. Please enter valid numbers.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to update product: {err}")

        save_button = ttk.Button(edit_window, text="Save Changes", command=save_changes)
        save_button.pack(pady=20)
    def create_entry_with_label(self, parent, label_text, default_value):
        """Create an Entry widget with a Label"""
        label = ttk.Label(parent, text=label_text, font=("Inter", 12), background="#130f10", foreground="white")
        label.pack(fill='x', padx=20, pady=5)
        entry = ttk.Entry(parent, font=("Inter", 12))
        entry.pack(fill='x', padx=20, pady=5)
        entry.insert(0, default_value)
        return entry

    def create_image_selector(self, parent, image_path_var, manage_window):
        """Create an image path selector"""
        image_label = ttk.Label(parent, text="Image Path:", font=("Inter", 12), background="#130f10", foreground="white")
        image_label.pack(fill='x', padx=20, pady=5)

        image_path_display = ttk.Entry(parent, textvariable=image_path_var, state='readonly', font=("Inter", 12))
        image_path_display.pack(fill='x', padx=20, pady=5)

        def choose_new_image():
            new_image_path = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")],
                title="Select New Product Image",
                parent=manage_window
            )
            manage_window.grab_release()

            if new_image_path:
                image_path_var.set(new_image_path)

        choose_image_btn = ttk.Button(parent, text="Choose New Image", command=choose_new_image)
        choose_image_btn.pack(fill='x', padx=20, pady=5)

    def add_product(self):
        """Create and display the 'Add New Product' window"""
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Product")
        add_window.geometry("500x600")
        add_window.configure(bg='#130f10')

        # Title
        self._create_title(add_window)

        # Product Form
        self._create_product_form(add_window)

        # Add Product Button
        self._create_add_button(add_window)

        # Start the Add Product Window
        add_window.mainloop()

    def _create_title(self, parent_window):
        """Creates the title label for the Add Product window"""
        title_label = tk.Label(
            parent_window,
            text="Add New Product",
            font=("Inter", 18, "bold"),
            bg='#130f10',
            fg='white'
        )
        title_label.pack(pady=(20, 10))

    def _create_product_form(self, parent_window):
        """Create and place the input fields for product details"""
        # Name
        self.name_entry = self._create_input_field(parent_window, "ชื่อสินค้า:")

        # Price
        self.price_entry = self._create_input_field(parent_window, "ราคา (บาท):")

        # Description
        self.description_entry = self._create_input_field(parent_window, "Description:")

        # Image Selection Button
        self._create_image_button(parent_window)

    def _create_input_field(self, parent_window, label_text):
        """Create labeled input field for product details"""
        label = ttk.Label(parent_window, text=label_text, font=("Inter", 12), anchor="w", background="#130f10", foreground="white")
        label.pack(fill='x', padx=20, pady=5)
        entry = ttk.Entry(parent_window, font=("Inter", 12))
        entry.pack(fill='x', padx=20, pady=5)
        return entry

    def _create_image_button(self, parent_window):
        """Create the image path selection button"""
        image_label = ttk.Label(parent_window, text="Image Path:", font=("Inter", 12), anchor="w")
        image_label.pack(fill='x', padx=20, pady=5)
        image_button = ttk.Button(parent_window, text="Choose Image", command=self.choose_image, style="TButton")
        image_button.pack(fill='x', padx=20, pady=5)

    def _create_add_button(self, parent_window):
        """Create the button to submit product information"""
        add_button = ttk.Button(
            parent_window, 
            text="Add Product", 
            command=self.submit_product, 
            style="TButton"
        )
        add_button.pack(pady=20)

    def choose_image(self, image_path_var, manage_window):
        """Open file dialog to choose an image for the product"""
        manage_window.grab_set()  # Focus on the manage_window

        image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")],
            title="Select Product Image",
            parent=manage_window
        )
        manage_window.grab_release()  # Release grab once filedialog is closed

        if image_path:
            image_path_var.set(image_path)

    def submit_product(self, name, price, description, image_path, db_cursor, product_tree):
        """Submit the new product to the database."""
        # Validate input fields
        if not name or not price or not description or not image_path:
            messagebox.showwarning("Input Error", "Please fill in all fields and select an image.")
            return

        try:
            price = float(price)  # Ensure the price is a valid float
            db_cursor.execute(
                """
                INSERT INTO items (name, price, image_path, description) 
                VALUES (%s, %s, %s, %s)
                """,
                (name, price, image_path, description),
            )
            self.db_connection.commit()

            # Add to the product treeview
            product_tree.insert('', 'end', values=(
                db_cursor.lastrowid,
                name,
                f"{price:.2f} บาท",
                description
            ))

            messagebox.showinfo("Success", "Product added successfully!")
        
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add product: {err}")

    def clear_form(self):
        """Clear all input fields after submitting the product"""
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.image_path = None

        
    def view_order_details(self):
        """Display detailed information for selected order"""
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an order to view details.")
            return
    
        order_number = self.order_tree.item(selected_item)['values'][0]
    
        try:
            self.db_cursor.execute("""
                SELECT order_number, first_name, last_name, address, 
                    telephone_number, order_details, created_at
                FROM product 
                WHERE order_number = %s
            """, (order_number,))
            order = self.db_cursor.fetchone()
        
            if order:
                details_window = tk.Toplevel(self.root)
                details_window.title(f"รายละเอียดสินค้า - {order_number}")
                details_window.geometry("600x400")
                details_window.configure(bg='#2c3e50')
            
                # Title
                tk.Label(
                    details_window, text="รายละเอียดออเดอร์", 
                    font=("Inter", 20, "bold"), bg="#2c3e50", fg="white"
                ).pack(pady=(20, 10))
            
                # Details Frame
                details_frame = tk.Frame(details_window, bg='#34495e')
                details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
                # Display key-value pairs
                details = [
                    ("หมายเลขคำสั่งซื้อ", order['order_number']),
                    ("ชื่อ", order['first_name']),
                    ("นามสกุล", order['last_name']),
                    ("ที่อยู่จัดส่ง", order['address']),
                    ("หมายเลขโทรศัพท์", order['telephone_number']),
                    ("รายละเอียดสินค้า", f"{order['order_details']} บาท"),
                    ("วันที่สั่ง", order['created_at'].strftime("%Y-%m-%d %H:%M:%S"))
                ]
            
                for idx, (key, value) in enumerate(details):
                    tk.Label(
                        details_frame, text=f"{key}:", 
                        font=("Inter", 12, "bold"), bg="#34495e", fg="white", anchor="w"
                    ).grid(row=idx, column=0, sticky="w", padx=10, pady=5)
                
                    tk.Label(
                        details_frame, text=f"{value}", 
                        font=("Inter", 12), bg="#34495e", fg="white", anchor="w"
                    ).grid(row=idx, column=1, sticky="w", padx=10, pady=5)
        
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch order details: {err}")


        
    def delete_order(self):
        """Delete selected order with confirmation"""
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an order to delete.")
            return
        
        order_number = self.order_tree.item(selected_item)['values'][0]
        
        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete order {order_number}?"
        )
        
        if confirm:
            try:
                self.db_cursor.execute(
                    "DELETE FROM product WHERE order_number = %s", 
                    (order_number,)
                )
                self.db_connection.commit()
                
                messagebox.showinfo("Success", f"Order {order_number} deleted successfully.")
                self.load_orders()
                
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to delete order: {err}")
    
    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'db_connection') and self.db_connection:
            self.db_connection.close()

# Function to open the AdminOrderManagement window after successful login
def open_admin_order_management():
    root = tk.Tk()
    app = AdminOrderManagement(root)
    root.mainloop()

if __name__ == "__main__":
    open_admin_order_management()