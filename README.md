# Real-time IoT Data Pipeline

A comprehensive data engineering project that simulates IoT sensor data (temperature and humidity) and processes it using both batch and streaming techniques with Apache Airflow, Apache Kafka, and MySQL.

## 📋 Project Overview

This project demonstrates a complete data pipeline for IoT sensor data:

- **Data Simulation**: Generates sensor readings with temperature and humidity values
- **Streaming Processing**: Real-time data ingestion using Apache Kafka
- **Batch Processing**: Scheduled data processing with Apache Airflow
- **Data Storage**: MySQL database for persistent storage
- **Monitoring**: Kafka UI and Airflow web interface for system monitoring

## 🏗️ Architecture

```
IoT Sensors (Simulated)
    ↓
Apache Kafka (Streaming)
    ↓
Apache Airflow (Orchestration)
    ↓
MySQL Database (Storage)
    ↓
Email Alerts (Threshold Monitoring)
```

## 🛠️ Technology Stack

- **Apache Airflow 3.1.0**: Workflow orchestration and scheduling
- **Apache Kafka 7.5.0**: Distributed streaming platform
- **MySQL 8.0**: Relational database
- **Redis 7.2**: Message broker for Celery
- **Zookeeper 7.5.0**: Kafka coordination service
- **Docker & Docker Compose**: Containerization
- **Python 3.x**: Data generation and processing

## 📦 Services Included

| Service             | Port | Description                                  |
| ------------------- | ---- | -------------------------------------------- |
| Airflow Web UI      | 8081 | Airflow dashboard and DAG management         |
| Kafka Broker        | 9092 | Kafka broker for external connections        |
| Kafka UI            | 8090 | Web interface for monitoring Kafka           |
| MySQL               | 3307 | MySQL database (host access)                 |
| Streamlit Dashboard | 8501 | Real-time sensor dashboard with auto-refresh |
| Redis               | 6379 | Redis for Celery backend (internal)          |
| Zookeeper           | 2181 | Kafka coordination (internal)                |
| Flower (optional)   | 5555 | Celery monitoring tool                       |

## ⚡ Quick Start (One-Click Setup)

### Option 1: Automated Setup (Recommended)

**Run everything with one command:**

```powershell
# Navigate to project folder
cd "d:\Mohamred data\data engineering DEPI\Technical\final project"

# Start all services and open web interfaces
.\start-all.ps1
```

This script will:

- ✅ Check Docker is running
- ✅ Start all Docker services (Kafka, MySQL, Airflow, Redis)
- ✅ Create Kafka topic automatically
- ✅ Launch Streamlit dashboard
- ✅ Open all web interfaces in your browser

**To stop everything:**

```powershell
.\stop-all.ps1
```

---

### Option 2: Manual Setup (Step by Step)

#### Step 1: Start All Services

```powershell
# 1. Navigate to project folder
cd "d:\Mohamred data\data engineering DEPI\Technical\final project"

# 2. Copy environment file (if not done already)
Copy-Item sample.env .env

# 3. Start Docker services (Kafka, Airflow, MySQL)
docker-compose up -d

# 4. Wait 2-3 minutes for all services to be healthy ☕
docker-compose ps
```

#### Step 2: Create Kafka Topic

```powershell
docker-compose exec kafka kafka-topics --create `
  --bootstrap-server localhost:29092 `
  --replication-factor 1 `
  --partitions 3 `
  --topic iot_sensor_data
```

#### Step 3: Access the Services

- **Airflow UI**: http://localhost:8081 (user: `airflow`, pass: `airflow`)
- **Kafka UI**: http://localhost:8090

#### Step 4: Run the Dashboard (Optional)

```powershell
# Install Python dependencies locally
python -m pip install -r requirements.txt

# Set environment for local MySQL access (note: port 3307)
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3307"
$env:MYSQL_USER="airflow"
$env:MYSQL_PASSWORD="airflow"
$env:MYSQL_DATABASE="airflow_db"

# Run Streamlit dashboard
python -m streamlit run dashboard_app.py
```

