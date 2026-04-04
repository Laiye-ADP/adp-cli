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
    print("[1/4] Checking Python environment...")
    version = sys.version_info
    print(f"  Python executable: {sys.executable}")
    print(f"  Python version: {version.major}.{version.minor}.{version.micro}")

    if version < MIN_PYTHON_VERSION:
        print(f"✗ Error: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher required")
        sys.exit(1)
    print(f"  ✓ Python version meets requirements (>= {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]})")
    print()

def check_pip():
    """检查pip"""
    print("[2/4] Checking pip...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        pip_version = result.stdout.strip().split()[1]
        print(f"  pip version: {pip_version}")
        print("  ✓ pip is available")
        print()
    except subprocess.CalledProcessError:
        print("✗ Error: pip not found")
        print(f"Please ensure pip is installed for Python {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)

def check_platform():
    """检查系统平台"""
    print("[3/4] Checking system platform...")
    print(f"  Platform: {sys.platform}")

    # 检查虚拟环境
    venv = getattr(sys, 'real_prefix', None) or getattr(sys, 'base_prefix', None)
    if venv:
        print(f"  Virtual environment: active ({venv})")
    else:
        print("  Virtual environment: none (system Python)")

    print("  ✓ System platform check completed")
    print()

def install_package():
    """安装包"""
    print(f"[4/4] Installing {PACKAGE_NAME} from PyPI...")

    # 安装包（使用国内源）
    # --user: 安装到当前用户的site-packages，避免需要管理员权限
    # --quiet: 减少输出信息
    # --no-warn-script-location: 不显示脚本安装路径的警告
    subprocess.run(
        [
            sys.executable, "-m", "pip", "install", PACKAGE_NAME,
            "-i", DEFAULT_PIP_INDEX_URL,
            "--extra-index-url", DEFAULT_PIP_INDEX_URL,
            "--user", "--quiet", "--no-warn-script-location"
        ],
        check=True
    )

    print("  ✓ Package installed successfully")
    print()

def verify_installation():
    """验证安装"""
    print("[5/5] Verifying installation...")

    # 检查adp命令是否可用
    try:
        result = subprocess.run(
            ["adp", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("  ✓ ADP CLI installed successfully")
            print(f"    Version: {result.stdout.strip()}")
            print()
            print("  You can now use: adp --help")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 如果adp不在PATH中，提供添加PATH的说明
    if sys.platform == "win32":
        print("  ✓ ADP CLI installed successfully")
        print()
        print("  To use ADP CLI, add the following to your PATH:")
        print("    %USERPROFILE%\\AppData\\Roaming\\Python\\Python3x\\Scripts")
        print()
        print("  Or add %USERPROFILE%\\.local\\bin to PATH")
    else:
        print("  ✓ ADP CLI installed successfully")
        print("    Location: ~/.local/bin/adp")
        print()
        print("  To use ADP CLI, add the following to your ~/.bashrc or ~/.zshrc:")
        print('    export PATH="$HOME/.local/bin:$PATH"')
        print()
        print("  Then run: source ~/.bashrc  (or source ~/.zshrc)")

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

    # 检查pip
    check_pip()

    # 检查系统平台
    check_platform()

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
