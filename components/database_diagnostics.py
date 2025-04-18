import streamlit as st
import pandas as pd
import os
import sys
import traceback
import pymysql
from datetime import datetime

def show_database_diagnostics():
    """Display the database diagnostics component."""
    st.header("🔍 Database Diagnostics")
    
    # Tabs for different database functions
    tab1, tab2, tab3 = st.tabs(["Connection Test", "Database Setup", "Configuration"])
    
    # Get current MySQL configuration from environment or default values
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_user = os.environ.get("MYSQL_USER", "root")
    mysql_password = os.environ.get("MYSQL_PASSWORD", "")
    mysql_database = os.environ.get("MYSQL_DATABASE", "college_management")
    mysql_port = int(os.environ.get("MYSQL_PORT", "3306"))
    
    # Connection Test Tab
    with tab1:
        st.subheader("Test Database Connection")
        
        connection_method = st.radio(
            "Connection Method",
            ["Standard MySQL Connection", "PyMySQL Direct", "SQLAlchemy Connection", "Environment Check"]
        )
        
        if st.button("Run Connection Test"):
            with st.spinner("Testing database connection..."):
                if connection_method == "Standard MySQL Connection":
                    test_standard_mysql_connection(mysql_host, mysql_user, mysql_password, mysql_database, mysql_port)
                elif connection_method == "PyMySQL Direct":
                    test_pymysql_connection(mysql_host, mysql_user, mysql_password, mysql_database, mysql_port)
                elif connection_method == "SQLAlchemy Connection":
                    test_sqlalchemy_connection(mysql_host, mysql_user, mysql_password, mysql_database, mysql_port)
                elif connection_method == "Environment Check":
                    check_environment_variables()
    
    # Database Setup Tab
    with tab2:
        st.subheader("Set Up Database")
        
        st.info(
            "This utility will help you set up your database structure. "
            "It will create the necessary tables for the College Management System."
        )
        
        setup_method = st.radio(
            "Setup Method",
            ["Run SQL Script", "Use Database ORM", "PHP Setup Script"]
        )
        
        if setup_method == "Run SQL Script":
            show_sql_script_setup()
        elif setup_method == "Use Database ORM":
            show_orm_setup()
        elif setup_method == "PHP Setup Script":
            show_php_setup()
    
    # Configuration Tab
    with tab3:
        st.subheader("Database Configuration")
        
        st.info(
            "Update your database connection settings here. "
            "These settings will be used for this session only unless you save them to environment variables."
        )
        
        with st.form("database_config_form"):
            config_host = st.text_input("Host", value=mysql_host)
            config_user = st.text_input("Username", value=mysql_user)
            config_password = st.text_input("Password", type="password", value=mysql_password)
            config_database = st.text_input("Database Name", value=mysql_database)
            config_port = st.number_input("Port", value=mysql_port, min_value=1, max_value=65535)
            
            save_to_env = st.checkbox("Save to Environment Variables")
            
            submitted = st.form_submit_button("Save Configuration")
            
            if submitted:
                # Save configuration
                os.environ["MYSQL_HOST"] = config_host
                os.environ["MYSQL_USER"] = config_user
                os.environ["MYSQL_PASSWORD"] = config_password
                os.environ["MYSQL_DATABASE"] = config_database
                os.environ["MYSQL_PORT"] = str(config_port)
                
                if save_to_env:
                    try:
                        # Save to .env file
                        with open(".env", "w") as f:
                            f.write(f"MYSQL_HOST={config_host}\n")
                            f.write(f"MYSQL_USER={config_user}\n")
                            f.write(f"MYSQL_PASSWORD={config_password}\n")
                            f.write(f"MYSQL_DATABASE={config_database}\n")
                            f.write(f"MYSQL_PORT={config_port}\n")
                        
                        st.success("Configuration saved to .env file. You'll need to restart the application for changes to take effect.")
                    except Exception as e:
                        st.error(f"Error saving to .env file: {str(e)}")
                else:
                    st.success("Configuration saved for this session. These settings will be lost when you restart the application.")
                
                # Show database URL
                st.code(f"mysql+pymysql://{config_user}:{config_password}@{config_host}:{config_port}/{config_database}")


