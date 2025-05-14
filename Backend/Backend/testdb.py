from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
for i in range(1, 101):
    email = f"test{i}@example.com"
    password = generate_password_hash("password123")
    cursor.execute(
        "INSERT INTO users (first_name, last_name, email, password, role, is_approved, is_blocked) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"Test{i}", "User", email, password, "Employee", 1, 0)
    )
conn.commit()
conn.close()