#!/bin/bash
# Build script for ADP CLI (Linux/macOS)
# Creates standalone executable using PyInstaller

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ADP CLI Build Script (Unix/Linux/macOS)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Detect platform
PLATFORM=$(uname -s)
case $PLATFORM in
    Linux*)
        PLATFORM_NAME="Linux"
        ;;
    Darwin*)
        PLATFORM_NAME="macOS"
        ;;
    *)
        PLATFORM_NAME="Unknown Unix"
        ;;
esac

echo -e "${YELLOW}Detected platform: $PLATFORM_NAME${NC}"
echo ""

# Find Python interpreter (try multiple possibilities)
PYTHON_CMD=""
for cmd in python3 python3.12 python3.11 python3.10 python3.9 python3.8; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}Error: Python 3.8+ not found${NC}"
    echo -e "${RED}Please install Python 3.8 or higher${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${YELLOW}Using Python: $PYTHON_CMD ($PYTHON_VERSION)${NC}"
echo ""

# Check if virtual environment exists (platform-specific to coexist with Windows .venv)
VENV_DIR="$PROJECT_ROOT/.venv-linux"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Install/upgrade dependencies
echo -e "${YELLOW}Installing/upgrading dependencies...${NC}"
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"
pip install pyinstaller

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -f "$PROJECT_ROOT/dist/adp" 2>/dev/null || true

# Run PyInstaller
echo -e "${YELLOW}Building executable with PyInstaller...${NC}"
cd "$PROJECT_ROOT"
pyinstaller "$PROJECT_ROOT/build/adp_cli.spec" --clean --noconfirm

# Check if build succeeded
if [ -f "$PROJECT_ROOT/dist/adp" ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Build successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}Executable location:${NC}"
    echo -e "  $PROJECT_ROOT/dist/adp"
    echo ""
    echo -e "${YELLOWGC}You can now run:${NC}"
    echo -e "  $PROJECT_ROOT/dist/adp --help"
    echo ""

    # Optionally create a symlink for easy access
    if [ "$1" = "--install" ]; then
        echo -e "${YELLOW}Installing system-wide symlink...${NC}"
        sudo ln -sf "$PROJECT_ROOT/dist/adp" /usr/local/bin/adp
        echo -e "${GREEN}You can now run 'adp' from anywhere${NC}"
    fi
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  Build failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi

# Deactivate virtual environment
deactivate
