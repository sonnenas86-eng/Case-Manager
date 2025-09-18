import sqlite3

conn = sqlite3.connect('case_management.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(cases)")
columns = cursor.fetchall()

for col in columns:
    print(col)

conn.close()
