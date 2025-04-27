from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import qrcode
from io import BytesIO
import base64
from models import db, User, Student, Subject, Attendance, TeacherSubject
import utils

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Flag to check if initial setup has been done
_is_db_initialized = False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    teacher_subjects = TeacherSubject.query.filter_by(teacher_id=current_user.id).all()
    
    # Get unique students across all subjects for this teacher
    unique_students = set()
    for ts in teacher_subjects:
        for student in ts.subject.students:
            unique_students.add(student.id)
    
    unique_student_count = len(unique_students)
    
    return render_template('dashboard/index.html', 
                           teacher_subjects=teacher_subjects,
                           unique_student_count=unique_student_count,
                           now=datetime.now)  # Pass the datetime.now function

@app.route('/students')
@login_required
def students():
    students = Student.query.all()
    return render_template('students/index.html', students=students)

@app.route('/students/<int:subject_id>')
@login_required
def students_by_subject(subject_id):
    """
    This route now includes attendance marking functionality directly
    via the buttons in the student list.
    """
    subject = Subject.query.get_or_404(subject_id)
    teacher_subject = TeacherSubject.query.filter_by(subject_id=subject_id, teacher_id=current_user.id).first_or_404()
    
    # Get today's date
    today = datetime.now().date()
    
    # Get students who are already marked for attendance today
    marked_attendance = Attendance.query.filter_by(
        subject_id=subject_id,
        date=today
    ).all()
    
    # Create a set of marked student IDs for quick lookup
    marked_students = {attendance.student_id for attendance in marked_attendance}
    
    return render_template('students/by_subject.html', 
                          subject=subject, 
                          marked_students=marked_students)

@app.route('/attendance/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def attendance(subject_id):
    """
    This route now combines the attendance dashboard and manual marking functionality
    """
    subject = Subject.query.get_or_404(subject_id)
    
    # Check if the current teacher is assigned to this subject
    teacher_subject = TeacherSubject.query.filter_by(
        subject_id=subject_id, 
        teacher_id=current_user.id
    ).first_or_404()
    
    today = datetime.now().date()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        
        # Check if attendance already exists
        existing_attendance = Attendance.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            date=today
        ).first()
        
        if not existing_attendance:
            attendance = Attendance(
                student_id=student_id,
                subject_id=subject_id,
                teacher_id=current_user.id,
                date=today,
                status='present'
            )
            db.session.add(attendance)
            db.session.commit()
            flash('Attendance marked successfully')
        else:
            flash('Attendance already marked for this student today')
    
    # Get students enrolled in this subject
    students = subject.students.all()
    
    # Get students who are already marked for attendance today
    marked_attendance = Attendance.query.filter_by(
        subject_id=subject_id,
        date=today
    ).all()
    
    # Create a set of marked student IDs for quick lookup
    marked_students = {attendance.student_id for attendance in marked_attendance}
    
    # Count today's attendance
    attendance_count = len(marked_students)
    
    return render_template('attendance/dashboard.html', 
                          subject=subject, 
                          students=students,
                          today=today,
                          marked_students=marked_students,
                          attendance_count=attendance_count)

@app.route('/api/generate-qr/<int:student_id>')
@login_required
def generate_qr_api(student_id):
    """API endpoint to get QR code data for a student"""
    student = Student.query.get_or_404(student_id)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(student.school_id))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return render_template('modals/qr_code_modal.html', student=student, qr_code=img_str)

@app.route('/generate-qr/<int:student_id>')
@login_required
def generate_qr(student_id):
    student = Student.query.get_or_404(student_id)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(student.school_id))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return render_template('students/qr_code.html', student=student, qr_code=img_str)

