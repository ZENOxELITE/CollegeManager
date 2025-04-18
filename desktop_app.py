"""
College Management System - Desktop Version
This standalone file contains all essential components for running the app locally.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import re
import hashlib
import os
from datetime import datetime, date, time
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Time, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from typing import List, Optional, Tuple

# Page configuration
st.set_page_config(
    page_title="College Management System",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for responsive design
st.markdown("""
<style>
    /* Make buttons more touch-friendly */
    .stButton>button {
        min-height: 40px;
        width: 100%;
    }

    /* Improve form elements on mobile */
    .stTextInput>div>div>input {
        min-height: 40px;
    }

    /* Better spacing for mobile */
    @media (max-width: 640px) {
        .main {
            padding: 1rem 0.5rem;
        }
        .stRadio > label {
            font-size: 14px;
            padding: 0.25rem 0.5rem;
        }
    }

    /* Navigation styling */
    .nav-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Database setup for desktop usage
# MySQL connection parameters - modify these to match your local setup
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""  # Set this to your MySQL password
MYSQL_DATABASE = "college_management"
MYSQL_PORT = 3306

# Set up database URL
try:
    # Try to use MySQL if available
    try:
        import pymysql
        print("Attempting to connect to MySQL database...")
        # Create MySQL connection URL
        DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        
        # Test if connection works
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=MYSQL_PORT,
            connect_timeout=5
        )
        conn.close()
        print("MySQL connection successful")
    except Exception as e:
        print(f"MySQL connection failed: {str(e)}")
        print("Falling back to SQLite database")
        DATABASE_URL = "sqlite:///college_management.db"
except Exception as e:
    print(f"Error setting up database connection: {str(e)}")
    print("Falling back to SQLite database")
    DATABASE_URL = "sqlite:///college_management.db"

# Log database connection information for debugging
print(f"Using database: {'MySQL' if 'mysql' in DATABASE_URL.lower() else 'SQLite'}")

# Configure SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

#-------------------- DATABASE MODELS --------------------#

# Define User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False)
    
    # Relationships for one-to-one with Student/Teacher
    student = relationship("Student", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)

# Define Student model
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="student")
    enrollments = relationship("ClassEnrollment", back_populates="student")

# Define Teacher model
class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    subjects = Column(String(200), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="teacher")
    classes = relationship("ClassSchedule", back_populates="teacher")

# Define Course model
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    department = Column(String(100), nullable=False)
    credit_hours = Column(Integer, nullable=False)
    
    # Relationships
    class_schedules = relationship("ClassSchedule", back_populates="course")

