<?php
/**
 * Example PHP file demonstrating usage of the database connection
 * This file shows how to perform common database operations using the db_connection.php file
 */

// Include the database connection file
require_once 'db_connection.php';

// Set page header
header('Content-Type: text/html; charset=utf-8');
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>College Management System - PHP Example</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2 {
            color: #2C3E50;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .form-group {
            margin-bottom: 15px;
        }
        input, select {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            margin-top: 5px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .success {
            color: green;
            background-color: #f0f9f0;
            padding: 10px;
            border-left: 5px solid green;
        }
        .error {
            color: red;
            background-color: #f9f0f0;
            padding: 10px;
            border-left: 5px solid red;
        }
    </style>
</head>
<body>
    <h1>College Management System - PHP Example</h1>
    <p>This page demonstrates how to use the database connection with PHP.</p>

    <?php
    // Process form submissions
    $message = '';
    
    // Process student add form
    if (isset($_POST['add_student'])) {
        $name = $_POST['name'] ?? '';
        $department = $_POST['department'] ?? '';
        $year = $_POST['year'] ?? 0;
        $email = $_POST['email'] ?? '';
        $phone = $_POST['phone'] ?? '';
        
        if (!empty($name) && !empty($department) && !empty($year) && !empty($email) && !empty($phone)) {
            $result = db_execute(
                "INSERT INTO students (name, department, year, email, phone) VALUES (?, ?, ?, ?, ?)",
                [$name, $department, (int)$year, $email, $phone]
            );
            
            if ($result !== false) {
                $message = "<p class='success'>Student added successfully!</p>";
            } else {
                $message = "<p class='error'>Failed to add student.</p>";
            }
        } else {
            $message = "<p class='error'>All fields are required!</p>";
        }
    }
    
    // Display message if any
    echo $message;
    ?>

    <h2>Students</h2>
    
    <?php
    // Get all students
    $students = db_select("SELECT * FROM students ORDER BY name");
    
    if (!empty($students)) {
        echo "<table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Year</th>
                    <th>Email</th>
                    <th>Phone</th>
                </tr>";
        
        foreach ($students as $student) {
            echo "<tr>
                    <td>{$student['id']}</td>
                    <td>{$student['name']}</td>
                    <td>{$student['department']}</td>
                    <td>{$student['year']}</td>
                    <td>{$student['email']}</td>
                    <td>{$student['phone']}</td>
                  </tr>";
        }
        
        echo "</table>";
    } else {
        echo "<p>No students found.</p>";
    }
    ?>
    
    <h2>Add New Student</h2>
    <form method="post" action="">
        <div class="form-group">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" required>
        </div>
        
        <div class="form-group">
            <label for="department">Department</label>
            <input type="text" id="department" name="department" required>
        </div>
        
        <div class="form-group">
            <label for="year">Year</label>
            <select id="year" name="year" required>
                <option value="">Select Year</option>
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" name="email" required>
        </div>
        
        <div class="form-group">
            <label for="phone">Phone</label>
            <input type="text" id="phone" name="phone" required>
        </div>
        
        <button type="submit" name="add_student">Add Student</button>
    </form>
    
    <h2>Teachers</h2>
    
    <?php
    // Get all teachers
    $teachers = db_select("SELECT * FROM teachers ORDER BY name");
    
    if (!empty($teachers)) {
        echo "<table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Subjects</th>
                    <th>Email</th>
                    <th>Phone</th>
                </tr>";
        
        foreach ($teachers as $teacher) {
            echo "<tr>
                    <td>{$teacher['id']}</td>
                    <td>{$teacher['name']}</td>
                    <td>{$teacher['department']}</td>
                    <td>{$teacher['subjects']}</td>
                    <td>{$teacher['email']}</td>
                    <td>{$teacher['phone']}</td>
                  </tr>";
        }
        
        echo "</table>";
    } else {
        echo "<p>No teachers found.</p>";
    }
    ?>
    
    <h2>Class Schedules</h2>
    
    <?php
    // Get all class schedules with course and teacher information
    $schedules = db_select("
        SELECT cs.id, cs.day_of_week, cs.start_time, cs.end_time, cs.room_number, cs.semester,
               c.course_code, c.title AS course_title, t.name AS teacher_name
        FROM class_schedules cs
        JOIN courses c ON cs.course_id = c.id
        JOIN teachers t ON cs.teacher_id = t.id
        ORDER BY cs.day_of_week, cs.start_time
    ");
    
    if (!empty($schedules)) {
        echo "<table>
                <tr>
                    <th>Day</th>
                    <th>Time</th>
                    <th>Course</th>
                    <th>Teacher</th>
                    <th>Room</th>
                    <th>Semester</th>
                </tr>";
        
        foreach ($schedules as $schedule) {
            echo "<tr>
                    <td>{$schedule['day_of_week']}</td>
                    <td>{$schedule['start_time']} - {$schedule['end_time']}</td>
                    <td>{$schedule['course_code']} - {$schedule['course_title']}</td>
                    <td>{$schedule['teacher_name']}</td>
                    <td>{$schedule['room_number']}</td>
                    <td>{$schedule['semester']}</td>
                  </tr>";
        }
        
        echo "</table>";
    } else {
        echo "<p>No class schedules found.</p>";
    }
    ?>
    
</body>
</html>

<?php
// Close the database connection when done
db_close();
?>