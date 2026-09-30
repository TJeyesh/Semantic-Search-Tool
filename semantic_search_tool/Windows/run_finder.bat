@echo off
cd /d "%~dp0"

echo Starting Finder...

:: Check if venv exists, if not, guide user (or assume they followed README)
if not exist "venv\" (
    echo Virtual environment not found. Please run:
    echo python -m venv venv
    echo venv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit
)

:: Activate venv and run
call venv\Scripts\activate
start http://localhost:8000
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
pause
