# College Management System - Local Setup Guide

This guide will help you set up and run the College Management System on your local computer without Replit.

## Prerequisites

You need to have the following software installed on your computer:

1. **Python 3.11** or newer
2. **MySQL** database server (recommended: MySQL 8.0 or newer)
3. **PHP** (only if you want to use the PHP database connection file)

## Step 1: Set Up MySQL Database

1. Install MySQL on your computer if you haven't already:
   - Windows: Download and install from [MySQL Website](https://dev.mysql.com/downloads/installer/)
   - Mac: Use Homebrew with `brew install mysql`
   - Linux: Use package manager, e.g., `sudo apt install mysql-server`

2. Start MySQL server:
   - Windows: It usually starts automatically as a service
   - Mac: `brew services start mysql`
   - Linux: `sudo systemctl start mysql`

3. Create the database and required tables:
   - Option 1: Use MySQL Workbench or phpMyAdmin to run the `setup_database.sql` script
   - Option 2: Run from command line:
     ```
     mysql -u root -p < setup_database.sql
     ```

## Step 2: Install Python Dependencies

1. Open a command prompt or terminal
2. Navigate to the project directory
3. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

5. Install required packages:
   ```
   pip install streamlit pandas plotly sqlalchemy pymysql python-dotenv
   ```

## Step 3: Configure Database Connection

1. Update the MySQL connection parameters in `database.py`:
   - Set `MYSQL_USER` to your MySQL username (default: "root")
   - Set `MYSQL_PASSWORD` to your MySQL password
   - Adjust `MYSQL_HOST`, `MYSQL_DATABASE`, and `MYSQL_PORT` if needed

2. Alternatively, create a `.env` file in the project root with:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password_here
   MYSQL_DATABASE=college_management
   MYSQL_PORT=3306
   ```

## Step 4: Run the Application

1. Make sure your virtual environment is activated
2. Start the Streamlit application:
   ```
   streamlit run main.py
   ```

3. Open your web browser and go to:
   ```
   http://localhost:8501
   ```

4. Log in with the default credentials:
   - Username: `admin`
   - Password: `admin123`

## Using PHP for Database Connection (Optional)

If you want to use the PHP database connection:

1. Install a PHP server like XAMPP, WAMP, or MAMP
2. Place the `db_connection.php` file in your PHP project
3. Include it in your PHP files with:
   ```php
   require_once 'db_connection.php';
   ```

4. Use the provided functions to interact with the database:
   ```php
   // Example: Select query
   $students = db_select("SELECT * FROM students WHERE department = ?", ["Computer Science"]);
   
   // Example: Insert query
   $result = db_execute(
       "INSERT INTO students (name, department, year, email, phone) VALUES (?, ?, ?, ?, ?)",
       ["John Doe", "Computer Science", 2, "john@example.com", "1234567890"]
   );
   ```

## Troubleshooting

### Database Connection Issues

1. Verify MySQL is running with:
   ```
   mysql --version
   ```

2. Test database connection:
   ```
   mysql -u root -p -e "USE college_management; SELECT * FROM users LIMIT 1;"
   ```

3. Check your MySQL credentials in `database.py`

### Application Not Starting

1. Verify all required packages are installed:
   ```
   pip list
   ```

2. Check Python version (should be 3.11+):
   ```
   python --version
   ```

3. Try running with debug mode:
   ```
   streamlit run main.py --server.enableCORS=false --server.enableXsrfProtection=false
   ```

## Required Python Modules

Here's a summary of all the Python modules you need to install:

```
streamlit
pandas
plotly
sqlalchemy
pymysql
python-dotenv
components
```

You can install them all at once with:
```
pip install streamlit pandas plotly sqlalchemy pymysql python-dotenv components
```