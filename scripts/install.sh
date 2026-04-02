#!/bin/bash
# ADP CLI PyPI 安装脚本（Linux/Mac）- 支持国内镜像源

set -e

PACKAGE_NAME="agentic_doc_parse_and_extract"
MIN_PYTHON_VERSION="3.8"

# 国内镜像源（可修改）
PYPI_MIRRORS=(
    "https://mirrors.aliyun.com/pypi/simple"     # 阿里云源
    "https://pypi.tuna.tsinghua.edu.cn/simple"  # 清华源
    "https://pypi.douban.com/simple"            # 豆瓣源
    "https://pypi.mirrors.ustc.edu.cn/simple"   # 中科大源
)

# 默认使用第一个镜像（阿里云源）
DEFAULT_PIP_INDEX_URL="${PYPI_MIRRORS[0]}"

echo "=========================================="
echo "ADP CLI Installation from PyPI"
echo "=========================================="
echo "Package: $PACKAGE_NAME"
echo "Minimum Python: $MIN_PYTHON_VERSION"
echo "Mirror: $DEFAULT_PIP_INDEX_URL"
echo "=========================================="
echo ""

# 1. 检查Python安装
echo "[1/3] Checking Python installation..."
PYTHON_CMD=""
for cmd in python3 python3.12 python3.11 python3.10 python3.9 python3.8; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python $MIN_PYTHON_VERSION or higher not found"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION ($PYTHON_CMD)"

# 2. 验证Python版本
echo ""
echo "[2/3] Validating Python version..."
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Error: Python $MIN_PYTHON_VERSION or higher is required"
    exit 1
fi
echo "✓ Python version meets requirements"

# 3. 安装包
echo ""
echo "[3/3] Installing $PACKAGE_NAME from PyPI..."

# 升级pip（使用国内源）
echo "Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip -i "$DEFAULT_PIP_INDEX_URL" --user --quiet

# 安装包（使用国内源）
echo "Installing package..."
$PYTHON_CMD -m pip install $PACKAGE_NAME -i "$DEFAULT_PIP_INDEX_URL" --user --quiet

echo "✓ Package installed successfully"

# 4. 验证安装
echo ""
echo "Verifying installation..."

# 检查adp命令是否在PATH中
if command -v adp &> /dev/null; then
    ADP_VERSION=$(adp --version 2>&1 || true)
    echo "✓ ADP CLI installed successfully"
    echo "  Version: $ADP_VERSION"
    echo ""
    echo "You can now use: adp --help"
else
    #    # 如果不在PATH中，提供添加PATH的说明
    USER_BIN="$HOME/.local/bin"
    echo "✓ ADP CLI installed successfully"
    echo "  Location: $USER_BIN/adp"
    echo ""
    echo "To use ADP CLI, add the following to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo
    echo "Then run: source ~/.bashrc  (或 source ~/.zshrc)"
fi

echo ""
echo "=========================================="
echo "Installation completed!"
echo "=========================================="
echo ""
echo "Usage: adp --help"
echo "=========================================="
