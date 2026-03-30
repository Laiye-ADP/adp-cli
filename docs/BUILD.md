# Building ADP CLI Standalone Executables

> 📚 **详细指南**: 请查看 [PACKAGING.md](PACKAGING.md) 获取完整的跨平台打包指南和故障排除信息。

## Quick Start

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

## 快速构建

### Windows 平台

```cmd
cd cli-anything
scripts\build.bat
```

The executable will be created at: `dist\adp.exe`

### Linux / macOS 平台

```bash
cd cli-anything
chmod +x scripts/build.sh
./scripts/build.sh
```

The executable will be created at: `dist/adp`

## 详细构建流程

### 1. 进入项目目录

```bash
cd adp-cli
```

### 2. (可选) 创建虚拟环境

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
pyinstaller adp_cli.spec
```

### 5. Test the Executable

```bash
# Windows
dist\adp.exe --help

# Linux/macOS
./dist/adp --help
```

## 构建配置

PyInstaller 配置文件位于项目根目录的 [`adp_cli.spec`](../adp_cli.spec)。

- **Output**: Single-file executable (`adp` or `adp.exe`)
- **Console**: Enabled (for CLI output)
- **UPX**: Enabled (for smaller size)
- **Excludes**: Unnecessary packages (tkinter, matplotlib, etc.) to reduce size

## 高级选项

### 安装到系统 PATH

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

### 为特定平台构建

要为不同平台构建可执行文件：

1. **Using GitHub Actions/CircleCI**: Set up CI/CD to build on each platform
2. **Cross-compilation**: Using Docker containers (for Linux on Windows/macOS)
3. **Multiple machines**: Build separately on each platform

Example Docker build for Linux on macOS:

```bash
docker run --rm -v $(pwd):/app -w /app python:3.11 \
  sh -c "pip install pyinstaller && pyinstaller adp_cli.spec"
```

### 自定义图标

To add a custom icon:

1. Create an `.ico` file (Windows) or `.icns` file (macOS)
2. Place it in `build/` directory
3. Update `adp_cli.spec` to reference the icon

## 故障排除

> 📋 详细的故障排除指南请查看 [PACKAGING.md](PACKAGING.md)。

### Build Fails with "ModuleNotFoundError"

Solution: Add the missing module to `hiddenimports` in `adp_cli.spec`:

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

## 分发

### 单个可执行文件

直接分发单个文件：
- Windows: `dist/adp.exe`
- Linux/macOS: `dist/adp`

### 压缩包 (推荐)

创建压缩包：

```bash
# Linux/macOS
tar -czf adp-cli-1.0.0-linux-x86_64.tar.gz dist/adp
zip -r adp-cli-1.0.0-linux-x86_64.zip dist/adp

# Windows (using PowerShell)
Compress-Archive -Path dist\adp.exe -DestinationPath adp-cli-1.0.0-win-x64.zip
```

#### GitHub Releases

When releasing via GitHub:

1. Create a **Release** with version tag
2. Upload platform-specific artifacts:
   - `adp-cli-1.0.0-win-x64.zip`
   - `adp-cli-1.0.0-linux-x86_64.tar.gz`
   - `adp-cli-1.0.0-darwin-x86_64.tar.gz` (Intel)
   - `adp-cli-1.0.0-darwin-arm64.tar.gz` (Apple Silicon)

## 自动化构建 (CI/CD)

项目包含预配置的 GitHub Actions 工作流：[.github/workflows/build.yml](../.github/workflows/build.yml)

触发构建：

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
      - run: cd cli-anything && pyinstaller adp_cli.spec
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

## 相关资源

- 📖 [详细打包指南](PACKAGING.md) - 完整的跨平台打包说明
- 📦 [PyInstaller 文档](https://pyinstaller.org/)
- 🛠️ [Python 打包指南](https://packaging.python.org/)
- 🚀 [GitHub Actions 工作流](../.github/workflows/build.yml)

## 获取帮助

如遇到构建问题：
1. 查看 [PACKAGING.md](PACKAGING.md) 中的故障排除部分
2. 检查 PyInstaller 文档
3. 在项目仓库提交 Issue
