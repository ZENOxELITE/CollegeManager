import streamlit as st
from components import dashboard, student_management, teacher_management, class_schedule, notifications, database_diagnostics
from utils import initialize_session_state
from auth import init_auth, show_login_form, logout
from database import init_db


st.set_page_config(
    page_title="College Management System",
    page_icon="🎓",
    layout="wide"
)

# Initialize theme setting in session state if not present
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Function to toggle theme
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    st.rerun()

# Set CSS based on selected theme
light_theme_css = """
<style>
    /* Light theme styles */
    body {
        color: #262730;
        background-color: #ffffff;
    }
    .main {
        background-color: #ffffff;
    }
    .stButton>button {
        min-height: 40px;
        width: 100%;
        background-color: #f0f2f6;
        color: #262730;
    }
    .css-1qg05tj {
        background-color: #f0f2f6;
        color: #262730;
    }
    .stTextInput>div>div>input {
        min-height: 40px;
    }
    /* Better spacing for mobile */
    @media (max-width: 640px) {
        .main {
            padding: 1rem 0.5rem;
        }
        .stRadio > label {
            font-size: 14px;
            padding: 0.25rem 0.5rem;
        }
    }
    /* Navigation styling */
    .nav-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
"""

dark_theme_css = """
<style>
    /* Dark theme styles */
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton>button {
        min-height: 40px;
        width: 100%;
        background-color: #262730;
        color: #fafafa;
    }
    .css-1qg05tj {
        background-color: #262730;
        color: #fafafa;
    }
    .stTextInput>div>div>input {
        min-height: 40px;
    }
    /* Better spacing for mobile */
    @media (max-width: 640px) {
        .main {
            padding: 1rem 0.5rem;
        }
        .stRadio > label {
            font-size: 14px;
            padding: 0.25rem 0.5rem;
        }
    }
    /* Navigation styling */
    .nav-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
"""

# Apply the appropriate CSS based on current theme
if st.session_state.theme == 'light':
    st.markdown(light_theme_css, unsafe_allow_html=True)
else:
    st.markdown(dark_theme_css, unsafe_allow_html=True)

def main():
    # Initialize session states
    initialize_session_state()
    init_auth()
    
    # Add theme toggle in sidebar
    with st.sidebar:
        st.subheader("🎨 Theme Settings")
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        theme_label = f"{theme_icon} Switch to {('Dark' if st.session_state.theme == 'light' else 'Light')} Mode"
        if st.button(theme_label, key="theme_toggle"):
            toggle_theme()
        st.divider()

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
                    ["Dashboard", "Student Management", "Teacher Management", "Class Schedule", "Notifications", "User Management", "Database Diagnostics"],
                    horizontal=True,
                    key="nav_admin"
                )
            elif st.session_state.user_role == 'teacher':
                page = st.radio(
                    "Navigation",
                    ["Dashboard", "Student Management", "Class Schedule", "Notifications"],
                    horizontal=True,
                    key="nav_teacher"
                )
            else:  # student role
                page = st.radio(
                    "Navigation",
                    ["Dashboard", "Class Schedule"],
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
    elif page == "Class Schedule":
        # All roles have access to class schedule, but with different permissions
        class_schedule.show_schedule_management()
    elif page == "User Management" and st.session_state.user_role == 'admin':
        from auth import show_register_form
        st.header("User Management")
        show_register_form()
    elif page == "Notifications" and st.session_state.user_role in ['admin', 'teacher']:
        notifications.show_notifications()
    elif page == "Database Diagnostics" and st.session_state.user_role == 'admin':
        database_diagnostics.show_database_diagnostics()
    else:
        st.error("You don't have permission to access this page")

if __name__ == "__main__":
    main()