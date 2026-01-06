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
