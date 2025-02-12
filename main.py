import streamlit as st
from components import dashboard, student_management, teacher_management
from database import init_db

# Initialize database
init_db()

st.set_page_config(
    page_title="College Management System",
    page_icon="🎓",
    layout="wide"
)

def main():
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Student Management", "Teacher Management"]
    )

    # Page header
    st.title("College Management System")
    st.divider()

    # Page routing
    if page == "Dashboard":
        dashboard.show_dashboard()
    elif page == "Student Management":
        student_management.show_student_management()
    else:
        teacher_management.show_teacher_management()

if __name__ == "__main__":
    main()