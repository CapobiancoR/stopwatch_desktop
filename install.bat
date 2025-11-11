@echo off
echo Desktop Activity Tracker Widget Installation
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Download and install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Python found!
echo.

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment and install packages
echo Installing dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo ==========================================
echo Installation complete!
echo.
echo To launch the application, run: start.bat
echo ==========================================
pause
