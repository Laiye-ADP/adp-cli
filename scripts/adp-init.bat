@echo off
REM ADP CLI 一键初始化脚本
REM 使用方式: 下载后执行 adp-init.bat

setlocal enabledelayedexpansion

set "ADP_BIN_DIR=%USERPROFILE%\.local\bin"
set "INSTALL_SCRIPT_URL=https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install_test.bat"

echo ADP CLI 初始化...

REM 检查是否已安装
if exist "%ADP_BIN_DIR%\adp.exe" (
    echo   ADP CLI 已安装
) else (
    echo   ADP CLI 未安装，开始安装...
    powershell -Command "Invoke-WebRequest -Uri '%INSTALL_SCRIPT_URL%' -OutFile '%TEMP%\install-adp.bat'"
    call "%TEMP%\install-adp.bat"
    del "%TEMP%\install-adp.bat" >nul 2>&1
)

REM 设置 PATH
set "PATH=%ADP_BIN_DIR%;%PATH%"

REM 验证 PATH
if echo %PATH% | findstr /C:"%ADP_BIN_DIR%" >nul 2>&1 (
    echo   PATH 设置成功
) else (
    echo   PATH 设置失败
)
