@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo ADP CLI PyPI Publish Script
echo ==================================================
echo.

REM Clean old Python build artifacts
echo [1/3] Cleaning old Python builds...
if exist build rmdir /s /q build
if exist *.egg-info rmdir /s /q *.egg-info
if exist src\*.egg-info rmdir /s /q src\*.egg-info
if exist dist\*.whl del /f /q dist\*.whl
if exist dist\*.tar.gz del /f /q dist\*.tar.gz
echo   [OK] Cleaned build artifacts

REM Build new Python packages
echo.
echo [2/3] Building Python packages...
python setup.py sdist bdist_wheel
echo   [OK] Built source distribution and wheel

REM Upload to PyPI
echo.
echo [3/3] Uploading to PyPI...
echo Packages to upload:
dir /b dist\*.whl dist\*.tar.gz
echo.
pause

twine upload dist\*.whl dist\*.tar.gz

echo.
echo ==================================================
echo   [OK] Published successfully!
echo ==================================================
echo.
echo Users can update with: pip install agentic_doc_parse_and_extract --upgrade
pause
