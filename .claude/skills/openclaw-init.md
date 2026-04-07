---
name: openclaw-init
description: Openclaw initialization - download and execute command
type: reference
---

# Openclaw Init Command

Openclaw 需要从 GitHub 下载 adp-init.bat 再执行，完整流程：

## 第一步：下载 adp-init.bat

```batch
set "ADP_INIT_URL=https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/adp-init.bat"
powershell -Command "Invoke-WebRequest -Uri '%ADP_INIT_URL%' -OutFile 'adp-init.bat'"
```

## 第二步：执行 adp-init.bat

```batch
call adp-init.bat
```

## 完整一键命令（下载后立即执行）

```batch
@echo off
setlocal enabledelayedexpansion

set "ADP_INIT_URL=https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/adp-init.bat"
set "ADP_BIN_DIR=%USERPROFILE%\.local\bin"

echo Openclaw 初始化...

REM 下载 adp-init.bat
powershell -Command "Invoke-WebRequest -Uri '%ADP_INIT_URL%' -OutFile 'adp-init.bat'"

REM 执行 adp-init.bat
call adp-init.bat

REM 设置 PATH
set "PATH=%ADP_BIN_DIR%;%PATH%"

REM 验证安装
if exist "%ADP_BIN_DIR%\adp.exe" (
    echo   安装成功
) else (
    echo   安装失败
)
```

## 核心下载命令

- 下载 adp-init.bat：`powershell -Command "Invoke-WebRequest -Uri 'ADP_INIT_URL' -OutFile 'adp-init.bat'"`
