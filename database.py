        import os
        from sqlalchemy import create_engine, Column, Integer, String
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker, scoped_session

        # Set up database URL (change this as needed)
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///college_management.db")

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

        # Define Student model
        class Student(Base):
            __tablename__ = "students"
            id = Column(Integer, primary_key=True, index=True)
            name = Column(String(100), nullable=False)
            department = Column(String(100), nullable=False)
            year = Column(Integer, nullable=False)
            email = Column(String(100), nullable=False)
            phone = Column(String(20), nullable=False)

        # Define Teacher model
        class Teacher(Base):
            __tablename__ = "teachers"
            id = Column(Integer, primary_key=True, index=True)
            name = Column(String(100), nullable=False)
            department = Column(String(100), nullable=False)
            subjects = Column(String(200), nullable=False)
            email = Column(String(100), nullable=False)
            phone = Column(String(20), nullable=False)

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
