#!/bin/bash
# ADP CLI PyPI Installation Script (Linux/Mac) - support China mirror sources

set -e

PACKAGE_NAME="agentic_doc_parse_and_extract"
MIN_PYTHON_VERSION="3.8"
SELECTED_MIRROR="aliyun"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mirror)
            if [ -z "$2" ]; then
                echo "Error: --mirror requires a value"
                exit 1
            fi
            SELECTED_MIRROR="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown option '$1'"
            exit 1
            ;;
    esac
done

# China mirror sources
declare -A PYPI_MIRRORS=(
    ["aliyun"]="https://mirrors.aliyun.com/pypi/simple"
    ["tsinghua"]="https://pypi.tuna.tsinghua.edu.cn/simple"
    ["douban"]="https://pypi.douban.com/simple"
    ["ustc"]="https://pypi.mirrors.ustc.edu.cn/simple"
)

# Default to Aliyun mirror
DEFAULT_PIP_INDEX_URL="${PYPI_MIRRORS[$SELECTED_MIRROR]}"
if [ -z "$DEFAULT_PIP_INDEX_URL" ]; then
    echo "Error: Invalid mirror name '$SELECTED_MIRROR'"
    echo "Available mirrors: aliyun, tsinghua, douban, ustc"
    exit 1
fi

echo "=========================================="
echo "ADP CLI Installation from PyPI"
echo "=========================================="
echo "Package: $PACKAGE_NAME"
echo "Minimum Python: $MIN_PYTHON_VERSION"
echo "Mirror: $DEFAULT_PIP_INDEX_URL"
echo "=========================================="
echo ""

# 1. Check Python installation
echo "[1/4] Checking Python environment..."

# Check Python command
PYTHON_CMD=""
for cmd in python3 python3.12 python3.11 python3.10 python3.9 python3.8 python; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python $MIN_PYTHON_VERSION or higher not found"
    echo "Please install Python $MIN_PYTHON_VERSION or higher first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "  Python command: $PYTHON_CMD"
echo "  Python version: $PYTHON_VERSION"

# Verify Python version
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Error: Python $MIN_PYTHON_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi
echo "  [OK] Python version meets requirements (>= $MIN_PYTHON_VERSION)"

# Get Python executable path
PYTHON_EXEC=$($PYTHON_CMD -c "import sys; print(sys.executable)" 2>/dev/null)
echo "  Python executable: $PYTHON_EXEC"

# 2. Check pip
echo ""
echo "[2/4] Checking pip..."
PIP_CMD=""
for cmd in pip3 pip; do
    if command -v $cmd &> /dev/null; then
        PIP_CMD=$cmd
        break
    fi
done

if [ -z "$PIP_CMD" ]; then
    # Try via python -m pip
    if $PYTHON_CMD -m pip --version &>/dev/null; then
        PIP_CMD="$PYTHON_CMD -m pip"
    else
        echo "Error: pip not found"
        echo "Please ensure pip is installed for Python $PYTHON_VERSION"
        exit 1
    fi
fi

PIP_VERSION=$($PIP_CMD --version 2>&1 | awk '{print $2}')
echo "  pip version: $PIP_VERSION"
echo "  [OK] pip is available"

# 3. Check system architecture and platform
echo ""
echo "[3/4] Checking system platform..."
UNAME_INFO=$(uname -a 2>/dev/null || echo "unknown")
echo "  System: $UNAME_INFO"

# Check if in virtual environment
VIRTUAL_ENV=$($PYTHON_CMD -c "import sys; print(getattr(sys, 'real_prefix', getattr(sys, 'base_prefix', None)) or '')" 2>/dev/null)
if [ -n "$VIRTUAL_ENV" ]; then
    echo "  Virtual environment: active ($VIRTUAL_ENV)"
else
    echo "  Virtual environment: none (system Python)"
fi
echo "  [OK] System platform check completed"

# 4. Install package
echo ""
echo "[4/4] Installing $PACKAGE_NAME from PyPI..."

$PYTHON_CMD -m pip install $PACKAGE_NAME \
    -i "$DEFAULT_PIP_INDEX_URL" \
    --user --quiet --no-warn-script-location \
    --extra-index-url "$DEFAULT_PIP_INDEX_URL" \
    --root-user-action=ignore

echo "  [OK] Package installed successfully"

# Verify installation
echo ""
echo "=========================================="
echo "Installation completed!"
echo "=========================================="
echo ""
echo "Next step: Setup PATH"
echo "  curl -sSL https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/adp-init.sh | bash"
echo ""
echo "Usage: adp --help"
echo "=========================================="
