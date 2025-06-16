@echo off
REM Batch file to start the WAN2GP Gradio server on Windows
REM This script will set up the environment and start the Gradio application

echo ========================================
echo Starting WAN2GP Gradio Server
echo ========================================

REM Check if conda is installed
conda --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda is not installed or not in PATH
    echo Please install Anaconda or Miniconda first
    echo Download from: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

REM Check if we're in the correct directory (look for wgp.py)
if not exist "wgp.py" (
    echo ERROR: wgp.py not found in current directory
    echo.
    echo This script should be run from the WAN2GP project directory.
    echo If you haven't cloned the repository yet, run:
    echo   git clone https://github.com/deepbeepmeep/Wan2GP.git
    echo   cd Wan2GP
    echo.
    pause
    exit /b 1
)

REM Check if conda environment exists, if not create it
conda info --envs | findstr "wan2gp" >nul 2>&1
if errorlevel 1 (
    echo Creating conda environment wan2gp with Python 3.10.9...
    conda create -n wan2gp python=3.10.9 -y
    if errorlevel 1 (
        echo ERROR: Failed to create conda environment
        pause
        exit /b 1
    )
    echo Conda environment created successfully
)

REM Activate conda environment
echo Activating conda environment wan2gp...
call conda activate wan2gp
if errorlevel 1 (
    echo ERROR: Failed to activate conda environment
    pause
    exit /b 1
)

REM Check if PyTorch is installed with correct version
python -c "import torch; print('PyTorch version:', torch.__version__)" >nul 2>&1
if errorlevel 1 (
    echo Installing PyTorch 2.6.0 with CUDA 12.4 support...
    pip install torch==2.6.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/test/cu124
    if errorlevel 1 (
        echo ERROR: Failed to install PyTorch
        pause
        exit /b 1
    )
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

REM Ask user to choose mode
echo.
echo ========================================
echo Choose WAN2GP Mode:
echo ========================================
echo 1. Text-to-Video (default)
echo 2. Image-to-Video
echo.
set /p MODE_CHOICE="Enter your choice (1 or 2, default is 1): "

REM Set default if no input
if "%MODE_CHOICE%"=="" set MODE_CHOICE=1

REM Set command based on choice
if "%MODE_CHOICE%"=="1" (
    set COMMAND=python wgp.py
    set MODE_NAME=Text-to-Video
) else if "%MODE_CHOICE%"=="2" (
    set COMMAND=python wgp.py --i2v
    set MODE_NAME=Image-to-Video
) else (
    echo Invalid choice. Using Text-to-Video mode as default.
    set COMMAND=python wgp.py
    set MODE_NAME=Text-to-Video
)

REM Set environment variables for better performance
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
set CUDA_VISIBLE_DEVICES=0

REM Start the Gradio server
echo.
echo ========================================
echo Starting WAN2GP in %MODE_NAME% mode...
echo Server will be available at: http://localhost:7860
echo Press Ctrl+C to stop the server
echo ========================================
echo.

%COMMAND%

REM If we get here, the server has stopped
echo.
echo ========================================
echo Server stopped
echo ========================================
pause
