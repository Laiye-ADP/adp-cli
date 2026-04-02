@echo off
REM ADP CLI PyPI 安装脚本（Windows）- 支持国内镜像源

setlocal enabledelayedexpansion

set PACKAGE_NAME=agentic_doc_parse_and_extract
set MIN_PYTHON_VERSION=3.8
set DO_UPGRADE=false
set CHECK_UPDATE_ONLY=false
set SELECTED_MIRROR=aliyun

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
if /i "%~1"=="--mirror" (
    if "%~2"=="" (
        echo Error: --mirror requires a value
        exit /b 1
    )
    set SELECTED_MIRROR=%~2
    shift
    shift
    goto parse_args
)
echo Error: Unknown option '%~1'
echo Use --help for usage information
exit /b 1

:args_done

REM 国内镜像源
if /i "%SELECTED_MIRROR%"=="aliyun" set DEFAULT_PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
if /i "%SELECTED_MIRROR%"=="tsinghua" set DEFAULT_PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
if /i "%SELECTED_MIRROR%"=="douban" set DEFAULT_PIP_INDEX_URL=https://pypi.douban.com/simple
if /i "%SELECTED_MIRROR%"=="ustc" set DEFAULT_PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple

if "%DEFAULT_PIP_INDEX_URL%"=="" (
    echo Error: Invalid mirror name '%SELECTED_MIRROR%'
    echo Available mirrors: aliyun, tsinghua, douban, ustc
    exit /b 1
)

echo ==========================================
echo ADP CLI Installation from PyPI
echo ==========================================
echo Package: %PACKAGE_NAME%
echo Minimum Python: %MIN_PYTHON_VERSION%
echo Mirror: %DEFAULT_PIP_INDEX_URL%
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

REM 3. 检查已安装版本
echo [3/5] Checking installed version...

for /f "tokens=2" %%i in ('python -m pip show %PACKAGE_NAME% 2^>nul ^| findstr /C:"Version:"') do set INSTALLED_VERSION=%%i

if "%INSTALLED_VERSION%"=="" (
    echo Not installed yet
) else (
    echo Current version: %INSTALLED_VERSION%
)

REM 4. 检查最新版本（从PyPI）
echo.
echo [4/5] Checking latest version from PyPI...

REM 升级pip（使用国内源）
echo   - Upgrading pip...
python -m pip install --upgrade pip -i %DEFAULT_PIP_INDEX_URL% --user --quiet

REM 获取最新版本
python -m pip index versions %PACKAGE_NAME% > temp_versions.txt 2>nul
for /f "delims=" %%i in ('type temp_versions.txt ^| findstr /N "^" ^| findstr "^1:"') do set LATEST_LINE=%%i
for /f "tokens=2*" %%i in ("%LATEST_LINE%") do set LATEST_VERSION=%%i
del temp_versions.txt

if "%LATEST_VERSION%"=="" (
    echo Warning: Could not retrieve latest version from PyPI
    set LATEST_VERSION=unknown
) else (
    echo Latest version: %LATEST_VERSION%
)

REM 如果是仅检查模式
if /i "%CHECK_UPDATE_ONLY%"=="true" goto check_update_only

REM 5. 安装/升级包
echo.
echo [5/5] Installing %PACKAGE_NAME% from PyPI...

if not "%INSTALLED_VERSION%"=="" (
    REM 已安装
    if /i "%DO_UPGRADE%"=="true" (
        if "%INSTALLED_VERSION%"=="%LATEST_VERSION%" (
            echo Already on latest version ^(%INSTALLED_VERSION%^)
            echo   No upgrade needed
        ) else if "%LATEST_VERSION%"=="unknown" (
            echo Warning: Could not determine latest version
            echo   Proceeding with upgrade attempt...
            python -m pip install --upgrade %PACKAGE_NAME% -i %DEFAULT_PIP_INDEX_URL% --user --quiet
            if errorlevel 1 (
                echo Error: Package upgrade failed
                exit /b 1
            )
            echo Package upgraded
        ) else (
            echo   Current: %INSTALLED_VERSION%
            echo   Upgrading to: %LATEST_VERSION%
            python -m pip install --upgrade %PACKAGE_NAME% -i %DEFAULT_PIP_INDEX_URL% --user --quiet
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
            echo   To upgrade: install.bat --upgrade
        ) else (
            echo Already installed ^(%INSTALLED_VERSION%^)
        )
    )
) else (
    REM 未安装
    echo   Installing: %LATEST_VERSION%
    python -m pip install %PACKAGE_NAME% -i %DEFAULT_PIP_INDEX_URL% --user --quiet
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
echo Update Check Results
echo ==========================================
if "%INSTALLED_VERSION%"=="" (
    echo Status: Not installed
    echo Latest version: %LATEST_VERSION%
    echo.
    echo To install: install.bat
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
    echo To upgrade: install.bat --upgrade
)
echo ==========================================
exit /b 0

:verify_installation
REM 6. 验证安装并自动添加到PATH
echo.
echo Verifying installation...

REM 检测 adp 命令的实际安装位置
for /f "delims=" %%i in ('where adp 2^>nul') do set ADP_PATH=%%i

if "%ADP_PATH%"=="" (
    REM 未在 PATH 中找到，尝试常见位置
    if exist "%USERPROFILE%\.local\bin\adp.exe" (
        set "ADP_BIN=%USERPROFILE%\.local\bin"
    ) else if exist "%USERPROFILE%\AppData\Roaming\Python\Python*\Scripts\adp.exe" (
        for /d %%i in ("%USERPROFILE%\AppData\Roaming\Python\Python*") do set "ADP_BIN=%%i\Scripts"
    )

    REM 找到了安装目录，添加到 PATH
    if defined ADP_BIN (
        echo   Adding %ADP_BIN% to PATH...

        REM 检查是否已在 PATH 中
        echo %PATH% | findstr /C:"%ADP_BIN%" >nul
        if errorlevel 1 (
            REM 添加到用户环境变量（永久生效）
            for /f "delims=" %%i in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set REG_PATH_VALUE=%%i

            if "%REG_PATH_VALUE%"=="" (
                REM PATH 不存在，创建新的
                setx PATH "%ADP_BIN%;%PATH%" >nul 2>&1
            ) else (
                REM PATH 已存在，追加
                setx PATH "%ADP_BIN%;%PATH%" >nul 2>&1
            )

            echo   PATH updated (may require reopening terminal)
        ) else (
            echo   PATH already configured
        )

        REM 在当前会话中更新 PATH
        set "PATH=%ADP_BIN%;%PATH%"
        echo   PATH updated in current session

        REM 验证
        where adp >nul 2>&1
        if not errorlevel 1 (
            adp --version
            echo ADP CLI installed successfully
        ) else (
            echo Package installed successfully
        )
    ) else (
        echo Package installed successfully
        echo   Location: ADP binaries not found in expected locations
    )
) else (
    REM 已在 PATH 中
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
echo ADP CLI Installation Script
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --upgrade         Upgrade to the latest version if already installed
echo   --check-update    Check for available updates without installing
echo   --mirror ^<name^>   Use specific PyPI mirror:
echo                      - aliyun ^(default^)
echo                      - tsinghua
echo                      - douban
echo                      - ustc
echo   --help            Show this help message
echo.
echo Examples:
echo   %~nx0                  Install or upgrade only if needed
echo   %~nx0 --upgrade        Force upgrade to latest version
echo   %~nx0 --check-update   Check if a newer version is available
echo   %~nx0 --mirror tsinghua Install using Tsinghua mirror
exit /b 0

endlocal
