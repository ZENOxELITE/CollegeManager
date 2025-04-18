import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Time, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

# Set up database URL using environment variables
try:
    # First try to use PostgreSQL if available
    if os.getenv("DATABASE_URL"):
        DATABASE_URL = os.getenv("DATABASE_URL")
        print("Attempting to connect to PostgreSQL database...")
        # Try to connect to test if credentials work
        import psycopg2
        conn_parts = DATABASE_URL.split("//")[1].split("@")
        user_pass = conn_parts[0].split(":")
        host_port_db = conn_parts[1].split("/")
        try:
            # Just testing connection, don't store
            conn = psycopg2.connect(
                host=host_port_db[0],
                database=host_port_db[1] if len(host_port_db) > 1 else "postgres",
                user=user_pass[0],
                password=user_pass[1] if len(user_pass) > 1 else ""
            )
            conn.close()
            print("PostgreSQL connection successful")
        except Exception as e:
            print(f"PostgreSQL connection failed: {str(e)}")
            print("Falling back to SQLite database")
            DATABASE_URL = "sqlite:///college_management.db"
    else:
        print("No DATABASE_URL found, using SQLite database")
        DATABASE_URL = "sqlite:///college_management.db"
except Exception as e:
    print(f"Error setting up database connection: {str(e)}")
    print("Falling back to SQLite database")
    DATABASE_URL = "sqlite:///college_management.db"

# Log database connection information for debugging (sanitized)
print(f"Using database: {'PostgreSQL' if 'postgres' in DATABASE_URL.lower() else 'SQLite'}")

# Configure SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False)
    
    # Relationships for one-to-one with Student/Teacher
    student = relationship("Student", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)

# Define Student model
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="student")
    enrollments = relationship("ClassEnrollment", back_populates="student")

# Define Teacher model
class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    subjects = Column(String(200), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="teacher")
    classes = relationship("ClassSchedule", back_populates="teacher")

# Define Course model
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    department = Column(String(100), nullable=False)
    credit_hours = Column(Integer, nullable=False)
    
    # Relationships
    class_schedules = relationship("ClassSchedule", back_populates="course")

# Define ClassSchedule model
class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    day_of_week = Column(String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room_number = Column(String(20), nullable=False)
    semester = Column(String(20), nullable=False)  # Fall 2025, Spring 2026, etc.
    
    # Relationships
    course = relationship("Course", back_populates="class_schedules")
    teacher = relationship("Teacher", back_populates="classes")
    enrollments = relationship("ClassEnrollment", back_populates="class_schedule")

# Define ClassEnrollment model (for many-to-many relationship between students and classes)
class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_schedule_id = Column(Integer, ForeignKey("class_schedules.id"), nullable=False)
    enrollment_date = Column(Date, nullable=False)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    class_schedule = relationship("ClassSchedule", back_populates="enrollments")

def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Database session generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
