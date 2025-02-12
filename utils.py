import streamlit as st
import pandas as pd
import re
from database import Student, Teacher, get_db
from sqlalchemy.orm import Session
from contextlib import contextmanager

@contextmanager
def get_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    pattern = r'^\d{10}$'
    return bool(re.match(pattern, phone))

def validate_student_data(id, name, department, year, email, phone):
    if not id or not name or not department or not year:
        return False, "All fields are required"
    if not validate_email(email):
        return False, "Invalid email format"
    if not validate_phone(phone):
        return False, "Phone number must be 10 digits"
    with get_session() as db:
        existing_student = db.query(Student).filter(Student.id == id).first()
        if existing_student:
            return False, "Student ID already exists"
    return True, "Valid"

def validate_teacher_data(id, name, department, subjects, email, phone):
    if not id or not name or not department or not subjects:
        return False, "All fields are required"
    if not validate_email(email):
        return False, "Invalid email format"
    if not validate_phone(phone):
        return False, "Phone number must be 10 digits"
    with get_session() as db:
        existing_teacher = db.query(Teacher).filter(Teacher.id == id).first()
        if existing_teacher:
            return False, "Teacher ID already exists"
    return True, "Valid"

def get_all_students():
    with get_session() as db:
        students = db.query(Student).all()
        return pd.DataFrame([
            {
                'ID': s.id,
                'Name': s.name,
                'Department': s.department,
                'Year': s.year,
                'Email': s.email,
                'Phone': s.phone
            } for s in students
        ])

def get_all_teachers():
    with get_session() as db:
        teachers = db.query(Teacher).all()
        return pd.DataFrame([
            {
                'ID': t.id,
                'Name': t.name,
                'Department': t.department,
                'Subjects': t.subjects,
                'Email': t.email,
                'Phone': t.phone
            } for t in teachers
        ])