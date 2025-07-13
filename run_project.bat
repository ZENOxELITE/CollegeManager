@echo off
title Starting CollegeManager Streamlit App
echo ============================================
echo     LAUNCHING COLLEGEMANAGER WEB APP
echo ============================================

REM Start XAMPP Control Panel
start "" "C:\xampp\xampp-control.exe"
timeout /t 5 /nobreak >nul

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Auto-install Python packages if not already installed
echo Checking Python requirements...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing required Python packages...
    pip install -r requirements.txt
) else (
    echo Requirements already installed.
)

REM Open browser at correct local address and port
start "" http://127.0.0.1:8502/

REM Run Streamlit on 127.0.0.1:8502 explicitly
streamlit run main.py --server.address=127.0.0.1 --server.port=8502

pause

