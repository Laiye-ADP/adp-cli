# Cross-Platform Development Setup

This guide explains how to work with ADP CLI on both Windows and Linux/macOS (including WSL).

## The Challenge

When working in a Windows environment with WSL (Windows Subsystem for Linux), both platforms share the same project files but require different virtual environment structures:

- **Windows**: `.venv/Scripts/activate` (Windows-style paths)
- **Linux/macOS**: `.venv/bin/activate` (Unix-style paths)

## The Solution: Platform-Specific Virtual Environments

To avoid conflicts, we use platform-specific virtual environment names:

| Platform | Virtual Environment Path |
|----------|------------------------|
| Windows  | `.venv/` |
| Linux/macOS | `.venv-linux/` |
| macOS (Apple Silicon) | `.venv-macos-arm64` |

## File Structure

```
cli-anything/
├── .venv/              # Windows virtual environment (created by Windows build.bat)
├── .venv-linux/        # Linux virtual environment (created by Linux build.sh)
├── scripts/
│   ├── build.bat       # Windows build script (uses .venv)
│   └── build.sh        # Linux/macOS build script (uses .venv-linux)
├── src/
└── requirements.txt
```

## Usage

### Windows (CMD/PowerShell)

```cmd
cd cli-thing
scripts\build.bat
```

This creates/uses: `.venv/`

### Linux/macOS (Bash/Zsh)

```bash
cd cli-thing
chmod +x scripts/build.sh
./scripts/build.sh
```

This creates/uses: `.venv-linux`

### WSL (Windows Subsystem for Linux)

When working in WSL, the Linux shell is used, so follow the **Linux/macOS** instructions:

```bash
cd cli-thing
./scripts/build.sh
```

This will create `.venv-linux` in the WSL environment, which is separate from Windows `.venv`.

## Benefits

1. **No conflicts**: Windows and Linux can have separate environments
2. **No overwrites**: Each platform maintains its own dependencies
3. **Easy switching**: Use the appropriate script for your current shell
4. **Shared code**: Same source files, different runtime environments

## Manual Setup (Optional)

If you want to manually set up the virtual environment:

### Windows

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

### Linux/macOS

```bash
python3 -m venv .venv-linux
source .venv-linux/bin/activate
pip install -r requirements.txt
pip install pyinstaller
```

## Troubleshooting

### Issue: "No such file or directory: .venv/bin/activate"

**Cause**: You're on Linux/WSL but `.venv` was created by Windows.

**Solution**:
```bash
rm -rf .venv
./scripts/build.sh
# This will create .venv-linux instead
```

### Issue: Windows virtual environment in WSL

**Cause**: WSL mounts Windows filesystem at `/mnt/d/`, Windows paths don't work in WSL.

**Solution**: Always run Linux build scripts from within WSL, which creates `.venv-linux`.

### Issue: Different Python versions

Each virtual environment is isolated, so you can have different Python versions:

```bash
# Windows might use Python 3.11
.venv\Scripts\activate

# Linux might use Python 3.12
source .venv-linux/bin/activate
```

## Clean All Virtual Environments

To remove all platform-specific virtual environments:

```bash
# From Linux/macOS/WSL
rm -rf .venv-linux

# From Windows (CMD/PowerShell)
rmdir /s /q .venv
```

## IDE Setup

### VS Code

VS Code will automatically detect the virtual environment if you select the Python interpreter:

- Windows: Select `.venv/` folder → Python interpreter
- Linux/WSL: Select `.venv-linux/` folder → Python interpreter

### PyCharm

Configure separate run configurations:

1. **Windows Configuration**: Use `.venv/` as interpreter
2. **Linux Configuration**: Use `.venv-linux/` as interpreter

## Additional Notes

- **Disk Space**: Having multiple virtual environments uses more disk space (~200-500MB each)
- **Sync Issues**: Since environments are separate, package versions might differ
- **Git**: Add `.venv*` to `.gitignore` to avoid committing virtual environments
