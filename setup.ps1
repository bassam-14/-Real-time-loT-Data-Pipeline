# PowerShell Setup Script for IoT Data Pipeline
# Run this script to set up the environment on Windows

Write-Host ">> Setting up IoT Data Pipeline Environment..." -ForegroundColor Cyan

# Check if Docker is running
Write-Host "`n[*] Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1 | Select-String "Server Version"
if (-not $dockerRunning) {
    Write-Host "[X] Error: Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Docker is running" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "`n[*] Creating .env file from sample..." -ForegroundColor Yellow
    Copy-Item "sample.env" ".env"
    Write-Host "[OK] .env file created. Please edit it with your credentials!" -ForegroundColor Green
    Write-Host "[!] Remember to change default passwords!" -ForegroundColor Yellow
}
else {
    Write-Host "`n[OK] .env file already exists" -ForegroundColor Green
}

# Create required directories
Write-Host "`n[*] Creating required directories..." -ForegroundColor Yellow
$directories = @("dags", "logs", "plugins", "config")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  [OK] Created $dir/" -ForegroundColor Green
    }
    else {
        Write-Host "  [OK] $dir/ already exists" -ForegroundColor Green
    }
}

# Set AIRFLOW_UID
Write-Host "`n[*] Setting AIRFLOW_UID..." -ForegroundColor Yellow
$env:AIRFLOW_UID = 50000
Write-Host "[OK] AIRFLOW_UID set to 50000" -ForegroundColor Green

# Build custom Docker image
Write-Host "`n[*] Building custom Airflow image with dependencies..." -ForegroundColor Yellow
Write-Host "   This may take 5-10 minutes on first build..." -ForegroundColor Gray
docker-compose build
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Docker image built successfully" -ForegroundColor Green
}
else {
    Write-Host "[X] Error building Docker image" -ForegroundColor Red
    exit 1
}

# Initialize Airflow
Write-Host "`n[*] Initializing Airflow (this may take a few minutes)..." -ForegroundColor Yellow
docker-compose up airflow-init
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Airflow initialized successfully" -ForegroundColor Green
}
else {
    Write-Host "[X] Error initializing Airflow" -ForegroundColor Red
    exit 1
}

# Start all services
Write-Host "`n[*] Starting all services..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] All services started successfully" -ForegroundColor Green
}
else {
    Write-Host "[X] Error starting services" -ForegroundColor Red
    exit 1
}

# Wait for services to be healthy
Write-Host "`n[*] Waiting for services to be healthy (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "`n[*] Service Status:" -ForegroundColor Yellow
docker-compose ps

# Print access information
Write-Host "`n[OK] Setup Complete!" -ForegroundColor Green
Write-Host "`n[WEB] Access URLs:" -ForegroundColor Cyan
Write-Host "  - Airflow UI:  http://localhost:8080" -ForegroundColor White
Write-Host "    Username: airflow | Password: airflow (or your custom credentials)" -ForegroundColor Gray
Write-Host "  - Kafka UI:    http://localhost:8090" -ForegroundColor White
Write-Host "  - MySQL:       localhost:3306" -ForegroundColor White
Write-Host "`n[NEXT] Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Open Airflow UI at http://localhost:8080" -ForegroundColor White
Write-Host "  2. Create Kafka topics: docker-compose exec kafka kafka-topics --create --bootstrap-server localhost:29092 --topic iot_sensor_data --partitions 3" -ForegroundColor White
Write-Host "  3. Add your DAG files to the dags/ folder" -ForegroundColor White
Write-Host "`n[TIP] Tips:" -ForegroundColor Cyan
Write-Host "  - View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  - Stop services: docker-compose stop" -ForegroundColor White
Write-Host "  - Remove everything: docker-compose down -v" -ForegroundColor White
Write-Host "`nHappy Data Engineering!" -ForegroundColor Green
