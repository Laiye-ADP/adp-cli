# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for ADP CLI
# Generates a standalone executable for Windows, Linux, and macOS

import sys
from pathlib import Path

# Project configuration
project_name = "adp"
version = "1.10.6"
description = "AI Document Platform Command Line Tool"

# Determine the entry point
entry_point = Path("src/adp_cli/cli.py")

block_cipher = None

# Collect data files
datas = []

# Collect hidden imports (dependencies that PyInstaller might miss)
# Note: PyInstaller hooks will handle most dependencies automatically
hiddenimports = [
    "click",
    "click.core",
    "click.utils",
    "requests",
    "urllib3",  # requests now uses urllib3 directly (not requests.packages.urllib3)
    "cryptography",
    "cryptography.fernet",
    "pygments",
    "pygments.lexers",
    "pygments.formatters",
    "pygments.styles",
    "rich",
    "rich.console",
    "rich.text",
    "rich.table",
    "rich.progress",
    "rich.theme",
    "rich.panel",
    "rich.status",
    "rich.markup",
    "pydantic",  # pydantic v2 structure is different, hooks handle the rest
]

a = Analysis(
    [str(entry_point)],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['src/adp_cli/_pyinstaller_hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude large, unnecessary packages to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'pytest',
        'IPython',
        'jupyter',
        'notebook',
        'pip',
        'setuptools',
        'wheel',
        'distutils',
    ],
    noarchive=False,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=project_name,
    debug=False,
    bootloader_ignore_signals=False,
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=project_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
