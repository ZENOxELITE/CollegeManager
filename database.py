import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Configure SQLAlchemy with proper connection parameters
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections every hour
)

SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    subjects = Column(String(200), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)

def init_db():
    """Initialize database and create tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

def get_db():
    """Database session generator with error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise
    finally:
        db.close()