@echo off
REM ADP CLI TestPyPI 安装脚本（Windows）- 用于测试版本安装

setlocal enabledelayedexpansion

set PACKAGE_NAME=agentic_doc_parse_and_extract
set MIN_PYTHON_VERSION=3.8

REM REM TestPyPI 官方地址
set DEFAULT_PIP_INDEX_URL=https://test.pypi.org/simple/

REM 解析参数
:parse_args
if "%~1"=="" goto args_done
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
exit /b 1

:args_done

echo ==========================================
echo ADP CLI Installation from TestPyPI
echo ==========================================
echo Package: %PACKAGE_NAME%
echo Minimum Python: %MIN_PYTHON_VERSION%
echo Index URL: %DEFAULT_PIP_INDEX_URL%
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
echo.
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

REM 3. 安装包
echo.
echo [3/3] Installing %PACKAGE_NAME% from TestPyPI...

python -m pip install --index-url %DEFAULT_PIP_INDEX_URL% %PACKAGE_NAME% --user --quiet --no-warn-script-location

if errorlevel 1 (
    echo Error: Package installation failed
    exit /b 1
)

echo Package installed successfully

REM 4. 验证安装并自动添加到PATH
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

        REM 验证（使用完整路径）
        "%ADP_BIN%\adp.exe" --version
        echo ADP CLI installed successfully
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

endlocal
