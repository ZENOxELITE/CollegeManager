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
                    ["Dashboard", "Student Management", "Teacher Management", "User Management"],
                    horizontal=True,
                    key="nav_admin"
                )
            elif st.session_state.user_role == 'teacher':
                page = st.radio(
                    "Navigation",
                    ["Dashboard", "Student Management"],
                    horizontal=True,
                    key="nav_teacher"
                )
            else:  # student role
                page = st.radio(
                    "Navigation",
                    ["Dashboard"],
                    horizontal=True,
                    key="nav_student"
                )
    else:
        show_login_form()
        st.stop()

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