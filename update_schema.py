import sqlite3

conn = sqlite3.connect('case_management.db')
cursor = conn.cursor()

cursor.execute("ALTER TABLE cases ADD COLUMN court TEXT")
cursor.execute("ALTER TABLE cases ADD COLUMN presiding_judge TEXT")
cursor.execute("ALTER TABLE cases ADD COLUMN case_summary TEXT")

conn.commit()
conn.close()

print("Columns added successfully.")
