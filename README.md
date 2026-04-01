# OASS - Online Assignment Submission System

A small Flask + SQLAlchemy web app for student assignment upload and faculty grading.

## Features

- User registration and login
  - student or faculty role
- Student dashboard
  - list assignments
  - upload assignment files (.pdf/.doc/.docx)
  - update submission
- Faculty dashboard
  - create assignments
  - view all submissions
  - grade submissions with marks + feedback
  - persisted grades (reload on relogin)
- Download submission files
- Logout

## Data models

- `User` (id, name, email, password, role)
- `Assignment` (id, title, description, deadline, faculty_id)
- `Submission` (id, file_path, student_id, assignment_id)
- `Grade` (id, marks, feedback, submission_id)


## Files in project

- `app.py` (main Flask app + models + routes)
- `templates/` (UI pages)
  - `register.html`, `login.html`, `student.html`, `faculty.html`, `fileupload.html`
- `uploads/` (where submitted files are stored)

## Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   pip install flask flask_sqlalchemy pymysql werkzeug
   ```
4. Set up MySQL database:
   - Create DB `fsd` in MySQL.
   - Update database URL in `app.py`:
     ```python
     mysql+pymysql://root:Eswar%402004@localhost/fsd
     ```
5. Run the app:
   ```powershell
   python app.py
   ```
6. In browser, open:
   - `http://localhost:5000/register`
   - `http://localhost:5000/login`

## Routes

- `/` → redirect `/login`
- `/register` → register new user
- `/login` → login page
- `/student` → student dashboard
- `/upload/<assignment_id>` → upload assignment file
- `/faculty` → faculty dashboard
- `/grade/<submission_id>` → post marks/feedback
- `/download/<submission_id>` → download file
- `/logout` → clear session

## UI templates

- `templates/register.html`
- `templates/login.html`
- `templates/student.html`
- `templates/faculty.html`
- `templates/fileupload.html`

## Notes

- In `faculty.html`, grading form now pre-fills existing grade & feedback and shows saved grade values.
- For production, add secure file handling, user input validation, CSRF protection, and stronger secret management.

## Testing

1. Register student and faculty accounts.
2. Faculty creates assignment.
3. Student uploads file to assignment.
4. Faculty grades submission.
5. Logout and relogin as faculty to see persisted grade.

## Project Status

-  Assignment submission and grading is working properly  
-  All main features completed (register, login, upload, grading, download, logout)  
-  Future improvements:
- Add input validation  
- Add security (CSRF protection, secure passwords)  
- Improve file handling  
- Use environment variables  
- Add database migrations  
## Tech Stack
- Python (Flask)
- SQLAlchemy
- MySQL
- HTML, CSS