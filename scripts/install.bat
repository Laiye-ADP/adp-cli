@echo off
REM ADP CLI 安装脚本（Windows）

echo ==========================================
echo ADP CLI Installation Script (Windows)
echo ==========================================
echo.

REM 检查 Python 版本
python --version
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

echo.

REM 安装依赖
echo Installing dependencies...
pip install -e .
if errorlevel 1 (
    echo Error: Installation failed
    exit /b 1
)

echo.

REM 验证安装
echo Verifying installation...
adp --version
if errorlevel 1 (
    echo Error: ADP CLI not found
    exit /b 1
)

echo.
echo ==========================================
echo Installation completed!
echo ==========================================
echo.
echo Try: adp --help
