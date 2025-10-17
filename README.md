# Stock-Desk
A simple and easy to use store product manager.

# Stock-Desk: Desktop Inventory Management System

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Built with](https://img.shields.io/badge/Built%20with-Tkinter-red)

A complete, self-contained desktop application for managing shop inventory, built with Python and Tkinter. This application provides an intuitive graphical user interface (GUI) for small business owners to track products, process sales, and gain insights from their data without needing an internet connection (except for the AI Assistant feature).

---

## Screenshot

<img width="1919" height="1132" alt="image" src="https://github.com/user-attachments/assets/3f0d6f4b-63ef-4676-94cb-c085dab64fb5" />



---

## Features

The application is organized into a clean, tab-based interface with the following modules:

-   **Dashboard:** An at-a-glance overview of key business metrics, including:
    -   Total number of unique products.
    -   Count of low-stock items.
    -   Total number of sales transactions.
    -   Total revenue generated.
-   **Product Management:** Full CRUD (Create, Read, Update, Delete) functionality for your inventory.
    -   Add new products with a unique SKU, name, price, and quantity.
    -   View all products in a sortable list.
    -   Delete products from the inventory.
-   **Billing / Point of Sale (POS):** A simple and efficient interface for processing customer sales.
    -   Live search for products by SKU or name.
    -   Add items to a bill, which automatically calculates totals.
    -   Checkout process that records the transaction and updates product stock levels.
-   **Transaction History:** A detailed log of all past sales.
    -   View a list of all transactions with ID, date, and total.
    -   View detailed information for any selected transaction, including all items sold.
    -   Delete transaction records (note: this does not restock items).
-   **Sales Analytics:** Visualize your business performance with dynamic charts.
    -   Generate a line graph of revenue over custom time ranges (Week, Month, Year).
    -   Powered by Matplotlib for clear data representation.
-   **AI-Powered Assistant:** Get smart inventory recommendations.
    -   Connects to the OpenRouter API to analyze your current low-stock and top-selling items.
    -   Ask questions to get actionable advice on restocking and sales strategies.

---

## Tech Stack

-   **Language:** Python 3
-   **GUI Framework:** Tkinter / `ttk`
-   **Database:** SQLite 3 (self-contained, no external database server required)
-   **Charting Library:** Matplotlib
-   **API Communication:** `requests` (for the AI Assistant)

---

## Setup and Installation

Follow these steps to get the application running on your local machine.

#### 1. Prerequisites
-   Python 3.8 or newer installed on your system.
-   Git installed on your system.

#### 2. Clone the Repository
```bash
git clone https://github.com/HamzaKhan216/Stock-Desk.git
cd Stock-Desk
```
#### 3. Create a Virtual Environment (Recommended)

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
### 4. Install Dependencies
This project uses a requirements.txt file to manage dependencies. Install them using pip:
```bash
pip install -r requirements.txt
```
### Usage
Run the Application
Execute the main Python script from your terminal:
```bash
python main.py
```
The application window will open, and a database file named inventory.db will be automatically created in the same directory if it doesn't exist.
Configure the AI Assistant (Optional)
To use the AI Assistant tab, you must add your OpenRouter API key.
Open the main.py file.
Navigate to the send_ai_message method (around line 500).
Replace the placeholder value for the API_KEY variable with your own key:
code
## Python
```bash
# In the send_ai_message method...
API_KEY = "YOUR_OPENROUTER_API_KEY" # <-- PASTE YOUR KEY HERE
```
Creating a Standalone Executable (.exe)
This script is prepared for packaging into a single executable file using PyInstaller, allowing you to run it on any Windows computer without needing to install Python or any dependencies.
### 1. Install PyInstaller
```bash
pip install pyinstaller
```
### 2. Run the PyInstaller Command
Navigate to the project directory in your terminal and run the following command:
```bash
pyinstaller --onefile --windowed main.py
```
-  --onefile: Bundles everything into a single .exe file.
-  --windowed: Prevents the command prompt (console) from opening when you run the application.
### 3. Find Your Executable
PyInstaller will create a few folders. Your final application will be located in the dist folder. You can share this single main.exe file with others.
