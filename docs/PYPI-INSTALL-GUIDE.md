# ADP CLI PyPI Installation Guide

本指南说明如何从PyPI直接安装ADP CLI工具，无需虚拟环境。

**安装脚本默认使用清华源（国内镜像）以加速下载。**

---

## 可用镜像源

| 源名称 | URL |
|--------|-----|
| 阘里云源（默认） | https://mirrors.aliyun.com/pypi/simple |
| 清华源 | https://pypi.tuna.tsinghua.edu.cn/simple |
| 豆瓣源 | https://pypi.douban.com/simple |
| 中科大源 | https://pypi.mirrors.ustc.edu.cn/simple |

---

---

## 快速安装（推荐）

### Linux/macOS

```bash
# 一键安装（从GitHub获取脚本）
curl -fsSL https://raw.githubusercontent.com/adp/adp-aiem/main/scripts/install.sh | bash

# 或使用Python脚本
python3 -c "import urllib.request, subprocess, sys; exec(urllib.request.urlopen('https://raw.githubusercontent.com/adp/adp-aiem/main/scripts/install_adp_cli.py').read().decode())"
```

### Windows

```cmd
REM 一键安装
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/adp/adp-aiem/main/scripts/install.bat' -OutFile install.bat'; .\install.bat"

REM 或使用Python脚本
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/adp/adp-aiem/main/scripts/install_adp_cli.py').read().decode())"
```

---

## 手动安装步骤

### 1. 检查Python版本

```bash
# 检查Python版本（需要3.8+）
python --version  # Windows
python3 --version  # Linux/macOS
```

### 2. 安装ADP CLI

```bash
# 使用pip安装到用户目录（推荐，无需sudo）
pip install --user agentic_doc_parse_and_extract

# 或使用完整命令
python -m pip install --user agentic_doc_parse_and_extract
```

### 3. 配置PATH（如需要）

如果安装后`adp`命令不可用，需要添加到PATH：

**Linux/macOS** - 添加到 `~/.bashrc` 或 `~/.zshrc`：
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Windows** - 添加到系统环境变量：
```
%USERPROFILE%\AppData\Roaming\Python\Python3x\Scripts
```

### 4. 验证安装

```bash
adp --version
adp --help
```

---

## Agent使用指南

对于Agent自动化场景，推荐以下方式：

### 方式1：一键安装并配置（推荐）

```bash
#!/bin/bash

# 安装ADP CLI（如未安装）
if ! command -v adp &> /dev/null; then
    echo "Installing ADP CLI from PyPI..."
    python3 -m pip install --user --quiet agentic_doc_parse_and_extract

    # 添加到PATH（临时）
    export PATH="$HOME/.local/bin:$PATH"
fi

# 使用ADP CLI
adp --version
adp config set --api-key YOUR_API_KEY
adp parse --input document.pdf
```

### 方式2：使用Python直接调用

```python
import subprocess
import sys
import os

# 确保PATH包含用户bin目录
user_bin = os.path.expanduser("~/.local/bin")
if user_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{user_bin}:{os.environ['PATH']}"

# 执行ADP CLI命令
result = subprocess.run(
    ["adp", "--version"],
    capture_output=True,
    text=True
)
print(result.stdout)
```

### 方式3：完整自动安装脚本

```bash
#!/bin/bash

# 自动安装函数
install_adp_cli() {
    if ! command -v adp &> /dev/null; then
        echo "ADP CLI not found, installing..."

        # 检查Python
        if command -v python3 &> /dev/null; then
            PYTHON="python3"
        elif command -v python &> /dev/null; then
            PYTHON="python"
        else
            echo "Error: Python not found"
            exit 1
        fi

        # 安装
        $PYTHON -m pip install --user --quiet agentic_doc_parse_and_extract

        # 配置PATH
        export PATH="$HOME/.local/bin:$PATH"

        # 验证
        if command -v adp &> /dev/null; then
            echo "✓ ADP CLI installed successfully"
            adp --version
        else
            echo "✗ Installation failed"
            exit 1
        fi
    fi
}

# 使用
install_adp_cli

# 现在可以使用adp命令
adp --help
```

---

## 使用镜像加速（中国用户）

如果从PyPI下载较慢，可以使用国内镜像：

```bash
# 清华镜像
pip install --user -i https://pypi.tuna.tsinghua.edu.cn/simple agentic_doc_parse_and_extract

# 阿里云镜像
pip install --user -i https://mirrors.aliyun.com/pypi/simple agentic_doc_parse_and_extract

# 或配置为默认镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 更新

```bash
# 更新到最新版本
pip install --user --upgrade agentic_doc_parse_and_extract

# 检查当前版本
adp --version
```

---

## 卸载

```bash
# Linux/macOS
pip uninstall agentic_doc_parse_and_extract

# Windows
pip uninstall agentic_doc_parse_and_extract
```

---

## 故障排除

### 问题1：adp命令不可用

```bash
# 检查安装位置
pip show agentic_doc_parse_and_extract

# 检查用户bin目录
ls -la ~/.local/bin/adp  # Linux/macOS
dir %USERPROFILE%\AppData\Roaming\Python\Python3x\Scripts\adp.exe  # Windows

# 手动添加到PATH
export PATH="$HOME/.local/bin:$PATH"
"```

### 问题2：权限错误

```bash
# 使用--user选项安装到用户目录
pip install --user agentic_doc_parse_and_extract

# 如果需要系统级安装（需要sudo）
sudo pip install agentic_doc_parse_and_extract
```

### 问题3：pip版本过低

```bash
# 升级pip
python -m pip install --upgrade pip

# 然后重新安装
pip install --user agentic_doc_parse_and_extract
```

### 问题4：网络问题

```bash
# 使用国内镜像
pip install --user -i https://pypi.tuna.tsinghua.edu.cn/simple agentic_doc_parse_and_extract

# 或设置代理
pip install --user --proxy http://proxy.example.com:8080 agentic_doc_parse_and_extract
```

---

## 系统要求

- **Python**: 3.8 或更高版本
- **pip**: 20.0 或更高版本
- **操作系统**: Linux, macOS, Windows

---

## 相关资源

- **项目主页**: https://github.com/adp/adp-aiem
- **PyPI页面**: https://pypi.org/project/agentic_doc_parse_and_extract/
- **用户手册**: [ADP-CLI-USER-MANUAL.md](ADP-CLI-USER-MANUAL.md)
- **构建指南**: [BUILD.md](BUILD.md)

---

## 常用命令示例

```bash
# 查看帮助
adp --help

# 配置API密钥
adp config set --api-key YOUR_API_KEY

# 解析文档
adp parse --input document.pdf

# 提取信息
adp extract --input document.pdf --app-id your_app_id

# 查看应用列表
adp app-id list

# 查询任务状态
adp query task --task-id TASK_ID
```
