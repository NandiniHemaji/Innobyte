import sqlite3
import getpass
import datetime

# Database Setup
def init_db():
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        type TEXT,
                        category TEXT,
                        amount REAL,
                        date TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        category TEXT,
                        amount REAL,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )''')
    conn.commit()
    conn.close()

# User Registration and Authentication
def register():
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    finally:
        conn.close()

def login():
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        print("Login successful!")
        return user[0]
    else:
        print("Invalid credentials.")
        return None

# Income and Expense Tracking
def add_transaction(user_id):
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    t_type = input("Enter type (Income/Expense): ")
    category = input("Enter category: ")
    amount = float(input("Enter amount: "))
    date = input("Enter date (YYYY-MM-DD) or leave blank for today: ") or datetime.date.today().isoformat()
    cursor.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, t_type, category, amount, date))
    conn.commit()
    conn.close()
    print("Transaction added successfully.")

def view_transactions(user_id):
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    cursor.execute("SELECT type, category, amount, date FROM transactions WHERE user_id = ?", (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    for t in transactions:
        print(f"{t[0]} | {t[1]} | {t[2]} | {t[3]}")

# Financial Reports
def generate_report(user_id):
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY type", (user_id,))
    summary = cursor.fetchall()
    income = sum([s[1] for s in summary if s[0].lower() == 'income'])
    expense = sum([s[1] for s in summary if s[0].lower() == 'expense'])
    savings = income - expense
    print(f"Total Income: {income}")
    print(f"Total Expense: {expense}")
    print(f"Savings: {savings}")
    conn.close()

# Budgeting
def set_budget(user_id):
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    category = input("Enter category: ")
    amount = float(input("Enter budget amount: "))
    cursor.execute("INSERT INTO budgets (user_id, category, amount) VALUES (?, ?, ?)", (user_id, category, amount))
    conn.commit()
    conn.close()
    print("Budget set successfully.")

def check_budget(user_id):
    conn = sqlite3.connect('finance_manager.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, amount FROM budgets WHERE user_id = ?", (user_id,))
    budgets = cursor.fetchall()
    for budget in budgets:
        category, limit = budget
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND category = ? AND type = 'Expense'",
                       (user_id, category))
        spent = cursor.fetchone()[0] or 0
        if spent > limit:
            print(f"Budget exceeded for {category}! Spent: {spent}, Limit: {limit}")
    conn.close()

# Main Menu
def main():
    init_db()
    print("Welcome to Personal Finance Manager")
    while True:
        print("1. Register\n2. Login\n3. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            register()
        elif choice == '2':
            user_id = login()
            if user_id:
                while True:
                    print("1. Add Transaction\n2. View Transactions\n3. Generate Report\n4. Set Budget\n5. Check Budget\n6. Logout")
                    user_choice = input("Enter choice: ")
                    if user_choice == '1':
                        add_transaction(user_id)
                    elif user_choice == '2':
                        view_transactions(user_id)
                    elif user_choice == '3':
                        generate_report(user_id)
                    elif user_choice == '4':
                        set_budget(user_id)
                    elif user_choice == '5':
                        check_budget(user_id)
                    elif user_choice == '6':
                        break
                    else:
                        print("Invalid choice.")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
