# ADP CLI 一键初始化脚本
# 使用方式: 下载后执行 adp-init.ps1

param(
    [string]$InstallScriptUrl = "https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install_test.ps1"
)

$AdpBinDir = "$env:USERPROFILE\.local\bin"

Write-Host "ADP CLI 初始化..."

# 检查是否已安装
if (Test-Path "$AdpBinDir\adp.exe") {
    Write-Host "  ADP CLI 已安装"
} else {
    Write-Host "  ADP CLI 未安装，开始安装..."

    # 下载安装脚本
    $tempScript = "$env:TEMP\install-adp.ps1"
    try {
        Invoke-WebRequest -Uri $InstallScriptUrl -OutFile $tempScript -ErrorAction Stop
    } catch {
        Write-Host "  Error: 下载安装脚本失败" -ForegroundColor Red
        Write-Host "  $_"
        exit 1
    }

    # 执行安装脚本
    & $tempScript

    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Error: 安装失败" -ForegroundColor Red
        exit 1
    }
}

# 设置 PATH（当前会话）
$env:PATH = "$AdpBinDir;$env:PATH"

# 验证 PATH
if ($env:PATH -like "*$AdpBinDir*") {
    Write-Host "  PATH 设置成功"
} else {
    Write-Host "  PATH 设置失败" -ForegroundColor Yellow
}

# 永久添加 PATH（对当前用户）
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$AdpBinDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$AdpBinDir", "User")
    Write-Host "  PATH 已永久添加到用户环境变量"
}
