import streamlit as st
import pandas as pd
from utils import validate_student_data
from database import Student, get_db

def show_student_management():
    st.header("Student Management")

    tab1, tab2, tab3 = st.tabs(["Add Student", "View/Edit Students", "Search Students"])

    with tab1:
        with st.form("add_student_form"):
            st.subheader("Add New Student")
            id = st.text_input("Student ID")
            name = st.text_input("Name")
            department = st.selectbox(
                "Department",
                ["Computer Science", "Electronics", "Mechanical", "Civil", "Chemical"]
            )
            year = st.selectbox("Year", [1, 2, 3, 4])
            email = st.text_input("Email")
            phone = st.text_input("Phone")

            submitted = st.form_submit_button("Add Student")
            if submitted:
                valid, message = validate_student_data(id, name, department, year, email, phone)
                if valid:
                    db = next(get_db())
                    try:
                        new_student = Student(
                            id=id,
                            name=name,
                            department=department,
                            year=year,
                            email=email,
                            phone=phone
                        )
                        db.add(new_student)
                        db.commit()
                        st.success("Student added successfully!")
                    except Exception as e:
                        st.error(f"Error adding student: {str(e)}")
                    finally:
                        db.close()
                else:
                    st.error(message)

    with tab2:
        from utils import get_all_students
        students_df = get_all_students()
        if not students_df.empty:
            st.subheader("All Students")
            st.dataframe(students_df, use_container_width=True)
        else:
            st.info("No students registered yet")

    with tab3:
        st.subheader("Search Students")
        search_term = st.text_input("Search by Name or ID")
        if search_term:
            students_df = get_all_students()
            result = students_df[
                students_df['Name'].str.contains(search_term, case=False) |
                students_df['ID'].str.contains(search_term, case=False)
            ]
            if not result.empty:
                st.dataframe(result)
            else:
                st.warning("No matching records found")