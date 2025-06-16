@echo off
REM Batch file to start the WAN2GP Gradio server on Windows
REM This script will set up the environment and start the Gradio application

echo ========================================
echo Starting WAN2GP Gradio Server
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if we're in the correct directory (look for app.py)
if not exist "app.py" (
    echo ERROR: app.py not found in current directory
    echo Please run this script from the WAN2GP project directory
    pause
    exit /b 1
)

REM Check if virtual environment exists, if not create one
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show gradio >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Set environment variables for better performance
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
set CUDA_VISIBLE_DEVICES=0

REM Start the Gradio server
echo ========================================
echo Starting Gradio server...
echo Server will be available at: http://localhost:7860
echo Press Ctrl+C to stop the server
echo ========================================

python app.py

REM If we get here, the server has stopped
echo ========================================
echo Server stopped
echo ========================================
pause
