from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB = "attendance.db"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        course TEXT NOT NULL,
        semester TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        att_date TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
        UNIQUE(student_id, att_date),
        FOREIGN KEY(student_id) REFERENCES students(id)
    )""")
    con.commit()
    con.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    con = db()
    total = con.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    today = date.today().isoformat()
    present = con.execute("SELECT COUNT(*) FROM attendance WHERE att_date=? AND status='Present'", (today,)).fetchone()[0]
    absent = con.execute("SELECT COUNT(*) FROM attendance WHERE att_date=? AND status='Absent'", (today,)).fetchone()[0]
    marked = present + absent
    percentage = round((present / marked) * 100, 1) if marked else 0
    recent = con.execute("""SELECT s.roll_no, s.name, a.status, a.att_date
        FROM attendance a JOIN students s ON s.id=a.student_id
        ORDER BY a.att_date DESC, a.id DESC LIMIT 6""").fetchall()
    con.close()
    return render_template("dashboard.html", total=total, present=present, absent=absent,
                           percentage=percentage, recent=recent, today=today)

@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    con = db()
    if request.method == "POST":
        roll = request.form.get("roll_no", "").strip()
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()
        semester = request.form.get("semester", "").strip()
        if roll and name and course and semester:
            try:
                con.execute("INSERT INTO students(roll_no,name,course,semester) VALUES(?,?,?,?)",
                            (roll, name, course, semester))
                con.commit()
                flash("Student added successfully.", "success")
            except sqlite3.IntegrityError:
                flash("This roll number already exists.", "error")
        else:
            flash("Please fill all fields.", "error")
        con.close()
        return redirect(url_for("students"))
    search = request.args.get("q", "").strip()
    rows = con.execute("""SELECT * FROM students
        WHERE roll_no LIKE ? OR name LIKE ? ORDER BY id DESC""",
        (f"%{search}%", f"%{search}%")).fetchall()
    con.close()
    return render_template("students.html", students=rows, q=search)

@app.route("/students/delete/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    con = db()
    con.execute("DELETE FROM attendance WHERE student_id=?", (student_id,))
    con.execute("DELETE FROM students WHERE id=?", (student_id,))
    con.commit()
    con.close()
    flash("Student deleted.", "success")
    return redirect(url_for("students"))

@app.route("/attendance", methods=["GET", "POST"])
@login_required
def mark_attendance():
    con = db()
    selected_date = request.values.get("att_date", date.today().isoformat())
    students_list = con.execute("SELECT * FROM students ORDER BY roll_no").fetchall()
    if request.method == "POST":
        selected_date = request.form.get("att_date", date.today().isoformat())
        for student in students_list:
            status = request.form.get(f"status_{student['id']}")
            if status in ("Present", "Absent"):
                con.execute("""INSERT INTO attendance(student_id,att_date,status) VALUES(?,?,?)
                    ON CONFLICT(student_id,att_date) DO UPDATE SET status=excluded.status""",
                    (student["id"], selected_date, status))
        con.commit()
        flash("Attendance saved successfully.", "success")
        con.close()
        return redirect(url_for("mark_attendance", att_date=selected_date))
    existing = con.execute("SELECT student_id,status FROM attendance WHERE att_date=?",
                           (selected_date,)).fetchall()
    statuses = {r["student_id"]: r["status"] for r in existing}
    con.close()
    return render_template("attendance.html", students=students_list, selected_date=selected_date, statuses=statuses)

@app.route("/records")
@login_required
def records():
    con = db()
    selected_date = request.args.get("att_date", "")
    query = """SELECT a.att_date, s.roll_no, s.name, s.course, a.status
               FROM attendance a JOIN students s ON s.id=a.student_id"""
    params = []
    if selected_date:
        query += " WHERE a.att_date=?"
        params.append(selected_date)
    query += " ORDER BY a.att_date DESC, s.roll_no"
    rows = con.execute(query, params).fetchall()
    con.close()
    return render_template("records.html", records=rows, selected_date=selected_date)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
