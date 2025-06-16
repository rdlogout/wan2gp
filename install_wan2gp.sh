#!/bin/bash

# Quick installation script for WAN2GP on Linux/Mac
# This script will clone the repository and set up the environment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}WAN2GP Quick Installation Script${NC}"
echo -e "${CYAN}========================================${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: Git is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install Git first${NC}"
    exit 1
fi

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}ERROR: Conda is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install Anaconda or Miniconda first${NC}"
    echo -e "${YELLOW}Download from: https://docs.conda.io/en/latest/miniconda.html${NC}"
    exit 1
fi

echo -e "${GREEN}Git and Conda are available!${NC}"
echo ""

# Ask for installation directory
read -p "Enter installation directory (default: $HOME/WAN2GP): " INSTALL_DIR
if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$HOME/WAN2GP"
fi

# Create directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
fi

# Clone the repository
echo ""
echo -e "${YELLOW}Cloning WAN2GP repository...${NC}"
cd "$INSTALL_DIR"
git clone https://github.com/deepbeepmeep/Wan2GP.git .
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to clone repository${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Repository cloned successfully!${NC}"
echo ""

# Create conda environment
echo -e "${YELLOW}Creating conda environment wan2gp with Python 3.10.9...${NC}"
conda create -n wan2gp python=3.10.9 -y
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to create conda environment${NC}"
    exit 1
fi

# Activate environment and install dependencies
echo ""
echo -e "${YELLOW}Activating environment and installing dependencies...${NC}"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate wan2gp

echo -e "${YELLOW}Installing PyTorch 2.6.0 with CUDA 12.4 support...${NC}"
pip install torch==2.6.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/test/cu124
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install PyTorch${NC}"
    exit 1
fi

echo -e "${YELLOW}Installing requirements...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install requirements${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}WAN2GP has been installed to: $INSTALL_DIR${NC}"
echo ""
echo -e "${YELLOW}To start the application:${NC}"
echo -e "${YELLOW}1. Navigate to the installation directory${NC}"
echo -e "${YELLOW}2. Run ./start_gradio.sh${NC}"
echo ""
echo -e "${YELLOW}Or you can start it now by pressing Enter...${NC}"
read -p ""

# Start the application
./start_gradio.sh
