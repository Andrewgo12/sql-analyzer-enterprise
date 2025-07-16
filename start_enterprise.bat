@echo off
REM SQL Analyzer Enterprise - Windows Startup Script
REM Launches the enterprise system with automatic backend startup

echo.
echo ========================================
echo SQL Analyzer Enterprise - Startup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not available
    echo Please install Node.js with npm and try again
    pause
    exit /b 1
)

echo Starting SQL Analyzer Enterprise...
echo.

REM Run the Python startup manager
python start_enterprise.py

REM If we get here, the system has shut down
echo.
echo System has shut down.
pause
