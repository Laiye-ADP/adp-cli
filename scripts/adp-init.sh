#!/bin/bash
# ADP CLI 一键初始化脚本
# 使用方式: source <(curl -sSL https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/adp-init.sh)

ADP_BIN_DIR="$HOME/.local/bin"
INSTALL_SCRIPT_URL="https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install_test.sh"

echo "ADP CLI 初始化..."

# 检查是否已安装（直接检查安装目录）
if [ -x "$ADP_BIN_DIR/adp" ]; then
    echo "✓ ADP CLI 已安装"
else
    echo "ADP CLI 未安装，开始安装..."
    curl -sSL "$INSTALL_SCRIPT_URL" | bash
fi

# 设置 PATH（当前 shell）
export PATH="$ADP_BIN_DIR:$PATH"

# 验证 PATH
if echo ":$PATH:" | grep -q ":$ADP_BIN_DIR:"; then
    echo "✓ PATH 设置成功"
else
    echo "✗ PATH 设置失败"
fi