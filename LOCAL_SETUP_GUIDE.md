# Local Setup Guide for College Management System

This guide will help you set up the College Management System to run on your local computer without Replit.

## Prerequisites

### Required Software
- Python 3.8 or higher
- MySQL Server (recommended) or alternatively SQLite
- PHP and a web server (optional, for PHP components)

### Required Python Packages
```
pip install streamlit pandas plotly sqlalchemy pymysql python-dotenv twilio
```

## Step 1: Database Setup

You have two options for the database:

### Option 1: MySQL (Recommended)
1. Follow the instructions in `MYSQL_SETUP_GUIDE.md` to set up MySQL and create the necessary tables.
2. This is recommended for production use and better performance.

### Option 2: SQLite (Simple)
1. The application will automatically fall back to SQLite if MySQL is not available.
2. This is a good option for testing or if you don't want to install MySQL.

## Step 2: Choose How to Run the Application

You have two ways to run the application:

### Option 1: Run the Standalone Desktop Version
1. Open a terminal or command prompt
2. Navigate to the directory containing your project files
3. Run the standalone file:
   ```
   python desktop_app.py
   ```
4. The application will automatically open in your default web browser

### Option 2: Run the Modular Version
1. Open a terminal or command prompt
2. Navigate to the directory containing your project files
3. Run the Streamlit application:
   ```
   streamlit run main.py
   ```
4. The application will automatically open in your default web browser

## Step 3: Login to the Application

1. Use the default admin credentials:
   - Username: `admin`
   - Password: `admin123`

2. After logging in, you'll have access to all features based on your role (Admin, Teacher, or Student).

## Optional: PHP Components

If you want to use the PHP components of the application:

1. Set up a web server (e.g., Apache, Nginx) with PHP support
2. Place the PHP files in your web server directory
3. Update the database connection parameters in `db_connection.php`
4. Access the PHP files through your web server (e.g., http://localhost/phpmyadmin/)

## Troubleshooting

### Database Connection Issues
1. Check your MySQL credentials in `database.py` (or `desktop_app.py` if using the standalone version)
2. Verify that MySQL server is running
3. If using MySQL, run the `test_mysql_connection.php` script to check your connection

### Application Not Starting
1. Check that all required packages are installed:
   ```
   pip install -r requirements.txt
   ```
2. Verify that Python 3.8 or higher is installed:
   ```
   python --version
   ```
3. Check the console output for specific error messages

### Address Already in Use Error
If you see an error like `Address already in use`, another application might be using port 8501 (or the port Streamlit is trying to use).

To fix this:
1. Close any other Streamlit applications that might be running
2. Or create a `.streamlit/config.toml` file with:
   ```
   [server]
   port = 8502  # Use a different port
   ```

## Add SMS Notifications (Optional)

To enable SMS notifications, you'll need a Twilio account:

1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID, Auth Token, and a Twilio phone number
3. Set environment variables (or create a `.env` file) with:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ```
4. Use the provided `send_message.py` file to send SMS notifications

## Customization

### Changing the Theme
Edit the `.streamlit/config.toml` file to change the theme colors:

```toml
[theme]
primaryColor="#1E88E5"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F5F5F5"
textColor="#232323"
font="sans serif"
```

### Adding More Features
The application has a modular structure:
- Add new components in the `components` folder
- Update `main.py` to include your new components
- Modify database models in `database.py` as needed

## Documentation

For more detailed information on specific components:
- Database structure and models: `database.py`
- Authentication system: `auth.py`
- Utility functions: `utils.py`
- Component modules: `components` folder

## Contact

For issues or questions, please refer to the documentation or create an issue in the repository.