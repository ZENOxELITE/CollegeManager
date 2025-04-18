<?php
/**
 * Database Setup Utility for College Management System
 * 
 * This script helps to create the database and tables for the College Management System.
 * Run this script once to set up your database structure.
 */

// Include database connection
require_once 'db_connection.php';

// Function to check if a table exists
function table_exists($table_name) {
    global $conn;
    
    $sql = "SHOW TABLES LIKE ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param('s', $table_name);
    $stmt->execute();
    $result = $stmt->get_result();
    
    return $result->num_rows > 0;
}

// Create tables if they don't exist
function create_tables() {
    global $conn;
    
    // Create users table
    if (!table_exists('users')) {
        $sql = "CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(256) NOT NULL,
            role VARCHAR(20) NOT NULL
        )";
        
        if ($conn->query($sql) === TRUE) {
            echo "Users table created successfully<br>";
            
            // Insert default admin user
            $username = 'admin';
            $password = hash('sha256', 'admin123');
            $role = 'admin';
            
            $sql = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param('sss', $username, $password, $role);
            
            if ($stmt->execute()) {
                echo "Default admin user created successfully<br>";
            } else {
                echo "Error creating default admin user: " . $stmt->error . "<br>";
            }
            
        } else {
            echo "Error creating users table: " . $conn->error . "<br>";
        }
    } else {
        echo "Users table already exists<br>";
    }
    
    // Create students table
    if (!table_exists('students')) {
        $sql = "CREATE TABLE students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(100) NOT NULL,
            year INT NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )";
        
        if ($conn->query($sql) === TRUE) {
            echo "Students table created successfully<br>";
        } else {
            echo "Error creating students table: " . $conn->error . "<br>";
        }
    } else {
        echo "Students table already exists<br>";
    }
    
    // Create teachers table
    if (!table_exists('teachers')) {
        $sql = "CREATE TABLE teachers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(100) NOT NULL,
            subjects VARCHAR(200) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )";
        
        if ($conn->query($sql) === TRUE) {
            echo "Teachers table created successfully<br>";
        } else {
            echo "Error creating teachers table: " . $conn->error . "<br>";
        }
    } else {
        echo "Teachers table already exists<br>";
    }
    
    // Create courses table
    if (!table_exists('courses')) {
        $sql = "CREATE TABLE courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            course_code VARCHAR(20) NOT NULL UNIQUE,
            title VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            department VARCHAR(100) NOT NULL,
            credit_hours INT NOT NULL
        )";
        
        if ($conn->query($sql) === TRUE) {
            echo "Courses table created successfully<br>";
        } else {
            echo "Error creating courses table: " . $conn->error . "<br>";
        }
    } else {
        echo "Courses table already exists<br>";
    }
    
    // Create class_schedules table
    if (!table_exists('class_schedules')) {
        $sql = "CREATE TABLE class_schedules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            course_id INT NOT NULL,
            teacher_id INT NOT NULL,
            day_of_week VARCHAR(10) NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            room_number VARCHAR(20) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
        )";
        
        if ($conn->query($sql) === TRUE) {
            echo "Class schedules table created successfully<br>";
        } else {
            echo "Error creating class schedules table: " . $conn->error . "<br>";
        }
    } else {
        echo "Class schedules table already exists<br>";
    }
    
    // Create class_enrollments table
    if (!table_exists('class_enrollments')) {
        $sql = "CREATE TABLE class_enrollments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            class_schedule_id INT NOT NULL,
            enrollment_date DATE NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (class_schedule_id) REFERENCES class_schedules(id) ON DELETE CASCADE
        )";
        
        if ($conn->query($sql) === TRUE) {
            echo "Class enrollments table created successfully<br>";
        } else {
            echo "Error creating class enrollments table: " . $conn->error . "<br>";
        }
    } else {
        echo "Class enrollments table already exists<br>";
    }
}

// Check if database exists, create it if it doesn't
$check_db_sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '$db_name'";
$result = $conn->query($check_db_sql);

if ($result->num_rows == 0) {
    // Database doesn't exist, create it
    $create_db_sql = "CREATE DATABASE $db_name";
    
    if ($conn->query($create_db_sql) === TRUE) {
        echo "Database created successfully<br>";
        // Select the new database
        $conn->select_db($db_name);
    } else {
        echo "Error creating database: " . $conn->error . "<br>";
        exit;
    }
} else {
    echo "Database already exists<br>";
}

// Create tables
create_tables();

echo "<br>Database setup completed. You can now <a href='php_example.php'>view the application</a>.";

// Close connection
$conn->close();
?>