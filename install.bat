@echo off
REM SQL Analyzer Enterprise - Installation Script for Windows
REM Version: 2.0.0

setlocal enabledelayedexpansion

REM Colors (limited in Windows CMD)
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

echo %BLUE%
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                SQL Analyzer Enterprise v2.0.0               ║
echo ║                    Installation Script                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %NC%

echo %BLUE%[STEP]%NC% Checking system requirements...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%[SUCCESS]%NC% Python %PYTHON_VERSION% found

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% pip not found. Please install pip
    pause
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% pip found

echo %BLUE%[STEP]%NC% Creating virtual environment...

REM Remove existing venv if present
if exist venv (
    echo %YELLOW%[WARNING]%NC% Virtual environment already exists. Removing...
    rmdir /s /q venv
)

REM Create virtual environment
python -m venv venv
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip
echo %GREEN%[SUCCESS]%NC% Virtual environment created and activated

echo %BLUE%[STEP]%NC% Installing Python dependencies...

REM Install dependencies
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo %RED%[ERROR]%NC% Failed to install dependencies
        pause
        exit /b 1
    )
    echo %GREEN%[SUCCESS]%NC% Dependencies installed successfully
) else (
    echo %RED%[ERROR]%NC% requirements.txt not found
    pause
    exit /b 1
)

echo %BLUE%[STEP]%NC% Creating necessary directories...

REM Create directories
if not exist uploads mkdir uploads
if not exist logs mkdir logs
if not exist exports mkdir exports
if not exist cache mkdir cache

REM Create .gitkeep files
echo. > uploads\.gitkeep
echo. > logs\.gitkeep
echo. > exports\.gitkeep
echo. > cache\.gitkeep

echo %GREEN%[SUCCESS]%NC% Directories created

echo %BLUE%[STEP]%NC% Creating configuration files...

REM Create .env file if it doesn't exist
if not exist .env (
    (
        echo # SQL Analyzer Enterprise Configuration
        echo FLASK_ENV=development
        echo FLASK_DEBUG=True
        echo SECRET_KEY=your-secret-key-here-change-in-production
        echo.
        echo # File upload settings
        echo MAX_CONTENT_LENGTH=104857600
        echo UPLOAD_FOLDER=uploads
        echo.
        echo # Security settings
        echo SECURITY_SCAN_ENABLED=True
        echo MALWARE_SCAN_ENABLED=False
        echo.
        echo # Database settings ^(optional^)
        echo DATABASE_URL=sqlite:///analyzer.db
    ) > .env
    echo %GREEN%[SUCCESS]%NC% Configuration file created: .env
) else (
    echo %YELLOW%[WARNING]%NC% Configuration file already exists: .env
)

echo %BLUE%[STEP]%NC% Running installation tests...

REM Test Python imports
python -c "import flask; import werkzeug; print('✓ Core dependencies imported successfully')"
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Dependency test failed
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Installation tests completed

echo %GREEN%
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    INSTALLATION COMPLETE!                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %NC%

echo %BLUE%Next steps:%NC%
echo 1. Activate virtual environment: %YELLOW%venv\Scripts\activate.bat%NC%
echo 2. Start the application: %YELLOW%python web_app.py%NC%
echo 3. Open browser: %YELLOW%http://localhost:5000%NC%
echo.
echo %BLUE%Documentation:%NC%
echo • Installation guide: %YELLOW%INSTALLATION.md%NC%
echo • User manual: %YELLOW%README.md%NC%
echo • API documentation: %YELLOW%http://localhost:5000/help%NC%
echo.
echo %GREEN%Happy analyzing! 🚀%NC%

pause
