import streamlit as st
import pandas as pd

def initialize_session_state():
    if 'students' not in st.session_state:
        st.session_state.students = pd.DataFrame(
            columns=['ID', 'Name', 'Department', 'Year', 'Email', 'Phone']
        )
    if 'teachers' not in st.session_state:
        st.session_state.teachers = pd.DataFrame(
            columns=['ID', 'Name', 'Department', 'Subjects', 'Email', 'Phone']
        )

def validate_email(email):
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    import re
    pattern = r'^\d{10}$'
    return bool(re.match(pattern, phone))

def validate_student_data(id, name, department, year, email, phone):
    if not id or not name or not department or not year:
        return False, "All fields are required"
    if not validate_email(email):
        return False, "Invalid email format"
    if not validate_phone(phone):
        return False, "Phone number must be 10 digits"
    if any(st.session_state.students['ID'] == id):
        return False, "Student ID already exists"
    return True, "Valid"

def validate_teacher_data(id, name, department, subjects, email, phone):
    if not id or not name or not department or not subjects:
        return False, "All fields are required"
    if not validate_email(email):
        return False, "Invalid email format"
    if not validate_phone(phone):
        return False, "Phone number must be 10 digits"
    if any(st.session_state.teachers['ID'] == id):
        return False, "Teacher ID already exists"
    return True, "Valid"

def get_all_students():
    return st.session_state.students

def get_all_teachers():
    return st.session_state.teachers