def test_standard_mysql_connection(host, user, password, database, port):
    """Test a standard MySQL connection."""
    try:
        # Standard MySQL connection using pymysql
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connect_timeout=10
        )
        
        # Test if we can get database version
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
        
        # Close connection
        connection.close()
        
        # Show success message
        st.success(f"✅ Successfully connected to MySQL database at {host}:{port}")
        st.info(f"MySQL Version: {version[0]}")
        
        # Test tables
        test_database_tables(host, user, password, database, port)
        
    except Exception as e:
        st.error(f"❌ Error connecting to MySQL database: {str(e)}")
        st.error(f"Exception type: {type(e).__name__}")
        st.expander("Stack trace").code(traceback.format_exc())
        
        # Provide suggestions based on the error
        provide_error_suggestions(e)


def test_pymysql_connection(host, user, password, database, port):
    """Test a PyMySQL connection with more detailed error handling."""
    try:
        # First try connecting to the server without specifying the database
        server_connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            connect_timeout=10
        )
        
        st.success(f"✅ Successfully connected to MySQL server at {host}:{port}")
        
        # Now check if the database exists
        with server_connection.cursor() as cursor:
            cursor.execute(f"SHOW DATABASES LIKE '{database}'")
            result = cursor.fetchone()
            
            if result:
                st.success(f"✅ Database '{database}' exists")
            else:
                st.warning(f"⚠️ Database '{database}' does not exist")
                st.info("You need to create the database first. You can do this in the 'Database Setup' tab.")
                
                # Offer to create the database
                if st.button("Create Database"):
                    try:
                        with server_connection.cursor() as create_cursor:
                            create_cursor.execute(f"CREATE DATABASE {database}")
                        st.success(f"✅ Database '{database}' created successfully")
                    except Exception as create_e:
                        st.error(f"❌ Error creating database: {str(create_e)}")
        
        # Close server connection
        server_connection.close()
        
        # Now try connecting to the specific database
        try:
            db_connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                connect_timeout=10
            )
            
            st.success(f"✅ Successfully connected to database '{database}'")
            
            # Check for tables
            with db_connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if tables:
                    table_list = [table[0] for table in tables]
                    st.success(f"✅ Found {len(table_list)} tables in the database")
                    st.json(table_list)
                else:
                    st.warning("⚠️ No tables found in the database")
                    st.info("You need to create tables. Go to the 'Database Setup' tab to set up the database schema.")
            
            # Close database connection
            db_connection.close()
            
        except Exception as db_e:
            st.error(f"❌ Error connecting to database '{database}': {str(db_e)}")
        
    except Exception as e:
        st.error(f"❌ Error connecting to MySQL server: {str(e)}")
        st.error(f"Exception type: {type(e).__name__}")
        st.expander("Stack trace").code(traceback.format_exc())
        
        # Provide suggestions based on the error
        provide_error_suggestions(e)


def test_sqlalchemy_connection(host, user, password, database, port):
    """Test an SQLAlchemy connection."""
    try:
        from sqlalchemy import create_engine, text
        
        # Create engine
        conn_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(conn_string)
        
        # Test connection by executing a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
        
        # Show success message
        st.success(f"✅ Successfully connected to MySQL database at {host}:{port} using SQLAlchemy")
        st.info(f"MySQL Version: {version}")
        
        # Test ORM
        try:
            from sqlalchemy.ext.declarative import declarative_base
            from sqlalchemy.orm import sessionmaker
            
            # Create session
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            # Try a simple ORM query
            db.execute(text("SELECT 1"))
            
            st.success("✅ SQLAlchemy ORM working correctly")
            
            # Close session
            db.close()
            
        except Exception as orm_e:
            st.error(f"❌ Error with SQLAlchemy ORM: {str(orm_e)}")
        
    except Exception as e:
        st.error(f"❌ Error connecting to MySQL database using SQLAlchemy: {str(e)}")
        st.error(f"Exception type: {type(e).__name__}")
        st.expander("Stack trace").code(traceback.format_exc())
        
        # Provide suggestions based on the error
        provide_error_suggestions(e)


