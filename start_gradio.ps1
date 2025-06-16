# PowerShell script to start the WAN2GP Gradio server on Windows
# This script will set up the environment and start the Gradio application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting WAN2GP Gradio Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check if conda is installed
if (-not (Test-Command "conda")) {
    Write-Host "ERROR: Conda is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Anaconda or Miniconda first" -ForegroundColor Yellow
    Write-Host "Download from: https://docs.conda.io/en/latest/miniconda.html" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Display conda version
$condaVersion = conda --version
Write-Host "Found: $condaVersion" -ForegroundColor Green

# Check if we're in the correct directory (look for wgp.py)
if (-not (Test-Path "wgp.py")) {
    Write-Host "ERROR: wgp.py not found in current directory" -ForegroundColor Red
    Write-Host "" -ForegroundColor Yellow
    Write-Host "This script should be run from the WAN2GP project directory." -ForegroundColor Yellow
    Write-Host "If you haven't cloned the repository yet, run:" -ForegroundColor Yellow
    Write-Host "  git clone https://github.com/deepbeepmeep/Wan2GP.git" -ForegroundColor Yellow
    Write-Host "  cd Wan2GP" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if conda environment exists, if not create it
$envExists = conda info --envs | Select-String "wan2gp"
if (-not $envExists) {
    Write-Host "Creating conda environment wan2gp with Python 3.10.9..." -ForegroundColor Yellow
    conda create -n wan2gp python=3.10.9 -y
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create conda environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Conda environment created successfully" -ForegroundColor Green
}

# Activate conda environment
Write-Host "Activating conda environment wan2gp..." -ForegroundColor Yellow
conda activate wan2gp
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate conda environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if PyTorch is installed with correct version
try {
    $torchCheck = python -c "import torch; print('PyTorch version:', torch.__version__)" 2>$null
    if (-not $torchCheck) {
        throw "PyTorch not found"
    }
    Write-Host "PyTorch is installed: $torchCheck" -ForegroundColor Green
}
catch {
    Write-Host "Installing PyTorch 2.6.0 with CUDA 12.4 support..." -ForegroundColor Yellow
    pip install torch==2.6.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/test/cu124
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install PyTorch" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
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

# Ask user to choose mode
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Choose WAN2GP Mode:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Text-to-Video (default)" -ForegroundColor White
Write-Host "2. Image-to-Video" -ForegroundColor White
Write-Host ""

$modeChoice = Read-Host "Enter your choice (1 or 2, default is 1)"

# Set default if no input
if ([string]::IsNullOrWhiteSpace($modeChoice)) {
    $modeChoice = "1"
}

# Set command based on choice
switch ($modeChoice) {
    "1" {
        $command = "python wgp.py"
        $modeName = "Text-to-Video"
    }
    "2" {
        $command = "python wgp.py --i2v"
        $modeName = "Image-to-Video"
    }
    default {
        Write-Host "Invalid choice. Using Text-to-Video mode as default." -ForegroundColor Yellow
        $command = "python wgp.py"
        $modeName = "Text-to-Video"
    }
}

# Set environment variables for better performance
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:512"
$env:CUDA_VISIBLE_DEVICES = "0"

# Start the Gradio server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting WAN2GP in $modeName mode..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:7860" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    Invoke-Expression $command
}
catch {
    Write-Host "ERROR: Failed to start the server" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Server stopped" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
}
