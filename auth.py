import streamlit as st
import hashlib
from typing import Optional, Tuple
from database import User, SessionLocal

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
    
    # Check if admin user exists, if not create one
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            # Create default admin user
            admin_user = User(
                username='admin',
                password=hash_password('admin123'),
                role='admin'
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created")
    except Exception as e:
        print(f"Error checking for admin user: {str(e)}")
    finally:
        db.close()

def login(username: str, password: str) -> bool:
    """Authenticate a user and set up their session using database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and user.password == hash_password(password):
            st.session_state.authenticated = True
            st.session_state.user_role = user.role
            st.session_state.username = username
            return True
        return False
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False
    finally:
        db.close()

def logout():
    """Clear the session state."""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None

def register_user(username: str, password: str, role: str) -> Tuple[bool, str]:
    """Register a new user in the database."""
    if role not in ['admin', 'teacher', 'student']:
        return False, "Invalid role"
    
    db = SessionLocal()
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists"
        
        # Create new user
        new_user = User(
            username=username,
            password=hash_password(password),
            role=role
        )
        db.add(new_user)
        db.commit()
        return True, "User registered successfully"
    except Exception as e:
        db.rollback()
        return False, f"Registration error: {str(e)}"
    finally:
        db.close()

def show_login_form():
    """Display the login form."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=True):
            st.subheader("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

def show_register_form():
    """Display the registration form."""
    if st.session_state.get('user_role') != 'admin':
        st.error("Only administrators can register new users")
        return

    with st.form("register_form", clear_on_submit=True):
        st.subheader("📝 Register New User")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ['teacher', 'student'])
        submitted = st.form_submit_button("Register User", use_container_width=True)

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