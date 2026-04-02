#!/usr/bin/env python3
"""
ADP CLI 安装脚本（跨平台）- 支持国内镜像源
从PyPI直接安装ADP CLI工具

用法:
    python install_adp_cli.py

可选镜像源:
    - 清华源（默认）: https://pypi.tuna.tsinghua.edu.cn/simple
    - 阿里云源: https://mirrors.aliyun.com/pypi/simple
    - 豆瓣源: https://pypi.douban.com/simple
    - 中科大源: https://pypi.mirrors.ustc.edu.cn/simple
"""

import os
import sys
import subprocess
from pathlib import Path

PACKAGE_NAME = "agentic_doc_parse_and_extract"
MIN_PYTHON_VERSION = (3, 8)

# 国内镜像源（默认使用阿里云源）
PYPI_MIRRORS = [
    "https://mirrors.aliyun.com/pypi/simple",     # 阿里云源
    "https://pypi.tuna.tsinghua.edu.cn/simple",  # 清华源
    "https://pypi.douban.com/simple",            # 豆瓣源
    "https://pypi.mirrors.ustc.edu.cn/simple",   # 中科大源
]

DEFAULT_PIP_INDEX_URL = PYPI_MIRRORS[0]

def print_header():
    print("=" * 50)
    print("ADP CLI Installation from PyPI")
    print("=" * 50)
    print(f"Package: {PACKAGE_NAME}")
    print(f"Minimum Python: {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}")
    print(f"Mirror: {DEFAULT_PIP_INDEX_URL}")
    print("=" * 50)
    print()

def check_python_version():
    """检查Python版本"""
    print(f"[1/3] Checking Python installation...")
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")

    if version < MIN_PYTHON_VERSION:
        print(f"✗ Error: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher required")
        sys.exit(1)

    print("✓ Python version meets requirements")
    print()

def install_package():
    """安装包"""
    print(f"[2/3] Installing {PACKAGE_NAME} from PyPI...")

    # 升级pip（使用国内源）
    print("Upgrading pip...")
    subprocess.run(
        [
            sys.executable, "-m", "pip", "install", "--upgrade", "pip",
            "-i", DEFAULT_PIP_INDEX_URL, "--user", "--quiet"
        ],
        check=True
    )

    # 安装包（使用国内源）
    print("Installing package...")
    subprocess.run(
        [
            sys.executable, "-m", "pip", "install", PACKAGE_NAME,
            "-i", DEFAULT_PIP_INDEX_URL, "--user", "--quiet"
        ],
        check=True
    )

    print("✓ Package installed successfully")
    print()

def verify_installation():
    """验证安装"""
    print("[3/3] Verifying installation...")

    # 检查adp命令是否可用
    try:
        result = subprocess.run(
            ["adp", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ ADP CLI installed successfully")
            print(f"  Version: {result.stdout.strip()}")
            print()
            print("You can now use: adp --help")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 如果adp不在PATH中，提供添加PATH的说明
    if sys.platform == "win32":
        print("✓ ADP CLI installed successfully")
        print()
        print("To use ADP CLI, add the following to your PATH:")
        print("  %USERPROFILE%\\AppData\\Roaming\\Python\\Python3x\\Scripts")
        print()
        print("Or add %USERPROFILE%\\.local\\bin to PATH")
    else:
        print("✓ ADP CLI installed successfully")
        print(f"  Location: ~/.local/bin/adp")
        print()
        print("To use ADP CLI, add the following to your ~/.bashrc or ~/.zshrc:")
        print("  export PATH=\"$HOME/.local/bin:$PATH\"")
        print()
        print("Then run: source ~/.bashrc  (or source ~/.zshrc)")

    return False

def print_completion():
    """打印完成信息"""
    print()
    print("=" * 50)
    print("Installation completed!")
    print("=" * 50)
    print()
    print("Usage: adp --help")
    print("=" * 50)

def main():
    print_header()

    # 检查Python版本
    check_python_version()

    # 安装包
    install_package()

    # 验证安装
    verify_installation()

    # 打印完成信息
    print_completion()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n\n✗ Error: Command failed with exit code {e.returncode}")
        if e.cmd:
            print(f"  Command: {' '.join(str(c) for c in e.cmd)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        sys.exit(1)