def check_environment_variables():
    """Check environment variables for database configuration."""
    env_vars = [
        "MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE", "MYSQL_PORT",
        "DATABASE_URL", "REPLIT_DB_URL"
    ]
    
    st.subheader("Environment Variables")
    
    # Check each environment variable
    env_data = []
    for var in env_vars:
        value = os.environ.get(var)
        status = "✅ Set" if value else "❌ Not set"
        
        # Mask passwords
        if var == "MYSQL_PASSWORD" and value:
            value = "********"
        elif var == "DATABASE_URL" and value:
            # Mask the password in the URL if present
            parts = value.split(":")
            if len(parts) > 2:
                parts[2] = "********" + parts[2].split("@")[1]
                value = ":".join(parts)
        
        env_data.append({"Variable": var, "Status": status, "Value": value if value else ""})
    
    # Display environment variables as a table
    st.table(pd.DataFrame(env_data))
    
    # Check database type
    if "DATABASE_URL" in os.environ:
        url = os.environ.get("DATABASE_URL", "")
        if "mysql" in url.lower():
            st.info("Using MySQL database (from DATABASE_URL)")
        elif "postgresql" in url.lower():
            st.info("Using PostgreSQL database (from DATABASE_URL)")
        elif "sqlite" in url.lower():
            st.info("Using SQLite database (from DATABASE_URL)")
        else:
            st.info(f"Using unknown database type: {url.split(':')[0]}")
    else:
        st.info("DATABASE_URL not set, will use MySQL (if configured) or fall back to SQLite")
    
    # Check Python version
    st.subheader("Python Environment")
    st.info(f"Python Version: {sys.version}")
    
    # Check PyMySQL
    try:
        st.info(f"PyMySQL Version: {pymysql.__version__}")
    except Exception:
        st.warning("PyMySQL not installed or version not available")


def test_database_tables(host, user, password, database, port):
    """Test the database tables structure."""
    try:
        # Connect to database
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connect_timeout=10
        )
        
        # Get list of tables
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                table_list = [table[0] for table in tables]
                st.success(f"✅ Found {len(table_list)} tables in the database")
                
                # Check required tables
                required_tables = [
                    "users", "students", "teachers", "courses", 
                    "class_schedules", "class_enrollments"
                ]
                
                missing_tables = [table for table in required_tables if table not in table_list]
                
                if missing_tables:
                    st.warning(f"⚠️ Missing tables: {', '.join(missing_tables)}")
                    st.info("You need to create these tables. Go to the 'Database Setup' tab.")
                else:
                    st.success("✅ All required tables are present")
                
                # Test key tables
                if "users" in table_list:
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    st.info(f"Users table has {user_count} records")
                    
                    # Check for admin user
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
                    admin_count = cursor.fetchone()[0]
                    
                    if admin_count > 0:
                        st.success("✅ Admin user exists")
                    else:
                        st.warning("⚠️ Admin user not found")
            else:
                st.warning("⚠️ No tables found in the database")
                st.info("You need to create tables. Go to the 'Database Setup' tab to set up the database schema.")
        
        # Close connection
        connection.close()
        
    except Exception as e:
        st.error(f"❌ Error checking database tables: {str(e)}")


