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
echo -e "${GREEN}  ADP CLI Build Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Detect platform and architecture
PLATFORM=$(uname -s)
ARCH=$(uname -m)

case $PLATFORM in
    Linux*)
        PLATFORM_NAME="Linux"
        if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
            OUTPUT_DIR="$PROJECT_ROOT/dist/linux-arm64"
            OUTPUT_NAME="adp"
        else
            OUTPUT_DIR="$PROJECT_ROOT/dist/linux-x64"
            OUTPUT_NAME="adp"
        fi
        ;;
    Darwin*)
        PLATFORM_NAME="macOS"
        if [ "$ARCH" = "arm64" ]; then
            OUTPUT_DIR="$PROJECT_ROOT/dist/darwin-arm64"
            OUTPUT_NAME="adp"
        else
            OUTPUT_DIR="$PROJECT_ROOT/dist/darwin-x64"
            OUTPUT_NAME="adp"
        fi
        ;;
    *)
        PLATFORM_NAME="Unknown Unix"
        OUTPUT_DIR="$PROJECT_ROOT/dist/unknown"
        OUTPUT_NAME="adp"
        ;;
esac

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${YELLOW}Detected platform: $PLATFORM_NAME ($ARCH)${NC}"
echo -e "${YELLOW}Output directory: $OUTPUT_DIR${NC}"
echo ""

# Add custom Python locations to PATH (for self-built Python with shared library)
export PATH="/usr/local/python3.8/bin:/usr/local/python3.11/bin:/usr/local/bin:$PATH"

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
pip install --upgrade pip || {
    echo -e "${RED}Error: Failed to upgrade pip${NC}"
    exit 1
}
pip install -r "$PROJECT_ROOT/requirements.txt" || {
    echo -e "${RED}Error: Failed to install dependencies${NC}"
    exit 1
}
pip install pyinstaller || {
    echo -e "${RED}Error: Failed to install PyInstaller${NC}"
    exit 1
}

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -f "$OUTPUT_DIR/$OUTPUT_NAME" 2>/dev/null || true

# Run PyInstaller with output to platform directory
echo -e "${YELLOW}Building executable with PyInstaller...${NC}"
cd "$PROJECT_ROOT"

# When using .spec file, --distpath and --name are ignored
# The spec file already defines name="adp" and we need to move the output afterwards
pyinstaller "$PROJECT_ROOT/adp_cli.spec" --clean --noconfirm || {
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  Build failed!${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}PyInstaller encountered errors. Check output above.${NC}"
    exit 1
}

# Check if build succeeded (spec file outputs to dist/ by default)
if [ -f "$PROJECT_ROOT/dist/$OUTPUT_NAME" ]; then
    # Move to platform-specific directory
    mv "$PROJECT_ROOT/dist/$OUTPUT_NAME" "$OUTPUT_DIR/$OUTPUT_NAME"
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Build successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}Executable location:${NC}"
    echo -e "  $OUTPUT_DIR/$OUTPUT_NAME"
    echo ""
    echo -e "${YELLOW}You can now run:${NC}"
    echo -e "  $OUTPUT_DIR/$OUTPUT_NAME --help"
    echo ""

    # Optionally create a symlink for easy access
    if [ "$1" = "--install" ]; then
        echo -e "${YELLOW}Installing system-wide symlink...${NC}"
        sudo ln -sf "$OUTPUT_DIR/$OUTPUT_NAME" /usr/local/bin/adp
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
