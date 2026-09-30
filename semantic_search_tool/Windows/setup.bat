@echo off
cd /d "%~dp0"

echo ==========================================
echo       Finder App - Windows Installer      
echo ==========================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found! 
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit
)
echo [OK] Python found.

:: 2. Create Virtual Environment
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit
    )
) else (
    echo [INFO] Virtual environment already exists. Skipping creation.
)

:: 3. Install Dependencies
echo [INFO] Installing dependencies (this may take a few minutes)...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit
)

echo.
echo ==========================================
echo        Installation Complete!             
echo ==========================================
echo.
echo You can now double-click 'run_finder.bat' to start the app.
pause
