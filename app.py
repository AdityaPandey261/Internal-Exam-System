from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

DB_NAME = 'database.db'

# -------------------- DATABASE SETUP --------------------
def init_db():
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            reg_no TEXT,
            student_class TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            course TEXT,
            total_questions INTEGER,
            marks_per_question INTEGER
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            question_text TEXT,
            option1 TEXT,
            option2 TEXT,
            option3 TEXT,
            option4 TEXT,
            correct_option INTEGER
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            exam_id INTEGER,
            score INTEGER,
            date_taken TEXT
        )''')

        conn.commit()

# Initialize DB and insert default teacher if not exists
init_db()

with sqlite3.connect(DB_NAME, timeout=10) as conn:
    c = conn.cursor()
    c.execute("SELECT * FROM teachers WHERE username = ?", ("admin",))
    if not c.fetchone():
        c.execute("INSERT INTO teachers (username, password) VALUES (?, ?)", ("admin", "admin123"))
        conn.commit()
        print("Default teacher user added!")

# -------------------- STUDENT ROUTES --------------------

@app.route('/')
def home():
    return render_template('student_register.html')

@app.route('/register_student', methods=['POST'])
def register_student():
    name = request.form['name']
    email = request.form['email']
    reg_no = request.form['reg_no']
    student_class = request.form['class']

    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO students (name, email, reg_no, student_class) VALUES (?, ?, ?, ?)",
                  (name, email, reg_no, student_class))
        student_id = c.lastrowid
        conn.commit()

    session['student_id'] = student_id
    return redirect('/exams')

@app.route('/exams')
def exams():
    if 'student_id' not in session:
        flash("Please register/login first.")
        return redirect('/')

    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM exams")
        exams = c.fetchall()

    return render_template('student_exam.html', exams=exams)

@app.route('/start_exam/<int:exam_id>')
def start_exam(exam_id):
    if 'student_id' not in session:
        flash("Please register/login first.")
        return redirect('/')

    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM questions WHERE exam_id=?", (exam_id,))
        questions = c.fetchall()

    return render_template('take_exam.html', questions=questions, exam_id=exam_id)

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'student_id' not in session:
        flash("Please register/login first.")
        return redirect('/')

    exam_id = int(request.form['exam_id'])
    student_id = session.get('student_id')

    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("SELECT id, correct_option FROM questions WHERE exam_id=?", (exam_id,))
        questions = c.fetchall()

        score = 0
        for q in questions:
            qid = str(q[0])
            correct = str(q[1])
            selected = request.form.get(f'q{qid}')
            if selected == correct:
                score += 1

        c.execute("INSERT INTO results (student_id, exam_id, score, date_taken) VALUES (?, ?, ?, ?)",
                  (student_id, exam_id, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    return render_template('student_result.html', score=score, total=len(questions))

# -------------------- TEACHER ROUTES --------------------

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM teachers WHERE username=? AND password=?", (username, password))
            teacher = c.fetchone()

        if teacher:
            session['teacher'] = username
            return redirect('/teacher_dashboard')
        else:
            flash("Invalid credentials")
            return redirect('/teacher_login')

    return render_template('teacher_login.html')

@app.route('/teacher_logout')
def teacher_logout():
    session.pop('teacher', None)
    return redirect('/teacher_login')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'teacher' not in session:
        return redirect('/teacher_login')

    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM exams")
        exams = c.fetchall()

    return render_template('teacher_dashboard.html', exams=exams)

@app.route('/view_exams')
def view_exams():
    if 'teacher' not in session:
        return redirect('/teacher_login')

    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM exams")
        exams = c.fetchall()

    return render_template('view_exams.html', exams=exams)


@app.route('/create_exam', methods=['GET', 'POST'])
def create_exam():
    if 'teacher' not in session:
        return redirect('/teacher_login')

    if request.method == 'POST':
        subject = request.form['subject']
        course = request.form['course']
        total_questions = int(request.form['total_questions'])
        marks_per_question = int(request.form['marks_per_question'])

        with sqlite3.connect(DB_NAME, timeout=10) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO exams (subject, course, total_questions, marks_per_question) VALUES (?, ?, ?, ?)",
                      (subject, course, total_questions, marks_per_question))
            exam_id = c.lastrowid
            conn.commit()

        return redirect(f'/add_questions/{exam_id}')

    return render_template('create_exam.html')

@app.route('/add_questions/<int:exam_id>', methods=['GET', 'POST'])
def add_questions(exam_id):
    if 'teacher' not in session:
        return redirect('/teacher_login')

    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
        exam = c.fetchone()

        if not exam:
            return "Exam not found", 404

        if request.method == 'POST':
            question_text = request.form['question_text']
            option1 = request.form['option1']
            option2 = request.form['option2']
            option3 = request.form['option3']
            option4 = request.form['option4']
            correct_option = int(request.form['correct_option'])

            c.execute('''
                INSERT INTO questions (exam_id, question_text, option1, option2, option3, option4, correct_option)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (exam_id, question_text, option1, option2, option3, option4, correct_option))

            conn.commit()

    exam_dict = {
        'id': exam[0],
        'subject': exam[1],
        'course': exam[2],
        'total_questions': exam[3],
        'marks_per_question': exam[4]
    }
    return render_template('add_questions.html', exam=exam_dict)

@app.route('/view_results')
def view_results():
    if 'teacher' not in session:
        return redirect('/teacher_login')

    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        query = '''
        SELECT s.name AS student_name, s.email, e.subject, e.course, r.score, r.date_taken
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        JOIN students s ON r.student_id = s.id
        ORDER BY r.date_taken DESC
        '''
        c.execute(query)
        results = c.fetchall()

    return render_template('view_results.html', results=results)

# -------------------- RUN FLASK --------------------

if __name__ == '__main__':
    app.run(debug=True)
