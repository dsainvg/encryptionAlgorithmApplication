@echo off
REM Run GUI with Python 3.14
REM This script ensures the application runs with the correct Python version

echo Starting Secure File Encrypter GUI...
echo Using Python 3.14
echo.

C:\Users\dsain\AppData\Local\Programs\Python\Python314\python.exe "%~dp0python\gui.py"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo Make sure Python 3.14 is installed at the expected location
    pause
)
