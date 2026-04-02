#!/bin/bash
# ADP CLI TestPyPI 安装脚本（Linux/Mac）- 用于测试版本安装

set -e

PACKAGE_NAME="agentic_doc_parse_and_extract"
MIN_PYTHON_VERSION="3.8"
DO_UPGRADE=false
CHECK_UPDATE_ONLY=false

# TestPyPI 官方地址
DEFAULT_PIP_INDEX_URL="https://test.pypi.org/simple/"

# 帮助信息
show_help() {
    echo "ADP CLI TestPyPI Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "This script installs from TestPyPI (test.pypi.org) for testing purposes."
    echo ""
    echo "Options:"
    echo "  --upgrade         Upgrade to the latest version if already installed"
    echo "  --check-update    Check for available updates without installing"
    echo "  --index-url <url> Use custom PyPI index URL (default: TestPyPI)"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Install from TestPyPI"
    echo "  $0 --upgrade          # Upgrade from TestPyPI"
    echo "  $0 --check-update     # Check for updates on TestPyPI"
    echo "  $0 --index-url https://pypi.org/simple/  # Install from production PyPI"
    exit 0
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --upgrade)
            DO_UPGRADE=true
            shift
            ;;
        --check-update)
            CHECK_UPDATE_ONLY=true
            shift
            ;;
        --index-url)
            if [ -z "$2" ]; then
                echo "Error: --index-url requires a value"
                exit 1
            fi
            DEFAULT_PIP_INDEX_URL="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            ;;
        *)
            echo "Error: Unknown option '$1'"
            echo "Use --help for usage information"
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
if [ "$DO_UPGRADE" = true ]; then
    echo "Mode: Upgrade to latest"
elif [ "$CHECK_UPDATE_ONLY" = true ]; then
    echo "Mode: Check updates only"
else
    echo "Mode: Install (no upgrade)"
fi
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

# 3. 检查已安装版本
echo ""
echo "[3/5] Checking installed version..."

INSTALLED_VERSION=$($PYTHON_CMD -m pip show $PACKAGE_NAME 2>/dev/null | grep "^Version:" | cut -d' ' -f2)

if [ -n "$INSTALLED_VERSION" ]; then
    echo "✓ Current version: $INSTALLED_VERSION"
else
    echo "✓ Not installed yet"
fi

# 4. 检查最新版本（从TestPyPI）
echo ""
echo "[4/5] Checking latest version from TestPyPI..."

# 获取最新版本
LATEST_VERSION=$($PYTHON_CMD -m pip index versions --index-url "$DEFAULT_PIP_INDEX_URL" $PACKAGE_NAME 2>/dev/null | head -1 || echo "")

if [ -z "$LATEST_VERSION" ]; then
    echo "Warning: Could not retrieve latest version from TestPyPI"
    echo "  Make sure the package is published to TestPyPI"
    LATEST_VERSION="unknown"
else
    echo "✓ Latest version: $LATEST_VERSION"
fi

# 如果是仅检查模式
if [ "$CHECK_UPDATE_ONLY" = true ]; then
    echo ""
    echo "=========================================="
    echo "Update Check Results (TestPyPI)"
    echo "=========================================="
    if [ -z "$INSTALLED_VERSION" ]; then
        echo "Status: Not installed"
        echo "Latest version: $LATEST_VERSION"
        echo ""
        echo "To install: $0"
    elif [ "$INSTALLED_VERSION" = "$LATEST_VERSION" ]; then
        echo "Status: Up to date"
        echo "Current version: $INSTALLED_VERSION"
    elif [ "$LATEST_VERSION" = "unknown" ]; then
        echo "Status: Could not determine latest version"
        echo "Current version: $INSTALLED_VERSION"
    else
        echo "Status: Update available"
        echo "Current version: $INSTALLED_VERSION"
        echo "Latest version: $LATEST_VERSION"
        echo ""
        echo "To upgrade: $0 --upgrade"
    fi
    echo "=========================================="
    exit 0
fi

# 5. 安装/升级包
echo ""
echo "[5/5] Installing $PACKAGE_NAME from TestPyPI..."

if [ -n "$INSTALLED_VERSION" ]; then
    # 已安装
    if [ "$DO_UPGRADE" = true ]; then
        if [ "$INSTALLED_VERSION" = "$LATEST_VERSION" ]; then
            echo "✓ Already on latest version ($INSTALLED_VERSION)"
            echo "  No upgrade needed"
        elif [ "$LATEST_VERSION" = "unknown" ]; then
            echo "Warning: Could not determine latest version"
            echo "  Proceeding with upgrade attempt..."
            $PYTHON_CMD -m pip install --upgrade --index-url "$DEFAULT_PIP_INDEX_URL" $PACKAGE_NAME --user --quiet
            echo "✓ Package upgraded"
        else
            echo "  Current: $INSTALLED_VERSION"
            echo "  Upgrading to: $LATEST_VERSION"
            $PYTHON_CMD -m pip install --upgrade --index-url "$DEFAULT_PIP_INDEX_URL" $PACKAGE_NAME --user --quiet
            echo "✓ Package upgraded to $LATEST_VERSION"
        fi
    else
        if [ "$INSTALLED_VERSION" = "$LATEST_VERSION" ]; then
            echo "✓ Already up to date ($INSTALLED_VERSION)"
        elif [ "$LATEST_VERSION" != "unknown" ]; then
            echo "✓ Already installed ($INSTALLED_VERSION)"
            echo "  Note: New version available: $LATEST_VERSION"
            echo "  To upgrade: $0 --upgrade"
        else
            echo "✓ Already installed ($INSTALLED_VERSION)"
        fi
    fi
else
    # 未安装
    echo "  Installing: $LATEST_VERSION"
    $PYTHON_CMD -m pip install --index-url "$DEFAULT_PIP_INDEX_URL" $PACKAGE_NAME --user --quiet
    echo "✓ Package installed successfully"
fi

# 6. 验证安装
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
