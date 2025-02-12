import streamlit as st
from utils import validate_teacher_data, get_all_teachers
from database import Teacher, get_db

def show_teacher_management():
    st.header("Teacher Management")

    tab1, tab2, tab3 = st.tabs(["Add Teacher", "View/Edit Teachers", "Search Teachers"])

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
                    db = next(get_db())
                    try:
                        new_teacher = Teacher(
                            id=id,
                            name=name,
                            department=department,
                            subjects=subjects,
                            email=email,
                            phone=phone
                        )
                        db.add(new_teacher)
                        db.commit()
                        st.success("Teacher added successfully!")
                    except Exception as e:
                        st.error(f"Error adding teacher: {str(e)}")
                    finally:
                        db.close()
                else:
                    st.error(message)

    with tab2:
        teachers_df = get_all_teachers()
        if not teachers_df.empty:
            st.subheader("All Teachers")
            st.dataframe(teachers_df, use_container_width=True)
        else:
            st.info("No teachers registered yet")

    with tab3:
        st.subheader("Search Teachers")
        search_term = st.text_input("Search by Name or ID")
        if search_term:
            result = teachers_df[
                teachers_df['Name'].str.contains(search_term, case=False) |
                teachers_df['ID'].str.contains(search_term, case=False)
            ]
            if not result.empty:
                st.dataframe(result)
            else:
                st.warning("No matching records found")