#!/bin/bash
# ADP CLI 安装脚本（Linux/Mac）

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "ADP CLI Installation Script"
echo "=========================================="
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
    echo "Error: Python 3.8+ not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION ($PYTHON_CMD)"

if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi

echo ""

# 创建虚拟环境（平台特定）
VENV_DIR="$PROJECT_ROOT/.venv-linux"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# 激活虚拟环境
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 安装依赖
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"
pip install -e "$PROJECT_ROOT"

echo ""

# 验证安装
echo "Verifying installation..."
if command -v adp &> /dev/null; then
    echo "✓ ADP CLI installed successfully"
    echo ""
    echo "Try: adp --help"
else
    echo "✗ Installation failed"
    exit 1
fi

# 退出虚拟环境
deactivate

echo ""
echo "=========================================="
echo "Installation completed!"
echo "=========================================="
echo ""
echo "Virtual environment location: $VENV_DIR"
