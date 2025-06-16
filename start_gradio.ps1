# PowerShell script to start the WAN2GP Gradio server on Windows
# This script will set up the environment and start the Gradio application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting WAN2GP Gradio Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check if Python is installed
if (-not (Test-Command "python")) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add it to your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Display Python version
$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Check if we're in the correct directory (look for app.py)
if (-not (Test-Path "app.py")) {
    Write-Host "ERROR: app.py not found in current directory" -ForegroundColor Red
    Write-Host "Please run this script from the WAN2GP project directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists, if not create one
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$gradioInstalled = pip show gradio 2>$null
if (-not $gradioInstalled) {
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install requirements" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Requirements installed successfully" -ForegroundColor Green
}

# Set environment variables for better performance
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:512"
$env:CUDA_VISIBLE_DEVICES = "0"

# Start the Gradio server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Gradio server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:7860" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

try {
    python app.py
}
catch {
    Write-Host "ERROR: Failed to start the server" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
finally {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Server stopped" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
}
