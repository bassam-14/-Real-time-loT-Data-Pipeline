# PowerShell Commands Cheat Sheet
# Save this file and source it: . .\commands.ps1
# Then you can use short commands like: Start-Pipeline, Stop-Pipeline, etc.

function Start-Pipeline {
    Write-Host "🚀 Starting IoT Data Pipeline..." -ForegroundColor Cyan
    docker-compose up -d
    Write-Host "✅ Pipeline started! Access:" -ForegroundColor Green
    Write-Host "   Airflow UI: http://localhost:8081" -ForegroundColor White
    Write-Host "   Kafka UI:   http://localhost:8090" -ForegroundColor White
    Write-Host "   MySQL:      localhost:3307" -ForegroundColor White
}

function Stop-Pipeline {
    Write-Host "🛑 Stopping IoT Data Pipeline..." -ForegroundColor Yellow
    docker-compose stop
    Write-Host "✅ Pipeline stopped!" -ForegroundColor Green
}

function Restart-Pipeline {
    Write-Host "🔄 Restarting IoT Data Pipeline..." -ForegroundColor Yellow
    docker-compose restart
    Write-Host "✅ Pipeline restarted!" -ForegroundColor Green
}

function Show-PipelineStatus {
    Write-Host "📊 Pipeline Status:" -ForegroundColor Cyan
    docker-compose ps
}

function Show-PipelineLogs {
    param(
        [string]$Service = ""
    )
    if ($Service -eq "") {
        Write-Host "📋 Showing all logs (Ctrl+C to stop)..." -ForegroundColor Cyan
        docker-compose logs -f
    }
    else {
        Write-Host "📋 Showing logs for $Service (Ctrl+C to stop)..." -ForegroundColor Cyan
        docker-compose logs -f $Service
    }
}

function Remove-Pipeline {
    $confirm = Read-Host "⚠️  This will remove all containers and data. Continue? (yes/no)"
    if ($confirm -eq "yes") {
        Write-Host "🗑️  Removing IoT Data Pipeline..." -ForegroundColor Red
        docker-compose down -v
        Write-Host "✅ Pipeline removed!" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Operation cancelled." -ForegroundColor Yellow
    }
}

function Test-KafkaConnection {
    Write-Host "🧪 Testing Kafka connection..." -ForegroundColor Cyan
    python utils.py
}

function Create-KafkaTopic {
    param(
        [string]$TopicName = "iot_sensor_data",
        [int]$Partitions = 3
    )
    Write-Host "📝 Creating Kafka topic: $TopicName..." -ForegroundColor Cyan
    docker-compose exec kafka kafka-topics --create `
        --bootstrap-server localhost:29092 `
        --replication-factor 1 `
        --partitions $Partitions `
        --topic $TopicName
    Write-Host "✅ Topic created!" -ForegroundColor Green
}

function Show-KafkaTopics {
    Write-Host "📋 Kafka Topics:" -ForegroundColor Cyan
    docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:29092
}

