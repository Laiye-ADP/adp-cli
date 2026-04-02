# ADP CLI 安装脚本

此目录包含从 PyPI 安装 ADP CLI 的脚本。

## 脚本说明

### `install.sh` / `install.bat`
- **用途**: 从 PyPI 安装 ADP CLI 工具（生产环境）
- **平台**: Linux/macOS / Windows
- **特性**:
  - 自动检测 Python 版本（需要 3.8+）
  - 使用国内镜像源（默认阿里云，支持切换）
  - 安装到用户目录（无需 sudo）
  - **自动添加到 PATH**（无需手动配置）
  - 支持版本检测和升级

### `install_test.sh` / `install_test.bat`
- **用途**: 从 TestPyPI 安装测试版本
- **平台**: Linux/macOS / Windows
- **特性**:
  - 用于测试发布的包
  - 支持自定义 PyPI 索引 URL
  - 其他特性同 `install.sh/bat`

## 命令行参数

### install.sh / install.bat

```bash
# 默认安装/检查
install.sh                    # 已安装则跳过升级
install.bat

# 强制升级到最新版本
install.sh --upgrade
install.bat --upgrade

# 仅检查更新（不安装）
install.sh --check-update
install.bat --check-update

# 使用指定镜像源
install.sh --mirror tsinghua   # 清华源
install.sh --mirror douban      # 豆瓣源
install.bat --mirror tsinghua

# 查看帮助
install.sh --help
install.bat --help
```

### install_test.sh / install_test.bat

```bash
# 从 TestPyPI 安装
install_test.sh
install_test.bat

# 使用自定义源
install_test.sh --index-url https://pypi.org/simple/
```

## 快速安装

### Linux/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install.sh | bash
```

### Windows
```cmd
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install.bat' -OutFile install.bat'; .\install.bat"
```

## Agent 使用示例

```bash
#!/bin/bash

# 自动安装 ADP CLI
if ! command -v adp &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install.sh | bash
fi

# 使用 ADP CLI（脚本已自动配置 PATH）
adp --version
```

## 镜像源

### 生产环境（install.sh/bat）
| 名称 | 地址 |
|------|------|
| aliyun | `https://mirrors.aliyun.com/pypi/simple` (默认) |
| tsinghua | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| douban | `https://pypi.douban.com/simple` |
| ustc | `https://pypi.mirrors.ustc.edu.cn/simple` |

### 测试环境（install_test.sh/bat）
| 源 | 地址 |
|-----|------|
| TestPyPI | `https://test.pypi.org/simple/` (默认) |
| PyPI | `https://pypi.org/simple/` |

## 升级说明

- **默认行为**: 已安装则不自动升级，提示有新版本可用
- **--upgrade**: 强制升级到最新版本
- **--check-update**: 仅检查版本，不执行安装

## 其他脚本

- `build.sh` / `build.bat`: 构建独立可执行文件
- `publish.sh` / `publish.bat`: 发布到 PyPI

详细文档请参考 [../docs/PYPI-INSTALL-GUIDE.md](../docs/PYPI-INSTALL-GUIDE.md)
