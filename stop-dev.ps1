# ============================================
# ZenTea License 停止开发环境
# ============================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  停止 ZenTea License 开发环境" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 停止 Docker 容器
Write-Host "[1/2] 停止 Docker 容器..." -ForegroundColor Yellow
Set-Location $ScriptDir
docker compose down 2>$null

if ($LASTEXITCODE -ne 0) {
    docker-compose down 2>$null
}

Write-Host "      Docker 容器已停止" -ForegroundColor Green

# 提示关闭前端窗口
Write-Host ""
Write-Host "[2/2] 请手动关闭前端开发服务器窗口" -ForegroundColor Yellow
Write-Host ""

# 是否清理数据
Write-Host "是否清理数据库数据？(Y/N) " -ForegroundColor Yellow -NoNewline
$cleanData = Read-Host

if ($cleanData -eq "Y" -or $cleanData -eq "y") {
    Write-Host ""
    Write-Host "正在清理数据..." -ForegroundColor Yellow
    docker compose down -v 2>$null
    Write-Host "数据已清理" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  开发环境已停止" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""


