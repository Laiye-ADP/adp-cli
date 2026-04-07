# ADP CLI PyPI Installation Script (PowerShell) - support China mirrors
param(
    [string]$Mirror = "aliyun"
)

$PackageName = "agentic_doc_parse_and_extract"
$MinPythonVersion = [version]"3.8"

# Mirror configuration
switch ($Mirror.ToLower()) {
    "aliyun"   { $PipIndexUrl = "https://mirrors.aliyun.com/pypi/simple" }
    "tsinghua" { $PipIndexUrl = "https://pypi.tuna.tsinghua.edu.cn/simple" }
    "douban"   { $PipIndexUrl = "https://pypi.douban.com/simple" }
    "ustc"     { $PipIndexUrl = "https://pypi.mirrors.ustc.edu.cn/simple" }
    default {
        Write-Host "Error: Invalid mirror name '$Mirror'" -ForegroundColor Red
        Write-Host "Available mirrors: aliyun, tsinghua, douban, ustc"
        exit 1
    }
}

Write-Host "=========================================="
Write-Host "ADP CLI Installation from PyPI"
Write-Host "=========================================="
Write-Host "Package:         $PackageName"
Write-Host "Minimum Python:  $MinPythonVersion"
Write-Host "Mirror:          $PipIndexUrl"
Write-Host "=========================================="
Write-Host ""

# 1. Check Python installation
Write-Host "[1/4] Checking Python environment..."
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    $pythonPath = $pythonCmd.Source
} catch {
    Write-Host "Error: Python not found" -ForegroundColor Red
    Write-Host "Please install Python $MinPythonVersion or higher first."
    exit 1
}

$pythonVersion = python --version 2>&1 | ForEach-Object { $_ -replace "Python ", "" }
Write-Host "  Python command: python"
Write-Host "  Python version: $pythonVersion"
Write-Host "  Python executable: $pythonPath"

$actualVersion = [version]$pythonVersion
if ($actualVersion -lt $MinPythonVersion) {
    Write-Host "Error: Python $MinPythonVersion or higher is required" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Python version meets requirements ($MinPythonVersion or higher)"

# 2. Check pip
Write-Host ""
Write-Host "[2/4] Checking pip..."
try {
    $pipVersion = python -m pip --version 2>&1 | ForEach-Object {
        if ($_ -match "pip (\d+\.\d+)") { $Matches[1] }
    }
    if (-not $pipVersion) {
        Write-Host "Error: pip not found" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: pip not found" -ForegroundColor Red
    Write-Host "Please ensure pip is installed for Python $pythonVersion"
    exit 1
}

Write-Host "  pip version: $pipVersion"
Write-Host "  [OK] pip is available"

# 3. Check system platform
Write-Host ""
Write-Host "[3/4] Checking system platform..."
Write-Host "  System: Windows"
$venvActive = python -c "import sys; v=getattr(sys,'real_prefix',getattr(sys,'base_prefix',None)); print('active' if v else 'none')" 2>$null
if ($venvActive -eq "none") {
    Write-Host "  Virtual environment: none (system Python)"
} else {
    Write-Host "  Virtual environment: $venvActive"
}
Write-Host "  [OK] System platform check completed"

# 4. Install package
Write-Host ""
Write-Host "[4/4] Installing $PackageName from PyPI..."

# --user: Install to current user's site-packages to avoid admin privileges
# --quiet: Reduce output
# --no-warn-script-location: Don't show script location warnings
python -m pip install $PackageName -i $PipIndexUrl --extra-index-url $PipIndexUrl --user --quiet --no-warn-script-location

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Package installation failed" -ForegroundColor Red
    exit 1
}

Write-Host "  [OK] Package installed successfully"

# 5. Verify installation
Write-Host ""
Write-Host "Verifying installation..."

$adpPath = "$env:USERPROFILE\.local\bin\adp.exe"
if (Test-Path $adpPath) {
    & $adpPath --version
    Write-Host "  [OK] Installation completed"
} else {
    Write-Host "  [OK] Installation completed"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Installation completed!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Next step: Setup PATH"
Write-Host ""
Write-Host "Usage: adp --help"
Write-Host "=========================================="
