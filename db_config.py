# db_config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Database configuration
DB_CONFIG = {
    'mysql': {
        'driver': 'pymysql',
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'college_management'),
        'port': os.getenv('DB_PORT', '3306')
    },
    'sqlite': {
        'file': 'college_management.db'
    }
}

def get_db_engine():
    """Create and return database engine based on configuration"""
    try:
        # Try MySQL first
        mysql_config = DB_CONFIG['mysql']
        db_url = f"mysql+{mysql_config['driver']}://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"
        engine = create_engine(db_url, pool_pre_ping=True)
        engine.connect()  # Test connection
        print("✅ Connected to MySQL database")
        return engine
    except Exception as e:
        print(f"⚠️ MySQL connection failed: {e}. Falling back to SQLite")
        sqlite_config = DB_CONFIG['sqlite']
        return create_engine(f"sqlite:///{sqlite_config['file']}", connect_args={"check_same_thread": False})

# Create engine and session
engine = get_db_engine()
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

def get_db():
    """Database session generator for FastAPI dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()