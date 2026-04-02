# ADP CLI 安装脚本

此目录包含从PyPI安装ADP CLI的脚本。

## 脚本说明

### `install.sh` / `install.bat`
- **用途**: 从PyPI安装ADP CLI工具
- **平台**: Linux/macOS / Windows
- **特性**:
  - 自动检测Python版本（需要3.8+）
  - 使用阿里云镜像源（国内加速）
  - 安装到用户目录（无需sudo）
  - 自动验证安装

### `install_adp_cli.py`
- **用途**: 跨平台Python安装脚本
- **平台**: Linux/macOS/Windows
- **特性**: 同上，使用Python脚本实现

## 快速安装

### Linux/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install.sh | bash
```

### Windows
```cmd
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install.bat' -OutFile install.bat'; .\install.bat"
```

### 使用Python脚本
```bash
python install_adp_cli.py
```

## Agent使用示例

```bash
#!/bin/bash

# 自动安装ADP CLI
if ! command -v adp &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
fi

# 使用ADP CLI
adp --version
```

## 镜像源

默认使用阿里云镜像源：
```
https://mirrors.aliyun.com/pypi/simple
```

可修改脚本中的 `DEFAULT_PIP_INDEX_URL` 变量切换到其他镜像源。

## 其他脚本

- `build.sh` / `build.bat`: 构建独立可执行文件
- `publish.sh` / `publish.bat`: 发布到PyPI
- `install.bat`: 本地开发环境安装（已废弃）

详细文档请参考 [../docs/PYPI-INSTALL-GUIDE.md](../docs/PYPI-INSTALL-GUIDE.md)
