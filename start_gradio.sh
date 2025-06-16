#!/bin/bash

# Shell script to start the WAN2GP Gradio server on Linux/Mac
# This script will set up the environment and start the Gradio application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Starting WAN2GP Gradio Server${NC}"
echo -e "${CYAN}========================================${NC}"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}ERROR: Conda is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install Anaconda or Miniconda first${NC}"
    echo -e "${YELLOW}Download from: https://docs.conda.io/en/latest/miniconda.html${NC}"
    exit 1
fi

# Display conda version
CONDA_VERSION=$(conda --version)
echo -e "${GREEN}Found: $CONDA_VERSION${NC}"

# Check if we're in the correct directory (look for wgp.py)
if [ ! -f "wgp.py" ]; then
    echo -e "${RED}ERROR: wgp.py not found in current directory${NC}"
    echo ""
    echo -e "${YELLOW}This script should be run from the WAN2GP project directory.${NC}"
    echo -e "${YELLOW}If you haven't cloned the repository yet, run:${NC}"
    echo -e "${YELLOW}  git clone https://github.com/deepbeepmeep/Wan2GP.git${NC}"
    echo -e "${YELLOW}  cd Wan2GP${NC}"
    echo ""
    exit 1
fi

# Check if conda environment exists, if not create it
if ! conda info --envs | grep -q "wan2gp"; then
    echo -e "${YELLOW}Creating conda environment wan2gp with Python 3.10.9...${NC}"
    conda create -n wan2gp python=3.10.9 -y
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to create conda environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}Conda environment created successfully${NC}"
fi

# Activate conda environment
echo -e "${YELLOW}Activating conda environment wan2gp...${NC}"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate wan2gp
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to activate conda environment${NC}"
    exit 1
fi

# Check if PyTorch is installed with correct version
if ! python -c "import torch; print('PyTorch version:', torch.__version__)" &> /dev/null; then
    echo -e "${YELLOW}Installing PyTorch 2.6.0 with CUDA 12.4 support...${NC}"
    pip install torch==2.6.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/test/cu124
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install PyTorch${NC}"
        exit 1
    fi
else
    TORCH_VERSION=$(python -c "import torch; print('PyTorch version:', torch.__version__)")
    echo -e "${GREEN}PyTorch is installed: $TORCH_VERSION${NC}"
fi

# Check if requirements are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! pip show gradio &> /dev/null; then
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install requirements${NC}"
        exit 1
    fi
    echo -e "${GREEN}Requirements installed successfully${NC}"
fi

# Ask user to choose mode
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Choose WAN2GP Mode:${NC}"
echo -e "${CYAN}========================================${NC}"
echo "1. Text-to-Video (default)"
echo "2. Image-to-Video"
echo ""
read -p "Enter your choice (1 or 2, default is 1): " MODE_CHOICE

# Set default if no input
if [ -z "$MODE_CHOICE" ]; then
    MODE_CHOICE=1
fi

# Set command based on choice
case $MODE_CHOICE in
    1)
        COMMAND="python wgp.py"
        MODE_NAME="Text-to-Video"
        ;;
    2)
        COMMAND="python wgp.py --i2v"
        MODE_NAME="Image-to-Video"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice. Using Text-to-Video mode as default.${NC}"
        COMMAND="python wgp.py"
        MODE_NAME="Text-to-Video"
        ;;
esac

# Set environment variables for better performance
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_VISIBLE_DEVICES=0

# Start the Gradio server
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Starting WAN2GP in $MODE_NAME mode...${NC}"
echo -e "${YELLOW}Server will be available at: http://localhost:7860${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

$COMMAND

# If we get here, the server has stopped
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${YELLOW}Server stopped${NC}"
echo -e "${CYAN}========================================${NC}"
