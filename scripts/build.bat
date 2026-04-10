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

REM Create platform output directory
set "OUTPUT_DIR=%PROJECT_ROOT%\dist\win32-x64"
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

echo Detected platform: Windows
echo Output directory: %OUTPUT_DIR%
echo.

REM Check if virtual environment exists (prefer Python 3.8 venv)
set "VENV_DIR=%PROJECT_ROOT%\.venv38"
if not exist "%VENV_DIR%" (
    set "VENV_DIR=%PROJECT_ROOT%\.venv"
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Install/upgrade dependencies
echo [INFO] Installing/upgrading dependencies...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b 1
)
python -m pip install -r "%PROJECT_ROOT%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    pause
    exit /b 1
)
python -m pip install pyinstaller
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)

REM Clean previous builds
echo [INFO] Cleaning previous builds...
if exist "%OUTPUT_DIR%\adp.exe" (
    del /f /q "%OUTPUT_DIR%\adp.exe" 2>nul
)

REM Run PyInstaller with output to platform directory
echo [INFO] Building executable with PyInstaller...
cd /d "%PROJECT_ROOT%"
pyinstaller "%PROJECT_ROOT%\adp_cli.spec" --clean --noconfirm --distpath "%OUTPUT_DIR%"
if errorlevel 1 (
    echo.
    echo ========================================
    echo   Build failed!
    echo ========================================
    echo PyInstaller encountered errors. Check the output above.
    pause
    exit /b 1
)

REM Check if build succeeded
if exist "%OUTPUT_DIR%\adp.exe" (
    echo.
    echo ========================================
    echo   Build successful!
    echo ========================================
    echo.
    echo Executable location:
    echo   %OUTPUT_DIR%\adp.exe
    echo.
    echo You can now: %OUTPUT_DIR%\adp.exe --help
    echo.

    REM Check for --install parameter
    if "%1"=="--install" (
        echo [INFO] Adding to PATH (user scope)...
        setx PATH "%PATH%;%OUTPUT_DIR%"
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
