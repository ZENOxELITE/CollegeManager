-- College Management System Database Setup Script
-- Run this script to set up your MySQL database structure

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS college_management;

-- Use the college_management database
USE college_management;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    subjects VARCHAR(200) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create courses table
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    department VARCHAR(100) NOT NULL,
    credit_hours INT NOT NULL
);

-- Create class_schedules table
CREATE TABLE IF NOT EXISTS class_schedules (
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
);

-- Create class_enrollments table
CREATE TABLE IF NOT EXISTS class_enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_schedule_id INT NOT NULL,
    enrollment_date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (class_schedule_id) REFERENCES class_schedules(id) ON DELETE CASCADE
);

-- Insert default admin user (username: admin, password: admin123)
-- Password is stored as SHA-256 hash
INSERT INTO users (username, password, role)
SELECT 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- Insert sample data for testing
-- Sample departments
INSERT INTO students (name, department, year, email, phone)
SELECT 'John Smith', 'Computer Science', 2, 'john.smith@example.com', '1234567890'
WHERE NOT EXISTS (SELECT 1 FROM students WHERE email = 'john.smith@example.com');

INSERT INTO students (name, department, year, email, phone)
SELECT 'Maria Garcia', 'Mathematics', 3, 'maria.garcia@example.com', '2345678901'
WHERE NOT EXISTS (SELECT 1 FROM students WHERE email = 'maria.garcia@example.com');

INSERT INTO teachers (name, department, subjects, email, phone)
SELECT 'Dr. James Wilson', 'Computer Science', 'Programming, Algorithms', 'james.wilson@example.com', '3456789012'
WHERE NOT EXISTS (SELECT 1 FROM teachers WHERE email = 'james.wilson@example.com');

INSERT INTO teachers (name, department, subjects, email, phone)
SELECT 'Dr. Emily Chen', 'Mathematics', 'Calculus, Linear Algebra', 'emily.chen@example.com', '4567890123'
WHERE NOT EXISTS (SELECT 1 FROM teachers WHERE email = 'emily.chen@example.com');

INSERT INTO courses (course_code, title, description, department, credit_hours)
SELECT 'CS101', 'Introduction to Programming', 'Basic programming concepts using Python', 'Computer Science', 3
WHERE NOT EXISTS (SELECT 1 FROM courses WHERE course_code = 'CS101');

INSERT INTO courses (course_code, title, description, department, credit_hours)
SELECT 'MATH201', 'Calculus I', 'Introduction to differential and integral calculus', 'Mathematics', 4
WHERE NOT EXISTS (SELECT 1 FROM courses WHERE course_code = 'MATH201');

-- Note: For class_schedules and class_enrollments, you may want to add these after confirming 
-- the IDs of the inserted teachers, courses, and students in your database.