# ============================================
# ZenTea License 本地开发环境一键启动脚本
# 适用于 Windows 11 + Docker Desktop
# ============================================

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ZenTea License 本地开发环境启动" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker Desktop 是否运行
Write-Host "[1/5] 检查 Docker Desktop..." -ForegroundColor Yellow

$dockerRunning = $false
try {
    $null = docker info 2>$null
    $dockerRunning = $true
    Write-Host "      Docker Desktop 已运行" -ForegroundColor Green
} catch {
    Write-Host "      Docker Desktop 未运行，正在启动..." -ForegroundColor Yellow
    
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-Host "      等待 Docker 启动（约 30 秒）..." -ForegroundColor Yellow
        
        $timeout = 60
        $elapsed = 0
        while ($elapsed -lt $timeout) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            try {
                $null = docker info 2>$null
                $dockerRunning = $true
                Write-Host "      Docker Desktop 已就绪" -ForegroundColor Green
                break
            } catch {
                Write-Host "      等待中... ($elapsed 秒)" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "      [ERROR] 未找到 Docker Desktop，请先安装" -ForegroundColor Red
        exit 1
    }
}

if (-not $dockerRunning) {
    Write-Host "      [ERROR] Docker Desktop 启动超时" -ForegroundColor Red
    exit 1
}

# 启动后端服务
Write-Host ""
Write-Host "[2/5] 启动后端服务 (Docker Compose)..." -ForegroundColor Yellow

Set-Location $ScriptDir
docker compose up -d 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "      [WARN] docker compose 命令失败，尝试 docker-compose..." -ForegroundColor Yellow
    docker-compose up -d
}

Write-Host "      后端服务已启动" -ForegroundColor Green

# 等待后端就绪
Write-Host ""
Write-Host "[3/5] 等待后端服务就绪..." -ForegroundColor Yellow

$maxRetries = 30
$retryCount = 0
$backendReady = $false

while ($retryCount -lt $maxRetries) {
    Start-Sleep -Seconds 2
    $retryCount++
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.status -eq "ok") {
            $backendReady = $true
            Write-Host "      后端服务已就绪 ($($retryCount * 2) 秒)" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "      等待中... ($($retryCount * 2) 秒)" -ForegroundColor Gray
    }
}

if (-not $backendReady) {
    Write-Host "      [WARN] 后端服务可能未完全就绪，请手动检查" -ForegroundColor Yellow
    Write-Host "      查看日志: docker compose logs -f backend" -ForegroundColor Gray
}

# 启动管理后台前端
Write-Host ""
Write-Host "[4/5] 启动管理后台前端..." -ForegroundColor Yellow

$adminPath = Join-Path $ScriptDir "frontend-admin"
if (Test-Path $adminPath) {
    $adminCmd = "cd '$adminPath'; if (-not (Test-Path 'node_modules')) { npm install }; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $adminCmd
    Write-Host "      管理后台已启动 (新窗口)" -ForegroundColor Green
} else {
    Write-Host "      [WARN] 未找到 frontend-admin 目录" -ForegroundColor Yellow
}

# 启动用户门户前端
Write-Host ""
Write-Host "[5/5] 启动用户门户前端..." -ForegroundColor Yellow

$portalPath = Join-Path $ScriptDir "frontend-portal"
if (Test-Path $portalPath) {
    $portalCmd = "cd '$portalPath'; if (-not (Test-Path 'node_modules')) { npm install }; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $portalCmd
    Write-Host "      用户门户已启动 (新窗口)" -ForegroundColor Green
} else {
    Write-Host "      [WARN] 未找到 frontend-portal 目录" -ForegroundColor Yellow
}

# 完成
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  启动完成！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  服务地址:" -ForegroundColor White
Write-Host "    API 文档:   http://localhost:8001/docs" -ForegroundColor Gray
Write-Host "    管理后台:   http://localhost:3001" -ForegroundColor Gray
Write-Host "    用户门户:   http://localhost:3002" -ForegroundColor Gray
Write-Host ""
Write-Host "  默认管理员: admin / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "  停止服务: docker compose down" -ForegroundColor Gray
Write-Host ""

# 打开浏览器
Write-Host "是否打开浏览器？(Y/N) " -ForegroundColor Yellow -NoNewline
$openBrowser = Read-Host

if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:8001/docs"
    Start-Process "http://localhost:3001"
    Start-Process "http://localhost:3002"
}


