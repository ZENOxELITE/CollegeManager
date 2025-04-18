import streamlit as st
import pandas as pd
from datetime import datetime
import os

from database import get_db, Student, Teacher, ClassSchedule, Course, ClassEnrollment
from send_message import send_twilio_message, send_notification_to_student, send_class_notification

def show_notifications():
    """Display the notifications management component."""
    st.header("📲 Notifications")
    
    # Check if Twilio is configured
    twilio_configured = all([
        os.environ.get("TWILIO_ACCOUNT_SID"),
        os.environ.get("TWILIO_AUTH_TOKEN"),
        os.environ.get("TWILIO_PHONE_NUMBER")
    ])
    
    if not twilio_configured:
        st.warning(
            "Twilio is not configured. Please set the following environment variables to enable SMS notifications:\n"
            "- TWILIO_ACCOUNT_SID\n"
            "- TWILIO_AUTH_TOKEN\n"
            "- TWILIO_PHONE_NUMBER"
        )
        
        # Show configuration form
        with st.expander("Configure Twilio"):
            st.info("Enter your Twilio credentials. These will be stored as environment variables for the current session.")
            
            with st.form("twilio_config_form"):
                account_sid = st.text_input("Account SID", placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                auth_token = st.text_input("Auth Token", type="password", placeholder="your_auth_token")
                phone_number = st.text_input("Twilio Phone Number", placeholder="+1234567890")
                
                submitted = st.form_submit_button("Save Configuration")
                
                if submitted:
                    if account_sid and auth_token and phone_number:
                        # Set environment variables
                        os.environ["TWILIO_ACCOUNT_SID"] = account_sid
                        os.environ["TWILIO_AUTH_TOKEN"] = auth_token
                        os.environ["TWILIO_PHONE_NUMBER"] = phone_number
                        
                        st.success("Twilio configuration saved for this session")
                        st.rerun()
                    else:
                        st.error("Please fill in all fields")
    
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
                    help="This message will be sent as an SMS to the student's phone number."
                )
                
                submitted = st.form_submit_button("Send Notification")
                
                if submitted:
                    if message:
                        student_id = student_options[student_selection]
                        
                        # Display a spinner while sending
                        with st.spinner("Sending notification..."):
                            # Send notification
                            result = send_notification_to_student(student_id, message, db)
                            
                            if result["success"]:
                                st.success(result["message"])
                            else:
                                st.error(result["message"])
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
                    help="This message will be sent as an SMS to all students enrolled in the selected class."
                )
                
                submitted = st.form_submit_button("Send to All Enrolled Students")
                
                if submitted:
                    if message:
                        class_id = class_options[class_selection]
                        
                        # Display a spinner while sending
                        with st.spinner("Sending notifications..."):
                            # Send notifications
                            result = send_class_notification(class_id, message, db)
                            
                            if result["success"]:
                                st.success(result["message"])
                                
                                # Show details in an expander
                                with st.expander("Details"):
                                    # Create a DataFrame for the results
                                    details_df = pd.DataFrame(result["details"])
                                    if not details_df.empty:
                                        st.dataframe(details_df)
                                    else:
                                        st.info("No details available")
                            else:
                                st.error(result["message"])
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
        
        if recipient_type == "All Students":
            # Get count of all students
            student_count = db.query(Student).count()
            st.info(f"This will send to all {student_count} students in the database.")
            
            recipients = db.query(Student).all()
            
        elif recipient_type == "By Department":
            # Get all unique departments
            departments = db.query(Student.department).distinct().all()
            department_list = [dept[0] for dept in departments]
            
            selected_dept = st.selectbox("Select Department", department_list)
            
            # Get students in the selected department
            recipients = db.query(Student).filter(Student.department == selected_dept).all()
            st.info(f"This will send to {len(recipients)} students in the {selected_dept} department.")
            
        elif recipient_type == "By Year":
            # Get all unique years
            years = db.query(Student.year).distinct().all()
            year_list = [year[0] for year in years]
            
            selected_year = st.selectbox("Select Year", year_list)
            
            # Get students in the selected year
            recipients = db.query(Student).filter(Student.year == selected_year).all()
            st.info(f"This will send to {len(recipients)} students in Year {selected_year}.")
            
        elif recipient_type == "Custom List":
            # Get all students
            all_students = db.query(Student).all()
            
            # Create multiselect with student names
            selected_students = st.multiselect(
                "Select Students",
                options=[f"{s.id}: {s.name}" for s in all_students],
                default=[]
            )
            
            # Extract IDs from selections
            selected_ids = [int(s.split(":")[0]) for s in selected_students]
            
            # Get selected students
            recipients = db.query(Student).filter(Student.id.in_(selected_ids)).all()
            st.info(f"This will send to {len(recipients)} selected students.")
        
        # Message input
        message = st.text_area(
            "Message", 
            placeholder="Enter your message here",
            help="This message will be sent as an SMS to all selected recipients."
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
                # Display a spinner while sending
                with st.spinner(f"Sending to {len(recipients)} recipients..."):
                    # Collect results
                    results = {
                        "success": True,
                        "total": len(recipients),
                        "sent": 0,
                        "failed": 0,
                        "details": []
                    }
                    
                    # Send to each recipient
                    for student in recipients:
                        # Format phone number for Twilio
                        phone = student.phone
                        if not phone.startswith('+'):
                            phone = f"+{phone}"
                        
                        # Send message
                        result = send_twilio_message(phone, message)
                        
                        # Update results
                        if result["success"]:
                            results["sent"] += 1
                        else:
                            results["failed"] += 1
                        
                        results["details"].append({
                            "student_id": student.id,
                            "student_name": student.name,
                            "success": result["success"],
                            "message": result["message"]
                        })
                    
                    # Show results
                    if results["failed"] == results["total"]:
                        st.error(f"Failed to send all {results['total']} messages")
                    elif results["failed"] > 0:
                        st.warning(f"Sent {results['sent']} messages, {results['failed']} failed")
                    else:
                        st.success(f"Successfully sent all {results['total']} messages")
                    
                    # Show details in an expander
                    with st.expander("Detailed Results"):
                        # Create a DataFrame for the results
                        details_df = pd.DataFrame(results["details"])
                        if not details_df.empty:
                            st.dataframe(details_df)
                        else:
                            st.info("No details available")
    
    # Close the database session
    db.close()