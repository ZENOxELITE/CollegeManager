<?php
/**
 * Database Connection File for College Management System
 * This file handles the connection to MySQL database
 */

// Database configuration - modify these to match your local setup
$db_host = 'localhost';      // Database host (usually localhost)
$db_user = 'root';           // Database username (usually root for local development)
$db_password = '';           // Database password (set this to your MySQL password)
$db_name = 'college_management'; // Database name
$db_port = 3306;             // Database port (default is 3306 for MySQL)

// CREATE DATABASE IF NOT EXISTS college_management;
// If you're running this the first time, uncomment the line above or create the database manually

// Create database connection
$conn = null;

try {
    // Create connection using mysqli
    $conn = new mysqli($db_host, $db_user, $db_password, $db_name, $db_port);
    
    // Check connection
    if ($conn->connect_error) {
        throw new Exception("Connection failed: " . $conn->connect_error);
    }
    
    // Set charset to ensure proper encoding
    $conn->set_charset("utf8mb4");
    
    // Uncomment to display success message (for testing only)
    // echo "Connected successfully to MySQL database";
    
} catch (Exception $e) {
    // Handle connection errors
    die("Database connection failed: " . $e->getMessage());
}

/**
 * Function to perform a select query and return results as an associative array
 * 
 * @param string $sql SQL query to execute
 * @param array $params Parameters for the prepared statement (optional)
 * @return array|null Array of results or null on error
 */
function db_select($sql, $params = []) {
    global $conn;
    
    try {
        $stmt = $conn->prepare($sql);
        
        if (!$stmt) {
            throw new Exception("Query preparation failed: " . $conn->error);
        }
        
        // Bind parameters if any
        if (!empty($params)) {
            $types = str_repeat('s', count($params)); // Assuming all parameters are strings
            $stmt->bind_param($types, ...$params);
        }
        
        // Execute the statement
        if (!$stmt->execute()) {
            throw new Exception("Query execution failed: " . $stmt->error);
        }
        
        // Get results
        $result = $stmt->get_result();
        $data = [];
        
        while ($row = $result->fetch_assoc()) {
            $data[] = $row;
        }
        
        $stmt->close();
        return $data;
        
    } catch (Exception $e) {
        error_log("Database query error: " . $e->getMessage());
        return null;
    }
}

/**
 * Function to perform an insert, update, or delete query
 * 
 * @param string $sql SQL query to execute
 * @param array $params Parameters for the prepared statement (optional)
 * @return bool|int Number of affected rows or false on error
 */
function db_execute($sql, $params = []) {
    global $conn;
    
    try {
        $stmt = $conn->prepare($sql);
        
        if (!$stmt) {
            throw new Exception("Query preparation failed: " . $conn->error);
        }
        
        // Bind parameters if any
        if (!empty($params)) {
            $types = str_repeat('s', count($params)); // Assuming all parameters are strings
            $stmt->bind_param($types, ...$params);
        }
        
        // Execute the statement
        if (!$stmt->execute()) {
            throw new Exception("Query execution failed: " . $stmt->error);
        }
        
        // Get number of affected rows
        $affected_rows = $stmt->affected_rows;
        
        $stmt->close();
        return $affected_rows;
        
    } catch (Exception $e) {
        error_log("Database query error: " . $e->getMessage());
        return false;
    }
}

/**
 * Function to close the database connection when done
 */
function db_close() {
    global $conn;
    
    if ($conn) {
        $conn->close();
    }
}

// Register a shutdown function to close the database connection when the script ends
register_shutdown_function('db_close');
?>