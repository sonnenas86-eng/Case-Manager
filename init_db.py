from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

# Connect to a new database file
conn = sqlite3.connect('case_management.db')

# Create the 'cases' table
conn.execute('''
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_name TEXT NOT NULL,
    case_type TEXT NOT NULL,
    case_number TEXT,
    lawyer_assigned TEXT,
    status TEXT,
    next_hearing DATE,
    date_opened TEXT,
    date_closed TEXT
)
''')

# Create the 'documents' table
conn.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number INTEGER,
    filename TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_number) REFERENCES cases (case_number)
)
""")

# File movements table
conn.execute("""
CREATE TABLE IF NOT EXISTS file_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number TEXT NOT NULL,
    from_dept TEXT NOT NULL,
    to_dept TEXT NOT NULL,
    remarks TEXT,
    moved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_number) REFERENCES cases (case_number)
)
""")
# Create the 'users' table
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ Fresh 'case_management.db' created successfully.")
