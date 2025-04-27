from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='teacher')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.name}>'

# Subject-Student association table (many-to-many)
subject_student = db.Table('subject_student',
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add relationship to attendance records
    attendances = db.relationship('Attendance', backref='student_record', lazy=True)
    
    # Add relationship to subjects (many-to-many)
    subjects = db.relationship('Subject', secondary=subject_student, 
                               backref=db.backref('students', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Student {self.name}>'
    
    def get_attendance_percentage(self, subject_id, dates):
        """Calculate attendance percentage for a student in a specific subject"""
        if not dates:
            return 0
            
        present_count = sum(1 for a in self.attendances 
                           if a.subject_id == subject_id 
                           and a.date in dates 
                           and a.status == 'present')
        return (present_count / len(dates)) * 100

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add relationship to attendance records
    attendances = db.relationship('Attendance', backref='subject_record', lazy=True)
    
    def __repr__(self):
        return f'<Subject {self.name}>'
    
    def get_average_attendance(self, students, dates):
        """Calculate average attendance percentage across all students"""
        if not students or not dates:
            return 0
            
        total_percentage = 0
        for student in students:
            total_percentage += student.get_attendance_percentage(self.id, dates)
        
        return total_percentage / len(students)

class TeacherSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    teacher = db.relationship('User', backref='subjects')
    subject = db.relationship('Subject', backref='teachers')
    
    def __repr__(self):
        return f'<TeacherSubject {self.teacher.name} - {self.subject.name}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(20), default='present')  # present, absent, late
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Existing relationships
    student = db.relationship('Student', backref='attendance_records')
    subject = db.relationship('Subject', backref='attendance_records')
    teacher = db.relationship('User')
    
    def __repr__(self):
        return f'<Attendance {self.student.name} - {self.subject.name} - {self.date}>'
