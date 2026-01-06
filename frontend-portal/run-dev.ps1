if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}
Write-Host "Portal frontend starting..." -ForegroundColor Green
npm run dev