Dashboard will open at: http://localhost:8501

---

## 🚀 Detailed Setup Guide

### Prerequisites

- Docker Desktop installed and running
- Docker Compose V2
- Minimum 4GB RAM allocated to Docker
- 10GB free disk space
- Python 3.8+ (for running dashboard locally)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/bassam-14/-Real-time-loT-Data-Pipeline.git
cd -Real-time-loT-Data-Pipeline
```

#### 2. Create Environment File

Copy the sample environment file and customize it:

```bash
cp sample.env .env
```

Edit `.env` file with your credentials:

```bash
# MySQL Configuration
MYSQL_USER=your_username
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=airflow_db
MYSQL_ROOT_PASSWORD=your_root_password

# Airflow Admin
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin_password
```

**⚠️ Important**: Change default passwords before deploying to production!

#### 3. Initialize the Environment

On **Windows (PowerShell)**:

```powershell
# Create required directories
mkdir -p dags,logs,plugins,config

# Set Airflow UID (Windows uses default)
$env:AIRFLOW_UID=50000

# Initialize Airflow database
docker-compose up airflow-init
```

On **Linux/Mac**:

```bash
# Create required directories
mkdir -p dags logs plugins config

# Set Airflow UID to your user ID
echo "AIRFLOW_UID=$(id -u)" >> .env

# Initialize Airflow database
docker-compose up airflow-init
```

#### 4. Start All Services

```bash
docker-compose up -d
```

This will start:

- ✅ MySQL database
- ✅ Redis
- ✅ Zookeeper
- ✅ Kafka broker
- ✅ Kafka UI
- ✅ Airflow webserver, scheduler, triggerer, and workers

#### 5. Verify Services Are Running

```bash
docker-compose ps
```

All services should show status as "healthy" or "running".

### Accessing the Services

- **Airflow Web UI**: http://localhost:8080

  - Username: `airflow` (or what you set in .env)
  - Password: `airflow` (or what you set in .env)

- **Kafka UI**: http://localhost:8090
  - No authentication required
  - View topics, messages, and consumer groups

## 📧 Email Alerts Setup

The pipeline includes **automated email alerts** for threshold violations:

- 🌡️ **High Temperature Alert**: > 45°C
- 💧 **High Humidity Alert**: > 85%

**Quick Setup:**

1. Copy `sample.env` to `.env`
2. Configure SMTP settings (Gmail, Outlook, etc.)
3. Set your `ALERT_EMAIL` address
4. Restart services: `.\stop-all.ps1` then `.\start-all.ps1`

📖 **Detailed Guide**: See [EMAIL_ALERTS_SETUP.md](EMAIL_ALERTS_SETUP.md) for complete configuration instructions.

---

## 📊 Working with the Pipeline

### Creating Kafka Topics

Create a topic for sensor data:

```bash
docker-compose exec kafka kafka-topics --create \
  --bootstrap-server localhost:29092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic iot_sensor_data
```

List all topics:

```bash
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:29092
```

### Connecting to MySQL

From your local machine:

```bash
mysql -h 127.0.0.1 -P 3306 -u airflow -p
```

From within Docker:

```bash
docker-compose exec mysql mysql -u airflow -p
```

### Testing Kafka Producer/Consumer

**Producer** (send test message):

```bash
docker-compose exec kafka kafka-console-producer \
  --bootstrap-server localhost:29092 \
  --topic iot_sensor_data
```

**Consumer** (read messages):

```bash
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:29092 \
  --topic iot_sensor_data \
  --from-beginning
```

## 🔧 Development Workflow

### Adding Python Dependencies

1. Add packages to `requirements.txt`
2. Restart Airflow services:

```bash
docker-compose restart airflow-apiserver airflow-scheduler airflow-worker
```

### Creating DAGs

1. Add your DAG Python files to the `dags/` folder
2. Airflow will automatically detect them within 30-60 seconds
3. Refresh the Airflow UI to see your new DAGs

### Viewing Logs

```bash
# Airflow scheduler logs
docker-compose logs -f airflow-scheduler

