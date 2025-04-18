# MySQL Setup Guide for College Management System

This guide will help you set up the College Management System with MySQL database on your local computer.

## Step 1: Set Up MySQL Database

1. **Install MySQL Server**:
   - Windows: Download and install from [MySQL Website](https://dev.mysql.com/downloads/installer/)
   - Mac: Use Homebrew with `brew install mysql`
   - Linux: Use package manager, e.g., `sudo apt install mysql-server`

2. **Start MySQL Server**:
   - Windows: MySQL usually starts automatically as a service
   - Mac: `brew services start mysql`
   - Linux: `sudo systemctl start mysql`

3. **Set Up MySQL User and Password**:
   - The default root password might be empty ('') or 'root'
   - You can set a new password using:
     ```
     mysql -u root -p
     ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_new_password';
     FLUSH PRIVILEGES;
     EXIT;
     ```

## Step 2: Create the Database and Tables

### Option 1: Using the PHP Setup Script (Recommended)

1. **Set Up a PHP Server**:
   - Install XAMPP, WAMP, or any PHP server
   - Place the project files in the web server directory (e.g., htdocs for XAMPP)
   - Start the web server

2. **Configure Database Connection**:
   - Open `db_connection.php` and update these lines with your MySQL credentials:
     ```php
     $db_host = 'localhost';      // Usually localhost
     $db_user = 'root';           // Your MySQL username
     $db_password = '';           // Your MySQL password
     $db_name = 'college_management'; // Database name
     $db_port = 3306;             // Default MySQL port
     ```

3. **Run the Setup Script**:
   - Navigate to `http://localhost/your_project_folder/db_setup.php` in your browser
   - This script will create the database and all necessary tables
   - It will also add a default admin user (username: admin, password: admin123)

### Option 2: Using the SQL Script

1. **Run the SQL Script**:
   - Open MySQL command line or a tool like MySQL Workbench
   - Execute the `setup_database.sql` script:
     ```
     mysql -u root -p < setup_database.sql
     ```
   - This will create the database, tables, and default admin user

## Step 3: Configure the Python Application

1. **Update Database Connection in Python Code**:
   - Open `desktop_app.py` (or `database.py` if you're using the modular version)
   - Update the MySQL connection parameters:
     ```python
     # MySQL connection parameters - modify these to match your local setup
     MYSQL_HOST = "localhost"
     MYSQL_USER = "root"           # Your MySQL username
     MYSQL_PASSWORD = ""           # Your MySQL password
     MYSQL_DATABASE = "college_management"
     MYSQL_PORT = 3306
     ```

2. **Install Required Python Packages**:
   ```
   pip install streamlit pandas plotly sqlalchemy pymysql python-dotenv
   ```

## Step 4: Run the Application

### Option 1: Using the Standalone Desktop Version
```
python desktop_app.py
```

### Option 2: Using the Modular Version
```
streamlit run main.py
```

## Step 5: Access the Application

1. **Access the Python Web Application**:
   - Open your browser and go to `http://localhost:8501` (or the port shown in the console)
   - Log in with the default credentials:
     - Username: `admin`
     - Password: `admin123`

2. **Access the PHP Example** (if you want to use the PHP version):
   - Open your browser and go to `http://localhost/your_project_folder/php_example.php`

## Troubleshooting

### Common MySQL Connection Issues

1. **Access Denied Error**:
   ```
   Access denied for user 'root'@'localhost'
   ```
   - Check your MySQL username and password
   - Make sure you have permissions to access the database

2. **Cannot Connect to MySQL Server**:
   ```
   Can't connect to MySQL server on 'localhost'
   ```
   - Check if MySQL server is running
   - Verify the port number (default is 3306)

3. **Unknown Database Error**:
   ```
   Unknown database 'college_management'
   ```
   - Run the setup script to create the database
   - Check if the database name is correct in your configuration

### Testing MySQL Connection

Use this simple PHP script to test your MySQL connection:

```php
<?php
$host = 'localhost';
$user = 'root';
$password = ''; // Your MySQL password
$db = 'college_management';

$conn = new mysqli($host, $user, $password, $db);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} else {
    echo "Connected successfully!";
    
    // Test a simple query
    $result = $conn->query("SELECT COUNT(*) as total FROM users");
    if ($result) {
        $row = $result->fetch_assoc();
        echo "<br>Number of users: " . $row['total'];
    }
}
$conn->close();
?>
```

Save this as `test_connection.php` and access it through your web server.

## Additional Notes

- The PHP version of the application requires a web server with PHP support (e.g., XAMPP, WAMP, MAMP)
- The Python version can run as a standalone application without a web server
- If you want to use both PHP and Python parts, make sure they're configured to use the same database
- If you're using the application in a production environment, make sure to:
  - Use strong passwords
  - Configure proper permissions
  - Set up database backups