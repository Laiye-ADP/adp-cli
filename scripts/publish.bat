@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo ADP CLI PyPI Publish Script
echo ==================================================
echo.

REM 清理旧的Python构建产物
echo [1/3] Cleaning old Python builds...
if exist build rmdir /s /q build
if exist *.egg-info rmdir /s /q *.egg-info
if exist src\*.egg-info rmdir /s /q src\*.egg-info
if exist dist\*.whl del /f /q dist\*.whl
if exist dist\*.tar.gz del /f /q dist\*.tar.gz
echo [*] Cleaned build artifacts

REM 构建新的Python包
echo.
echo [2/3] Building Python packages...
python setup.py sdist bdist_wheel
echo [*] Built source distribution and wheel

REM 上传到PyPI
echo.
echo [3/3] Uploading to PyPI...
echo Packages to upload:
dir /b dist\*.whl dist\*.tar.gz
echo.
pause

twine upload dist\*.whl dist\*.tar.gz

echo.
echo ==================================================
echo [*] Published successfully!
echo ==================================================
echo.
echo Users can update with: pip install agentic_doc_parse_and_extract --upgrade
pause
