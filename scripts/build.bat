@echo off
REM Build script for ADP CLI (Windows)
REM Creates standalone executable using PyInstaller

setlocal enabledelayedexpansion

echo ========================================
echo   ADP CLI Build Script (Windows)
echo ========================================
echo.

REM Detect Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH. Please install Python 3.8+ first.
    echo.
    pause
    exit /b 1
)

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Convert to absolute path
for /f "delims=" %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"

echo Detected platform: Windows
echo.

REM Check if virtual environment exists
set "VENV_DIR=%PROJECT_ROOT%\.venv"
if not exist "%VENV_DIR%" (
    echo [INFO] Virtual environment not found. Creating...
    python -m venv "%VENV_DIR%"
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Install/upgrade dependencies
echo [INFO] Installing/upgrading dependencies...
python -m pip install --upgrade pip
python -m pip install -r "%PROJECT_ROOT%\requirements.txt"
python -m pip install pyinstaller

REM Clean previous builds
echo [INFO] Cleaning previous builds...
if exist "%PROJECT_ROOT%\dist\adp.exe" (
    del /f /q "%PROJECT_ROOT%\dist\adp.exe" 2>nul
)

REM Run PyInstaller
echo [INFO] Building executable with PyInstaller...
cd /d "%PROJECT_ROOT%"
pyinstaller "%PROJECT_ROOT%\build\adp_cli.spec" --clean --noconfirm

REM Check if build succeeded
if exist "%PROJECT_ROOT%\dist\adp.exe" (
    echo.
    echo ========================================
    echo   Build successful!
    echo ========================================
    echo.
    echo Executable location:
    echo   %PROJECT_ROOT%\dist\adp.exe
    echo.
    echo You can now: %PROJECT_ROOT%\dist\adp.exe --help
    echo.

    REM Check for --install parameter
    if "%1"=="--install" (
        echo [INFO] Adding to PATH (user scope)...
        setx PATH "%PATH%;%PROJECT_ROOT%\dist%"
        echo [SUCCESS] Added to PATH. Please restart your terminal.
    )
) else (
    echo.
    echo ========================================
    echo   Build failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    pause
    exit /b 1
)

REM Deactivate virtual environment
call deactivate

pause
