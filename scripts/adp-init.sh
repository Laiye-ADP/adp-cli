#!/bin/bash
# ADP CLI One-click Initialization Script
# Usage: source <(curl -sSL https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/adp-init.sh)

ADP_BIN_DIR="$HOME/.local/bin"
INSTALL_SCRIPT_URL="https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install_test.sh"

echo "ADP CLI initializing..."

# Check if already installed
if [ -x "$ADP_BIN_DIR/adp" ]; then
    echo "  ADP CLI is already installed"
else
    echo "  ADP CLI not installed, starting installation..."
    curl -sSL "$INSTALL_SCRIPT_URL" | bash
fi

# Set PATH (current shell)
export PATH="$ADP_BIN_DIR:$PATH"

# Verify PATH
if echo ":$PATH:" | grep -q ":$ADP_BIN_DIR:"; then
    echo "  PATH configured successfully"
else
    echo "  PATH configuration failed"
fi
