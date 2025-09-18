import sqlite3

# Connect to your database
conn = sqlite3.connect('case_management.db')  # Make sure this is the correct file name
cursor = conn.cursor()

# Confirm the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables in DB:")
print(cursor.fetchall())

# Get column info
cursor.execute("PRAGMA table_info(cases)")
columns = cursor.fetchall()

print("\nStructure of 'cases' table:")
for col in columns:
    print(col)
