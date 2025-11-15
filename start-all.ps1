# IoT Pipeline - Complete Startup Script
# This script starts all services and opens web interfaces

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   IoT Data Pipeline - Starting Up     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/5] Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "OK Docker is running" -ForegroundColor Green
} catch {
    Write-Host "X Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Start Docker services
Write-Host "[2/5] Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "X Failed to start Docker services" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "OK Docker services started" -ForegroundColor Green
Write-Host ""

# Wait for services to be healthy
Write-Host "[3/5] Waiting for services (60 seconds)..." -ForegroundColor Yellow
Write-Host "    Initializing MySQL, Kafka, and Airflow..." -ForegroundColor Gray
Start-Sleep -Seconds 60
Write-Host "OK Services ready" -ForegroundColor Green
Write-Host ""

# Create Kafka topic
Write-Host "[4/5] Setting up Kafka topic..." -ForegroundColor Yellow
docker-compose exec -T kafka kafka-topics --create --bootstrap-server localhost:29092 --replication-factor 1 --partitions 3 --topic iot_sensor_data 2>$null | Out-Null
Write-Host "OK Kafka topic ready" -ForegroundColor Green
Write-Host ""

# Start Streamlit Dashboard
Write-Host "[5/5] Starting Dashboard..." -ForegroundColor Yellow
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3307"
$env:MYSQL_USER = "airflow"
$env:MYSQL_PASSWORD = "airflow"
$env:MYSQL_DATABASE = "airflow_db"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:MYSQL_HOST='127.0.0.1'; `$env:MYSQL_PORT='3307'; `$env:MYSQL_USER='airflow'; `$env:MYSQL_PASSWORD='airflow'; `$env:MYSQL_DATABASE='airflow_db'; python -m streamlit run dashboard_app.py" -WindowStyle Minimized

Write-Host "OK Dashboard starting..." -ForegroundColor Green
Start-Sleep -Seconds 5
Write-Host ""

# Open browsers
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Opening Web Interfaces..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 2
Start-Process "http://localhost:8081"
Start-Sleep -Seconds 2
Start-Process "http://localhost:8090"
Start-Sleep -Seconds 2
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor White
Write-Host "  Airflow:   http://localhost:8081" -ForegroundColor White
Write-Host "  Kafka UI:  http://localhost:8090" -ForegroundColor White
Write-Host "  Dashboard: http://localhost:8501" -ForegroundColor White
Write-Host "  MySQL:     localhost:3307" -ForegroundColor White
Write-Host ""
