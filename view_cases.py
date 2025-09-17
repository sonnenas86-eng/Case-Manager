import sqlite3

conn = sqlite3.connect('case_management.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM cases")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
