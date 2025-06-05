@echo off
setlocal enabledelayedexpansion

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Check if customtkinter is installed
python -c "import customtkinter" > nul 2>&1
if errorlevel 1 (
    echo Installing customtkinter...
    pip install customtkinter
    if errorlevel 1 (
        echo Failed to install customtkinter. Please try installing it manually using: pip install customtkinter
        pause
        exit /b 1
    )
)

REM Run the application
python main.py

pause