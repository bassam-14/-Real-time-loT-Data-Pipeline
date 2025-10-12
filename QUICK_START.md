# ⚡ Quick Start Guide

Get your IoT Data Pipeline up and running in 5 minutes!

## 📋 Prerequisites

- ✅ Docker Desktop installed and **running**
- ✅ At least 4GB RAM allocated to Docker
- ✅ 10GB free disk space

## 🚀 Setup (Choose Your Platform)

### Windows (PowerShell)

```powershell
# 1. Navigate to project
cd "D:\Mohamred data\data engineering DEPI\Technical\final project"

# 2. Create environment file (edit with your passwords!)
Copy-Item sample.env .env
notepad .env  # Change the passwords!

# 3. Run automated setup (builds image, initializes, starts everything)
.\setup.ps1

# Wait 2-3 minutes... ☕

# 4. Create Kafka topic
docker-compose exec kafka kafka-topics --create `
  --bootstrap-server localhost:29092 `
  --replication-factor 1 `
  --partitions 3 `
  --topic iot_sensor_data

# 5. Open in browser
start http://localhost:8080  # Airflow (user: airflow, pass: airflow)
start http://localhost:8090  # Kafka UI
```

### Linux/Mac (Bash)

```bash
# 1. Navigate to project
cd ~/path/to/final-project

# 2. Create environment file
cp sample.env .env
nano .env  # Change the passwords!

# 3. Make scripts executable
chmod +x setup.sh build.sh

# 4. Run automated setup
./setup.sh

# Wait 2-3 minutes... ☕

# 5. Create Kafka topic
docker-compose exec kafka kafka-topics --create \
  --bootstrap-server localhost:29092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic iot_sensor_data

# 6. Open in browser
open http://localhost:8080  # Airflow
open http://localhost:8090  # Kafka UI
```

## ✅ Verify Setup

```powershell
# Check all services are healthy
docker-compose ps

# You should see all services with "healthy" or "Up" status

# Test connections (optional)
python utils.py
# Select option 7 (Run All Tests)
```

## 🎯 What Just Happened?

1. ✅ **Built custom Docker image** with all Python packages from `requirements.txt`
2. ✅ **Started 10+ services**: Kafka, MySQL, Airflow, etc.
3. ✅ **Created Kafka topic** for sensor data
4. ✅ **Ready to develop!**

## 🌐 Access Your Services

| Service        | URL                   | Login             |
| -------------- | --------------------- | ----------------- |
| **Airflow UI** | http://localhost:8080 | airflow / airflow |
| **Kafka UI**   | http://localhost:8090 | No login needed   |
| **MySQL**      | localhost:3306        | airflow / airflow |

## 📝 Next Steps

### 1. Explore Airflow UI

- Go to http://localhost:8080
- Login with `airflow` / `airflow`
- Browse DAGs → You'll see any DAGs in the `dags/` folder

### 2. Create Your First DAG

```python
# Create file: dags/my_first_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello():
    print("Hello from Airflow!")

with DAG(
    'my_first_dag',
    start_date=datetime(2025, 10, 1),
    schedule='@daily',
    catchup=False
) as dag:

    task = PythonOperator(
        task_id='say_hello',
        python_callable=hello
    )
```

Wait 30-60 seconds → Refresh Airflow UI → You'll see your DAG!

### 3. Test Kafka

```powershell
# Send a test message
docker-compose exec kafka kafka-console-producer `
  --bootstrap-server localhost:29092 `
  --topic iot_sensor_data

# Type a message and press Enter
# Press Ctrl+C to exit

# Read messages
docker-compose exec kafka kafka-console-consumer `
  --bootstrap-server localhost:29092 `
  --topic iot_sensor_data `
  --from-beginning
```

### 4. Generate Sample Sensor Data

```powershell
# Use the utility script
python utils.py
# Select option 4 or 5 to generate sample data
```

### 5. Query MySQL

```powershell
# Connect to MySQL
docker-compose exec mysql mysql -u airflow -p
# Password: airflow (or what you set in .env)

# Run queries
USE airflow_db;
SHOW TABLES;
```

## 🛑 Stop/Start Services

```powershell
# Stop (keeps data)
docker-compose stop

# Start again
docker-compose start

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart airflow-scheduler
```

## 📚 Learn More

- **ARCHITECTURE.md** - Understand how everything connects
- **REQUIREMENTS_EXPLAINED.md** - How Python packages are installed
- **TEAM_SETUP.md** - Detailed setup guide for team members
- **QUICK_REFERENCE.md** - Command cheat sheet
- **README.md** - Complete documentation

## 🆘 Troubleshooting

### Services won't start?

```powershell
docker-compose down -v
.\setup.ps1  # Start fresh
```

### Need to rebuild after changing requirements.txt?

```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use?

```powershell
# Windows: Find what's using port 8080
netstat -ano | findstr :8080

# Linux/Mac
lsof -i :8080

# Kill the process or change port in docker-compose.yaml
```

### Can't see my DAG?

- Wait 60 seconds for Airflow to scan
- Check file has no syntax errors
- Check logs: `docker-compose logs airflow-scheduler`
- Make sure file is in `dags/` folder

## 💡 Pro Tips

### Use PowerShell Helper Functions

```powershell
# Load helper functions
. .\commands.ps1

# Now use simple commands
Start-Pipeline
Show-PipelineStatus
Show-PipelineLogs
Create-KafkaTopic "my_topic" 3
```

### View Real-time Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
docker-compose logs -f kafka
```

### Quick Health Check

```powershell
# See all services status
docker-compose ps

# Test Airflow
curl http://localhost:8080/health
```

## 🎓 Development Workflow

```
1. Edit DAG files in dags/
   ↓
2. Airflow auto-detects changes (30-60s)
   ↓
3. Test in Airflow UI
   ↓
4. Check logs if needed
   ↓
5. Iterate and improve
   ↓
6. Commit to Git
```

## ✨ You're Ready!

Your IoT Data Pipeline is now running! 🎉

Start building your DAGs and processing sensor data!

---

**Need help?** Check the documentation files or ask your team members.

**Happy Coding! 🚀**
