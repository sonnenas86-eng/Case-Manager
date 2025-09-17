from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecurekey123'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('case_management.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'jpg', 'png'}

def get_current_holder(case_number):
    conn = get_db_connection()
    result = conn.execute(
        'SELECT to_dept FROM file_movements WHERE case_number = ? ORDER BY moved_at DESC LIMIT 1',
        (case_number,)
    ).fetchone()
    conn.close()
    return result['to_dept'] if result else 'Not yet moved'

from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials. Try again."

    return render_template('login.html')


@app.route('/')
def home():
    # If user is logged in, show dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    # Otherwise, show login page
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        conn = get_db_connection()

        total = conn.execute('SELECT COUNT(*) FROM cases').fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM cases WHERE status LIKE '%Pending%'").fetchone()[0]
        sentenced = conn.execute("SELECT COUNT(*) FROM cases WHERE status LIKE '%Sentenced%'").fetchone()[0]
        adjourned = conn.execute("SELECT COUNT(*) FROM cases WHERE status LIKE '%Adjourned%'").fetchone()[0]
        trial = conn.execute("SELECT COUNT(*) FROM cases WHERE status LIKE '%Trial Ongoing%'").fetchone()[0]

        conn.close()
        return render_template('dashboard.html',
                               total=total,
                               pending=pending,
                               sentenced=sentenced,
                               adjourned=adjourned,
                               trial=trial)
    else:
        return redirect(url_for('login'))



@app.route('/cases')
def case_list():
    if 'user' in session:
        conn = get_db_connection()
        cases = conn.execute('SELECT * FROM cases').fetchall()
        user = conn.execute('SELECT role FROM users WHERE username = ?', (session['user'],)).fetchone()
        conn.close()
        return render_template('case_list.html', cases=cases, user_role=user['role'] if user else None)
    else:
        return redirect(url_for('login'))

    
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cases = conn.execute('SELECT case_number, case_title FROM cases').fetchall()

    if request.method == 'POST':
        case_number = request.form.get('case_number')
        file = request.files.get('file')

        if not case_number or not file:
            return "Missing case number or file."

        if file.filename == '':
            return "No selected file."

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            conn.execute(
                'INSERT INTO documents (case_number, filename) VALUES (?, ?)',
                (case_number, filename)
            )
            conn.commit()
            conn.close()
            return f"✅ File '{filename}' uploaded and linked to case number {case_number}."

    conn.close()
    return render_template('upload.html', cases=cases)

@app.route('/cases/status/<status>')
def filter_by_status(status):
    if 'user' in session:
        conn = get_db_connection()
        cases = conn.execute(
            "SELECT * FROM cases WHERE status LIKE ?",
            (f"%{status}%",)
        ).fetchall()
        conn.close()
        return render_template('case_list.html', cases=cases, filter=status)
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        case_name = request.form['case_name']
        case_type = request.form['case_type']
        case_number = request.form['case_number']
        lawyer_assigned = request.form['lawyer_assigned']
        status = request.form['status']
        next_hearing = request.form['next_hearing']
          
        conn = get_db_connection()
        (conn.execute('INSERT INTO cases (case_name, case_type, case_number, lawyer_assigned, status, next_hearing) VALUES (?, ?, ?, ?, ?, ?)',
             (case_name, case_type, case_number, lawyer_assigned, status, next_hearing)))

        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('register.html')

@app.route('/file-tracking')
def file_tracking():
    conn = get_db_connection()
    cases = conn.execute('SELECT case_number, case_title FROM cases').fetchall()
    tracking_data = []

    for case in cases:
        latest = conn.execute(
            'SELECT to_dept, moved_at FROM file_movements WHERE case_number = ? ORDER BY moved_at DESC LIMIT 1',
            (case['case_number'],)
        ).fetchone()

        tracking_data.append({
            'case_number': case['case_number'],
            'case_title': case['case_title'],
            'current_holder': latest['to_dept'] if latest else 'Not yet moved',
            'last_moved': latest['moved_at'] if latest else '—'
        })

    conn.close()
    return render_template('file_tracking.html', tracking=tracking_data)


@app.route('/track', methods=('GET', 'POST'))
def track():
    if request.method == 'POST':
        case_number = request.form['case_number']
        from_dept = request.form['from_dept']
        to_dept = request.form['to_dept']
        remarks = request.form['remarks']

        conn = get_db_connection()
        conn.execute('INSERT INTO file_movements (case_number, from_dept, to_dept, remarks) VALUES (?, ?, ?, ?)',
                     (case_number, from_dept, to_dept, remarks))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('track.html')

@app.route('/search_case')
def search_case():
    query = request.args.get('query')
    conn = get_db_connection()
    results = conn.execute("SELECT * FROM cases WHERE case_number LIKE ?", ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('search_results.html', results=results, query=query)


@app.route('/history/<case_number>')
def movement_history(case_number):
    conn = get_db_connection()
    movements = conn.execute(
        'SELECT from_dept, to_dept, remarks, moved_at FROM file_movements WHERE case_number = ? ORDER BY moved_at DESC',
        (case_number,)
    ).fetchall()
    conn.close()
    return render_template('history.html', case_number=case_number, movements=movements)

from werkzeug.security import generate_password_hash

@app.route('/register-user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                         (username, password_hash, role))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "❌ Username already exists."
        conn.close()
        return "✅ User registered successfully!"
    
    return render_template('register_user.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

