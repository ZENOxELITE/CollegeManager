# College Management System

A comprehensive web-based system for managing college administrative tasks, built with Streamlit, SQLAlchemy, and a flexible database backend.

## Features

- **Student Management**: Add, edit, and manage student records
- **Teacher Management**: Maintain teacher information and assignments
- **Class Scheduling**: Create and manage course schedules and enrollments
- **User Authentication**: Role-based access control (Admin, Teacher, Student)
- **Dashboard**: Visual analytics for key metrics
- **Notifications**: Send notifications to students (email-based)
- **Dynamic Theme**: Toggle between light and dark mode
- **Responsive Design**: Mobile-friendly interface

## Getting Started

### Running on Replit

This project is ready to run on Replit without any additional configuration.

### Local Setup

To run this application locally, follow these steps:

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd college-management-system
   ```

2. **Install required packages:**
   ```
   pip install -r requirements.txt
   ```

3. **Set up database connection:**
   - Create a `.env` file based on `.env.example`
   - Configure your MySQL connection details (or SQLite will be used as fallback)

4. **Run the application:**
   ```
   streamlit run main.py
   ```

## Database Configuration

The system supports both MySQL and SQLite databases:

- **MySQL**: Configure by setting the environment variables in `.env` file
- **SQLite**: Used automatically as a fallback if MySQL connection fails

## Default Credentials

For testing purposes, use the following default admin account:

- **Username**: admin
- **Password**: admin123

## Project Structure

- **main.py**: Application entry point and main UI code
- **auth.py**: Authentication and user management
- **database.py**: Database models and connection handlers
- **utils.py**: Utility functions
- **components/**: UI components for different sections
  - **dashboard.py**: Dashboard visualizations
  - **student_management.py**: Student CRUD operations
  - **teacher_management.py**: Teacher CRUD operations
  - **class_schedule.py**: Course scheduling
  - **notifications.py**: Notification system
  - **database_diagnostics.py**: Database connection troubleshooting
- **.streamlit/**: Streamlit configuration
- **LOCAL_SETUP_GUIDE.md**: Detailed local setup instructions
- **MYSQL_SETUP_GUIDE.md**: MySQL configuration guide

## License

This project is for educational purposes. See the LICENSE file for details.