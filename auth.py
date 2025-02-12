import streamlit as st
import hashlib
from typing import Optional

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_auth():
    """Initialize authentication state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'users' not in st.session_state:
        # Initialize with a default admin user
        st.session_state.users = {
            'admin': {
                'password': hash_password('admin123'),
                'role': 'admin'
            }
        }

def login(username: str, password: str) -> bool:
    """Authenticate a user and set up their session."""
    if username in st.session_state.users:
        if st.session_state.users[username]['password'] == hash_password(password):
            st.session_state.authenticated = True
            st.session_state.user_role = st.session_state.users[username]['role']
            st.session_state.username = username
            return True
    return False

def logout():
    """Clear the session state."""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None

def register_user(username: str, password: str, role: str) -> tuple[bool, str]:
    """Register a new user."""
    if username in st.session_state.users:
        return False, "Username already exists"
    if role not in ['admin', 'teacher', 'student']:
        return False, "Invalid role"

    st.session_state.users[username] = {
        'password': hash_password(password),
        'role': role
    }
    return True, "User registered successfully"

def show_login_form():
    """Display the login form."""
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if login(username, password):
                st.success("Logged in successfully!")
                st.rerun()  # Using st.rerun() instead of experimental_rerun
            else:
                st.error("Invalid username or password")

def show_register_form():
    """Display the registration form."""
    if st.session_state.get('user_role') != 'admin':
        st.error("Only administrators can register new users")
        return

    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ['teacher', 'student'])
        submitted = st.form_submit_button("Register User")

        if submitted:
            success, message = register_user(username, password, role)
            if success:
                st.success(message)
            else:
                st.error(message)

def require_auth(role: Optional[str] = None):
    """Decorator to require authentication and optionally a specific role."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.authenticated:
                st.error("Please log in to access this page")
                show_login_form()
                return
            
            if role and st.session_state.user_role != role and st.session_state.user_role != 'admin':
                st.error("You don't have permission to access this page")
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator