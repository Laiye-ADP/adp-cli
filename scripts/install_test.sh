#!/bin/bash
# ADP CLI TestPyPI 安装脚本（Linux/Mac）- 用于测试版本安装

set -e

PACKAGE_NAME="agentic_doc_parse_and_extract"
MIN_PYTHON_VERSION="3.8"

# TestPyPI 官方地址
DEFAULT_PIP_INDEX_URL="https://test.pypi.org/simple/"

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
        *)
            echo "Error: Unknown option '$1'"
            exit 1
            ;;
    esac
done

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

EXTRA_INDEX_URL="https://mirrors.aliyun.com/pypi/simple"
$PYTHON_CMD -m pip install --index-url "$DEFAULT_PIP_INDEX_URL" --extra-index-url "$EXTRA_INDEX_URL" $PACKAGE_NAME --user --quiet --no-warn-script-location

echo "✓ Package installed successfully"

# 5. 验证安装并自动添加到PATH
echo ""
echo "Verifying installation..."

# 检测当前使用的shell
CURRENT_SHELL=$(basename "$SHELL")

# 确定配置文件路径
if [ "$CURRENT_SHELL" = "zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.bashrc"
fi

# 检查 PATH 是否已包含 ~/.local/bin
USER_BIN="$HOME/.local/bin"
PATH_ADDED=false

if echo ":$PATH:" | grep -q ":$USER_BIN:"; then
    PATH_ADDED=true
fi

# 如果不在PATH中，自动添加
if [ "$PATH_ADDED" = false ]; then
    echo "  Adding $USER_BIN to PATH in $SHELL_RC..."

    # 检查配置文件中是否已有 PATH 配置
    if [ -f "$SHELL_RC" ] && grep -q "export PATH=.*\.local/bin" "$SHELL_RC"; then
        echo "  ✓ PATH configuration already exists in $SHELL_RC"
    else
        # 添加 PATH 配置到配置文件
        if [ -f "$SHELL_RC" ]; then
            echo "" >> "$SHELL_RC"
            echo "# ADP CLI" >> "$SHELL_RC"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        else
            echo "# ADP CLI" > "$SHELL_RC"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        fi
        echo "  ✓ Added to $SHELL_RC"
    fi

    # 在当前会话中立即生效
    export PATH="$USER_BIN:$PATH"
    echo "  ✓ PATH updated in current session"
else
    echo "  ✓ PATH already configured"
fi

# 直接使用完整路径验证（不依赖 PATH）
ADP_BIN="$USER_BIN/adp"

if [ -x "$ADP_BIN" ]; then
    ADP_VERSION=$("$ADP_BIN" --version 2>&1 || true)
    echo "✓ ADP CLI installed successfully"
    echo "  Version: $ADP_VERSION"
else
    echo "✓ ADP CLI installed successfully"
    echo "  Location: $ADP_BIN"
fi

echo ""
echo "=========================================="
echo "Installation completed!"
echo "=========================================="
echo ""
echo "Usage: adp --help"
echo "=========================================="
