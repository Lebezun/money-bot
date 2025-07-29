import sqlite3
from datetime import datetime, date

DB_NAME = "expenses.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)
        conn.commit()

def add_expense(category, amount):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)",
                       (category, amount, datetime.now().date().isoformat()))
        conn.commit()

def get_total_by_period(start_date, end_date):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?
        """, (start_date.isoformat(), end_date.isoformat()))
        result = cursor.fetchone()[0]
        return result or 0

def get_biggest_category():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) as total FROM expenses
            GROUP BY category ORDER BY total DESC LIMIT 1
        """)
        result = cursor.fetchone()
        return result if result else ("Немає витрат", 0)

def get_all_expenses():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) FROM expenses GROUP BY category
        """)
        return cursor.fetchall()

def get_today_expenses_grouped():
    today = date.today().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) FROM expenses 
            WHERE date = ? GROUP BY category
        """, (today,))
        return cursor.fetchall()

def clear_today_expenses():
    today = date.today().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE date = ?", (today,))
        conn.commit()
