import streamlit as st
from components import dashboard, student_management, teacher_management
from utils import initialize_session_state
from auth import init_auth, show_login_form, logout

st.set_page_config(
    page_title="College Management System",
    page_icon="🎓",
    layout="wide"
)

def main():
    # Initialize session states
    initialize_session_state()
    init_auth()

    # Sidebar
    st.sidebar.title("Navigation")

    # Show authentication status and logout button
    if st.session_state.authenticated:
        st.sidebar.success(f"Logged in as: {st.session_state.username}")
        st.sidebar.success(f"Role: {st.session_state.user_role}")
        if st.sidebar.button("Logout"):
            logout()
            st.experimental_rerun()

        # Show navigation based on role
        if st.session_state.user_role == 'admin':
            page = st.sidebar.radio(
                "Go to",
                ["Dashboard", "Student Management", "Teacher Management", "User Management"]
            )
        elif st.session_state.user_role == 'teacher':
            page = st.sidebar.radio(
                "Go to",
                ["Dashboard", "Student Management"]
            )
        else:  # student role
            page = st.sidebar.radio(
                "Go to",
                ["Dashboard"]
            )
    else:
        show_login_form()
        st.stop()

    # Page header
    st.title("College Management System")
    st.divider()

    # Page routing with role-based access
    if page == "Dashboard":
        dashboard.show_dashboard()
    elif page == "Student Management" and st.session_state.user_role in ['admin', 'teacher']:
        student_management.show_student_management()
    elif page == "Teacher Management" and st.session_state.user_role == 'admin':
        teacher_management.show_teacher_management()
    elif page == "User Management" and st.session_state.user_role == 'admin':
        from auth import show_register_form
        st.header("User Management")
        show_register_form()
    else:
        st.error("You don't have permission to access this page")

if __name__ == "__main__":
    main()