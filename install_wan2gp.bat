@echo off
REM Quick installation script for WAN2GP on Windows
REM This script will clone the repository and set up the environment

echo ========================================
echo WAN2GP Quick Installation Script
echo ========================================

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git first: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Check if conda is installed
conda --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda is not installed or not in PATH
    echo Please install Anaconda or Miniconda first
    echo Download from: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo Git and Conda are available!
echo.

REM Ask for installation directory
set /p INSTALL_DIR="Enter installation directory (default: %USERPROFILE%\WAN2GP): "
if "%INSTALL_DIR%"=="" set INSTALL_DIR=%USERPROFILE%\WAN2GP

REM Create directory if it doesn't exist
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM Clone the repository
echo.
echo Cloning WAN2GP repository...
cd /d "%INSTALL_DIR%"
git clone https://github.com/deepbeepmeep/Wan2GP.git .
if errorlevel 1 (
    echo ERROR: Failed to clone repository
    pause
    exit /b 1
)

echo.
echo Repository cloned successfully!
echo.

REM Create conda environment
echo Creating conda environment wan2gp with Python 3.10.9...
conda create -n wan2gp python=3.10.9 -y
if errorlevel 1 (
    echo ERROR: Failed to create conda environment
    pause
    exit /b 1
)

REM Activate environment and install dependencies
echo.
echo Activating environment and installing dependencies...
call conda activate wan2gp

echo Installing PyTorch 2.6.0 with CUDA 12.4 support...
pip install torch==2.6.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/test/cu124
if errorlevel 1 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)

echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo WAN2GP has been installed to: %INSTALL_DIR%
echo.
echo To start the application:
echo 1. Navigate to the installation directory
echo 2. Run start_gradio.bat or start_gradio.ps1
echo.
echo Or you can start it now by pressing any key...
pause

REM Start the application
call start_gradio.bat
