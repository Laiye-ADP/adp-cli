# ADP CLI 跨平台打包指南

本文档提供关于如何在 Windows、Linux 和 macOS 平台上打包 ADP CLI 的详细说明。

---

## 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [本地构建](#本地构建)
4. [自动化构建 (GitHub Actions)](#自动化构建-github-actions)
5. [故障排除](#故障排除)
6. [发布流程](#发布流程)

---

## 概述

ADP CLI 可以通过两种方式分发：

### 方式 1: Python 包
需要目标机器安装 Python 3.8+
```bash
pip install agentic_doc_parse_and_extract
```

### 方式 2: 独立可执行文件 (推荐)
无需 Python，单个二进制文件

| 平台 | 输出格式 | 大小 (约) |
|------|---------|-----------|
| Windows | `adp.exe` | 15-25 MB |
| Linux | `adp` | 12-20 MB |
| macOS | `adp` | 13-22 MB |

---

## 快速开始

### 前置要求

- Python 3.8 或更高版本 (仅构建时需要)
- pip 包管理器
- (可选) Docker - 用于跨平台构建

### 本地构建当前平台

**Windows:**
```cmd
cd adp-cli
scripts\build.bat
```

**Linux/macOS:**
```bash
cd adp-cli
chmod +x scripts/build.sh
./scripts/build.sh
```

构建完成后，可执行文件位于 `dist/` 目录中。

---

## 本地构建

### 使用打包脚本 (推荐)

项目提供了三个构建脚本：

| 脚本 | 用途 |
|------|------|
| [build.bat](scripts/build.bat) | Windows 构建 |
| [build.sh](scripts/build.sh) | Linux/macOS 构建 |
| [build_all.py](scripts/build_all.py) | 跨平台辅助工具 |

### build_all.py 功能

`build_all.py` 是一个 Python 工具，用于简化本地构建：

```bash
# 构建当前平台
python scripts/build_all.py

# 构建并创建压缩包
python scripts/build_all.py --archive

# 使用 Docker 构建 Linux 版本 (从 Windows/macOS)
python scripts/build_all.py linux --archive
```

### 手动使用 PyInstaller

如果需要更多自定义选项，可以直接使用 PyInstaller：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 构建可执行文件
pyinstaller adp_cli.spec

# 清理构建并重新构建
pyinstaller adp_cli.spec --clean --noconfirm

# 仅收集分析 (不构建)
pyinstaller adp_cli.spec --log-level DEBUG
```

### PyInstaller 配置

配置文件：[adp_cli.spec](adp_cli.spec)

关键配置：
- **single file**: 生成单个可执行文件
- **console enabled**: 显示 CLI 输出
- **UPX compression**: 减小文件大小
- **excludes**: 排除不必要的包
- **hiddenimports**: 确保所有依赖被包含

### 添加新的依赖

如果在运行构建的可执行文件时遇到 `ImportError`，需要在 `adp_cli.spec` 中添加：

```python
hiddenimports=[
    # ... 现有导入
    "your_new_package",
    "your_new_package.submodule",
],
```

---

## 自动化构建 (GitHub Actions)

### GitHub Actions 工作流

项目包含预配置的 GitHub Actions 工作流：[.github/workflows/build.yml](.github/workflows/build.yml)

### 触发构建

**通过 Git 标签：**
```bash
git tag v1.10.0
git push origin v1.10.0
```

**通过 GitHub Release：**
1. 在 GitHub 上创建新 Release
2. 发布时自动触发构建
3. 构建产物自动附加到 Release

**手动触发：**
1. 访问 GitHub Actions 页面
2. 选择 "Build ADP CLI" 工作流
3. 点击 "Run workflow"

### 支持的平台

GitHub Actions 自动构建以下平台：

| 平台 | 架构 | 构建产物 |
|------|------|----------|
| Windows | x64 | `adp-cli-windows-x64.zip` |
| Linux | x64 | `adp-cli-linux-x64.tar.gz` |
| macOS | Intel x64 | `adp-cli-macos-x64.tar.gz` |
| macOS | Apple Silicon | `adp-cli-macos-arm64.tar.gz` |

### 工作流配置

工作流在以下情况触发：
- 推送以 `v*` 开头的标签 (如 `v1.10.0`)
- 创建 GitHub Release
- 手动触发 (workflow_dispatch)

---

## 故障排除

### 问题: ModuleNotFoundError

**症状：**
```
ImportError: No module named 'some_module'
```

**解决方案：**

1. 在 [adp_cli.spec](adp_cli.spec) 的 `hiddenimports` 中添加缺失的模块
2. 为复杂依赖创建自定义 hook

示例 hook：
```python
# src/adp_cli/_pyinstaller_hooks/hook-package.py
.pyfrom PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('package_name')
hiddenimports = collect_submodules('package_name')
```

### 问题: 可执行文件过大

**常见原因和解决方案：**

1. **包含不必要的包**
   - 在 `excludes` 中添加包名
   - 示例: `excludes=['numpy', 'matplotlib', ...]`

2. **调试符号未去除**
   - 确保 `debug=False`

3. **UPX 压缩禁用**
   - 确保 `upx=True`

4. **使用单文件模式**
   - 使用 `onefile` (默认) 而非 `onedir`

### 问题: Windows Defender 标记

**症状：**
Windows Defender 将构建的 .exe 标记为潜在威胁。

**解决方案：**

1. **临时方案：** 添加到排除列表
2. **永久方案：** 使用代码签名证书签名
3. **分发方案：** 通过可信安装程序分发

### 问题: macOS "无法验证开发者"

**症状：**
```
"adp" 无法打开，因为无法验证开发者。
```

**解决方案：**

```bash
# 移除隔离属性
xattr -d com.apple.quarantine dist/adp

# 或添加到可信任列表 (需要管理员权限)
sudo spctl --add --label "ADP CLI" dist/adp
```

### 问题: 构建超时

**症状：**
PyInstaller 构建过程中超时或挂起。

**解决方案：**

1. 增加 PyInstaller 超时时间
2. 检查网络连接 (用于下载依赖)
3. 使用 `--log-level DEBUG` 查看详细日志

### 问题: Linux 权限错误

**症状：**
```
Permission denied: './dist/adp'
```

**解决方案：**

```bash
# 添加执行权限
chmod +x dist/adp
```

---

## 发布流程

### 版本发布清单

在发布新版本之前，确保：

- [ ] 更新版本号
  - [setup.py](setup.py)
  - [cli.py](src/adp_cli/cli.py) 中的版本选项
  - [adp_cli.spec](adp_cli.spec)

- [ ] 更新 CHANGELOG.md

- [ ] 测试所有平台
  - 运行完整测试套件
  - 在 Windows、Linux、macOS 上测试构建的可执行文件

- [ ] 创建 Git 标签
  ```bash
  git tag -a v1.10.0 -m "Release version 1.10.0"
  git push origin v1.10.0
  ```

- [ ] 创建 GitHub Release
  - 访问 GitHub Releases 页面
  - 点击 "Draft a new release"
  - 选择标签 (如 v1.10.0)
  - 填写发布说明
  - 点击 "Publish release"

- [ ] GitHub Actions 自动构建并附加文件

### 发布后验证

1. 从 GitHub Release 下载各平台的可执行文件
2. 解压并测试基本功能：
   ```bash
   ./adp --version
   ./adp --help
   ./adp config set --api-key test_key
   ```

3. 验证文档更新：
   - [用户手册](docs/ADP-CLI-USER-MANUAL.md)
   - [本指南](docs/PACKAGING.md)

---

## 高级主题

### 自定义图标

**Windows (.ico):**
1. 使用工具将 PNG 转换为 .ico
2. 在 `adp_cli.spec` 中添加：
   ```python
   exe = EXE(
       # ... 其他参数
       icon='build/icon.ico',
   )
   ```

**macOS (.icns):**
1. 使用 iconutil 创建 .icns
2. 在 `adp_cli.spec` 中添加：
   ```python
   exe = EXE(
       # ... 其他参数
       icon='build/icon.icns',
   )
   ```

### 代码签名

**Windows:**
```bash
signtool sign /f cert.pfx /p password /t http://timestamp.digicert.com dist/adp.exe
```

**macOS:**
```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/adp
```

### 减小文件大小技巧

1. 使用 `strip=True` 移除调试符号
2. 使用 UPX 压缩
3. 排除不必要的包
4. 使用更小的 Python 版本 (如 Python 3.8)

### 跨平台 Docker 构建

```bash
# 构建 Linux 可执行文件
docker run --rm -v $(pwd):/app -w /app python:3.11-slim \
  sh -c "pip install pyinstaller && pip install -r requirements.txt && pyinstaller adp_cli.spec"

# 使用多阶段构建进一步减小大小
# (需要自定义 Dockerfile)
```

---

## 资源链接

- [PyInstaller - 官方文档](https://pyinstaller.org/)
- [Python 打包指南](https://packaging.python.org/)
- [GitHub Actions - 文档](https://docs.github.com/en/actions)
- [ADP CLI - 用户手册](docs/ADP-CLI-USER-MANUAL.md)
- [ADP CLI - 开发指南](docs/CLI-DEVELOPER-GUIDE.md)

---

## 问题反馈

如果遇到问题，请按以下步骤：

1. 查看本文档的故障排除部分
2. 检查 PyInstaller 官方文档
3. 在项目仓库中搜索 Issues
4. 创建新的 Issue，包含：
   - 操作系统和版本
   - Python 版本
   - 完整的错误信息
   - 复现步骤
