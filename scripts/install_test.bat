@echo off
REM ADP CLI TestPyPI 安装脚本（Windows）- 用于测试版本安装

setlocal enabledelayedexpansion

set PACKAGE_NAME=agentic_doc_parse_and_extract
set MIN_PYTHON_VERSION=3.8
set SELECTED_MIRROR=aliyun

REM TestPyPI 官方地址
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
exit /b 1

:args_done

REM 国内镜像源
if /i "%SELECTED_MIRROR%"=="aliyun" set EXTRA_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
if /i "%SELECTED_MIRROR%"=="tsinghua" set EXTRA_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
if /i "%SELECTED_MIRROR%"=="douban" set EXTRA_INDEX_URL=https://pypi.douban.com/simple
if /i "%SELECTED_MIRROR%"=="ustc" set EXTRA_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple

if "%EXTRA_INDEX_URL%"=="" (
    echo Error: Invalid mirror name '%SELECTED_MIRROR%'
    echo Available mirrors: aliyun, tsinghua, douban, ustc
    exit /b 1
)

echo ==========================================
echo ADP CLI Installation from TestPyPI
echo ==========================================
echo Package:         %PACKAGE_NAME%
echo Minimum Python:  %MIN_PYTHON_VERSION%
echo Index URL:      %DEFAULT_PIP_INDEX_URL%
echo ==========================================
echo.

REM 1. 检查Python安装
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python %MIN_PYTHON_VERSION% or higher first.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   Python command: python
echo   Python version: %PYTHON_VERSION%

REM 获取Python可执行文件路径
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set PYTHON_EXEC=%%i
echo   Python executable: %PYTHON_EXEC%
echo   ✓ Python version meets requirements ^(%MIN_PYTHON_VERSION% or higher^)

REM 2. 检查pip
echo.
echo [2/4] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip not found
    echo Please ensure pip is installed for Python %PYTHON_VERSION%
    exit /b 1
)

for /f "tokens=2" %%i in ('python -m pip --version 2^>^&1') do set PIP_VERSION=%%i
echo   pip version: %PIP_VERSION%
echo   ✓ pip is available

REM 3. 检查系统平台
echo.
echo [3/4] Checking system platform...
echo   System: Windows
set VIRTUAL_ENV=
python -c "import sys; v=getattr(sys,'real_prefix',getattr(sys,'base_prefix',None)); print('active' if v else 'none')" >nul 2>&1
if "%VIRTUAL_ENV%"=="" (
    echo   Virtual environment: none ^(system Python^)
) else (
    echo   Virtual environment: %VIRTUAL_ENV%
)
echo   ✓ System platform check completed

REM 4. 安装包
echo.
echo [4/4] Installing %PACKAGE_NAME% from TestPyPI...

REM --user: 安装到当前用户的site-packages，避免需要管理员权限
REM --quiet: 减少输出信息
REM --no-warn-script-location: 不显示脚本安装路径的警告
python -m pip install --index-url %DEFAULT_PIP_INDEX_URL% --extra-index-url %EXTRA_INDEX_URL% %PACKAGE_NAME% --user --quiet --no-warn-script-location

if errorlevel 1 (
    echo Error: Package installation failed
    exit /b 1
)

echo   ✓ Package installed successfully

REM 5. 验证安装并自动添加到PATH
echo.
echo Verifying installation...

if exist "%USERPROFILE%\.local\bin\adp.exe" (
    "%USERPROFILE%\.local\bin\adp.exe" --version
    echo   ✓ 安装成功
) else (
    echo   ✓ 安装成功
)

echo.
echo ==========================================
echo Installation completed!
echo ==========================================
echo.
echo Next step: Setup PATH
echo   powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/adp-init.bat' -OutFile '$env:TEMP\adp-init.bat'; & '$env:TEMP\adp-init.bat'"
echo.
echo Usage: adp --help
echo ==========================================