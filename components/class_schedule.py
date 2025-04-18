import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from typing import List, Optional

from database import SessionLocal, ClassSchedule, Course, Teacher, Student, ClassEnrollment, User

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def get_student_schedule(student_id: int, db: Session = None) -> List[dict]:
    """Get the class schedule for a specific student."""
    if db is None:
        db = get_db()
    
    enrollments = (
        db.query(
            ClassSchedule.day_of_week,
            ClassSchedule.start_time,
            ClassSchedule.end_time,
            ClassSchedule.room_number,
            ClassSchedule.semester,
            Course.course_code,
            Course.title.label("course_title"),
            Teacher.name.label("teacher_name")
        )
        .join(ClassEnrollment, ClassEnrollment.class_schedule_id == ClassSchedule.id)
        .join(Course, Course.id == ClassSchedule.course_id)
        .join(Teacher, Teacher.id == ClassSchedule.teacher_id)
        .filter(ClassEnrollment.student_id == student_id)
        .all()
    )
    
    return [
        {
            "day": enrollment.day_of_week,
            "start_time": enrollment.start_time.strftime("%H:%M"),
            "end_time": enrollment.end_time.strftime("%H:%M"),
            "course_code": enrollment.course_code,
            "course_title": enrollment.course_title,
            "teacher": enrollment.teacher_name,
            "room": enrollment.room_number,
            "semester": enrollment.semester
        }
        for enrollment in enrollments
    ]

def get_teacher_schedule(teacher_id: int, db: Session = None) -> List[dict]:
    """Get the class schedule for a specific teacher."""
    if db is None:
        db = get_db()
    
    classes = (
        db.query(
            ClassSchedule.day_of_week,
            ClassSchedule.start_time,
            ClassSchedule.end_time,
            ClassSchedule.room_number,
            ClassSchedule.semester,
            Course.course_code,
            Course.title.label("course_title")
        )
        .join(Course, Course.id == ClassSchedule.course_id)
        .filter(ClassSchedule.teacher_id == teacher_id)
        .all()
    )
    
    return [
        {
            "day": class_item.day_of_week,
            "start_time": class_item.start_time.strftime("%H:%M"),
            "end_time": class_item.end_time.strftime("%H:%M"),
            "course_code": class_item.course_code,
            "course_title": class_item.course_title,
            "room": class_item.room_number,
            "semester": class_item.semester
        }
        for class_item in classes
    ]

def get_available_courses(db: Session = None) -> List[dict]:
    """Get all available courses."""
    if db is None:
        db = get_db()
    
    courses = db.query(Course).all()
    return [
        {
            "id": course.id,
            "course_code": course.course_code,
            "title": course.title,
            "department": course.department,
            "credit_hours": course.credit_hours,
            "description": course.description
        }
        for course in courses
    ]

def get_class_schedules(course_id: Optional[int] = None, db: Session = None) -> List[dict]:
    """Get class schedules, optionally filtered by course."""
    if db is None:
        db = get_db()
    
    query = (
        db.query(
            ClassSchedule.id,
            ClassSchedule.day_of_week,
            ClassSchedule.start_time,
            ClassSchedule.end_time,
            ClassSchedule.room_number,
            ClassSchedule.semester,
            Course.course_code,
            Course.title.label("course_title"),
            Teacher.name.label("teacher_name")
        )
        .join(Course, Course.id == ClassSchedule.course_id)
        .join(Teacher, Teacher.id == ClassSchedule.teacher_id)
    )
    
    if course_id:
        query = query.filter(ClassSchedule.course_id == course_id)
    
    class_schedules = query.all()
    
    return [
        {
            "id": cs.id,
            "day": cs.day_of_week,
            "start_time": cs.start_time.strftime("%H:%M"),
            "end_time": cs.end_time.strftime("%H:%M"),
            "course_code": cs.course_code,
            "course_title": cs.course_title,
            "teacher": cs.teacher_name,
            "room": cs.room_number,
            "semester": cs.semester
        }
        for cs in class_schedules
    ]

