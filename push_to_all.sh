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
else
    echo -e "${RED}✗ Failed to push to Hugging Face${NC}"
    exit 1
fi

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
if git push github main; then
    echo -e "${GREEN}✓ Successfully pushed to GitHub${NC}"
else
    echo -e "${RED}✗ Failed to push to GitHub${NC}"
    exit 1
fi

echo -e "${GREEN}=== Successfully pushed to both repositories ===${NC}"
