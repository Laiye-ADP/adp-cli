@echo off
REM ADP CLI PyPI Installation Script (Windows) - support China mirror sources

setlocal enabledelayedexpansion

set PACKAGE_NAME=agentic_doc_parse_and_extract
set MIN_PYTHON_VERSION=3.8
set SELECTED_MIRROR=aliyun

REM Parse arguments
:parse_args
if "%~1"=="" goto args_done
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

REM China mirror sources
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
echo Package:         %PACKAGE_NAME%
echo Minimum Python:  %MIN_PYTHON_VERSION%
echo Mirror:          %DEFAULT_PIP_INDEX_URL%
echo ==========================================
echo.

REM 1. Check Python installation
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

REM Get Python executable path
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set PYTHON_EXEC=%%i
echo   Python executable: %PYTHON_EXEC%
echo   [OK] Python version meets requirements ^(%MIN_PYTHON_VERSION% or higher^)

REM 2. Check pip
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
echo   [OK] pip is available

REM 3. Check system platform
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
echo   [OK] System platform check completed

REM 4. Install package
echo.
echo [4/4] Installing %PACKAGE_NAME% from PyPI...

REM --user: Install to current user's site-packages to avoid admin privileges
REM --quiet: Reduce output
REM --no-warn-script-location: Don't show script location warnings
python -m pip install %PACKAGE_NAME% ^
    -i %DEFAULT_PIP_INDEX_URL% ^
    --extra-index-url %DEFAULT_PIP_INDEX_URL% ^
    --user --quiet --no-warn-script-location

if errorlevel 1 (
    echo Error: Package installation failed
    exit /b 1
)

echo   [OK] Package installed successfully

REM 5. Verify installation
echo.
echo Verifying installation...

if exist "%USERPROFILE%\.local\bin\adp.exe" (
    "%USERPROFILE%\.local\bin\adp.exe" --version
    echo   [OK] Installation completed
) else (
    echo   [OK] Installation completed
)

echo.
echo ==========================================
echo Installation completed!
echo ==========================================
echo.
echo Next step: Setup PATH
echo   powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/adp-init.ps1' -OutFile '$env:TEMP\adp-init.ps1'; & '$env:TEMP\adp-init.ps1'"
echo.
echo Usage: adp --help
echo ==========================================
