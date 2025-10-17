import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import requests
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ... other imports
import os  # <-- Add this import
import sys # <-- Add this import
import tempfile
import platform

# Try to import pywin32 printing helpers (optional, faster/raw printing on Windows)
try:
    import win32print
    import win32api
    WIN32_AVAILABLE = True
except Exception:
    WIN32_AVAILABLE = False

# --- Function to handle paths for PyInstaller ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- 1. DATABASE SETUP ---
# ...

# --- MODIFICATION HERE ---
# Change the original DB_FILE line to use the new function
DB_FILE = resource_path("inventory.db") 

# ... the rest of your code remains the same

# --- 1. DATABASE SETUP ---
# All functions related to database interaction are here.

DB_FILE = "inventory.db"

def setup_database():
    """Creates the necessary tables in the SQLite database if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Products table: Stores all product information.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            sku TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # Transactions table: Stores records of each sale.
    # The 'items' column will store a JSON string of the products sold.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
            created_at TEXT NOT NULL,
            items TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# --- 2. GUI APPLICATION ---
# The main application class that builds and manages the user interface.

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shop Inventory Management")
        self.root.geometry("1200x800")

        # Style configuration for a modern look
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TNotebook.Tab", font=('Helvetica', 12, 'bold'))
        self.style.configure("TLabel", font=('Helvetica', 11))
        self.style.configure("TButton", font=('Helvetica', 11))
        self.style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'))

        # Create the main tabbed interface
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Initialize and create each tab
        self.create_dashboard_tab()
        self.create_products_tab()
        self.create_billing_tab()
        self.create_analytics_tab()
        self.create_transactions_tab()  # <-- ADDED Transactions tab
        self.create_ai_assistant_tab()
        
        # Load initial data
        self.refresh_all_data()

    def refresh_all_data(self):
        """Refreshes the data across all tabs."""
        self.update_dashboard_stats()
        self.load_products()
        self.load_transactions()  # <-- ADDED load of transactions
        self.update_analytics_chart('month') # Default to month view

    # --- Dashboard Tab ---
    def create_dashboard_tab(self):
        self.dashboard_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.dashboard_frame, text='Dashboard')
        
        stats_frame = ttk.Frame(self.dashboard_frame)
        stats_frame.pack(pady=20, padx=10, fill='x')

        self.stat_vars = {
            "total_products": tk.StringVar(value="0"),
            "low_stock": tk.StringVar(value="0"),
            "total_sales": tk.StringVar(value="0"),
            "revenue": tk.StringVar(value="$0.00")
        }

        # Create stat cards
        self.create_stat_card(stats_frame, "Total Products", self.stat_vars["total_products"]).grid(row=0, column=0, padx=10, sticky='ew')
        self.create_stat_card(stats_frame, "Low Stock Items (<5)", self.stat_vars["low_stock"]).grid(row=0, column=1, padx=10, sticky='ew')
        self.create_stat_card(stats_frame, "Total Sales", self.stat_vars["total_sales"]).grid(row=0, column=2, padx=10, sticky='ew')
        self.create_stat_card(stats_frame, "Total Revenue", self.stat_vars["revenue"]).grid(row=0, column=3, padx=10, sticky='ew')
        
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)

    def create_stat_card(self, parent, title, string_var):
        card = ttk.Frame(parent, borderwidth=2, relief="groove", padding="20")
        title_label = ttk.Label(card, text=title, font=('Helvetica', 12, 'bold'))
        title_label.pack()
        value_label = ttk.Label(card, textvariable=string_var, font=('Helvetica', 24, 'bold'))
        value_label.pack(pady=10)
        return card

    def update_dashboard_stats(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN quantity < 5 THEN 1 ELSE 0 END) FROM products")
        products_data = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*), SUM(total) FROM transactions")
        sales_data = cursor.fetchone()
        
        conn.close()

        self.stat_vars["total_products"].set(products_data[0] if products_data else 0)
        self.stat_vars["low_stock"].set(products_data[1] if products_data and products_data[1] else 0)
        self.stat_vars["total_sales"].set(sales_data[0] if sales_data else 0)
        self.stat_vars["revenue"].set(f"${sales_data[1]:.2f}" if sales_data and sales_data[1] else "$0.00")

    # --- Products Tab ---
    def create_products_tab(self):
        self.products_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.products_frame, text='Products')

        # Form for adding a new product
        form_frame = ttk.LabelFrame(self.products_frame, text="Add/Edit Product", padding="15")
        form_frame.pack(fill='x', pady=10)

        labels = ["SKU:", "Name:", "Price:", "Quantity:"]
        self.product_entries = {}
        for i, label_text in enumerate(labels):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            self.product_entries[label_text.replace(":", "").lower()] = entry
        
        form_frame.grid_columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Add Product", command=self.add_product).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_product_form).pack(side='left', padx=5)

        # Treeview to display products
        tree_frame = ttk.Frame(self.products_frame)
        tree_frame.pack(expand=True, fill='both', pady=10)
        
        self.product_tree = ttk.Treeview(tree_frame, columns=("SKU", "Name", "Price", "Quantity"), show='headings')
        self.product_tree.heading("SKU", text="SKU")
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Price", text="Price")
        self.product_tree.heading("Quantity", text="Quantity")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.product_tree.pack(expand=True, fill='both')

        # Delete button
        ttk.Button(self.products_frame, text="Delete Selected Product", command=self.delete_product).pack(pady=10)

    def load_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT sku, name, price, quantity FROM products ORDER BY name")
        for row in cursor.fetchall():
            self.product_tree.insert("", "end", values=(row[0], row[1], f"${row[2]:.2f}", row[3]))
        conn.close()

    def add_product(self):
        sku = self.product_entries['sku'].get()
        name = self.product_entries['name'].get()
        price = self.product_entries['price'].get()
        quantity = self.product_entries['quantity'].get()

        if not all([sku, name, price, quantity]):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Price and Quantity must be valid numbers.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO products (sku, name, price, quantity) VALUES (?, ?, ?, ?)", (sku, name, price, quantity))
            conn.commit()
            messagebox.showinfo("Success", "Product added successfully.")
            self.clear_product_form()
            self.refresh_all_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Product with SKU '{sku}' already exists.")
        finally:
            conn.close()

    def delete_product(self):
        selected_item = self.product_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete.")
            return

        product_details = self.product_tree.item(selected_item)
        sku = product_details['values'][0]

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete product with SKU {sku}?"):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE sku = ?", (sku,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Product deleted.")
            self.refresh_all_data()
            
    def clear_product_form(self):
        for entry in self.product_entries.values():
            entry.delete(0, 'end')

    # --- Billing Tab ---
    def create_billing_tab(self):
        self.billing_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.billing_frame, text='Billing')

        main_pane = ttk.PanedWindow(self.billing_frame, orient='horizontal')
        main_pane.pack(expand=True, fill='both')

        # Left side: Product Search and Add
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=2)
        
        search_frame = ttk.LabelFrame(left_frame, text="Search Products", padding="10")
        search_frame.pack(fill='x', pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.search_products)
        ttk.Entry(search_frame, textvariable=self.search_var, width=50).pack(fill='x')
        
        self.search_results_tree = ttk.Treeview(left_frame, columns=("SKU", "Name", "Price", "Stock"), show='headings', height=10)
        self.search_results_tree.pack(expand=True, fill='both', pady=5)
        for col in ("SKU", "Name", "Price", "Stock"):
            self.search_results_tree.heading(col, text=col)
        self.search_products() # Initial load

        ttk.Button(left_frame, text="Add Selected to Bill", command=self.add_to_bill).pack(pady=10)

        # Right side: Bill Summary
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)
        
        bill_frame = ttk.LabelFrame(right_frame, text="Bill Summary", padding="10")
        bill_frame.pack(expand=True, fill='both')

        self.bill_tree = ttk.Treeview(bill_frame, columns=("Name", "Qty", "Price", "Total"), show='headings')
        self.bill_tree.pack(expand=True, fill='both')
        for col in ("Name", "Qty", "Price", "Total"):
            self.bill_tree.heading(col, text=col)

        self.total_var = tk.StringVar(value="Total: $0.00")
        ttk.Label(right_frame, textvariable=self.total_var, font=('Helvetica', 16, 'bold')).pack(pady=10)

        checkout_btn_frame = ttk.Frame(right_frame)
        checkout_btn_frame.pack(pady=5, fill='x')
        ttk.Button(checkout_btn_frame, text="Checkout", command=self.checkout).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(checkout_btn_frame, text="Clear Bill", command=self.clear_bill).pack(side='left', expand=True, fill='x', padx=5)

    def search_products(self, *args):
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
        
        search_term = self.search_var.get()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT sku, name, price, quantity FROM products WHERE name LIKE ? OR sku LIKE ?", 
                       (f'%{search_term}%', f'%{search_term}%'))
        for row in cursor.fetchall():
            self.search_results_tree.insert("", "end", values=row)
        conn.close()

    def add_to_bill(self):
        selected_item = self.search_results_tree.focus()
        if not selected_item: return

        # Original line that retrieves string values from the Treeview
        sku, name, price_str, stock_str = self.search_results_tree.item(selected_item)['values']

        # --- FIX HERE ---
        # Convert the retrieved strings to their proper numeric types (float and int)
        try:
            price = float(price_str)
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid price or stock value in the product list.")
            return
    
        # Check if item already in bill to update quantity
        for item in self.bill_tree.get_children():
            if self.bill_tree.item(item)['values'][0] == name:
                qty = int(self.bill_tree.item(item)['values'][1]) + 1
            
                # Now we can safely compare two integers
                if qty > stock:
                    messagebox.showwarning("Stock Alert", f"Cannot add more '{name}'. Only {stock} available in stock.")
                    return

                self.bill_tree.item(item, values=(name, qty, f"${price:.2f}", f"${price * qty:.2f}"))
                self.update_bill_total()
                return
            
        # Now we can safely compare two integers
        if stock < 1:
            messagebox.showwarning("Stock Alert", f"'{name}' is out of stock.")
            return

        # Add new item to bill (price is now a float and can be formatted)
        self.bill_tree.insert("", "end", values=(name, 1, f"${price:.2f}", f"${price:.2f}"))
        self.update_bill_total()

    def update_bill_total(self):
        total = 0.0
        for item in self.bill_tree.get_children():
            total += float(self.bill_tree.item(item)['values'][3].replace('$', ''))
        self.total_var.set(f"Total: ${total:.2f}")

    def clear_bill(self):
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        self.update_bill_total()

    def checkout(self):
        if not self.bill_tree.get_children():
            messagebox.showerror("Error", "The bill is empty.")
            return
    
        total = float(self.total_var.get().replace('Total: $', ''))
        items_sold = []
    
        # Use a 'with' statement for safer database connection handling
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            # Before committing, check if there is enough stock for the entire transaction
            for item in self.bill_tree.get_children():
                name, qty_str, _, _ = self.bill_tree.item(item)['values']
                qty = int(qty_str) # Convert quantity to int for checking
            
                cursor.execute("SELECT quantity FROM products WHERE name = ?", (name,))
                stock = cursor.fetchone()[0]

                if qty > stock:
                    messagebox.showerror("Checkout Error", f"Not enough stock for '{name}'. Required: {qty}, Available: {stock}.")
                    return # Stop the checkout process

            # If all stock checks pass, proceed with the transaction
            for item in self.bill_tree.get_children():
                name, qty_str, _, _ = self.bill_tree.item(item)['values']
            
                # --- FIX HERE ---
                # Convert the quantity string to an integer for the database operation
                qty = int(qty_str)

                items_sold.append({"name": name, "quantity": qty})
                cursor.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (qty, name))
        
            # Record transaction
            created_at = datetime.datetime.now().isoformat()
            cursor.execute("INSERT INTO transactions (total, created_at, items) VALUES (?, ?, ?)",
                        (total, created_at, json.dumps(items_sold)))
        
            # No need to call conn.commit() explicitly when using a 'with' statement
    
        messagebox.showinfo("Success", "Checkout complete. Transaction recorded.")
        self.clear_bill()
        self.refresh_all_data()
        # --- Analytics Tab ---
    def create_analytics_tab(self):
        self.analytics_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.analytics_frame, text='Analytics')
        
        controls_frame = ttk.Frame(self.analytics_frame)
        controls_frame.pack(pady=10, fill='x')
        
        ttk.Label(controls_frame, text="Time Range:", font=('Helvetica', 12, 'bold')).pack(side='left', padx=10)
        ttk.Button(controls_frame, text="Week", command=lambda: self.update_analytics_chart('week')).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Month", command=lambda: self.update_analytics_chart('month')).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Year", command=lambda: self.update_analytics_chart('year')).pack(side='left', padx=5)
        
        self.chart_frame = ttk.Frame(self.analytics_frame)
        self.chart_frame.pack(expand=True, fill='both')
        
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

    def update_analytics_chart(self, time_range):
        self.ax.clear()

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        end_date = datetime.date.today()
        if time_range == 'week':
            start_date = end_date - datetime.timedelta(days=7)
        elif time_range == 'month':
            start_date = end_date - datetime.timedelta(days=30)
        elif time_range == 'year':
            start_date = end_date - datetime.timedelta(days=365)
        
        cursor.execute("""
            SELECT DATE(created_at), SUM(total)
            FROM transactions
            WHERE DATE(created_at) BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """, (start_date.isoformat(), end_date.isoformat()))
        
        data = cursor.fetchall()
        conn.close()
        
        if data:
            dates = [datetime.datetime.strptime(row[0], '%Y-%m-%d').date() for row in data]
            revenues = [row[1] for row in data]
            
            self.ax.plot(dates, revenues, marker='o', linestyle='-', color='b')
            self.ax.set_title(f"Revenue Over Last {time_range.capitalize()}", fontsize=16)
            self.ax.set_ylabel("Revenue ($)", fontsize=12)
            self.ax.grid(True)
            self.fig.autofmt_xdate()
        else:
            self.ax.text(0.5, 0.5, "No sales data available for this period.",
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=14)
        
        self.canvas.draw()

    # --- AI Assistant Tab ---
    def create_ai_assistant_tab(self):
        self.ai_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.ai_frame, text='AI Assistant')

        chat_frame = ttk.Frame(self.ai_frame)
        chat_frame.pack(expand=True, fill='both', pady=5)

        self.chat_history = tk.Text(chat_frame, state='disabled', wrap='word', height=20, font=('Helvetica', 11))
        scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_history.yview)
        self.chat_history.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.chat_history.pack(expand=True, fill='both')
        
        # Add initial greeting
        self.add_message_to_chat("AI Assistant", "Hello! I'm your AI inventory assistant. Ask me for recommendations based on your sales data.")

        input_frame = ttk.Frame(self.ai_frame)
        input_frame.pack(fill='x', pady=10)
        
        self.ai_input = ttk.Entry(input_frame)
        self.ai_input.pack(side='left', expand=True, fill='x', padx=5)
        self.ai_input.bind("<Return>", self.send_ai_message)
        ttk.Button(input_frame, text="Send", command=self.send_ai_message).pack(side='right')

    def add_message_to_chat(self, sender, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert('end', f"{sender}: {message}\n\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see('end')

    def send_ai_message(self, event=None):
        user_message = self.ai_input.get()
        if not user_message: return

        self.add_message_to_chat("You", user_message)
        self.ai_input.delete(0, 'end')
        
        # --- THIS IS WHERE YOU CONFIGURE THE AI ---
        # 1. Add your OpenRouter API Key here
        API_KEY = "YOUR_OPENROUTER_API_KEY" 
        
        # 2. Specify the model you want to use (e.g., "mistralai/mistral-7b-instruct")
        MODEL_NAME = "MODEL NAME"

        if API_KEY == "YOUR_OPENROUTER_API_KEY":
            self.add_message_to_chat("AI Assistant", "Error: OpenRouter API Key is not configured in the code.")
            return

        # Prepare data for the AI prompt
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, quantity FROM products ORDER BY quantity ASC LIMIT 10")
        low_stock_products = cursor.fetchall()
        cursor.execute("SELECT items FROM transactions ORDER BY created_at DESC LIMIT 50")
        recent_transactions = cursor.fetchall()
        conn.close()

        # Process sales data to find top sellers
        sales_count = {}
        for trans in recent_transactions:
            items = json.loads(trans[0])
            for item in items:
                sales_count[item['name']] = sales_count.get(item['name'], 0) + item['quantity']
        
        top_sellers = sorted(sales_count.items(), key=lambda x: x[1], reverse=True)[:10]

        # Build the system prompt
        system_prompt = f"""You are an expert inventory management AI assistant. Your goal is to provide clear, actionable advice to a shop owner. Analyze the following data and answer the user's question.
        DO NOT create heandings only do simple formating.
        **Inventory & Sales Data Summary:**
        - Low Stock Products (Top 10): {low_stock_products}
        - Top Selling Products (from recent transactions): {top_sellers}

        Based on this data, provide a concise recommendation. Focus on what to restock, what might be overstocked, and potential sales strategies.
        """

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                })
            )
            response.raise_for_status() # Raise an exception for bad status codes
            ai_response = response.json()['choices'][0]['message']['content']
            self.add_message_to_chat("AI Assistant", ai_response.strip())

        except requests.exceptions.RequestException as e:
            self.add_message_to_chat("AI Assistant", f"Error connecting to AI service: {e}")
        except Exception as e:
            self.add_message_to_chat("AI Assistant", f"An unexpected error occurred: {e}")

    # --- Transactions Tab ---
    def create_transactions_tab(self):
        self.transactions_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.transactions_frame, text='Transactions')
        controls = ttk.Frame(self.transactions_frame)

        controls.pack(fill='x', pady=5)
        ttk.Button(controls, text="Refresh", command=self.load_transactions).pack(side='left', padx=5)
        ttk.Button(controls, text="View Details", command=self.view_transaction_details).pack(side='left', padx=5)
        ttk.Button(controls, text="Delete Selected", command=self.delete_transaction).pack(side='left', padx=5)

        tree_frame = ttk.Frame(self.transactions_frame)
        tree_frame.pack(expand=True, fill='both', pady=10)

        # Columns: ID, Total, Created At, Items Count
        self.trans_tree = ttk.Treeview(tree_frame, columns=("ID", "Total", "Created At", "Items Count"), show='headings')
        self.trans_tree.heading("ID", text="ID")
        self.trans_tree.heading("Total", text="Total")
        self.trans_tree.heading("Created At", text="Created At")
        self.trans_tree.heading("Items Count", text="Items Count")
        self.trans_tree.pack(expand=True, fill='both', side='left')

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Initial load
        self.load_transactions()

    def load_transactions(self):
        # Clear existing rows
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, total, created_at, items FROM transactions ORDER BY created_at DESC")
        for row in cursor.fetchall():
            tid, total, created_at, items_json = row
            try:
                items = json.loads(items_json)
                items_count = sum(it.get("quantity", 0) for it in items)
            except Exception:
                items_count = ""
            self.trans_tree.insert("", "end", values=(tid, f"${total:.2f}", created_at, items_count))
        conn.close()

    def view_transaction_details(self):
        sel = self.trans_tree.focus()
        if not sel:
            messagebox.showerror("Error", "Please select a transaction to view.")
            return

        tid = self.trans_tree.item(sel)['values'][0]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT total, created_at, items FROM transactions WHERE id = ?", (tid,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Error", "Transaction not found.")
            return

        total, created_at, items_json = row
        try:
            items = json.loads(items_json)
        except Exception:
            items = []

        details = f"Transaction ID: {tid}\nTotal: ${total:.2f}\nDate: {created_at}\n\nItems:\n"
        for it in items:
            name = it.get("name", "Unknown")
            qty = it.get("quantity", 0)
            details += f"- {name}  x{qty}\n"

        # show in a simple messagebox (could be replaced with a larger Toplevel if desired)
        messagebox.showinfo("Transaction Details", details)

    def delete_transaction(self):
        sel = self.trans_tree.focus()
        if not sel:
            messagebox.showerror("Error", "Please select a transaction to delete.")
            return

        tid = self.trans_tree.item(sel)['values'][0]
        if not messagebox.askyesno("Confirm", f"Delete transaction {tid}? This will not modify product stock."):
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tid,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", f"Transaction {tid} deleted.")
        self.load_transactions()
# --- 3. MAIN EXECUTION ---
# This block runs when the script is executed.
if __name__ == "__main__":
    setup_database()  # Ensure the database and tables exist
    
    root = tk.Tk()
    app = InventoryApp(root)

    root.mainloop()
