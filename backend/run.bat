@echo off
REM AgroScan AI Backend Startup Script for Windows

echo.
echo ===============================================
echo  AgroScan AI - Plant Disease Detection Backend
echo ===============================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Virtual environment not found
    echo [ACTION] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [ACTION] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo [ACTION] Checking dependencies...
pip list | findstr fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo [ACTION] Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Validate setup
echo [ACTION] Validating setup...
python validate_setup.py
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some setup checks failed. Continuing anyway...
    echo.
)

REM Start the server
echo.
echo [ACTION] Starting AgroScan AI Backend...
echo.
echo ===============================================
echo  Server: http://localhost:8000
echo  Docs:   http://localhost:8000/docs
echo ===============================================
echo.

python main.py

REM If script exits, show message
echo.
echo [INFO] Backend server stopped
pause
