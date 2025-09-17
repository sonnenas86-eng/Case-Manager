import sqlite3

# Connect to the correct database
conn = sqlite3.connect('case_management.db')
cursor = conn.cursor()

# Add the missing column
cursor.execute("ALTER TABLE cases ADD COLUMN reference TEXT")

# Save the changes
conn.commit()
conn.close()

print("Column 'reference' added successfully.")

