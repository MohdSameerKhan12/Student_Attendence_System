# Student Attendance Management System

A mini-project built using Python Flask, SQLite, HTML and CSS.

## Features
- Admin login
- Dashboard with student count and today's attendance summary
- Add, search and delete students
- Mark or update Present/Absent attendance by date
- View and filter attendance records by date
- SQLite database is created automatically

## Requirements
- Python 3.10 or later
- Flask

## Run on Windows (VS Code terminal / PowerShell)
1. Extract the ZIP and open the `Student_Attendance_System` folder in VS Code.
2. Install Flask:
   ```powershell
   py -m pip install -r requirements.txt
   ```
   If `py` does not work, use `python -m pip install -r requirements.txt`.
3. Start the app:
   ```powershell
   py app.py
   ```
   Or use `python app.py`.
4. Open `http://127.0.0.1:5000` in your browser.

## Demo login
- Username: `admin`
- Password: `admin123`

The `attendance.db` database file is generated automatically on first run.
For a real deployment, change the Flask secret key and replace the demo login with secure user authentication.
