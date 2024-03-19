# File path: /path/to/your/initialize_users.py

import sqlite3
from utility_modules.password_handling import hash_password

# Create a list of tuples containing usernames and plaintext passwords
users = [
    ("Sikos Mark", "Neaddfel2")
    # Add more users as needed
]

# Connect to the SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash BLOB NOT NULL
)
""")

# Insert users into the database with hashed passwords
for username, plaintext_password in users:
    hashed_password = hash_password(plaintext_password)
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))

# Commit changes and close the connection
conn.commit()
conn.close()
