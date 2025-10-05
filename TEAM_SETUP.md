# Team Setup Guide - IoT Data Pipeline Project

## 👥 For Team Members

This guide will help you get started with the IoT Data Pipeline project.

## 📋 Prerequisites Checklist

Before you begin, make sure you have:

- [ ] Docker Desktop installed and running
  - Windows: https://docs.docker.com/desktop/install/windows-install/
  - Mac: https://docs.docker.com/desktop/install/mac-install/
  - Linux: https://docs.docker.com/engine/install/
- [ ] Git installed
  - Download: https://git-scm.com/downloads
- [ ] At least 4GB RAM allocated to Docker
  - Docker Desktop → Settings → Resources → Memory (set to 4GB+)
- [ ] At least 10GB free disk space

- [ ] Text editor (VS Code recommended)
  - Download: https://code.visualstudio.com/

## 🚀 Step-by-Step Setup (Windows)

### Step 1: Clone the Repository

```powershell
# Navigate to your workspace
cd "D:\Mohamred data\data engineering DEPI\Technical"

# Clone the repository (if not already done)
git clone https://github.com/bassam-14/-Real-time-loT-Data-Pipeline.git
cd -Real-time-loT-Data-Pipeline

# Or if already cloned, just navigate to it
cd "final project"
```

### Step 2: Create Your Environment File

```powershell
# Copy the sample environment file
Copy-Item sample.env .env

# Open .env in notepad or your preferred editor
notepad .env
```

**Edit the .env file and change these values:**

```bash
MYSQL_USER=your_username                    # Your MySQL username
MYSQL_PASSWORD=YourSecurePassword123       # Your MySQL password (CHANGE THIS!)
MYSQL_ROOT_PASSWORD=YourRootPassword123    # MySQL root password (CHANGE THIS!)
_AIRFLOW_WWW_USER_USERNAME=admin           # Airflow admin username
_AIRFLOW_WWW_USER_PASSWORD=AdminPass123    # Airflow admin password (CHANGE THIS!)
```

⚠️ **Important**: Never commit the .env file to Git!

### Step 3: Run the Setup Script

```powershell
# Run the automated setup script
.\setup.ps1
```

This script will:

- ✅ Check if Docker is running
- ✅ Create necessary directories
- ✅ Initialize Airflow database
- ✅ Start all services

**Wait 2-3 minutes** for all services to start and become healthy.

### Step 4: Verify Installation

Open your browser and check:

- Airflow UI: http://localhost:8080 (login with your credentials)
- Kafka UI: http://localhost:8090 (no login needed)

### Step 5: Create Kafka Topic

```powershell
# Create the main sensor data topic
docker-compose exec kafka kafka-topics --create `
  --bootstrap-server localhost:29092 `
  --replication-factor 1 `
  --partitions 3 `
  --topic iot_sensor_data

# Verify topic was created
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:29092
```

### Step 6: Test the Setup

```powershell
# Install Python dependencies locally (optional, for testing)
pip install -r requirements.txt

# Run the utility script to test everything
python utils.py
```

Select option 7 to run all tests.

## 🚀 Step-by-Step Setup (Linux/Mac)

### Step 1: Clone the Repository

```bash
cd ~/workspace
git clone https://github.com/bassam-14/-Real-time-loT-Data-Pipeline.git
cd -Real-time-loT-Data-Pipeline
```

### Step 2: Create Environment File

```bash
cp sample.env .env
nano .env  # or use vim, code, etc.
```

### Step 3: Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

### Step 4-6: Same as Windows above

## 📁 Project Structure

```
final project/
├── dags/                  # Put your Airflow DAG files here
│   └── Datagenerator.py  # Sample sensor data generator
├── logs/                  # Airflow logs (auto-generated)
├── plugins/               # Custom Airflow plugins
├── config/                # Configuration files
│   └── airflow.cfg       # Airflow configuration
├── docker-compose.yaml    # Docker services definition
├── requirements.txt       # Python dependencies
├── .env                   # Your environment variables (DO NOT COMMIT!)
├── sample.env            # Sample environment template
├── README.md             # Main documentation
├── QUICK_REFERENCE.md    # Quick command reference
├── TEAM_SETUP.md         # This file
├── setup.ps1             # Windows setup script
├── setup.sh              # Linux/Mac setup script
└── utils.py              # Utility testing script
```

## 🔄 Daily Workflow

### Starting Work

```powershell
# 1. Pull latest changes from Git
git pull origin Elshewy

# 2. Start Docker services (if not running)
docker-compose up -d

# 3. Check services are healthy
docker-compose ps
```

### During Development

```powershell
# Create/edit DAG files in dags/ folder
# Airflow will automatically detect changes in 30-60 seconds

# View logs if needed
docker-compose logs -f airflow-scheduler

# Test Kafka connection
python utils.py  # Select option 1
```

### Ending Work

