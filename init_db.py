# init_db.py
from db_config import Base, engine
from database import User, Student, Teacher, Course, ClassSchedule, ClassEnrollment
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/college_management"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def init_db():
    """Initialize database tables and default data"""
    Base.metadata.create_all(bind=engine)
    
    # Add default admin user
    from auth import hash_password
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == 'admin').first():
            admin = User(
                username='admin',
                password=hash_password('admin123'),
                role='admin'
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin user created")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()