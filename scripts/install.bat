@echo off
REM ADP CLI PyPI 安装脚本（Windows）- 支持国内镜像源

setlocal enabledelayedexpansion

set PACKAGE_NAME=agentic_doc_parse_and_extract
set MIN_PYTHON_VERSION=3.8

REM 国内镜像源（阿里云源，可修改）
set DEFAULT_PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple

echo ==========================================
echo ADP CLI Installation from PyPI
echo ==========================================
echo Package: %PACKAGE_NAME%
echo Minimum Python: %MIN_PYTHON_VERSION%
echo Mirror: %DEFAULT_PIP_INDEX_URL%
echo ==========================================
echo.

REM 1. 检查Python安装
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
echo.

REM 2. 验证Python版本
echo [2/3] Validating Python version...
python -c "import sys; exit(0 if sys.version_info ^>= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo Error: Python %MIN_PYTHON_VERSION% or higher is required
    exit /b 1
)
echo Python version meets requirements
echo.

REM 3. 安装包
echo [3/3] Installing %PACKAGE_NAME% from PyPI...

REM 升级pip（使用国内源）
echo Upgrading pip...
python -m pip install --upgrade pip -i %DEFAULT_PIP_INDEX_URL% --user --quiet

REM 安装包（使用国内源）
echo Installing package...
python -m pip install %PACKAGE_NAME% -i %DEFAULT_PIP_INDEX_URL% --user --quiet

if errorlevel 1 (
    echo Error: Package installation failed
    exit /b 1
)

echo Package installed successfully

REM 4. 验证安装
echo.
echo Verifying installation...

where adp >nul 2>&1
if errorlevel 1 (
    echo Package installed successfully
    echo.
    echo To use ADP CLI, add the following to your PATH:
    echo %%USERPROFILE%%\AppData\Roaming\Python\Python3x\Scripts
    echo.
    echo Or add %%USERPROFILE%%\.local\bin to PATH
) else (
    adp --version
    echo ADP CLI installed successfully
)

echo.
echo ==========================================
echo Installation completed!
echo ==========================================
echo.
echo Usage: adp --help
echo ==========================================

endlocal
