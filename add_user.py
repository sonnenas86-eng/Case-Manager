import sqlite3
from werkzeug.security import generate_password_hash

# Define your admin credentials
username = 'admin'
password = 'admin123'

# Hash the password
password_hash = generate_password_hash(password)

# Connect to the database
conn = sqlite3.connect('case_management.db')

# Insert the user
conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
conn.commit()
conn.close()

print("✅ Admin user added securely.")
