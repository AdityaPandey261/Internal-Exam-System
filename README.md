# Internal-Exam-System
A full-stack web application to manage online internal exams. It allows **students** to register and take exams, and **teachers** to create, schedule, and evaluate tests.

---

## 👨‍🏫 Key Features

### 🧑‍🎓 For Students:
- ✅ Register/Login
- 📝 Attempt multiple-choice exams
- 📈 Instant result after submission
- 📚 View exam history

### 👩‍🏫 For Teachers:
- 🖊️ Create & manage exams
- ➕ Add/edit/delete questions
- 🧮 Define total marks & time limit
- 📊 View student performances

---

## 🔧 Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite3
- **Templating**: Jinja2

---

## 📂 Project Structure

internal_exam_system/
├── app.py
├── database.db
├── static/
│ └── css/
├── templates/
│ ├── login.html
│ ├── register.html
│ ├── dashboard_student.html
│ ├── dashboard_teacher.html
│ ├── create_exam.html
│ ├── take_exam.html
│ └── view_results.html
└── README.md

---

## ⚙️ How to Run

```bash
git clone https://github.com/yourusername/internal_exam_system.git
cd internal_exam_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

# Install requirements
pip install Flask

# Run the app
python app.py
Visit: http://127.0.0.1:5000/
