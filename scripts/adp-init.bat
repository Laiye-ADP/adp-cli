@echo off
REM ADP CLI Auto-Initialization Script
REM Modified to dynamically detect Python environment with fallback

REM Set UTF-8 encoding
chcp 65001 >nul 2>&1

setlocal enabledelayedexpansion

set "INSTALL_SCRIPT_URL=https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install_test.bat"

REM Function to find Python in common installation directories
set "PYTHON_DIRS=D:\Programs\Python\Python38;D:\Programs\Python\Python39;D:\Programs\Python\Python310;D:\Programs\Python\Python311;D:\Programs\Python\Python312;C:\Python38;C:\Python39;C:\Python310;C:\Python311;C:\Python312;%LOCALAPPDATA%\Programs\Python\Python38;%LOCALAPPDATA%\Programs\Python\Python39;%LOCALAPPDATA%\Programs\Python\Python310;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python312;%USERPROFILE%\AppData\Local\Programs\Python\Python38;%USERPROFILE%\AppData\Local\Programs\Python\Python39;%USERPROFILE%\AppData\Local\Programs\Python\Python310;%USERPROFILE%\AppData\Local\Programs\Python\Python311;%USERPROFILE%\AppData\Local\Programs\Python\Python312;C:\Program Files\Python38;C:\Program Files\Python39;C:\Program Files\Python310;C:\Program Files\Python311;C:\Program Files\Python312"

echo === Detecting Python Environment ===

REM Step 1: Try to find Python from PATH
set "python_cmd="
where python >nul 2>&1
if ! errorlevel 1 (
    set "python_cmd=python"
)

REM Step 2: If not found in PATH, try common installation directories
if not defined python_cmd (
    echo Python not found in PATH, searching common installation directories...
    for %%d in (%PYTHON_DIRS%) do (
        if exist "%%d\python.exe" (
            set "python_cmd=%%d\python.exe"
            goto :found_python
        )
    )
)

:found_python
REM Step 3: Report result
if defined python_cmd (
    for %%i in ("!python_cmd!") do set "python_dir=%%~dpi"
    set "python_dir=!python_dir:~0,-1!"
    set "AdpBinDir=!python_dir!"
    echo Found Python: !python_cmd!
    echo Using Scripts directory: !AdpBinDir!
) else (
    echo Python not found in PATH or common directories
    echo Please install Python 3.8 or higher first
    echo Download from: https://www.python.org/downloads/
    exit /b 1
)

echo.

REM Step 4: Check if ADP CLI already installed
if exist "!AdpBinDir!\adp.exe" (
    echo ADP CLI already installed at !AdpBinDir!
) else (
    echo ADP CLI not found, starting installation...

    REM Download install script
    set "temp_script=%TEMP%\install-adp.bat"
    powershell -Command "Invoke-WebRequest -Uri '!INSTALL_SCRIPT_URL!' -OutFile '!temp_script!'"
    if errorlevel 1 (
        echo Error: Failed to download install script
        exit /b 1
    )

    REM Execute install script
    echo Running install script...
    call "!temp_script!"

    if errorlevel 1 (
        echo Error: Installation failed
        exit /b 1
    )
)

REM Step 5: Set PATH for current session
set "PATH=!AdpBinDir!;%PATH%"

REM Verify PATH
echo !PATH! | findstr /C:"!AdpBinDir!" >nul 2>&1
if ! errorlevel 1 (
    echo PATH setting for current session: SUCCESS
) else (
    echo PATH setting for current session: FAILED
)

REM Step 6: Permanently add to user environment variable
set "user_path="
for /f "skip=2 tokens=3*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do (
    set "user_path=%%a %%b"
)
if not "!user_path!"=="" (
    echo !user_path! | findstr /C:"!AdpBinDir!" >nul 2>&1
    if errorlevel 1 (
        set "NEW_USER_PATH=!user_path!;!AdpBinDir!"
        setx PATH "!NEW_USER_PATH!" >nul 2>&1
        echo PATH permanently added to user environment variable: SUCCESS
    ) else (
        echo PATH already exists in user environment variable
    )
)

echo.
echo === Initialization Complete ===
