import streamlit as st
import pandas as pd
from utils import validate_teacher_data

def show_teacher_management():
    st.header("Teacher Management")

    tab1, tab2, tab3 = st.tabs(["Add Teacher", "View/Edit Teachers", "Search Teachers"])

    if "teachers" not in st.session_state:
        st.session_state.teachers = pd.DataFrame(columns=['ID', 'Name', 'Department', 'Subjects', 'Email', 'Phone'])

    with tab1:
        with st.form("add_teacher_form"):
            st.subheader("Add New Teacher")
            id = st.text_input("Teacher ID")
            name = st.text_input("Name")
            department = st.selectbox(
                "Department",
                ["Computer Science", "Electronics", "Mechanical", "Civil", "Chemical"]
            )
            subjects = st.text_input("Subjects (comma-separated)")
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
                    st.success("Teacher added successfully!")
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
        search_term = st.text_input("Search by Name or ID")
        if search_term:
            result = st.session_state.teachers[
                st.session_state.teachers['Name'].str.contains(search_term, case=False) |
                st.session_state.teachers['ID'].str.contains(search_term, case=False)
            ]
            if not result.empty:
                st.dataframe(result)
            else:
                st.warning("No matching records found")