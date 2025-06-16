#!/bin/bash

# Script to push to both Hugging Face and GitHub repositories
# Usage: ./push_to_all.sh [commit_message]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Pushing to both Hugging Face and GitHub ===${NC}"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Clean up any cache files that might cause issues
echo -e "${YELLOW}Cleaning up cache files...${NC}"
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Check if there are any changes to commit
if git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}No changes to commit. Pushing existing commits...${NC}"
else
    # Get commit message from argument or prompt user
    if [ -z "$1" ]; then
        echo -e "${YELLOW}Enter commit message:${NC}"
        read -r COMMIT_MSG
    else
        COMMIT_MSG="$1"
    fi

    # Add all changes and commit
    echo -e "${YELLOW}Adding and committing changes...${NC}"
    git add .
    git commit -m "$COMMIT_MSG"
fi

# Push to Hugging Face (origin)
echo -e "${YELLOW}Pushing to Hugging Face...${NC}"
if git push origin main; then
    echo -e "${GREEN}✓ Successfully pushed to Hugging Face${NC}"
    HF_SUCCESS=true
else
    echo -e "${RED}✗ Failed to push to Hugging Face${NC}"
    echo -e "${YELLOW}This might be due to binary files or other restrictions${NC}"
    HF_SUCCESS=false
fi

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
if git push github main; then
    echo -e "${GREEN}✓ Successfully pushed to GitHub${NC}"
    GH_SUCCESS=true
else
    echo -e "${RED}✗ Failed to push to GitHub${NC}"
    GH_SUCCESS=false
fi

# Summary
if [ "$HF_SUCCESS" = true ] && [ "$GH_SUCCESS" = true ]; then
    echo -e "${GREEN}=== Successfully pushed to both repositories ===${NC}"
elif [ "$HF_SUCCESS" = true ] || [ "$GH_SUCCESS" = true ]; then
    echo -e "${YELLOW}=== Partially successful - check failed pushes above ===${NC}"
    exit 1
else
    echo -e "${RED}=== Failed to push to both repositories ===${NC}"
    exit 1
fi