@app.route('/scan-qr/<int:subject_id>')
@login_required
def scan_qr(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('attendance/scan.html', subject=subject)

@app.route('/api/mark-attendance', methods=['POST'])
@login_required
def mark_attendance_api():
    data = request.json
    school_id = data.get('school_id')
    subject_id = data.get('subject_id')
    
    student = Student.query.filter_by(school_id=school_id).first()
    if not student:
        return jsonify({'status': 'error', 'message': 'Student not found'}), 404
    
    date = datetime.now().date()
    existing_attendance = Attendance.query.filter_by(
        student_id=student.id,
        subject_id=subject_id,
        date=date
    ).first()
    
    if existing_attendance:
        # Return the existing attendance info with already marked status
        return jsonify({
            'status': 'success', 
            'message': 'Attendance already marked for today',
            'student': {
                'name': student.name,
                'school_id': student.school_id,
                'id': student.id,
                'initials': ''.join(name[0].upper() for name in student.name.split() if name)
            },
            'attendance': {
                'id': existing_attendance.id,
                'date': existing_attendance.date.strftime('%Y-%m-%d'),
                'time': existing_attendance.created_at.strftime('%H:%M:%S')
            }
        })
    
    attendance = Attendance(
        student_id=student.id,
        subject_id=subject_id,
        teacher_id=current_user.id,
        date=date,
        status='present'
    )
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': 'Attendance marked successfully',
        'student': {
            'name': student.name,
            'school_id': student.school_id,
            'id': student.id,
            'initials': ''.join(name[0].upper() for name in student.name.split() if name)
        },
        'attendance': {
            'id': attendance.id,
            'date': attendance.date.strftime('%Y-%m-%d'),
            'time': attendance.created_at.strftime('%H:%M:%S')
        }
    })

@app.route('/api/attendance-data/<int:subject_id>')
@login_required
def attendance_data_api(subject_id):
    """API to get attendance data for charts"""
    subject = Subject.query.get_or_404(subject_id)
    
    # Check teacher authorization
    TeacherSubject.query.filter_by(
        subject_id=subject_id, 
        teacher_id=current_user.id
    ).first_or_404()
    
    # Get all dates where attendance was taken for this subject
    today = datetime.now().date()
    
    # Get students in this subject
    students = subject.students.all()
    
    # Get past 7 days
    past_days = []
    attendance_rates = []
    
    for i in range(6, -1, -1):  # 6 days ago to today
        day = today - timedelta(days=i)
        past_days.append(day.strftime('%a %d'))
        
        # Get attendance for this day
        day_attendance = Attendance.query.filter_by(
            subject_id=subject_id,
            date=day
        ).all()
        
        present_count = len(day_attendance)
        student_count = len(students)
        
        if student_count > 0:
            rate = (present_count / student_count) * 100
        else:
            rate = 0
            
        attendance_rates.append(round(rate, 1))
    
    # Get top performing students
    top_students = []
    for student in students[:5]:  # Get first 5 students
        # In real implementation, you would calculate actual attendance rate
        # For now, we'll just use sample data
        attendance_rate = student.get_attendance_percentage(subject_id, [today])
        top_students.append({
            'name': student.name,
            'rate': attendance_rate
        })
    
    # Sort by attendance rate
    top_students.sort(key=lambda x: x['rate'], reverse=True)
    
    return jsonify({
        'weekly': {
            'days': past_days,
            'rates': attendance_rates
        },
        'topStudents': top_students,
        'today': {
            'present': len([s for s in students if s.id in {a.student_id for a in Attendance.query.filter_by(
                subject_id=subject_id, date=today).all()}]),
            'total': len(students)
        }
    })

@app.route('/reports')
@login_required
def reports():
    subjects = Subject.query.join(TeacherSubject).filter(TeacherSubject.teacher_id == current_user.id).all()
    return render_template('reports/index.html', subjects=subjects)

