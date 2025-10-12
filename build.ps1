# Build Script for IoT Data Pipeline
# This script builds the custom Airflow Docker image with all dependencies

Write-Host "🔨 Building IoT Data Pipeline Docker Image..." -ForegroundColor Cyan

# Check if Docker is running
$dockerRunning = docker info 2>&1 | Select-String "Server Version"
if (-not $dockerRunning) {
    Write-Host "❌ Error: Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker is running" -ForegroundColor Green
Write-Host ""

# Build the custom Airflow image
Write-Host "📦 Building custom Airflow image (this may take 5-10 minutes)..." -ForegroundColor Yellow
Write-Host "   This installs all Python packages from requirements.txt" -ForegroundColor Gray
Write-Host ""

docker-compose build --no-cache

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Docker image built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Run: .\setup.ps1  (to initialize and start services)" -ForegroundColor White
    Write-Host "   OR" -ForegroundColor Gray
    Write-Host "   2. Run: docker-compose up -d  (if already initialized)" -ForegroundColor White
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "❌ Build failed! Check the error messages above." -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Common issues:" -ForegroundColor Yellow
    Write-Host "   • Check requirements.txt syntax" -ForegroundColor White
    Write-Host "   • Ensure Dockerfile exists" -ForegroundColor White
    Write-Host "   • Check Docker has enough disk space" -ForegroundColor White
    exit 1
}
