@echo off
REM ADP CLI One-click Initialization Script
REM Usage: Download and run adp-init.bat

setlocal enabledelayedexpansion

set "ADP_BIN_DIR=%USERPROFILE%\.local\bin"
set "INSTALL_SCRIPT_URL=https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install_test.bat"

echo ADP CLI initializing...

REM Check if already installed
if exist "%ADP_BIN_DIR%\adp.exe" (
    echo   ADP CLI is already installed
) else (
    echo   ADP CLI not installed, starting installation...
    powershell -Command "Invoke-WebRequest -Uri '%INSTALL_SCRIPT_URL%' -OutFile '%TEMP%\install-adp.bat'"
    call "%TEMP%\install-adp.bat"
)

REM Set PATH (current session)
set "PATH=%ADP_BIN_DIR%;%PATH%"

REM Verify PATH
if echo %PATH% | findstr /C:"%ADP_BIN_DIR%" >nul 2>&1 (
    echo   PATH configured successfully
) else (
    echo   PATH configuration failed
)

REM Permanently add PATH (for current user)
set "USER_PATH="
for /f "skip=2 tokens=3*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do (
    set "USER_PATH=%%a %%b"
)
if not "%USER_PATH%"=="" (
    set "NEW_USER_PATH=%USER_PATH%;%ADP_BIN_DIR%"
    setx PATH "%NEW_USER_PATH%" >nul 2>&1
    echo   PATH has been permanently added to user environment
)
