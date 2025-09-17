import sqlite3

# Connect to the database
conn = sqlite3.connect('case_management.db')
cursor = conn.cursor()

# Create the 'cases' table with all required columns
cursor.execute('''
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    case_title TEXT NOT NULL,
    department TEXT,
    status TEXT,
    assigned_to TEXT,
    date_opened TEXT,
    date_closed TEXT
)
''')

conn.commit()
conn.close()

print("✅ 'cases' table created successfully.")
