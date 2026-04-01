from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "secret123"

# MySQL Connection

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Eswar%402004@localhost/fsd'
app.config['SQLALCHEMY_Track_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# MODELS 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(20))

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    deadline = db.Column(db.String(50))
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    faculty = db.relationship('User', backref=db.backref('assignments', lazy=True))

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(200))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    student = db.relationship('User', backref=db.backref('submissions', lazy=True))
    assignment = db.relationship('Assignment', backref=db.backref('submissions', lazy=True))

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marks = db.Column(db.Integer)
    feedback = db.Column(db.String(200))
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    submission = db.relationship('Submission', backref=db.backref('grade', uselist=False))

#  ROUTES 

@app.route('/')
def home():
    return redirect('/login')

# REGISTER 

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error="Email already registered")

        user = User(name=name, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')

# LOGIN 

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role

            if user.role == 'student':
                return redirect('/student')
            elif user.role == 'faculty':
                return redirect('/faculty')

        return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')

#  STUDENT DASHBOARD 

@app.route('/student')
def student():
    if session.get('role') != 'student':
        return redirect('/login')

    assignments = Assignment.query.all()
    student_submissions = Submission.query.filter_by(student_id=session['user_id']).all()
    submissions_by_assignment = {sub.assignment_id: sub for sub in student_submissions}

    return render_template(
        'student.html',
        assignments=assignments,
        submissions_by_assignment=submissions_by_assignment
    )

# UPLOAD

@app.route('/upload/<int:id>', methods=['POST'])
def upload(id):
    if session.get('role') != 'student':
        return redirect('/login')

    file = request.files.get('file')
    if not file or file.filename == '':
        return "No file selected"

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.pdf', '.doc', '.docx']:
        return "Invalid file type. Only PDF / DOC / DOCX allowed"

    upload_folder = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    existing = Submission.query.filter_by(student_id=session['user_id'], assignment_id=id).first()
    if existing:
        existing.file_path = 'uploads/' + filename
        db.session.commit()
    else:
        sub = Submission(
            file_path='uploads/' + filename,
            student_id=session['user_id'],
            assignment_id=id
        )
        db.session.add(sub)
        db.session.commit()

    return redirect('/student')

# FACULTY DASHBOARD

@app.route('/faculty', methods=['GET','POST'])
def faculty():
    if session.get('role') != 'faculty':
        return redirect('/login')

    # Create assignment
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        desc = request.form['description']
        deadline = request.form['deadline']

        assignment = Assignment(
            name=name,
            title=title,
            description=desc,
            deadline=deadline,
            faculty_id=session['user_id']
        )

        db.session.add(assignment)
        db.session.commit()

        return redirect('/faculty')

    assignments = Assignment.query.filter_by(
        faculty_id=session['user_id']
    ).all()

    return render_template('faculty.html', assignments=assignments)

@app.route('/delete_assignment/<int:id>')
def delete_assignment(id):
    if session.get('role') != 'faculty':
        return redirect('/login')

    assignment = Assignment.query.get(id)

    if assignment:
        # delete grades
        for sub in assignment.submissions:
            if sub.grade:
                db.session.delete(sub.grade)

        # delete submissions
        for sub in assignment.submissions:
            db.session.delete(sub)

        # delete assignment
        db.session.delete(assignment)
        db.session.commit()

    return redirect('/faculty')

# GRADING 

@app.route('/download/<int:submission_id>')
def download(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return "Submission not found"

    filename = os.path.basename(submission.file_path)
    folder = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(folder, filename, as_attachment=True)


@app.route('/grade/<int:id>', methods=['POST'])
def grade(id):
    if session.get('role') != 'faculty':
        return redirect('/login')

    marks = request.form['marks']
    feedback = request.form['feedback']

    existing_grade = Grade.query.filter_by(submission_id=id).first()
    if existing_grade:
        existing_grade.marks = marks
        existing_grade.feedback = feedback
    else:
        existing_grade = Grade(
            marks=marks,
            feedback=feedback,
            submission_id=id
        )
        db.session.add(existing_grade)

    db.session.commit()
    return redirect('/faculty')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)