# Kafka logs
docker-compose logs -f kafka

# All services
docker-compose logs -f
```

## 🔍 Monitoring & Troubleshooting

### Check Service Health

```bash
# Check all containers
docker-compose ps

# Check specific service logs
docker-compose logs <service-name>

# Check Airflow health
curl http://localhost:8080/health
```

### Common Issues

#### Issue: Services not starting

**Solution**: Ensure Docker has enough resources (4GB+ RAM)

```bash
docker-compose down -v
docker-compose up -d
```

#### Issue: Airflow shows "Connection refused" to database

**Solution**: Wait for MySQL to be fully healthy

```bash
docker-compose logs mysql
# Wait until you see "mysqld: ready for connections"
```

#### Issue: Kafka not accepting connections

**Solution**: Verify Zookeeper is running first

```bash
docker-compose logs zookeeper
docker-compose restart kafka
```

#### Issue: Permission denied on logs folder

**Solution** (Linux/Mac):

```bash
sudo chown -R $(id -u):$(id -g) logs dags plugins
```

### Accessing Airflow CLI

```bash
docker-compose exec airflow-apiserver airflow <command>

# Examples:
docker-compose exec airflow-apiserver airflow dags list
docker-compose exec airflow-apiserver airflow tasks list <dag_id>
docker-compose exec airflow-apiserver airflow dags trigger <dag_id>
```

## 🧪 Testing Your Setup

### Test 1: Verify Airflow Connection to MySQL

```bash
docker-compose exec airflow-apiserver airflow connections test mysql_default
```

### Test 2: Verify Kafka Topics

```bash
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:29092
```

### Test 3: Run Data Generator (Standalone)

```bash
python dags/Datagenerator.py
```

## 🛑 Stopping the Environment

```bash
# Stop all services (keep data)
docker-compose stop

# Stop and remove containers (keep data)
docker-compose down

# Stop and remove everything including volumes (⚠️ deletes all data)
docker-compose down -v
```

## 📁 Project Structure

```
.
├── dags/                      # Airflow DAG definitions
│   └── Datagenerator.py      # IoT sensor data simulator
├── logs/                      # Airflow logs
├── plugins/                   # Airflow plugins (custom operators, hooks)
├── config/                    # Configuration files
│   └── airflow.cfg           # Airflow configuration
├── docker-compose.yaml        # Docker services definition
├── requirements.txt           # Python dependencies
├── sample.env                 # Sample environment variables
├── .env                       # Your environment variables (create this)
└── README.md                  # This file
```

## 🔐 Security Best Practices

- ✅ Change all default passwords in `.env`
- ✅ Never commit `.env` file to version control
- ✅ Use strong passwords for MySQL and Airflow
- ✅ Restrict network access in production environments
- ✅ Use secrets management for production (e.g., AWS Secrets Manager, Azure Key Vault)

## 🤝 Team Collaboration

### Setting Up for Team Members

1. Each team member clones the repository
2. Copy `sample.env` to `.env` and configure
3. Run `docker-compose up airflow-init`
4. Run `docker-compose up -d`

### Sharing DAGs

- Commit DAG files to the `dags/` directory
- Team members pull changes and Airflow auto-detects new DAGs
- Use version control branches for development

### Database Migrations

- Use Airflow's built-in migration system
- Changes are applied automatically on container restart

## 📚 Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🐛 Reporting Issues

If you encounter any issues:

1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs <service-name>`
3. Open an issue on GitHub with logs and error messages

## 📝 License

This project is licensed under the Apache License 2.0.

## 👥 Contributors

- DEPI Data Engineering Team
- Branch: Elshewy

---

**Happy Data Engineering! 🚀**