@app.route('/reports/<int:subject_id>')
@login_required
def subject_report(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Get today's date
    today = datetime.now().date()
    
    # Get all dates where attendance was taken for this subject
    dates_query = db.session.query(Attendance.date).filter_by(subject_id=subject_id).distinct().order_by(Attendance.date)
    dates = [date[0] for date in dates_query.all()]
    
    # Get all students
    students = Student.query.all()
    
    if not dates:
        # No attendance records found for this subject at all
        attendance_data = {}
        subject_attendance_percentage = 0
    else:
        # Get attendance records for all students on each date
        attendance_data = {}
        
        # Efficiently fetch all relevant attendance records at once
        attendance_records = Attendance.query.filter_by(subject_id=subject_id).all()
        
        # Create lookup dict for faster access
        attendance_lookup = {}
        for record in attendance_records:
            key = (record.student_id, record.date.strftime('%Y-%m-%d'))
            attendance_lookup[key] = record.status
        
        # Process each student
        for student in students:
            attendance_data[student.id] = {}
            
            # Initialize all dates as 'absent' by default
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                # Check if record exists in our lookup
                key = (student.id, date_str)
                status = attendance_lookup.get(key, 'absent')
                attendance_data[student.id][date_str] = status
        
        # Calculate overall subject attendance percentage
        total_attendance = 0
        student_count = len(students)
        if student_count > 0:
            for student in students:
                # Calculate attendance percentage for this student
                present_count = sum(1 for date in dates 
                                    if (student.id, date.strftime('%Y-%m-%d')) in attendance_lookup 
                                    and attendance_lookup[(student.id, date.strftime('%Y-%m-%d'))] == 'present')
                
                if dates:
                    student_percentage = (present_count / len(dates)) * 100
                    total_attendance += student_percentage
            
            subject_attendance_percentage = total_attendance / student_count
        else:
            subject_attendance_percentage = 0
    
    return render_template('reports/subject.html', 
                          subject=subject, 
                          students=students, 
                          dates=dates, 
                          attendance_data=attendance_data,
                          subject_attendance_percentage=subject_attendance_percentage,
                          today=today)

# Database initialization and sample data
@app.before_request
def create_tables():
    global _is_db_initialized
    if not _is_db_initialized:
        with app.app_context():
            db.create_all()
            utils.add_sample_data()
            _is_db_initialized = True

@app.route('/api/get-add-student-modal')
@login_required
def get_add_student_modal():
    """API endpoint to return the add student modal HTML"""
    subjects = Subject.query.all()
    return render_template('modals/add_student_modal.html', subjects=subjects)

@app.route('/api/get-edit-student-modal/<int:student_id>')
@login_required
def get_edit_student_modal(student_id):
    """API endpoint to return the edit student modal HTML"""
    student = Student.query.get_or_404(student_id)
    subjects = Subject.query.all()
    return render_template('modals/edit_student_modal.html', student=student, subjects=subjects)

@app.route('/add-student', methods=['POST'])
@login_required
def add_student():
    """Add a new student to the system"""
    name = request.form.get('name')
    school_id = request.form.get('school_id')
    email = request.form.get('email')
    subject_ids = request.form.getlist('subjects[]')
    
    # Check if school_id already exists
    existing_student = Student.query.filter_by(school_id=school_id).first()
    if existing_student:
        flash('Student with this School ID already exists.')
        return redirect(url_for('students'))
    
    # Create new student
    new_student = Student(name=name, school_id=school_id, email=email)
    
    # Add subjects
    for subject_id in subject_ids:
        subject = Subject.query.get(subject_id)
        if subject:
            new_student.subjects.append(subject)
    
    db.session.add(new_student)
    db.session.commit()
    
    flash('Student added successfully!')
    return redirect(url_for('students'))

@app.route('/update-student/<int:student_id>', methods=['POST'])
@login_required
def update_student(student_id):
    """Update an existing student's information"""
    student = Student.query.get_or_404(student_id)
    
    name = request.form.get('name')
    school_id = request.form.get('school_id')
    email = request.form.get('email')
    subject_ids = request.form.getlist('subjects[]')
    
    # Check if school_id already exists and it's not this student's ID
    existing_student = Student.query.filter_by(school_id=school_id).first()
    if existing_student and existing_student.id != student_id:
        flash('Another student with this School ID already exists.')
        return redirect(url_for('students'))
    
    # Update student details
    student.name = name
    student.school_id = school_id
    student.email = email
    
    # Update subjects
    student.subjects = []
    for subject_id in subject_ids:
        subject = Subject.query.get(subject_id)
        if subject:
            student.subjects.append(subject)
    
    db.session.commit()
    
    flash('Student updated successfully!')
    return redirect(url_for('students'))

@app.route('/delete-student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    """Delete a student from the system"""
    student = Student.query.get_or_404(student_id)
    
    # Delete the student's attendance records
    Attendance.query.filter_by(student_id=student_id).delete()
    
    # Get the student name before deleting for the flash message
    student_name = student.name
    
    # Delete the student
    db.session.delete(student)
    db.session.commit()
    
    flash(f'Student "{student_name}" has been deleted successfully', 'success')
    return redirect(url_for('students'))

if __name__ == '__main__':
    app.run(debug=True)