function Watch-KafkaTopic {
    param(
        [string]$TopicName = "iot_sensor_data"
    )
    Write-Host "👀 Watching topic: $TopicName (Ctrl+C to stop)..." -ForegroundColor Cyan
    docker-compose exec kafka kafka-console-consumer `
        --bootstrap-server localhost:29092 `
        --topic $TopicName `
        --from-beginning
}

function Connect-MySQL {
    Write-Host "🗄️  Connecting to MySQL..." -ForegroundColor Cyan
    docker-compose exec mysql mysql -u airflow -p
}

function Show-AirflowDags {
    Write-Host "📋 Airflow DAGs:" -ForegroundColor Cyan
    docker-compose exec airflow-apiserver airflow dags list
}

function Trigger-AirflowDag {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DagId
    )
    Write-Host "▶️  Triggering DAG: $DagId..." -ForegroundColor Cyan
    docker-compose exec airflow-apiserver airflow dags trigger $DagId
    Write-Host "✅ DAG triggered!" -ForegroundColor Green
}

function Show-AirflowConnections {
    Write-Host "🔗 Airflow Connections:" -ForegroundColor Cyan
    docker-compose exec airflow-apiserver airflow connections list
}

function Generate-SampleData {
    param(
        [int]$Records = 10
    )
    Write-Host "📊 Generating $Records sample sensor readings..." -ForegroundColor Cyan
    python -c @"
import sys
sys.path.append('.')
from utils import generate_sample_data
generate_sample_data($Records)
"@
}

function Quick-Setup {
    Write-Host "⚡ Running quick setup..." -ForegroundColor Cyan
    
    # Create .env if not exists
    if (-not (Test-Path ".env")) {
        Copy-Item "sample.env" ".env"
        Write-Host "📝 Created .env file - please edit it!" -ForegroundColor Yellow
    }
    
    # Initialize Airflow
    Write-Host "🔧 Initializing Airflow..." -ForegroundColor Cyan
    docker-compose up airflow-init
    
    # Start services
    Start-Pipeline
    
    # Wait for services
    Write-Host "⏳ Waiting for services to be ready (30s)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Create default topic
    Create-KafkaTopic -TopicName "iot_sensor_data" -Partitions 3
    
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Show-PipelineStatus
}

function Show-PipelineInfo {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         IoT Data Pipeline - Quick Commands                ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🚀 Pipeline Management:" -ForegroundColor Yellow
    Write-Host "   Start-Pipeline              Start all services" -ForegroundColor White
    Write-Host "   Stop-Pipeline               Stop all services" -ForegroundColor White
    Write-Host "   Restart-Pipeline            Restart all services" -ForegroundColor White
    Write-Host "   Show-PipelineStatus         Show service status" -ForegroundColor White
    Write-Host "   Show-PipelineLogs [service] View logs" -ForegroundColor White
    Write-Host "   Remove-Pipeline             Remove everything (⚠️ deletes data)" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Kafka Commands:" -ForegroundColor Yellow
    Write-Host "   Create-KafkaTopic [name] [partitions]  Create topic" -ForegroundColor White
    Write-Host "   Show-KafkaTopics                        List topics" -ForegroundColor White
    Write-Host "   Watch-KafkaTopic [name]                 Watch topic messages" -ForegroundColor White
    Write-Host ""
    Write-Host "🗄️  Database Commands:" -ForegroundColor Yellow
    Write-Host "   Connect-MySQL               Connect to MySQL shell" -ForegroundColor White
    Write-Host ""
    Write-Host "✈️  Airflow Commands:" -ForegroundColor Yellow
    Write-Host "   Show-AirflowDags            List all DAGs" -ForegroundColor White
    Write-Host "   Trigger-AirflowDag <dag_id> Trigger a DAG" -ForegroundColor White
    Write-Host "   Show-AirflowConnections     List connections" -ForegroundColor White
    Write-Host ""
    Write-Host "🧪 Testing:" -ForegroundColor Yellow
    Write-Host "   Test-KafkaConnection        Run connection tests" -ForegroundColor White
    Write-Host "   Generate-SampleData [count] Generate sample data" -ForegroundColor White
    Write-Host ""
    Write-Host "⚡ Quick Actions:" -ForegroundColor Yellow
    Write-Host "   Quick-Setup                 Run complete setup" -ForegroundColor White
    Write-Host "   Show-PipelineInfo           Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Access URLs:" -ForegroundColor Yellow
    Write-Host "   Airflow UI: http://localhost:8081" -ForegroundColor White
    Write-Host "   Kafka UI:   http://localhost:8090" -ForegroundColor White
    Write-Host "   MySQL:      localhost:3307" -ForegroundColor White
    Write-Host ""
}

# Show info on load
Show-PipelineInfo

Write-Host "💡 Tip: Functions loaded! Try: Start-Pipeline" -ForegroundColor Green
Write-Host ""
