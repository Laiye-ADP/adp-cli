# ADP CLI 打包快速指南

## 本地构建

### Windows
```cmd
cd adp-cli
scripts\build.bat
# 输出: dist\adp.exe
```

### Linux/macOS
```bash
cd adp-cli
./scripts/build.sh
# 输出: dist/adp
```

### 使用构建辅助工具
```bash
# 构建当前平台
python scripts/build_all.py

# 构建并创建压缩包
python scripts/build_all.py --archive

# 在 Windows/macOS 上使用 Docker 构建 Linux 版本
python scripts/build_all.py linux --archive
```

---

## 自动化构建 (GitHub Actions)

### 触发构建

**方式 1: 推送标签**
```bash
git tag v1.10.0
git push origin v1.10.0
```

**方式 2: 创建 Release**
在 GitHub 上创建 Release，自动触发构建。

**方式 3: 手动触发**
在 GitHub Actions 页面手动运行 "Build ADP CLI" 工作流。

### 支持的平台

| 平台 | 架构 | 构建产物 |
|------|------|----------|
| Windows | x64 | `adp-cli-windows-x64.zip` |
| Linux | x64 | `adp-cli-linux-x64.tar.gz` |
| macOS | Intel | `adp-cli-macos-x64.tar.gz` |
| macOS | Apple Silicon | `adp-cli-macos-arm64.tar.gz` |

---

## 测试构建的可执行文件

```bash
# Windows
dist\adp.exe --version
dist\adp.exe --help

# Linux/macOS
chmod +x dist/adp
./dist/adp --version
./dist/adp --help
```

---

## 详细文档

- 📖 [完整打包指南](PACKAGING.md) - 详细的打包说明和故障排除
- 📦 [构建文档](BUILD.md) - 快速构建参考
