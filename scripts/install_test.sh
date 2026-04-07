#!/bin/bash
# ADP CLI TestPyPI 安装脚本（Linux/Mac）- 用于测试版本安装

set -e

PACKAGE_NAME="agentic_doc_parse_and_extract"
MIN_PYTHON_VERSION="3.8"
SELECTED_MIRROR="aliyun"

# TestPyPI 官方地址
DEFAULT_PIP_INDEX_URL="https://test.pypi.org/simple/"

# 国内镜像源映射
declare -A PYPI_MIRRORS=(
    ["aliyun"]="https://mirrors.aliyun.com/pypi/simple"
    ["tsinghua"]="https://pypi.tuna.tsinghua.edu.cn/simple"
    ["douban"]="https://pypi.douban.com/simple"
    ["ustc"]="https://pypi.mirrors.ustc.edu.cn/simple"
)

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --index-url)
            if [ -z "$2" ]; then
                echo "Error: --index-url requires a value"
                exit 1
            fi
            DEFAULT_PIP_INDEX_URL="$2"
            shift 2
            ;;
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

# 国内镜像源
if [ -n "${PYPI_MIRRORS[$SELECTED_MIRROR]}" ]; then
    EXTRA_INDEX_URL="${PYPI_MIRRORS[$SELECTED_MIRROR]}"
else
    echo "Error: Invalid mirror name '$SELECTED_MIRROR'"
    echo "Available mirrors: aliyun, tsinghua, douban, ustc"
    exit 1
fi

echo "=========================================="
echo "ADP CLI Installation from TestPyPI"
echo "=========================================="
echo "Package: $PACKAGE_NAME"
echo "Minimum Python: $MIN_PYTHON_VERSION"
echo "Index URL: $DEFAULT_PIP_INDEX_URL"
echo "=========================================="
echo ""

# 1. 检查Python安装
echo "[1/4] Checking Python environment..."

# 检查Python命令
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

# 验证Python版本
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Error: Python $MIN_PYTHON_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi
echo "  ✓ Python version meets requirements (>= $MIN_PYTHON_VERSION)"

# 检查Python可执行文件路径
PYTHON_EXEC=$($PYTHON_CMD -c "import sys; print(sys.executable)" 2>/dev/null)
echo "  Python executable: $PYTHON_EXEC"

# 2. 检查pip
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
    # 尝试通过python -m pip
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
echo "  ✓ pip is available"

# 3. 检查系统架构和平台
echo ""
echo "[3/4] Checking system platform..."
UNAME_INFO=$(uname -a 2>/dev/null || echo "unknown")
echo "  System: $UNAME_INFO"

# 检查是否为虚拟环境
VIRTUAL_ENV=$($PYTHON_CMD -c "import sys; print(getattr(sys, 'real_prefix', getattr(sys, 'base_prefix', None)) or '')" 2>/dev/null)
if [ -n "$VIRTUAL_ENV" ]; then
    echo "  Virtual environment: active ($VIRTUAL_ENV)"
else
    echo "  Virtual environment: none (system Python)"
fi
echo "  ✓ System platform check completed"

# 4. 安装包
echo ""
echo "[4/4] Installing $PACKAGE_NAME from TestPyPI..."

$PYTHON_CMD -m pip install --index-url "$DEFAULT_PIP_INDEX_URL" --extra-index-url "$EXTRA_INDEX_URL" $PACKAGE_NAME --user --quiet --no-warn-script-location

echo "✓ Package installed successfully"

# 验证安装
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