def enroll_student(student_id: int, class_schedule_id: int, db: Session = None):
    """Enroll a student in a class."""
    if db is None:
        db = get_db()
    
    # Check if already enrolled
    existing_enrollment = (
        db.query(ClassEnrollment)
        .filter(
            ClassEnrollment.student_id == student_id,
            ClassEnrollment.class_schedule_id == class_schedule_id
        )
        .first()
    )
    
    if existing_enrollment:
        return False, "Student is already enrolled in this class"
    
    # Create new enrollment
    new_enrollment = ClassEnrollment(
        student_id=student_id,
        class_schedule_id=class_schedule_id,
        enrollment_date=date.today()
    )
    
    db.add(new_enrollment)
    db.commit()
    return True, "Enrollment successful"

def add_course(course_data: dict, db: Session = None):
    """Add a new course."""
    if db is None:
        db = get_db()
    
    # Check if course code already exists
    existing_course = db.query(Course).filter(Course.course_code == course_data['course_code']).first()
    if existing_course:
        return False, "Course code already exists"
    
    new_course = Course(
        course_code=course_data['course_code'],
        title=course_data['title'],
        description=course_data.get('description', ''),
        department=course_data['department'],
        credit_hours=course_data['credit_hours']
    )
    
    db.add(new_course)
    db.commit()
    return True, "Course added successfully"

def add_class_schedule(schedule_data: dict, db: Session = None):
    """Add a new class schedule."""
    if db is None:
        db = get_db()
    
    new_schedule = ClassSchedule(
        course_id=schedule_data['course_id'],
        teacher_id=schedule_data['teacher_id'],
        day_of_week=schedule_data['day_of_week'],
        start_time=schedule_data['start_time'],
        end_time=schedule_data['end_time'],
        room_number=schedule_data['room_number'],
        semester=schedule_data['semester']
    )
    
    db.add(new_schedule)
    db.commit()
    return True, "Class schedule added successfully"

