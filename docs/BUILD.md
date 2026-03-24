# Building ADP CLI Standalone Executables

This document explains how to build ADP CLI standalone executables for different platforms.

## Overview

ADP CLI can be distributed in two ways:

1. **Python Package** (`pip install`) - Requires Python 3.8+ on target machine
2. **Standalone Executable** - No Python required, single binary file

This guide covers **Method 2: Building Standalone Executables**.

## Supported Platforms

- **Windows**: `.exe` executable
- **Linux**: Binary executable
- **macOS**: Binary executable (Intel & Apple Silicon)

## Prerequisites

- **Python 3.8 or higher** (only needed for building, not for running the executable)
- **Git** (optional, for cloning the repository)

## Quick Build

### Windows

```cmd
cd cli-anything
scripts\build.bat
```

The executable will be created at: `dist\adp.exe`

### Linux / macOS

```bash
cd cli-anything
chmod +x scripts/build.sh
./scripts/build.sh
```

The executable will be created at: `dist/adp`

## Detailed Build Process

### 1. Clone or Navigate to Project

```bash
# If cloning:
git clone <repository-url>
cd adp-aiem/cli-anything

# Or navigate:
cd /path/to/cli-anything
```

### 2. (Optional) Create Virtual Environment

The build scripts automatically create a virtual environment if not present:

```bash
# Manual creation (optional)
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate.bat  # Windows
```

### 3. Install Build Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 4. Build Executable

```bash
# Using the provided scripts (recommended)
scripts/build.sh          # Linux/macOS
scripts\build.bat         # Windows

# Or directly with PyInstaller
pyinstaller build/adp_cli.spec
```

### 5. Test the Executable

```bash
# Windows
dist\adp.exe --help

# Linux/macOS
./dist/adp --help
```

## Build Configuration

The PyInstaller configuration is defined in [`build/adp_cli.spec`](../build/adp_cli.spec):

- **Output**: Single-file executable (`adp` or `adp.exe`)
- **Console**: Enabled (for CLI output)
- **UPX**: Enabled (for smaller size)
- **Excludes**: Unnecessary packages (tkinter, matplotlib, etc.) to reduce size

## Advanced Options

### Install to System PATH

**Linux/macOS**:
```bash
./scripts/build.sh --install
```

This creates a symlink at `/usr/local/bin/adp` (requires sudo).

**Windows**:
```cmd
scripts\build.bat --install
```

This adds the `dist` folder to your user PATH.

### Build for Specific Platform

You can build executables for different platforms by:

1. **Using GitHub Actions/CircleCI**: Set up CI/CD to build on each platform
2. **Cross-compilation**: Using Docker containers (for Linux on Windows/macOS)
3. **Multiple machines**: Build separately on each platform

Example Docker build for Linux on macOS:

```bash
docker run --rm -v $(pwd):/app -w /app python:3.11 \
  sh -c "pip install pyinstaller && pyinstaller build/adp_cli.spec"
```

### Custom Icon

To add a custom icon:

1. Create an `.ico` file (Windows) or `.icns` file (macOS)
2. Place it in `build/` directory
3. Update `build/adp_cli.spec` to reference the icon

## Troubleshooting

### Build Fails with "ModuleNotFoundError"

Solution: Add the missing module to `hiddenimports` in `build/adp_cli.spec`:

```python
hiddenimports=[
    # ... existing imports
    "your_missing_module",
],
```

### Executable Too Large

Common causes and solutions:

1. **Unnecessary dependencies**: Add to `excludes` in spec file
2. **Debug symbols**: Ensure `debug=False` in EXE section
3. **UPX disabled**: Ensure `upx=True` in EXE section

### Windows Defender Flags Executable

This can happen for unsigned executables. Solutions:

1. **Exclude the build directory** from Windows Defender
2. **Sign the executable** (requires code signing certificate)
3. **Distribute via trusted installer**

### macOS "Unverified Developer"

After building on macOS, the executable may need to be allowed:

```bash
xattr -d com.apple.quarantine dist/adp
```

Or run:
```bash
sudo spctl --add --label "ADP CLI" dist/adp
```

## Distribution

### Single Executable

Distribute the single file:
- Windows: `dist/adp.exe`
- Linux/macOS: `dist/adp`

### Archive (Recommended)

Create a compressed archive:

```bash
# Linux/macOS
tar -czf adp-cli-1.0.0-linux-x86_64.tar.gz dist/adp
zip -r adp-cli-1.0.0-linux-x86_64.zip dist/adp

# Windows (using PowerShell)
Compress-Archive -Path dist\adp.exe -DestinationPath adp-cli-1.0.0-win-x64.zip
```

### GitHub Releases

When releasing via GitHub:

1. Create a **Release** with version tag
2. Upload platform-specific artifacts:
   - `adp-cli-1.0.0-win-x64.zip`
   - `adp-cli-1.0.0-linux-x86_64.tar.gz`
   - `adp-cli-1.0.0-darwin-x86_64.tar.gz` (Intel)
   - `adp-cli-1.0.0-darwin-arm64.tar.gz` (Apple Silicon)

## Automated Builds (CI/CD)

Example GitHub Actions workflow:

```yaml
name: Build ADP CLI

on:
  release:
    types: [published]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pyinstaller
      - run: pip install -r cli-anything/requirements.txt
      - run: cd cli-anything && pyinstaller build/adp_cli.spec
      - uses: actions/upload-artifact@v3
        with:
          name: adp-${{ matrix.os }}
          path: cli-anything/dist/*
```

## File Sizes (Approximate)

After optimization, expect these sizes:

| Platform | Extension | Size (approx) |
|----------|-----------|---------------|
| Windows  | .exe      | 15-25 MB      |
| Linux    | (none)    | 12-20 MB      |
| macOS    | (none)    | 13-22 MB      |

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [Cross-platform Python Packaging](https://packaging.python.org/)
- [Building Executables with PyInstaller](https://realpython.com/python-executable/)

## Support

For issues related to building:
1. Check this documentation first
2. Review PyInstaller documentation
3. Open an issue in the project repository
