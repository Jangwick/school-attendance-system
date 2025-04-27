from models import db, User, Student, Subject, TeacherSubject, Attendance
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def add_sample_data():
    # Check if we already have data
    if User.query.count() > 0:
        return
    
    # Create sample teacher
    teacher = User(
        name='John Smith',
        email='john.smith@school.edu',
        password=generate_password_hash('password123'),
        role='teacher'
    )
    db.session.add(teacher)
    
    # Create second sample teacher
    teacher2 = User(
        name='Mary Johnson',
        email='mary.johnson@school.edu',
        password=generate_password_hash('password123'),
        role='teacher'
    )
    db.session.add(teacher2)
    
    # Create sample subjects
    subjects = [
        Subject(name='Mathematics', code='MATH101'),
        Subject(name='Science', code='SCI101'),
        Subject(name='English', code='ENG101'),
        Subject(name='History', code='HIST101')
    ]
    for subject in subjects:
        db.session.add(subject)
    
    # Commit to generate IDs
    db.session.commit()
    
    # Assign subjects to teachers
    teacher_subjects = [
        TeacherSubject(teacher_id=teacher.id, subject_id=subjects[0].id),
        TeacherSubject(teacher_id=teacher.id, subject_id=subjects[1].id),
        TeacherSubject(teacher_id=teacher2.id, subject_id=subjects[2].id),
        TeacherSubject(teacher_id=teacher2.id, subject_id=subjects[3].id)
    ]
    for ts in teacher_subjects:
        db.session.add(ts)
    
    # Create sample students
    students = [
        Student(school_id='230116599', name='John Cristian Hermanito'),
        Student(school_id='220123456', name='Alice Brown'),
        Student(school_id='220123457', name='Bob Green'),
        Student(school_id='220123458', name='Charlie Davis'),
        Student(school_id='220123459', name='Diana Wilson'),
        Student(school_id='220123460', name='Edward Thompson')
    ]
    for student in students:
        db.session.add(student)
        
        # Enroll students in subjects - each student is enrolled in all subjects
        for subject in subjects:
            student.subjects.append(subject)
    
    # Commit changes to generate IDs for students
    db.session.commit()
    
    # Create sample attendance records
    # Create attendance for the past 2 weeks (10 school days) for Math class
    today = datetime.now().date()
    for i in range(10):
        # Skip weekends
        day_of_week = (today - timedelta(days=i)).weekday()
        if day_of_week >= 5:  # Skip Saturday (5) and Sunday (6)
            continue
            
        class_date = today - timedelta(days=i)
        
        # Math class attendance (subject_id=1)
        for student in students:
            # Randomly mark some students absent (every student has ~80% attendance)
            # Students 1, 3, 5 are present on all days
            # Student 2 is absent on days divisible by 3
            # Student 4 is absent on days divisible by 4
            # Student 6 is absent on days divisible by 2
            status = 'present'
            if (student.id == 2 and i % 3 == 0) or \
               (student.id == 4 and i % 4 == 0) or \
               (student.id == 6 and i % 2 == 0):
                status = 'absent'
            else:
                # Add attendance record for present students
                attendance = Attendance(
                    student_id=student.id,
                    subject_id=subjects[0].id,  # Math
                    teacher_id=teacher.id,
                    date=class_date,
                    status='present'
                )
                db.session.add(attendance)
        
        # Science class attendance (subject_id=2)
        if i % 2 == 0:  # Science class every other day
            for student in students:
                # Different attendance pattern for Science
                status = 'present'
                if (student.id == 1 and i % 5 == 0) or \
                   (student.id == 3 and i % 3 == 0) or \
                   (student.id == 5 and i % 2 == 0):
                    status = 'absent'
                else:
                    attendance = Attendance(
                        student_id=student.id,
                        subject_id=subjects[1].id,  # Science
                        teacher_id=teacher.id,
                        date=class_date,
                        status='present'
                    )
                    db.session.add(attendance)
    
    # Commit all attendance records
    db.session.commit()
