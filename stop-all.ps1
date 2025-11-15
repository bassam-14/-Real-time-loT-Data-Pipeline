# IoT Pipeline - Stop All Services Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   IoT Data Pipeline - Shutting Down   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop Docker services
Write-Host "Stopping Docker services..." -ForegroundColor Yellow
docker-compose down

Write-Host " Docker services stopped" -ForegroundColor Green

# Kill Streamlit processes
Write-Host ""
Write-Host "Stopping Streamlit dashboard..." -ForegroundColor Yellow
Get-Process -Name "streamlit" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host " Dashboard stopped" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    All Services Stopped              " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
