import streamlit as st
import pandas as pd
import re
from database import init_db, get_db, SessionLocal, Student, Teacher, User

def initialize_session_state():
    """Initialize session state and database."""
    # Initialize database
    init_db()
    
    # Initialize session state variables
    if 'students' not in st.session_state:
        st.session_state.students = pd.DataFrame(columns=[
            'ID', 'Name', 'Department', 'Year', 'Email', 'Phone'
        ])
    if 'teachers' not in st.session_state:
        st.session_state.teachers = pd.DataFrame(columns=[
            'ID', 'Name', 'Department', 'Subjects', 'Email', 'Phone'
        ])
    
    # Load data from database
    load_data_from_database()

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    pattern = r'^\d{10,11}$'  # Accept 10 or 11 digits
    return bool(re.match(pattern, phone))

def validate_student_data(id, name, department, year, email, phone):
    if not id or not name or not department or not year:
        return False, "All fields are required"
    if not validate_email(email):
        return False, "Invalid email format"
    if not validate_phone(phone):
        return False, "Phone number must be 10 or 11 digits"
    if id in st.session_state.students['ID'].values:
        return False, "Student ID already exists"
    return True, "Valid"

def validate_teacher_data(id, name, department, subjects, email, phone):
    if not id or not name or not department or not subjects:
        return False, "All fields are required"
    if not validate_email(email):
        return False, "Invalid email format"
    if not validate_phone(phone):
        return False, "Phone number must be 10 or 11 digits"
    if id in st.session_state.teachers['ID'].values:
        return False, "Teacher ID already exists"
    return True, "Valid"

def load_data_from_database():
    """Load data from database to session state for compatibility."""
    db = SessionLocal()
    try:
        # Load students
        students = db.query(Student).all()
        student_data = []
        for student in students:
            student_data.append({
                'ID': str(student.id),
                'Name': student.name,
                'Department': student.department,
                'Year': student.year,
                'Email': student.email,
                'Phone': student.phone
            })
        st.session_state.students = pd.DataFrame(student_data) if student_data else pd.DataFrame(columns=[
            'ID', 'Name', 'Department', 'Year', 'Email', 'Phone'
        ])
        
        # Load teachers
        teachers = db.query(Teacher).all()
        teacher_data = []
        for teacher in teachers:
            teacher_data.append({
                'ID': str(teacher.id),
                'Name': teacher.name,
                'Department': teacher.department,
                'Subjects': teacher.subjects,
                'Email': teacher.email,
                'Phone': teacher.phone
            })
        st.session_state.teachers = pd.DataFrame(teacher_data) if teacher_data else pd.DataFrame(columns=[
            'ID', 'Name', 'Department', 'Subjects', 'Email', 'Phone'
        ])
    finally:
        db.close()

def get_all_students():
    """Get all students from the database."""
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        student_data = []
        for student in students:
            student_data.append({
                'ID': str(student.id),
                'Name': student.name,
                'Department': student.department,
                'Year': student.year,
                'Email': student.email,
                'Phone': student.phone
            })
        return pd.DataFrame(student_data) if student_data else pd.DataFrame(columns=[
            'ID', 'Name', 'Department', 'Year', 'Email', 'Phone'
        ])
    finally:
        db.close()

def get_all_teachers():
    """Get all teachers from the database."""
    db = SessionLocal()
    try:
        teachers = db.query(Teacher).all()
        teacher_data = []
        for teacher in teachers:
            teacher_data.append({
                'ID': str(teacher.id),
                'Name': teacher.name,
                'Department': teacher.department,
                'Subjects': teacher.subjects,
                'Email': teacher.email,
                'Phone': teacher.phone
            })
        return pd.DataFrame(teacher_data) if teacher_data else pd.DataFrame(columns=[
            'ID', 'Name', 'Department', 'Subjects', 'Email', 'Phone'
        ])
    finally:
        db.close()
        
def add_student_to_db(student_data):
    """Add a student to the database."""
    db = SessionLocal()
    try:
        new_student = Student(
            name=student_data['Name'],
            department=student_data['Department'],
            year=int(student_data['Year']),
            email=student_data['Email'],
            phone=student_data['Phone']
        )
        db.add(new_student)
        db.commit()
        return True, "Student added successfully to database"
    except Exception as e:
        db.rollback()
        return False, f"Database error: {str(e)}"
    finally:
        db.close()
        
def add_teacher_to_db(teacher_data):
    """Add a teacher to the database."""
    db = SessionLocal()
    try:
        new_teacher = Teacher(
            name=teacher_data['Name'],
            department=teacher_data['Department'],
            subjects=teacher_data['Subjects'],
            email=teacher_data['Email'],
            phone=teacher_data['Phone']
        )
        db.add(new_teacher)
        db.commit()
        return True, "Teacher added successfully to database"
    except Exception as e:
        db.rollback()
        return False, f"Database error: {str(e)}"
    finally:
        db.close()