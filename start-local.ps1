# ZenTea License Local Dev Startup Script
# Only uses Docker for PostgreSQL

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ZenTea License Local Dev Environment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check and start PostgreSQL container
Write-Host "[1/4] Checking PostgreSQL container..." -ForegroundColor Yellow

$dbRunning = docker ps --filter "name=zentea-license-db" --format "{{.Names}}" 2>$null

if ($dbRunning -eq "zentea-license-db") {
    Write-Host "      PostgreSQL is running" -ForegroundColor Green
}
else {
    $dbExists = docker ps -a --filter "name=zentea-license-db" --format "{{.Names}}" 2>$null
    if ($dbExists -eq "zentea-license-db") {
        Write-Host "      Starting existing PostgreSQL container..." -ForegroundColor Yellow
        docker start zentea-license-db
    }
    else {
        Write-Host "      Creating PostgreSQL container..." -ForegroundColor Yellow
        docker run -d --name zentea-license-db -e POSTGRES_USER=license_admin -e POSTGRES_PASSWORD=license_dev_pwd -e POSTGRES_DB=zentea_license -p 5433:5432 postgres:15-alpine
    }
    Write-Host "      PostgreSQL started" -ForegroundColor Green
}

Write-Host "      Waiting for database..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 2. Start backend
Write-Host ""
Write-Host "[2/4] Starting backend service..." -ForegroundColor Yellow

$backendPath = Join-Path $ScriptDir "backend"

$backendScript = @'
$env:DATABASE_URL = "postgresql+asyncpg://license_admin:license_dev_pwd@localhost:5433/zentea_license"
$env:SECRET_KEY = "dev-secret-key-for-testing"
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet
Write-Host "Backend starting..." -ForegroundColor Green
python run.py
'@

$backendScriptPath = Join-Path $backendPath "run-dev.ps1"
$backendScript | Out-File -FilePath $backendScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-File", $backendScriptPath, "-WorkingDirectory", $backendPath
Write-Host "      Backend started (new window)" -ForegroundColor Green

Start-Sleep -Seconds 8

# 3. Start admin frontend
Write-Host ""
Write-Host "[3/4] Starting admin frontend..." -ForegroundColor Yellow

$adminPath = Join-Path $ScriptDir "frontend-admin"

$adminScript = @'
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}
Write-Host "Admin frontend starting..." -ForegroundColor Green
npm run dev
'@

$adminScriptPath = Join-Path $adminPath "run-dev.ps1"
$adminScript | Out-File -FilePath $adminScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-File", $adminScriptPath, "-WorkingDirectory", $adminPath
Write-Host "      Admin frontend started (new window)" -ForegroundColor Green

# 4. Start portal frontend
Write-Host ""
Write-Host "[4/4] Starting portal frontend..." -ForegroundColor Yellow

$portalPath = Join-Path $ScriptDir "frontend-portal"

$portalScript = @'
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}
Write-Host "Portal frontend starting..." -ForegroundColor Green
npm run dev
'@

$portalScriptPath = Join-Path $portalPath "run-dev.ps1"
$portalScript | Out-File -FilePath $portalScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-File", $portalScriptPath, "-WorkingDirectory", $portalPath
Write-Host "      Portal frontend started (new window)" -ForegroundColor Green

# Done
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Startup Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Service URLs:" -ForegroundColor White
Write-Host "    API Docs:    http://localhost:8001/docs" -ForegroundColor Gray
Write-Host "    Admin:       http://localhost:3001" -ForegroundColor Gray
Write-Host "    Portal:      http://localhost:3002" -ForegroundColor Gray
Write-Host ""
Write-Host "  Default Admin: admin / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3 PowerShell windows opened for services" -ForegroundColor Gray
Write-Host "  Close windows to stop services" -ForegroundColor Gray
Write-Host ""

$openBrowser = Read-Host "Open browser? (Y/N)"
if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:8001/docs"
    Start-Process "http://localhost:3001"
    Start-Process "http://localhost:3002"
}