# Define ClassSchedule model
class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    day_of_week = Column(String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room_number = Column(String(20), nullable=False)
    semester = Column(String(20), nullable=False)  # Fall 2025, Spring 2026, etc.
    
    # Relationships
    course = relationship("Course", back_populates="class_schedules")
    teacher = relationship("Teacher", back_populates="classes")
    enrollments = relationship("ClassEnrollment", back_populates="class_schedule")

# Define ClassEnrollment model (for many-to-many relationship between students and classes)
class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_schedule_id = Column(Integer, ForeignKey("class_schedules.id"), nullable=False)
    enrollment_date = Column(Date, nullable=False)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    class_schedule = relationship("ClassSchedule", back_populates="enrollments")

#-------------------- DATABASE FUNCTIONS --------------------#

def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user if it doesn't exist
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            # Create default admin user
            admin_user = User(
                username='admin',
                password=hashlib.sha256('admin123'.encode()).hexdigest(),
                role='admin'
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created")
    except Exception as e:
        print(f"Error checking for admin user: {str(e)}")
    finally:
        db.close()

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

#-------------------- UTILITY FUNCTIONS --------------------#

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'students' not in st.session_state:
        st.session_state.students = pd.DataFrame(columns=[
            'ID', 'Name', 'Department', 'Year', 'Email', 'Phone'
        ])
    if 'teachers' not in st.session_state:
        st.session_state.teachers = pd.DataFrame(columns=[
            'ID', 'Name', 'Department', 'Subjects', 'Email', 'Phone'
        ])

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
    return True, "Valid"

def validate_teacher_data(id, name, department, subjects, email, phone):
    if not id or not name or not department or not subjects:
        return False, "All fields are required"
    if not validate_email(email):
        return False, "Invalid email format"
    if not validate_phone(phone):
        return False, "Phone number must be 10 digits"
    return True, "Valid"

def load_data_from_database():
    """Load data from database to session state for compatibility."""
    db = get_db()
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
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def get_all_students():
    """Get all students from the database."""
    db = get_db()
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
    except Exception as e:
        st.error(f"Error getting students: {str(e)}")
        return pd.DataFrame(columns=['ID', 'Name', 'Department', 'Year', 'Email', 'Phone'])

def get_all_teachers():
    """Get all teachers from the database."""
    db = get_db()
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
    except Exception as e:
        st.error(f"Error getting teachers: {str(e)}")
        return pd.DataFrame(columns=['ID', 'Name', 'Department', 'Subjects', 'Email', 'Phone'])

def add_student_to_db(student_data):
    """Add a student to the database."""
    db = get_db()
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

def add_teacher_to_db(teacher_data):
    """Add a teacher to the database."""
    db = get_db()
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

#-------------------- AUTHENTICATION FUNCTIONS --------------------#

def login(username: str, password: str) -> bool:
    """Authenticate a user and set up their session using database."""
    db = get_db()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and user.password == hash_password(password):
            st.session_state.authenticated = True
            st.session_state.user_role = user.role
            st.session_state.username = username
            return True
        return False
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False

def logout():
    """Clear the session state."""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None

def register_user(username: str, password: str, role: str) -> Tuple[bool, str]:
    """Register a new user in the database."""
    if role not in ['admin', 'teacher', 'student']:
        return False, "Invalid role"
    
    db = get_db()
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists"
        
        # Create new user
        new_user = User(
            username=username,
            password=hash_password(password),
            role=role
        )
        db.add(new_user)
        db.commit()
        return True, "User registered successfully"
    except Exception as e:
        db.rollback()
        return False, f"Registration error: {str(e)}"

def show_login_form():
    """Display the login form."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=True):
            st.subheader("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

def show_register_form():
    """Display the registration form."""
    if st.session_state.get('user_role') != 'admin':
        st.error("Only administrators can register new users")
        return

    with st.form("register_form", clear_on_submit=True):
        st.subheader("📝 Register New User")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ['teacher', 'student'])
        submitted = st.form_submit_button("Register User", use_container_width=True)

        if submitted:
            success, message = register_user(username, password, role)
            if success:
                st.success(message)
            else:
                st.error(message)

#-------------------- COMPONENT FUNCTIONS --------------------#

def show_dashboard():
    """Display the dashboard component."""
    st.header("Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Student Statistics")
        if not st.session_state.students.empty:
            # Department-wise distribution
            dept_counts = st.session_state.students['Department'].value_counts()
            fig1 = px.pie(
                values=dept_counts.values,
                names=dept_counts.index,
                title="Students by Department"
            )
            st.plotly_chart(fig1)

            # Year-wise distribution
            year_counts = st.session_state.students['Year'].value_counts()
            fig2 = px.bar(
                x=year_counts.index,
                y=year_counts.values,
                title="Students by Year"
            )
            st.plotly_chart(fig2)
        else:
            st.info("No student data available")

    with col2:
        st.subheader("Teacher Statistics")
        if not st.session_state.teachers.empty:
            # Department-wise distribution
            dept_counts = st.session_state.teachers['Department'].value_counts()
            fig3 = px.pie(
                values=dept_counts.values,
                names=dept_counts.index,
                title="Teachers by Department"
            )
            st.plotly_chart(fig3)

            # Total numbers
            st.metric("Total Students", len(st.session_state.students))
            st.metric("Total Teachers", len(st.session_state.teachers))
        else:
            st.info("No teacher data available")

def show_student_management():
    """Display the student management component."""
    st.header("Student Management")
    
    tab1, tab2, tab3 = st.tabs(["Add Student", "View Students", "Search"])
    
    with tab1:
        st.subheader("Add New Student")
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                id = st.text_input("Student ID")
                name = st.text_input("Name")
                department = st.text_input("Department")
            with col2:
                year = st.selectbox("Year", [1, 2, 3, 4])
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            
            submitted = st.form_submit_button("Add Student")
            if submitted:
                valid, message = validate_student_data(id, name, department, year, email, phone)
                if valid:
                    new_student = pd.DataFrame([{
                        'ID': id,
                        'Name': name,
                        'Department': department,
                        'Year': year,
                        'Email': email,
                        'Phone': phone
                    }])
                    st.session_state.students = pd.concat([st.session_state.students, new_student], ignore_index=True)
                    
                    # Add to database
                    success, db_message = add_student_to_db({
                        'ID': id,
                        'Name': name,
                        'Department': department,
                        'Year': year,
                        'Email': email,
                        'Phone': phone
                    })
                    
                    if success:
                        st.success("Student added successfully!")
                    else:
                        st.warning(f"Added to session but database error: {db_message}")
                else:
                    st.error(message)

    with tab2:
        if not st.session_state.students.empty:
            st.subheader("All Students")
            st.dataframe(st.session_state.students, use_container_width=True)
        else:
            st.info("No students registered yet")

    with tab3:
        st.subheader("Search Students")
        search_term = st.text_input("Search by Name or ID")
        if search_term:
            result = st.session_state.students[
                st.session_state.students['Name'].str.contains(search_term, case=False) |
                st.session_state.students['ID'].str.contains(search_term, case=False)
            ]
            if not result.empty:
                st.dataframe(result)
            else:
                st.warning("No matching records found")

def show_teacher_management():
    """Display the teacher management component."""
    st.header("Teacher Management")
    
    tab1, tab2, tab3 = st.tabs(["Add Teacher", "View Teachers", "Search"])
    
    with tab1:
        st.subheader("Add New Teacher")
        with st.form("add_teacher_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                id = st.text_input("Teacher ID")
                name = st.text_input("Name")
                department = st.text_input("Department")
            with col2:
                subjects = st.text_input("Subjects (comma separated)")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            
            submitted = st.form_submit_button("Add Teacher")
            if submitted:
                valid, message = validate_teacher_data(id, name, department, subjects, email, phone)
                if valid:
                    new_teacher = pd.DataFrame([{
                        'ID': id,
                        'Name': name,
                        'Department': department,
                        'Subjects': subjects,
                        'Email': email,
                        'Phone': phone
                    }])
                    st.session_state.teachers = pd.concat([st.session_state.teachers, new_teacher], ignore_index=True)
                    
                    # Add to database
                    success, db_message = add_teacher_to_db({
                        'ID': id,
                        'Name': name,
                        'Department': department,
                        'Subjects': subjects,
                        'Email': email,
                        'Phone': phone
                    })
                    
                    if success:
                        st.success("Teacher added successfully!")
                    else:
                        st.warning(f"Added to session but database error: {db_message}")
                else:
                    st.error(message)

    with tab2:
        if not st.session_state.teachers.empty:
            st.subheader("All Teachers")
            st.dataframe(st.session_state.teachers, use_container_width=True)
        else:
            st.info("No teachers registered yet")

    with tab3:
        st.subheader("Search Teachers")
        search_term = st.text_input("Search by Name or Department")
        if search_term:
            result = st.session_state.teachers[
                st.session_state.teachers['Name'].str.contains(search_term, case=False) |
                st.session_state.teachers['Department'].str.contains(search_term, case=False)
            ]
            if not result.empty:
                st.dataframe(result)
            else:
                st.warning("No matching records found")

def get_student_schedule(student_id: int, db) -> List[dict]:
    """Get the class schedule for a specific student."""
    try:
        # For simplicity in the standalone version, return a placeholder schedule
        return [
            {
                "day": "Monday",
                "start_time": "09:00",
                "end_time": "10:30",
                "course_code": "CS101",
                "course_title": "Introduction to Programming",
                "teacher": "Dr. Smith",
                "room": "Room 101",
                "semester": "Spring 2025"
            },
            {
                "day": "Tuesday",
                "start_time": "13:00",
                "end_time": "14:30",
                "course_code": "CS201",
                "course_title": "Data Structures",
                "teacher": "Dr. Johnson",
                "room": "Room 203",
                "semester": "Spring 2025"
            }
        ]
    except Exception as e:
        st.error(f"Error getting student schedule: {str(e)}")
        return []

def get_teacher_schedule(teacher_id: int, db) -> List[dict]:
    """Get the class schedule for a specific teacher."""
    try:
        # For simplicity in the standalone version, return a placeholder schedule
        return [
            {
                "day": "Monday",
                "start_time": "09:00",
                "end_time": "10:30",
                "course_code": "CS101",
                "course_title": "Introduction to Programming",
                "room": "Room 101",
                "semester": "Spring 2025"
            },
            {
                "day": "Wednesday",
                "start_time": "15:00",
                "end_time": "16:30",
                "course_code": "CS301",
                "course_title": "Software Engineering",
                "room": "Room 205",
                "semester": "Spring 2025"
            }
        ]
    except Exception as e:
        st.error(f"Error getting teacher schedule: {str(e)}")
        return []

def show_schedule_management():
    """Display the class schedule management component."""
    st.header("Class Schedule Management")
    
    db = get_db()
    
    tabs = st.tabs(["View Schedule", "Courses", "Add Schedule"])
    
    with tabs[0]:
        st.subheader("Your Class Schedule")
        
        if st.session_state.authenticated:
            user_role = st.session_state.user_role
            username = st.session_state.username
            
            if user_role == 'student':
                # Get student ID (simulated for desktop version)
                student_id = 1  # Placeholder
                
                schedule = get_student_schedule(student_id, db)
                if schedule:
                    # Convert to DataFrame for display
                    df = pd.DataFrame(schedule)
                    
                    # Group by day for better organization
                    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    df['day'] = pd.Categorical(df['day'], categories=days_order, ordered=True)
                    df = df.sort_values(['day', 'start_time'])
                    
                    # Show schedule grouped by day
                    for day in df['day'].unique():
                        st.subheader(day)
                        day_schedule = df[df['day'] == day]
                        st.table(day_schedule[['start_time', 'end_time', 'course_code', 'course_title', 'teacher', 'room']])
                else:
                    st.info("You are not enrolled in any classes yet.")
            
            elif user_role == 'teacher':
                # Get teacher ID (simulated for desktop version)
                teacher_id = 1  # Placeholder
                
                schedule = get_teacher_schedule(teacher_id, db)
                if schedule:
                    # Convert to DataFrame for display
                    df = pd.DataFrame(schedule)
                    
                    # Group by day for better organization
                    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    df['day'] = pd.Categorical(df['day'], categories=days_order, ordered=True)
                    df = df.sort_values(['day', 'start_time'])
                    
                    # Show schedule grouped by day
                    for day in df['day'].unique():
                        st.subheader(day)
                        day_schedule = df[df['day'] == day]
                        st.table(day_schedule[['start_time', 'end_time', 'course_code', 'course_title', 'room']])
                else:
                    st.info("You don't have any classes scheduled.")
            
            elif user_role == 'admin':
                st.info("This is a simplified desktop version. The full database functionality works when set up properly with MySQL.")
                st.info("Sample schedule data is shown for demonstration.")
                
                # Show sample schedule
                sample_data = [
                    {
                        "day": "Monday",
                        "start_time": "09:00",
                        "end_time": "10:30",
                        "course_code": "CS101",
                        "course_title": "Introduction to Programming",
                        "teacher": "Dr. Smith",
                        "room": "Room 101",
                        "semester": "Spring 2025"
                    },
                    {
                        "day": "Tuesday",
                        "start_time": "13:00",
                        "end_time": "14:30",
                        "course_code": "CS201",
                        "course_title": "Data Structures",
                        "teacher": "Dr. Johnson",
                        "room": "Room 203",
                        "semester": "Spring 2025"
                    },
                    {
                        "day": "Wednesday",
                        "start_time": "15:00",
                        "end_time": "16:30",
                        "course_code": "CS301",
                        "course_title": "Software Engineering",
                        "teacher": "Dr. Williams",
                        "room": "Room 205",
                        "semester": "Spring 2025"
                    }
                ]
                df = pd.DataFrame(sample_data)
                st.dataframe(df, use_container_width=True)
        else:
            st.warning("Please log in to view your schedule.")
    
    with tabs[1]:
        st.subheader("Course Management")
        
        st.info("This is a simplified desktop version. Course management is available in the full database version.")
        
        # Sample courses
        sample_courses = [
            {
                "course_code": "CS101",
                "title": "Introduction to Programming",
                "department": "Computer Science",
                "credit_hours": 3
            },
            {
                "course_code": "CS201",
                "title": "Data Structures",
                "department": "Computer Science",
                "credit_hours": 4
            },
            {
                "course_code": "CS301",
                "title": "Software Engineering",
                "department": "Computer Science",
                "credit_hours": 3
            }
        ]
        
        df = pd.DataFrame(sample_courses)
        st.dataframe(df, use_container_width=True)
    
    with tabs[2]:
        st.info("This is a simplified desktop version. Schedule creation is available in the full database version.")
        st.info("For the desktop version, you can add sample class schedules.")
        
        with st.form("add_sample_schedule"):
            st.subheader("Add Sample Class Schedule")
            course = st.selectbox("Course", ["CS101 - Introduction to Programming", "CS201 - Data Structures", "CS301 - Software Engineering"])
            teacher = st.selectbox("Teacher", ["Dr. Smith", "Dr. Johnson", "Dr. Williams"])
            day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            start_time = st.time_input("Start Time", value=time(9, 0))
            end_time = st.time_input("End Time", value=time(10, 30))
            room = st.text_input("Room Number", "Room 101")
            
            submitted = st.form_submit_button("Add Sample Schedule")
            if submitted:
                st.success("Sample schedule added for demonstration!")

#-------------------- MAIN APPLICATION --------------------#

def main():
    # Initialize database and session state
    try:
        init_db()
        initialize_session_state()
        
        # Load data from database
        try:
            load_data_from_database()
        except Exception as e:
            st.warning(f"Could not load data from database: {str(e)}")
    except Exception as e:
        st.error(f"Error initializing application: {str(e)}")
        st.info("If this is your first time running the app, a new SQLite database will be created.")
    
    # Page header with navigation and auth info
    st.title("College Management System")

    # Create header with columns for nav and auth
    header_left, header_right = st.columns([3, 1])

    # Authentication status
    with header_right:
        if st.session_state.authenticated:
            st.info(f"👤 {st.session_state.username} ({st.session_state.user_role})")
            if st.button("Logout", key="logout_btn"):
                logout()
                st.rerun()

    # Navigation bar
    if st.session_state.authenticated:
        with header_left:
            # Show navigation based on role
            if st.session_state.user_role == 'admin':
                page = st.radio(
                    "Navigation",
                    ["Dashboard", "Student Management", "Teacher Management", "Class Schedule", "User Management"],
                    horizontal=True,
                    key="nav_admin"
                )
            elif st.session_state.user_role == 'teacher':
                page = st.radio(
                    "Navigation",
                    ["Dashboard", "Student Management", "Class Schedule"],
                    horizontal=True,
                    key="nav_teacher"
                )
            else:  # student role
                page = st.radio(
                    "Navigation",
                    ["Dashboard", "Class Schedule"],
                    horizontal=True,
                    key="nav_student"
                )
    else:
        show_login_form()
        st.stop()

    st.divider()

    # Page routing with role-based access
    if page == "Dashboard":
        show_dashboard()
    elif page == "Student Management" and st.session_state.user_role in ['admin', 'teacher']:
        show_student_management()
    elif page == "Teacher Management" and st.session_state.user_role == 'admin':
        show_teacher_management()
    elif page == "Class Schedule":
        # All roles have access to class schedule, but with different permissions
        show_schedule_management()
    elif page == "User Management" and st.session_state.user_role == 'admin':
        st.header("User Management")
        show_register_form()
    else:
        st.error("You don't have permission to access this page")

if __name__ == "__main__":
    main()