@echo off
REM ADP CLI TestPyPI 安装脚本（Windows）- 用于测试版本安装

setlocal enabledelayedexpansion

set PACKAGE_NAME=agentic_doc_parse_and_extract
set MIN_PYTHON_VERSION=3.8
set DO_UPGRADE=false
set CHECK_UPDATE_ONLY=false

REM TestPyPI 官方地址
set DEFAULT_PIP_INDEX_URL=https://test.pypi.org/simple/

REM 显示帮助信息
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help

REM 解析参数
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--upgrade" (
    set DO_UPGRADE=true
    shift
    goto parse_args
)
if /i "%~1"=="--check-update" (
    set CHECK_UPDATE_ONLY=true
    shift
    goto parse_args
)
if /i "%~1"=="--index-url" (
    if "%~2"=="" (
        echo Error: --index-url requires a value
        exit /b 1
    )
    set DEFAULT_PIP_INDEX_URL=%~2
    shift
    shift
    goto parse_args
)
echo Error: Unknown option '%~1'
echo Use --help for usage information
exit /b 1

:args_done

echo ==========================================
echo ADP CLI Installation from TestPyPI
echo ==========================================
echo Package: %PACKAGE_NAME%
echo Minimum Python: %MIN_PYTHON_VERSION%
echo Index URL: %DEFAULT_PIP_INDEX_URL%
if /i "%DO_UPGRADE%"=="true" (
    echo Mode: Upgrade to latest
) else if /i "%CHECK_UPDATE_ONLY%"=="true" (
    echo Mode: Check updates only
) else (
    echo Mode: Install ^(no upgrade^)
)
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
echo Python.
echo %PYTHON_VERSION%

REM 2. 验证Python版本
echo.
echo [2/3] Validating Python version...
python -c "import sys; exit(0 if sys.version_info ^>= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo Error: Python %MIN_PYTHON_VERSION% or higher is required
    exit /b 1
)
echo Python version meets requirements

REM 3. 检查已安装版本
echo.
echo [3/5] Checking installed version...

for /f "tokens=2" %%i in ('python -m pip show %PACKAGE_NAME% 2^>nul ^| findstr /C:"Version:"') do set INSTALLED_VERSION=%%i

if "%INSTALLED_VERSION%"=="" (
    echo Not installed yet
) else (
    echo Current version: %INSTALLED_VERSION%
)

REM 4. 检查最新版本（从TestPyPI）
echo.
echo [4/5] Checking latest version from TestPyPI...

REM 获取最新版本
python -m pip index versions --index-url %DEFAULT_PIP_INDEX_URL% %PACKAGE_NAME% > temp_versions.txt 2>nul
for /f "delims=" %%i in ('type temp_versions.txt ^| findstr /N "^" ^| findstr "^1:"') do set LATEST_LINE=%%i
for /f "tokens=2*" %%i in ("%LATEST_LINE%") do set LATEST_VERSION=%%i
del temp_versions.txt

if "%LATEST_VERSION%"=="" (
    echo Warning: Could not retrieve latest version from TestPyPI
    echo   Make sure the package is published to TestPyPI
set LATEST_VERSION=unknown
) else (
    echo Latest version: %LATEST_VERSION%
)

REM 如果是仅检查模式
if /i "%CHECK_UPDATE_ONLY%"=="true" goto check_update_only

REM 5. 安装/升级包
echo.
echo [5/5] Installing %PACKAGE_NAME% from TestPyPI...

if not "%INSTALLED_VERSION%"=="" (
    REM 已安装
    if /i "%DO_UPGRADE%"=="true" (
        if "%INSTALLED_VERSION%"=="%LATEST_VERSION%" (
            echo Already on latest version ^(%INSTALLED_VERSION%^)
            echo   No upgrade needed
        ) else if "%LATEST_VERSION%"=="unknown" (
            echo Warning: Could not determine latest version
            echo   Proceeding with upgrade attempt...
            python -m pip install --upgrade --index-url %DEFAULT_PIP_INDEX_URL% %PACKAGE_NAME% --user --quiet
            if errorlevel 1 (
                echo Error: Package upgrade failed
                exit /b 1
            )
            echo Package upgraded
        ) else (
            echo   Current: %INSTALLED_VERSION%
            echo   Upgrading to: %LATEST_VERSION%
            python -m pip install --upgrade --index-url %DEFAULT_PIP_INDEX_URL% %PACKAGE_NAME% --user --quiet
            if errorlevel 1 (
                echo Error: Package upgrade failed
                exit /b 1
            )
            echo Package upgraded to %LATEST_VERSION%
        )
    ) else (
        if "%INSTALLED_VERSION%"=="%LATEST_VERSION%" (
            echo Already up to date ^(%INSTALLED_VERSION%^)
        ) else if not "%LATEST_VERSION%"=="unknown" (
            echo Already installed ^(%INSTALLED_VERSION%^)
            echo   Note: New version available: %LATEST_VERSION%
            echo   To upgrade: install_test.bat --upgrade
        ) else (
            echo Already installed ^(%INSTALLED_VERSION%^)
        )
    )
) else (
    REM 未安装
    echo   Installing: %LATEST_VERSION%
    python -m pip install --index-url %DEFAULT_PIP_INDEX_URL% %PACKAGE_NAME% --user --quiet
    if errorlevel 1 (
        echo Error: Package installation failed
        exit /b 1
    )
    echo Package installed successfully
)

goto verify_installation

:check_update_only
echo.
echo ==========================================
echo Update Check Results ^(TestPyPI^)
echo ==========================================
if "%INSTALLED_VERSION%"=="" (
    echo Status: Not installed
    echo Latest version: %LATEST_VERSION%
    echo.
    echo To install: install_test.bat
) else if "%INSTALLED_VERSION%"=="%LATEST_VERSION%" (
    echo Status: Up to date
    echo Current version: %INSTALLED_VERSION%
) else if "%LATEST_VERSION%"=="unknown" (
    echo Status: Could not determine latest version
    echo Current version: %INSTALLED_VERSION%
) else (
    echo Status: Update available
    echo Current version: %INSTALLED_VERSION%
    echo Latest version: %LATEST_VERSION%
    echo.
    echo To upgrade: install_test.bat --upgrade
)
echo ==========================================
exit /b 0

:verify_installation
REM 6. 验证安装
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

goto :eof

:show_help
echo ADP CLI TestPyPI Installation Script
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo This script installs from TestPyPI ^(test.pypi.org^) for testing purposes.
echo.
echo Options:
echo   --upgrade         Upgrade to the latest version if already installed
echo   --check-update    Check for available updates without installing
echo   --index-url ^<url^> Use custom PyPI index URL ^(default: TestPyPI^)
echo   --help            Show this help message
echo.
echo Examples:
echo   %~nx0                              Install from TestPyPI
echo   %~nx0 --upgrade                    Upgrade from TestPyPI
echo   %~nx0 --check-update               Check for updates on TestPyPI
echo   %~nx0 --index-url https://pypi.org/simple/
exit /b 0

endlocal
