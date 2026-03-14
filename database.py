import sqlite3
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

DB_PATH = "ecommerce.db"

def create_database():
    """Create and populate the e-commerce database with realistic data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- CUSTOMERS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            city TEXT,
            state TEXT,
            age INTEGER,
            gender TEXT,
            signup_date TEXT,
            loyalty_tier TEXT
        )
    """)

    cities = [("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bengaluru", "Karnataka"),
              ("Hyderabad", "Telangana"), ("Chennai", "Tamil Nadu"), ("Pune", "Maharashtra"),
              ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan"),
              ("Surat", "Gujarat")]
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    genders = ["Male", "Female"]
    first_names = ["Aarav", "Vivaan", "Aditya", "Priya", "Sneha", "Ritika", "Rohit",
                   "Ananya", "Karan", "Neha", "Arjun", "Pooja", "Rahul", "Sanya", "Vikram"]
    last_names = ["Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Joshi",
                  "Mehta", "Nair", "Reddy", "Rao", "Bose", "Das", "Chopra", "Iyer"]

    random.seed(42)
    customers = []
    for i in range(1, 501):
        city, state = random.choice(cities)
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"user{i}@email.com"
        age = random.randint(18, 65)
        gender = random.choice(genders)
        days_ago = random.randint(30, 1000)
        signup_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        tier = random.choice(tiers)
        customers.append((i, name, email, city, state, age, gender, signup_date, tier))

    cursor.executemany("INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?,?,?,?,?)", customers)

    # --- PRODUCTS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            brand TEXT,
            price REAL,
            stock INTEGER,
            rating REAL
        )
    """)

    products_data = [
        (1, "iPhone 15", "Electronics", "Apple", 79999, 50, 4.8),
        (2, "Samsung Galaxy S24", "Electronics", "Samsung", 69999, 80, 4.6),
        (3, "OnePlus 12", "Electronics", "OnePlus", 49999, 120, 4.5),
        (4, "MacBook Air M2", "Laptops", "Apple", 114999, 30, 4.9),
        (5, "Dell XPS 15", "Laptops", "Dell", 89999, 25, 4.7),
        (6, "Sony WH-1000XM5", "Audio", "Sony", 24999, 200, 4.8),
        (7, "AirPods Pro", "Audio", "Apple", 19999, 150, 4.7),
        (8, "Nike Air Max", "Footwear", "Nike", 8999, 300, 4.4),
        (9, "Adidas Ultraboost", "Footwear", "Adidas", 9999, 250, 4.5),
        (10, "Levi's 511 Jeans", "Clothing", "Levi's", 3999, 500, 4.3),
        (11, "Allen Solly Shirt", "Clothing", "Allen Solly", 1999, 600, 4.2),
        (12, "Instant Pot", "Kitchen", "Instant Pot", 7999, 100, 4.6),
        (13, "Philips Air Fryer", "Kitchen", "Philips", 5999, 150, 4.5),
        (14, "Kindle Paperwhite", "Books & E-readers", "Amazon", 11999, 200, 4.7),
        (15, "Fitbit Charge 6", "Wearables", "Fitbit", 14999, 180, 4.3),
        (16, "iPad Air", "Electronics", "Apple", 59999, 60, 4.8),
        (17, "Boat Airdopes 141", "Audio", "Boat", 1299, 1000, 4.1),
        (18, "Puma RS-X", "Footwear", "Puma", 6999, 280, 4.2),
        (19, "Wildcraft Backpack", "Accessories", "Wildcraft", 2499, 400, 4.4),
        (20, "Prestige Cooker", "Kitchen", "Prestige", 2999, 350, 4.5),
    ]
    cursor.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,?,?)", products_data)

    # --- ORDERS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            total_amount REAL,
            status TEXT,
            payment_method TEXT,
            city TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)

    statuses = ["Delivered", "Delivered", "Delivered", "Shipped", "Processing", "Cancelled", "Returned"]
    payments = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]

    orders = []
    order_items = []
    order_id = 1

    for customer_id in range(1, 501):
        num_orders = random.randint(1, 8)
        for _ in range(num_orders):
            days_ago = random.randint(1, 365)
            order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            status = random.choice(statuses)
            payment = random.choice(payments)

            # Pick 1-4 products
            num_items = random.randint(1, 4)
            selected_products = random.sample(products_data, num_items)
            total = sum(p[4] * random.randint(1, 3) for p in selected_products)

            customer_city = customers[customer_id - 1][3]
            orders.append((order_id, customer_id, order_date, round(total, 2), status, payment, customer_city))

            for prod in selected_products:
                qty = random.randint(1, 3)
                order_items.append((order_id, prod[0], qty, prod[4]))

            order_id += 1

    cursor.executemany("INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?,?)", orders)

    # --- ORDER ITEMS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    cursor.executemany("INSERT OR IGNORE INTO order_items VALUES (?,?,?,?)", order_items)

    conn.commit()
    conn.close()
    print(f"✅ Database created with {len(orders)} orders, 500 customers, 20 products")

def get_schema():
    """Return the database schema as a string for the LLM prompt."""
    schema = """
DATABASE SCHEMA (SQLite):

TABLE: customers
- customer_id (INTEGER, PRIMARY KEY)
- name (TEXT)
- email (TEXT)  
- city (TEXT)
- state (TEXT)
- age (INTEGER)
- gender (TEXT)
- signup_date (TEXT, format: YYYY-MM-DD)
- loyalty_tier (TEXT: Bronze/Silver/Gold/Platinum)

TABLE: products
- product_id (INTEGER, PRIMARY KEY)
- product_name (TEXT)
- category (TEXT: Electronics/Laptops/Audio/Footwear/Clothing/Kitchen/Wearables/Accessories/Books & E-readers)
- brand (TEXT)
- price (REAL, in INR)
- stock (INTEGER)
- rating (REAL, 0-5)

TABLE: orders
- order_id (INTEGER, PRIMARY KEY)
- customer_id (INTEGER, FK → customers)
- order_date (TEXT, format: YYYY-MM-DD)
- total_amount (REAL, in INR)
- status (TEXT: Delivered/Shipped/Processing/Cancelled/Returned)
- payment_method (TEXT: UPI/Credit Card/Debit Card/Net Banking/Cash on Delivery)
- city (TEXT)

TABLE: order_items
- order_id (INTEGER, FK → orders)
- product_id (INTEGER, FK → products)
- quantity (INTEGER)
- unit_price (REAL, in INR)

RELATIONSHIPS:
- orders.customer_id → customers.customer_id
- order_items.order_id → orders.order_id
- order_items.product_id → products.product_id
"""
    return schema

def run_query(sql: str):
    """Execute SQL and return results as a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        conn.close()
        return None, str(e)

if __name__ == "__main__":
    create_database()
