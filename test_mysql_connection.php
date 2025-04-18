<?php
/**
 * MySQL Connection Test Script
 * 
 * This script tests the connection to your MySQL database and verifies if the required tables exist.
 * Run this script through your web server to check if your MySQL setup is working correctly.
 */

// Database configuration - modify these to match your local setup
$db_host = 'localhost';      // Database host (usually localhost)
$db_user = 'root';           // Database username (usually root for local development)
$db_password = '';           // Database password (set this to your MySQL password)
$db_name = 'college_management'; // Database name
$db_port = 3306;             // Database port (default is 3306 for MySQL)

// Style for the page
echo <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MySQL Connection Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #2C3E50;
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
        .warning {
            color: orange;
            background-color: #f9f8f0;
            padding: 10px;
            border-left: 5px solid orange;
        }
        .info {
            color: blue;
            background-color: #f0f5f9;
            padding: 10px;
            border-left: 5px solid blue;
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
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>MySQL Connection Test</h1>
HTML;

// Function to check MySQL connection
function check_mysql_connection($host, $user, $password, $port) {
    $conn = @new mysqli($host, $user, $password, "", $port);
    
    if ($conn->connect_error) {
        echo "<div class='error'><strong>Connection Error:</strong> " . $conn->connect_error . "</div>";
        return false;
    }
    
    echo "<div class='success'><strong>MySQL Connection:</strong> Successful!</div>";
    echo "<div class='info'><strong>MySQL Version:</strong> " . $conn->server_info . "</div>";
    
    return $conn;
}

// Function to check database existence
function check_database($conn, $db_name) {
    $result = $conn->query("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '$db_name'");
    
    if ($result->num_rows > 0) {
        echo "<div class='success'><strong>Database '$db_name':</strong> Exists</div>";
        return true;
    } else {
        echo "<div class='warning'><strong>Database '$db_name':</strong> Does not exist. You need to create it.</div>";
        return false;
    }
}

// Function to check table existence
function check_table($conn, $db_name, $table_name) {
    $result = $conn->query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '$db_name' AND TABLE_NAME = '$table_name'");
    
    if ($result->num_rows > 0) {
        echo "<li class='success'><strong>Table '$table_name':</strong> Exists</li>";
        return true;
    } else {
        echo "<li class='warning'><strong>Table '$table_name':</strong> Does not exist</li>";
        return false;
    }
}

// Function to count records in a table
function count_table_records($conn, $db_name, $table_name) {
    $result = $conn->query("SELECT COUNT(*) as count FROM `$db_name`.`$table_name`");
    
    if ($result) {
        $row = $result->fetch_assoc();
        return $row['count'];
    } else {
        return "Error counting records";
    }
}

// Start testing connection
$conn = check_mysql_connection($db_host, $db_user, $db_password, $db_port);

if ($conn) {
    // Check database
    $db_exists = check_database($conn, $db_name);
    
    if ($db_exists) {
        // Select the database
        $conn->select_db($db_name);
        
        // Check tables
        echo "<h2>Table Check</h2>";
        echo "<ul>";
        
        $tables = ['users', 'students', 'teachers', 'courses', 'class_schedules', 'class_enrollments'];
        $all_tables_exist = true;
        
        foreach ($tables as $table) {
            if (!check_table($conn, $db_name, $table)) {
                $all_tables_exist = false;
            }
        }
        
        echo "</ul>";
        
        // If all tables exist, check record counts
        if ($all_tables_exist) {
            echo "<h2>Record Counts</h2>";
            echo "<table>";
            echo "<tr><th>Table</th><th>Records</th></tr>";
            
            foreach ($tables as $table) {
                $count = count_table_records($conn, $db_name, $table);
                echo "<tr><td>$table</td><td>$count</td></tr>";
            }
            
            echo "</table>";
            
            // Check for default admin user
            $admin_result = $conn->query("SELECT * FROM `$db_name`.`users` WHERE username = 'admin'");
            if ($admin_result && $admin_result->num_rows > 0) {
                echo "<div class='success'><strong>Default Admin User:</strong> Exists</div>";
            } else {
                echo "<div class='warning'><strong>Default Admin User:</strong> Does not exist</div>";
            }
        }
    }
    
    // Database setup instructions
    echo "<h2>Next Steps</h2>";
    
    if (!$db_exists || !isset($all_tables_exist) || !$all_tables_exist) {
        echo "<div class='info'>";
        echo "<p>To set up the database and tables, you can:</p>";
        echo "<ol>";
        echo "<li>Run the <strong>db_setup.php</strong> script to automatically create the database and tables</li>";
        echo "<li>Or run the <strong>setup_database.sql</strong> script manually using MySQL command line or a tool like phpMyAdmin</li>";
        echo "</ol>";
        echo "</div>";
    } else {
        echo "<div class='success'>";
        echo "<p>Your database is set up correctly! You can now:</p>";
        echo "<ol>";
        echo "<li>Run the Python application with <code>streamlit run main.py</code> or <code>python desktop_app.py</code></li>";
        echo "<li>Use the PHP interface at <a href='php_example.php'>php_example.php</a></li>";
        echo "</ol>";
        echo "</div>";
    }
    
    // Close connection
    $conn->close();
} else {
    echo "<h2>Connection Failed</h2>";
    echo "<div class='info'>";
    echo "<p>Check the following:</p>";
    echo "<ol>";
    echo "<li>Verify that MySQL server is running</li>";
    echo "<li>Check your username and password</li>";
    echo "<li>Make sure the port is correct (default is 3306)</li>";
    echo "<li>Update the credentials in the script if needed</li>";
    echo "</ol>";
    echo "</div>";
}

echo <<<HTML
</body>
</html>
HTML;
?>