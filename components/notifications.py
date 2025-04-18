import streamlit as st
import pandas as pd
from datetime import datetime

from database import get_db, Student, Teacher, ClassSchedule, Course, ClassEnrollment

def show_notifications():
    """Display the notifications management component."""
    st.header("📧 Notifications")
    
    # Message about using email or other notification methods
    st.info("This is a simplified notification dashboard. In a production environment, you would connect to an email service or other notification system.")
    
    # Tabs for different notification types
    tab1, tab2, tab3 = st.tabs(["Individual Notifications", "Class Notifications", "Bulk Notifications"])
    
    db = next(get_db())
    
    # Individual Notifications Tab
    with tab1:
        st.subheader("Send to Individual Student")
        
        # Get all students
        students = db.query(Student).all()
        student_options = {f"{s.id}: {s.name}": s.id for s in students}
        
        if not student_options:
            st.info("No students found in the database. Please add students first.")
        else:
            with st.form("individual_notification_form"):
                student_selection = st.selectbox(
                    "Select Student", 
                    options=list(student_options.keys()),
                    index=0 if student_options else None
                )
                
                message = st.text_area(
                    "Message", 
                    placeholder="Enter your message here",
                    help="This would be sent as an email or notification to the student."
                )
                
                submitted = st.form_submit_button("Send Notification")
                
                if submitted:
                    if message:
                        student_id = student_options[student_selection]
                        student = db.query(Student).filter(Student.id == student_id).first()
                        
                        if student:
                            st.success(f"Message would be sent to {student.name} ({student.email})")
                            st.code(message)
                        else:
                            st.error("Student not found")
                    else:
                        st.error("Please enter a message")
    
    # Class Notifications Tab
    with tab2:
        st.subheader("Send to All Students in a Class")
        
        # Get all classes with course and teacher info
        class_schedules = db.query(
            ClassSchedule, Course, Teacher
        ).join(
            Course, ClassSchedule.course_id == Course.id
        ).join(
            Teacher, ClassSchedule.teacher_id == Teacher.id
        ).all()
        
        class_options = {}
        for cs, course, teacher in class_schedules:
            class_options[f"{course.course_code}: {course.title} ({teacher.name}, {cs.day_of_week})"] = cs.id
        
        if not class_options:
            st.info("No classes found in the database. Please add class schedules first.")
        else:
            with st.form("class_notification_form"):
                class_selection = st.selectbox(
                    "Select Class", 
                    options=list(class_options.keys()),
                    index=0 if class_options else None
                )
                
                message = st.text_area(
                    "Message", 
                    placeholder="Enter your message here",
                    help="This would be sent as an email or notification to all students enrolled in the selected class."
                )
                
                submitted = st.form_submit_button("Send to All Enrolled Students")
                
                if submitted:
                    if message:
                        class_id = class_options[class_selection]
                        
                        # Get enrollments for this class
                        enrollments = db.query(ClassEnrollment).filter(ClassEnrollment.class_schedule_id == class_id).all()
                        student_ids = [e.student_id for e in enrollments]
                        students = db.query(Student).filter(Student.id.in_(student_ids)).all()
                        
                        if students:
                            st.success(f"Message would be sent to {len(students)} students enrolled in {class_selection}")
                            
                            # Show recipients in an expander
                            with st.expander("Recipients"):
                                recipients_df = pd.DataFrame([
                                    {
                                        "ID": s.id,
                                        "Name": s.name,
                                        "Email": s.email,
                                        "Phone": s.phone
                                    }
                                    for s in students
                                ])
                                st.dataframe(recipients_df)
                            
                            st.code(message)
                        else:
                            st.warning("No students enrolled in this class")
                    else:
                        st.error("Please enter a message")
    
    # Bulk Notifications Tab
    with tab3:
        st.subheader("Send to Multiple Recipients")
        
        # Options for recipient types
        recipient_type = st.radio(
            "Select Recipients",
            options=["All Students", "By Department", "By Year", "Custom List"]
        )
        
        recipients = []
        
        if recipient_type == "All Students":
            # Get count of all students
            student_count = db.query(Student).count()
            st.info(f"This will send to all {student_count} students in the database.")
            
            recipients = db.query(Student).all()
            
        elif recipient_type == "By Department":
            # Get all unique departments
            departments = db.query(Student.department).distinct().all()
            department_list = [dept[0] for dept in departments]
            
            if department_list:
                selected_dept = st.selectbox("Select Department", department_list)
                
                # Get students in the selected department
                recipients = db.query(Student).filter(Student.department == selected_dept).all()
                st.info(f"This will send to {len(recipients)} students in the {selected_dept} department.")
            else:
                st.warning("No departments found")
            
        elif recipient_type == "By Year":
            # Get all unique years
            years = db.query(Student.year).distinct().all()
            year_list = [year[0] for year in years]
            
            if year_list:
                selected_year = st.selectbox("Select Year", year_list)
                
                # Get students in the selected year
                recipients = db.query(Student).filter(Student.year == selected_year).all()
                st.info(f"This will send to {len(recipients)} students in Year {selected_year}.")
            else:
                st.warning("No year data found")
            
        elif recipient_type == "Custom List":
            # Get all students
            all_students = db.query(Student).all()
            
            if all_students:
                # Create multiselect with student names
                selected_students = st.multiselect(
                    "Select Students",
                    options=[f"{s.id}: {s.name}" for s in all_students],
                    default=[]
                )
                
                # Extract IDs from selections
                if selected_students:
                    selected_ids = [int(s.split(":")[0]) for s in selected_students]
                    
                    # Get selected students
                    recipients = db.query(Student).filter(Student.id.in_(selected_ids)).all()
                    st.info(f"This will send to {len(recipients)} selected students.")
            else:
                st.warning("No students in database")
        
        # Message input
        message = st.text_area(
            "Message", 
            placeholder="Enter your message here",
            help="This would be sent as an email or notification to all selected recipients."
        )
        
        # Preview recipients in an expander
        with st.expander("Preview Recipients"):
            if recipients:
                # Create DataFrame for recipients
                recipients_df = pd.DataFrame([
                    {
                        "ID": r.id,
                        "Name": r.name,
                        "Department": r.department,
                        "Year": r.year,
                        "Email": r.email,
                        "Phone": r.phone
                    }
                    for r in recipients
                ])
                st.dataframe(recipients_df)
            else:
                st.info("No recipients selected")
        
        # Send button
        if st.button("Send Bulk Notification"):
            if not message:
                st.error("Please enter a message")
            elif not recipients:
                st.error("No recipients selected")
            else:
                st.success(f"Message would be sent to {len(recipients)} recipients")
                st.code(message)
    
    # Close the database session
    db.close()