```powershell
# 1. Commit your changes
git add .
git commit -m "Your commit message"
git push origin Elshewy

# 2. Stop services (optional - keeps data)
docker-compose stop

# Or keep them running for next session
```

## 🔧 Common Tasks

### Working with DAGs

1. **Create a new DAG**

   - Add a new Python file in `dags/` folder
   - Airflow will auto-detect it
   - Refresh the Airflow UI

2. **Test a DAG**

   ```powershell
   docker-compose exec airflow-apiserver airflow dags test <dag_id> 2025-10-05
   ```

3. **Trigger a DAG manually**
   - Go to Airflow UI → DAGs → Click the play button
   - Or use CLI: `docker-compose exec airflow-apiserver airflow dags trigger <dag_id>`

### Working with Kafka

1. **Send test data to Kafka**

   ```powershell
   # Use the utility script
   python utils.py  # Select option 4
   ```

2. **Monitor Kafka messages**

   - Open Kafka UI: http://localhost:8090
   - Go to Topics → iot_sensor_data → Messages

3. **Consume messages from terminal**
   ```powershell
   docker-compose exec kafka kafka-console-consumer `
     --bootstrap-server localhost:29092 `
     --topic iot_sensor_data `
     --from-beginning
   ```

### Working with MySQL

1. **Connect to MySQL**

   ```powershell
   docker-compose exec mysql mysql -u airflow -p
   ```

2. **Create tables**

   ```powershell
   # Use the utility script
   python utils.py  # Select option 3
   ```

3. **Query data**
   ```sql
   USE airflow_db;
   SHOW TABLES;
   SELECT * FROM sensor_readings LIMIT 10;
   ```

## ❓ Troubleshooting

### Problem: Services won't start

**Solution:**

```powershell
# Stop everything
docker-compose down -v

# Start fresh
docker-compose up airflow-init
docker-compose up -d
```

### Problem: "Port already in use"

**Solution:**

```powershell
# Check what's using the port
netstat -ano | findstr :8080  # Windows
lsof -i :8080                 # Mac/Linux

# Kill the process or change port in docker-compose.yaml
```

### Problem: Airflow UI shows connection errors

**Solution:**

```powershell
# Check MySQL is healthy
docker-compose logs mysql

# Wait for this message: "mysqld: ready for connections"
# Then restart Airflow services
docker-compose restart airflow-apiserver airflow-scheduler
```

### Problem: Can't see my DAG in Airflow UI

**Solution:**

1. Check the DAG file has no syntax errors
2. Check logs: `docker-compose logs airflow-scheduler`
3. Wait 60 seconds for auto-refresh
4. Make sure DAG file is in `dags/` folder
5. Check DAG isn't paused (toggle in UI)

### Problem: Kafka connection refused

**Solution:**

```powershell
# Check Kafka is healthy
docker-compose ps kafka

# Check Kafka logs
docker-compose logs kafka

# Restart Kafka
docker-compose restart zookeeper kafka
```

## 📞 Getting Help

1. **Check the documentation**

   - README.md - Full project documentation
   - QUICK_REFERENCE.md - Command reference
   - This file - Setup guide

2. **Check logs**

   ```powershell
   docker-compose logs <service-name>
   ```

3. **Ask the team**
   - Create an issue on GitHub
   - Ask in team chat
   - Schedule a pair programming session

## 🎯 Next Steps

After setup is complete:

1. ✅ Familiarize yourself with the Airflow UI
2. ✅ Explore the Kafka UI to understand topics
3. ✅ Review the existing DAG file: `dags/Datagenerator.py`
4. ✅ Read the project requirements document
5. ✅ Start working on your assigned tasks

## 📚 Learning Resources

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Kafka Quickstart](https://kafka.apache.org/quickstart)
- [MySQL Tutorial](https://dev.mysql.com/doc/mysql-tutorial-excerpt/8.0/en/)
- [Docker Compose](https://docs.docker.com/compose/)

## 🔐 Security Reminders

- ⚠️ Never commit `.env` file to Git
- ⚠️ Change all default passwords
- ⚠️ Use strong passwords (12+ characters, mixed case, numbers, symbols)
- ⚠️ Don't share credentials in chat or email
- ⚠️ This setup is for development only - production needs additional security

## ✅ Setup Checklist

After completing setup, verify:

- [ ] Docker services are running (`docker-compose ps`)
- [ ] Airflow UI is accessible (http://localhost:8080)
- [ ] Kafka UI is accessible (http://localhost:8090)
- [ ] Can login to Airflow with your credentials
- [ ] Kafka topic `iot_sensor_data` exists
- [ ] MySQL connection works
- [ ] Can see example DAG in Airflow UI
- [ ] All tests pass in `utils.py`

---

**Welcome to the team! Happy coding! 🚀**

For questions or issues, contact the project maintainers or create a GitHub issue.