def show_sql_script_setup():
    """Show SQL script setup options."""
    st.write("This will execute the SQL script to create the database structure.")
    
    # Display the SQL script
    with open("setup_database.sql", "r") as f:
        sql_script = f.read()
    
    with st.expander("View SQL Script"):
        st.code(sql_script, language="sql")
    
    # Options for running the script
    run_method = st.radio(
        "How to run the script",
        ["Using PyMySQL", "Using Command Line"]
    )
    
    if run_method == "Using PyMySQL":
        if st.button("Run SQL Script"):
            with st.spinner("Setting up database..."):
                try:
                    # Get database config
                    host = os.environ.get("MYSQL_HOST", "localhost")
                    user = os.environ.get("MYSQL_USER", "root")
                    password = os.environ.get("MYSQL_PASSWORD", "")
                    port = int(os.environ.get("MYSQL_PORT", "3306"))
                    
                    # First connect without database to create it if needed
                    connection = pymysql.connect(
                        host=host,
                        user=user,
                        password=password,
                        port=port,
                        connect_timeout=10
                    )
                    
                    # Execute script in parts
                    with connection.cursor() as cursor:
                        # Split script into statements
                        statements = sql_script.split(';')
                        
                        # Execute each statement
                        for statement in statements:
                            if statement.strip():
                                cursor.execute(statement)
                                connection.commit()
                    
                    # Close connection
                    connection.close()
                    
                    st.success("✅ Database setup completed successfully")
                    
                except Exception as e:
                    st.error(f"❌ Error setting up database: {str(e)}")
                    st.error(f"Exception type: {type(e).__name__}")
                    st.expander("Stack trace").code(traceback.format_exc())
    else:
        # Command line instructions
        st.write("To run the script using the command line:")
        
        command = f"mysql -u root -p < setup_database.sql"
        st.code(command, language="bash")
        
        st.write("Or for a specific user:")
        command_user = f"mysql -u [username] -p < setup_database.sql"
        st.code(command_user, language="bash")


def show_orm_setup():
    """Show ORM-based setup options."""
    st.write("This will use SQLAlchemy ORM to create the database structure.")
    
    if st.button("Initialize Database with ORM"):
        with st.spinner("Setting up database with ORM..."):
            try:
                # Import here to avoid circular imports
                from database import init_db
                
                # Initialize database
                init_db()
                
                st.success("✅ Database initialized successfully with ORM")
                
            except Exception as e:
                st.error(f"❌ Error initializing database with ORM: {str(e)}")
                st.error(f"Exception type: {type(e).__name__}")
                st.expander("Stack trace").code(traceback.format_exc())


def show_php_setup():
    """Show PHP-based setup options."""
    st.write("This will use the PHP setup script to create the database structure.")
    
    st.info(
        "To run the PHP setup script:\n"
        "1. Make sure you have PHP installed with MySQL support\n"
        "2. Configure your database settings in db_connection.php\n"
        "3. Run the db_setup.php script through a web server"
    )
    
    # Show URL to PHP script
    php_url = "http://localhost/your_project_folder/db_setup.php"
    st.code(php_url)
    
    # If we're in a web environment, offer a direct link
    st.write("Or you can use the test_mysql_connection.php script to check your connection:")
    php_test_url = "http://localhost/your_project_folder/test_mysql_connection.php"
    st.code(php_test_url)


