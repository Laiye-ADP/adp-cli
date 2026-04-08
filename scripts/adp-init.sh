#!/bin/bash
# ADP CLI Auto-Initialization Script
# Modified to dynamically detect Python environment with fallback

ADP_BIN_DIR="$HOME/.local/bin"
INSTALL_SCRIPT_URL="https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install_test.sh"

# Function to find Python in common installation directories
find_python() {
    local python_dirs=(
        "/usr/bin"
        "/usr/local/bin"
        "$HOME/.local/bin"
        "$HOME/.pyenv/shims"
        "/opt/python/bin"
        "/usr/bin/python3"
        "/usr/local/bin/python3"
        "/Library/Frameworks/Python.framework/Versions/3.8/bin"
        "/Library/Frameworks/Python.framework/Versions/3.9/bin"
        "/Library/Frameworks/Python.framework/Versions/3.10/bin"
        "/Library/Frameworks/Python.framework/Versions/3.11/bin"
        "/Library/Frameworks/Python.framework/Versions/3.12/bin"
    )

    for dir in "${python_dirs[@]}"; do
        if [ -x "$dir/python" ] || [ -x "$dir/python3" ]; then
            local python_cmd="$dir/python"
            [ -x "$python_cmd" ] || python_cmd="$dir/python3"
            echo "$python_cmd"
            return 0
        fi
    done
    return 1
}

echo "=== Detecting Python Environment ==="

# Step 1: Try to find Python from PATH
python_cmd=""
if command -v python &> /dev/null; then
    python_cmd=$(command -v python)
elif command -v python3 &> /dev/null; then
    python_cmd=$(command -v python3)
fi

# Step 2: If not found in PATH, try common installation directories
if [ -z "$python_cmd" ]; then
    echo "Python not found in PATH, searching common installation directories..."
    python_cmd=$(find_python)
fi

# Step 3: Report result
if [ -n "$python_cmd" ]; then
    python_dir=$(dirname "$python_cmd")
    ADP_BIN_DIR="$python_dir"
    echo "Found Python: $python_cmd"
    echo "Using directory: $ADP_BIN_DIR"
else
    echo "Python not found in PATH or common directories" >&2
    echo "Please install Python 3.8 or higher first" >&2
    echo "Download from: https://www.python.org/downloads/" >&2
    exit 1
fi

echo ""

# Step 4: Check if ADP CLI already installed
if [ -x "$ADP_BIN_DIR/adp" ]; then
    echo "ADP CLI already installed at $ADP_BIN_DIR"
else
    echo "ADP CLI not found, starting installation..."

    # Download install script
    temp_script="/tmp/install-adp.sh"
    if command -v curl &> /dev/null; then
        curl -sSL "$INSTALL_SCRIPT_URL" -o "$temp_script"
    elif command -v wget &> /dev/null; then
        wget -q "$INSTALL_SCRIPT_URL" -O "$temp_script"
    else
        echo "Error: Neither curl nor wget found" >&2
        exit 1
    fi

    if [ $? -ne 0 ]; then
        echo "Error: Failed to download install script" >&2
        exit 1
    fi

    chmod +x "$temp_script"

    # Execute install script
    echo "Running install script..."
    bash "$temp_script"

    if [ $? -ne 0 ]; then
        echo "Error: Installation failed" >&2
        exit 1
    fi
fi

# Step 5: Set PATH for current session
export PATH="$ADP_BIN_DIR:$PATH"

# Verify PATH
if echo ":$PATH:" | grep -q ":$ADP_BIN_DIR:"; then
    echo "PATH setting for current session: SUCCESS"
else
    echo "PATH setting for current session: FAILED"
fi

# Step 6: Permanently add to user environment variable
if [ -d "$ADP_BIN_DIR" ]; then
    if [ -w "$HOME/.bashrc" ]; then
        if ! grep -q "$ADP_BIN_DIR" "$HOME/.bashrc" 2>/dev/null; then
            echo "export PATH=\"$ADP_BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
            echo "PATH permanently added to ~/.bashrc: SUCCESS"
        else
            echo "PATH already exists in ~/.bashrc"
        fi
    fi
    if [ -w "$HOME/.zshrc" ]; then
        if ! grep -q "$ADP_BIN_DIR" "$HOME/.zshrc" 2>/dev/null; then
            echo "export PATH=\"$ADP_BIN_DIR:\$PATH\"" >> "$HOME/.zshrc"
            echo "PATH permanently added to ~/.zshrc: SUCCESS"
        else
            echo "PATH already exists in ~/.zshrc"
        fi
    fi
fi

echo ""
echo "=== Initialization Complete ==="
