import streamlit as st
import pandas as pd
from utils import validate_student_data

def show_student_management():
    st.header("Student Management")

    if "students" not in st.session_state:
        st.session_state.students = pd.DataFrame(columns=['ID', 'Name', 'Department', 'Year', 'Email', 'Phone'])

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
                    new_student = pd.DataFrame([{
                        'ID': id,
                        'Name': name,
                        'Department': department,
                        'Year': year,
                        'Email': email,
                        'Phone': phone
                    }])
                    st.session_state.students = pd.concat([st.session_state.students, new_student], ignore_index=True)
                    st.success("Student added successfully!")
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