def provide_error_suggestions(error):
    """Provide suggestions based on the error type."""
    error_str = str(error).lower()
    error_type = type(error).__name__
    
    if "access denied" in error_str:
        st.warning("⚠️ Authentication problem - check your username and password")
        st.info(
            "Solutions:\n"
            "1. Verify that you're using the correct username and password\n"
            "2. Check that the user has proper permissions\n"
            "3. Try resetting the password for the MySQL user"
        )
    
    elif "unknown database" in error_str:
        st.warning("⚠️ Database doesn't exist")
        st.info(
            "Solutions:\n"
            "1. Create the database using the 'Database Setup' tab\n"
            "2. Check the database name spelling\n"
            "3. Confirm that you have permission to access the database"
        )
    
    elif "cannot assign requested address" in error_str:
        st.warning("⚠️ Network-related problem")
        st.info(
            "Solutions:\n"
            "1. If running in a container, use 'host.docker.internal' instead of 'localhost'\n"
            "2. Check if MySQL is running on the specified host and port\n"
            "3. Verify network connectivity (firewall settings, VPN, etc.)\n"
            "4. Try using '127.0.0.1' instead of 'localhost'"
        )
    
    elif "timeout" in error_str or "timed out" in error_str:
        st.warning("⚠️ Connection timeout")
        st.info(
            "Solutions:\n"
            "1. Check if MySQL server is running\n"
            "2. Verify the host and port are correct\n"
            "3. Check for firewall or network issues\n"
            "4. Increase the connection timeout value"
        )
    
    elif "conn closed" in error_str or "not connected" in error_str:
        st.warning("⚠️ Connection closed unexpectedly")
        st.info(
            "Solutions:\n"
            "1. Check if MySQL server is stable and not overloaded\n"
            "2. Increase max_connections in MySQL configuration\n"
            "3. Check for network issues causing disconnections"
        )


# Function for testing direct database insertion
def test_direct_database_insertion():
    """Test direct database insertion without using the ORM."""
    st.subheader("Test Direct Database Insertion")
    
    st.info(
        "This will insert a test record directly into the database, "
        "bypassing the ORM. This can help diagnose if the problem is "
        "with the database connection or with the ORM."
    )
    
    with st.form("test_insertion_form"):
        test_name = st.text_input("Test Student Name", value=f"Test Student {datetime.now().strftime('%Y%m%d%H%M%S')}")
        test_department = st.text_input("Department", value="Test Department")
        test_year = st.number_input("Year", value=1, min_value=1, max_value=4)
        test_email = st.text_input("Email", value="test@example.com")
        test_phone = st.text_input("Phone", value="1234567890")
        
        submitted = st.form_submit_button("Insert Test Student")
        
        if submitted:
            try:
                # Get database config
                host = os.environ.get("MYSQL_HOST", "localhost")
                user = os.environ.get("MYSQL_USER", "root")
                password = os.environ.get("MYSQL_PASSWORD", "")
                database = os.environ.get("MYSQL_DATABASE", "college_management")
                port = int(os.environ.get("MYSQL_PORT", "3306"))
                
                # Connect to database
                connection = pymysql.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    port=port,
                    connect_timeout=10
                )
                
                # Insert test record
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO students (name, department, year, email, phone)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (test_name, test_department, test_year, test_email, test_phone))
                    connection.commit()
                    
                    # Get the ID of the inserted record
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    last_id = cursor.fetchone()[0]
                
                # Close connection
                connection.close()
                
                st.success(f"✅ Test student inserted successfully with ID: {last_id}")
                
                # Verify the insertion
                verify_insertion(host, user, password, database, port, last_id)
                
            except Exception as e:
                st.error(f"❌ Error inserting test student: {str(e)}")
                st.error(f"Exception type: {type(e).__name__}")
                st.expander("Stack trace").code(traceback.format_exc())


def verify_insertion(host, user, password, database, port, student_id):
    """Verify that a record was inserted correctly."""
    try:
        # Connect to database
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connect_timeout=10
        )
        
        # Check if the record exists
        with connection.cursor() as cursor:
            sql = "SELECT * FROM students WHERE id = %s"
            cursor.execute(sql, (student_id,))
            result = cursor.fetchone()
            
            if result:
                st.success("✅ Record verification succeeded")
                
                # Show the record
                columns = [desc[0] for desc in cursor.description]
                record = dict(zip(columns, result))
                
                st.json(record)
            else:
                st.error(f"❌ Record with ID {student_id} not found")
        
        # Close connection
        connection.close()
        
    except Exception as e:
        st.error(f"❌ Error verifying insertion: {str(e)}")