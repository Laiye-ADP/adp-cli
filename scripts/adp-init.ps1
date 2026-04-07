# ADP CLI Auto-Initialization Script
# Modified to dynamically detect Python environment with fallback

param(
    [string]$InstallScriptUrl = "https://raw.githubusercontent.com/Laiye-ADP/adp-cli/master/scripts/install_test.ps1"
)

# Set UTF-8 encoding for output
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Function to find Python in common installation directories
function Find-Python {
    $pythonDirs = @(
        "D:\Programs\Python\Python38",
        "D:\Programs\Python\Python39",
        "D:\Programs\Python\Python310",
        "D:\Programs\Python\Python311",
        "D:\Programs\Python\Python312",
        "C:\Python38",
        "C:\Python39",
        "C:\Python310",
        "C:\Python311",
        "C:\Python312",
        "$env:LOCALAPPDATA\Programs\Python\Python38",
        "$env:LOCALAPPDATA\Programs\Python\Python39",
        "$env:LOCALAPPDATA\Programs\Python\Python310",
        "$env:LOCALAPPDATA\Programs\Python\Python311",
        "$env:LOCALAPPDATA\Programs\Python\Python312",
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python38",
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python39",
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python310",
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python311",
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python312",
        "C:\Program Files\Python38",
        "C:\Program Files\Python39",
        "C:\Program Files\Python310",
        "C:\Program Files\Python311",
        "C:\Program Files\Python312"
    )

    foreach ($dir in $pythonDirs) {
        $pythonExe = Join-Path $dir "python.exe"
        if (Test-Path $pythonExe) {
            return Get-Command $pythonExe -ErrorAction SilentlyContinue
        }
    }

    return $null
}

# Step 1: Try to find Python from PATH
Write-Host "=== Detecting Python Environment ==="
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

# Step 2: If not found in PATH, try common installation directories
if (-not $pythonCmd) {
    Write-Host "Python not found in PATH, searching common installation directories..."
    $pythonCmd = Find-Python
}

# Step 3: Report result
if ($pythonCmd) {
    $pythonDir = Split-Path $pythonCmd.Source -Parent
    $AdpBinDir = $pythonDir
    Write-Host "Found Python: $($pythonCmd.Source)"
    Write-Host "Using Scripts directory: $AdpBinDir"
} else {
    Write-Host "Python not found in PATH or common directories" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher first" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/"
    exit 1
}

Write-Host ""

# Step 4: Check if ADP CLI already installed
if (Test-Path "$AdpBinDir\adp.exe") {
    Write-Host "ADP CLI already installed at $AdpBinDir"
} else {
    Write-Host "ADP CLI not found, starting installation..."

    # Download install script
    $tempScript = "$env:TEMP\install-adp.ps1"
    try {
        Invoke-WebRequest -Uri $InstallScriptUrl -OutFile $tempScript -ErrorAction Stop
        Write-Host "Install script downloaded successfully"
    } catch {
        Write-Host "Error: Failed to download install script" -ForegroundColor Red
        Write-Host "Error: $_"
        exit 1
    }

    # Execute install script
    Write-Host "Running install script..."
    & $tempScript

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Installation failed" -ForegroundColor Red
        exit 1
    }
}

# Step 5: Set PATH for current session
$env:PATH = "$AdpBinDir;$env:PATH"

# Verify PATH
if ($env:PATH -like "*$AdpBinDir*") {
    Write-Host "PATH setting for current session: SUCCESS"
} else {
    Write-Host "PATH setting for current session: FAILED" -ForegroundColor Yellow
}

# Step 6: Permanently add to user environment variable
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$AdpBinDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$AdpBinDir", "User")
    Write-Host "PATH permanently added to user environment variable: SUCCESS"
} else {
    Write-Host "PATH already exists in user environment variable"
}

# Step 7: Set UTF-8 encoding permanently in PowerShell profile
Write-Host ""
Write-Host "=== Setting UTF-8 encoding for PowerShell ==="
$profilePath = "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
$encodingSetting = "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8"

# Create profile file if not exists
if (-not (Test-Path $profilePath)) {
    New-Item -Path $profilePath -ItemType File -Force | Out-Null
    Write-Host "Created PowerShell profile: $profilePath"
}

# Add encoding setting if not exists
if ((Get-Content $profilePath -Raw -ErrorAction SilentlyContinue) -notmatch "OutputEncoding") {
    Add-Content -Path $profilePath -Value $encodingSetting
    Write-Host "UTF-8 encoding setting added to profile: SUCCESS"
} else {
    Write-Host "UTF-8 encoding already exists in profile"
}

Write-Host ""
Write-Host "=== Initialization Complete ==="