def show_schedule_management():
    st.header("Class Schedule Management")
    
    # Initialize the database session
    db = get_db()
    
    tabs = st.tabs(["View Schedule", "Courses", "Add Schedule"])
    
    with tabs[0]:
        st.subheader("Your Class Schedule")
        
        if st.session_state.authenticated:
            user_role = st.session_state.user_role
            username = st.session_state.username
            
            if user_role == 'student':
                # Get student ID from the database based on username
                student = db.query(Student).join(User).filter(User.username == username).first()
                
                if student:
                    schedule = get_student_schedule(student.id, db)
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
                else:
                    st.warning("Student record not found. Please contact an administrator.")
            
            elif user_role == 'teacher':
                # Get teacher ID from the database based on username
                teacher = db.query(Teacher).join(User).filter(User.username == username).first()
                
                if teacher:
                    schedule = get_teacher_schedule(teacher.id, db)
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
                else:
                    st.warning("Teacher record not found. Please contact an administrator.")
            
            elif user_role == 'admin':
                # Admin can see all schedules or filter by department/course
                st.subheader("Filter Options")
                filter_option = st.radio("Filter by:", ["All Schedules", "Course", "Department", "Teacher"])
                
                if filter_option == "All Schedules":
                    schedules = get_class_schedules(db=db)
                    if schedules:
                        df = pd.DataFrame(schedules)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No class schedules found.")
                
                elif filter_option == "Course":
                    courses = get_available_courses(db=db)
                    course_options = {f"{c['course_code']} - {c['title']}": c['id'] for c in courses}
                    
                    if course_options:
                        selected_course = st.selectbox("Select Course:", list(course_options.keys()))
                        course_id = course_options[selected_course]
                        
                        schedules = get_class_schedules(course_id=course_id, db=db)
                        if schedules:
                            df = pd.DataFrame(schedules)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("No schedules found for this course.")
                    else:
                        st.warning("No courses available. Add courses first.")
        else:
            st.warning("Please log in to view your schedule.")
    
    with tabs[1]:
        st.subheader("Course Management")
        
        if st.session_state.user_role == 'admin':
            course_tabs = st.tabs(["Available Courses", "Add Course"])
            
            with course_tabs[0]:
                courses = get_available_courses(db=db)
                if courses:
                    df = pd.DataFrame(courses)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No courses available.")
            
            with course_tabs[1]:
                with st.form("add_course_form"):
                    st.subheader("Add New Course")
                    course_code = st.text_input("Course Code (e.g., CS101)")
                    title = st.text_input("Course Title")
                    description = st.text_area("Description")
                    department = st.text_input("Department")
                    credit_hours = st.number_input("Credit Hours", min_value=1, max_value=6, value=3)
                    
                    submit = st.form_submit_button("Add Course")
                    if submit:
                        course_data = {
                            'course_code': course_code,
                            'title': title,
                            'description': description,
                            'department': department,
                            'credit_hours': credit_hours
                        }
                        
                        success, message = add_course(course_data, db)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        else:
            st.info("Courses available for enrollment will be shown here.")
            courses = get_available_courses(db=db)
            if courses:
                df = pd.DataFrame(courses)
                st.dataframe(df[['course_code', 'title', 'department', 'credit_hours']], use_container_width=True)
            else:
                st.info("No courses available.")
    
    with tabs[2]:
        if st.session_state.user_role == 'admin':
            st.subheader("Add Class Schedule")
            
            with st.form("add_schedule_form"):
                # Get courses for selection
                courses = get_available_courses(db=db)
                course_options = {f"{c['course_code']} - {c['title']}": c['id'] for c in courses}
                
                # Get teachers for selection
                teachers = db.query(Teacher).all()
                teacher_options = {t.name: t.id for t in teachers}
                
                if not course_options:
                    st.warning("No courses available. Add courses first.")
                    st.stop()
                
                if not teacher_options:
                    st.warning("No teachers available. Add teachers first.")
                    st.stop()
                
                selected_course = st.selectbox("Course:", list(course_options.keys()))
                selected_teacher = st.selectbox("Teacher:", list(teacher_options.keys()))
                
                day_of_week = st.selectbox("Day:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                
                start_time_str = st.time_input("Start Time:", time(8, 0))
                end_time_str = st.time_input("End Time:", time(9, 30))
                
                room_number = st.text_input("Room Number:")
                semester = st.text_input("Semester (e.g., Fall 2025):")
                
                submit = st.form_submit_button("Add Schedule")
                if submit:
                    schedule_data = {
                        'course_id': course_options[selected_course],
                        'teacher_id': teacher_options[selected_teacher],
                        'day_of_week': day_of_week,
                        'start_time': start_time_str,
                        'end_time': end_time_str,
                        'room_number': room_number,
                        'semester': semester
                    }
                    
                    success, message = add_class_schedule(schedule_data, db)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        elif st.session_state.user_role == 'student':
            st.subheader("Course Enrollment")
            
            # Get available class schedules
            schedules = get_class_schedules(db=db)
            if schedules:
                df = pd.DataFrame(schedules)
                st.dataframe(df, use_container_width=True)
                
                # Enrollment form
                with st.form("enroll_form"):
                    st.subheader("Enroll in a Class")
                    schedule_options = {f"{s['course_code']} - {s['course_title']} ({s['day']} {s['start_time']}-{s['end_time']})": s['id'] for s in schedules}
                    selected_class = st.selectbox("Select Class:", list(schedule_options.keys()))
                    
                    submit = st.form_submit_button("Enroll")
                    if submit:
                        # Get student ID
                        student = db.query(Student).join(User).filter(User.username == st.session_state.username).first()
                        
                        if student:
                            success, message = enroll_student(
                                student_id=student.id,
                                class_schedule_id=schedule_options[selected_class],
                                db=db
                            )
                            
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                        else:
                            st.error("Student record not found. Please contact an administrator.")
            else:
                st.info("No classes available for enrollment.")