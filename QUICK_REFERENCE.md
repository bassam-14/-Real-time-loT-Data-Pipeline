# Quick Reference Guide for IoT Data Pipeline

## 🎯 Quick Commands

### Starting & Stopping

```bash
# Start all services
docker-compose up -d

# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Remove everything including data ⚠️
docker-compose down -v

# Restart specific service
docker-compose restart <service-name>
```

### Monitoring

```bash
# View all service status
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f airflow-scheduler
docker-compose logs -f kafka
docker-compose logs -f mysql

# View last 100 lines
docker-compose logs --tail=100 airflow-worker
```

## 🔧 Kafka Commands

### Topics Management

```bash
# List all topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:29092

# Create a topic
docker-compose exec kafka kafka-topics --create \
  --bootstrap-server localhost:29092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic iot_sensor_data

# Describe a topic
docker-compose exec kafka kafka-topics --describe \
  --bootstrap-server localhost:29092 \
  --topic iot_sensor_data

# Delete a topic
docker-compose exec kafka kafka-topics --delete \
  --bootstrap-server localhost:29092 \
  --topic iot_sensor_data
```

### Producer & Consumer

```bash
# Start console producer
docker-compose exec kafka kafka-console-producer \
  --bootstrap-server localhost:29092 \
  --topic iot_sensor_data

# Start console consumer (from beginning)
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:29092 \
  --topic iot_sensor_data \
  --from-beginning

# Consumer with group
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:29092 \
  --topic iot_sensor_data \
  --group my-consumer-group \
  --from-beginning

# List consumer groups
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --list

# Describe consumer group
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --group airflow_consumer_group \
  --describe
```

## 🗄️ MySQL Commands

### Connect to MySQL

```bash
# From host machine
mysql -h 127.0.0.1 -P 3306 -u airflow -p

# From Docker container
docker-compose exec mysql mysql -u airflow -p
```

### Useful SQL Queries

```sql
-- Show all databases
SHOW DATABASES;

-- Use Airflow database
USE airflow_db;

-- Show all tables
SHOW TABLES;

-- Create sensor data table example
CREATE TABLE sensor_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_timestamp (sensor_id, timestamp)
);

-- Query sensor data
SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10;

-- Get statistics
SELECT
    sensor_id,
    COUNT(*) as reading_count,
    AVG(temperature) as avg_temp,
    AVG(humidity) as avg_humidity
FROM sensor_readings
GROUP BY sensor_id;
```

### Backup & Restore

```bash
# Backup database
docker-compose exec mysql mysqldump -u airflow -p airflow_db > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T mysql mysql -u airflow -p airflow_db < backup_20250105.sql
```

## ✈️ Airflow Commands

### CLI Commands

```bash
# List all DAGs
docker-compose exec airflow-apiserver airflow dags list

# Trigger a DAG
docker-compose exec airflow-apiserver airflow dags trigger <dag_id>

# List tasks in a DAG
docker-compose exec airflow-apiserver airflow tasks list <dag_id>

# Test a specific task
docker-compose exec airflow-apiserver airflow tasks test <dag_id> <task_id> 2025-10-05

# Pause/Unpause a DAG
docker-compose exec airflow-apiserver airflow dags pause <dag_id>
docker-compose exec airflow-apiserver airflow dags unpause <dag_id>

# List connections
docker-compose exec airflow-apiserver airflow connections list

# Add MySQL connection
docker-compose exec airflow-apiserver airflow connections add 'mysql_iot' \
  --conn-type 'mysql' \
  --conn-host 'mysql' \
  --conn-login 'airflow' \
  --conn-password 'airflow' \
  --conn-port '3306' \
  --conn-schema 'airflow_db'

# Test connection
docker-compose exec airflow-apiserver airflow connections test mysql_iot

# List variables
docker-compose exec airflow-apiserver airflow variables list

# Set a variable
docker-compose exec airflow-apiserver airflow variables set KAFKA_BOOTSTRAP_SERVERS "kafka:29092"

# Get a variable
docker-compose exec airflow-apiserver airflow variables get KAFKA_BOOTSTRAP_SERVERS
```

### User Management

```bash
# Create admin user
docker-compose exec airflow-apiserver airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com

# List users
docker-compose exec airflow-apiserver airflow users list

# Delete user
docker-compose exec airflow-apiserver airflow users delete -u <username>
```

## 🐳 Docker Troubleshooting

### Clean Up

```bash
# Remove stopped containers
docker-compose rm

# Remove unused volumes
docker volume prune

# Remove unused images
docker image prune -a

# Clean everything (⚠️ use carefully)
docker system prune -a --volumes
```

### Resource Check

```bash
# Check container resource usage
docker stats

# Check disk usage
docker system df

# Inspect container
docker inspect <container-name>

# View container processes
docker-compose top
```

### Rebuild Services

```bash
# Rebuild specific service
docker-compose up -d --build airflow-apiserver

# Rebuild all services
docker-compose build --no-cache
docker-compose up -d
```

## 🔍 Debugging Tips

### Check Service Health

```bash
# Airflow health endpoint
curl http://localhost:8080/health

# Check if Kafka is accepting connections
nc -zv localhost 9092

# Check MySQL connection
docker-compose exec mysql mysqladmin -u airflow -p ping
```

### Access Container Shell

```bash
# Access Airflow container
docker-compose exec airflow-apiserver bash

# Access Kafka container
docker-compose exec kafka bash

# Access MySQL container
docker-compose exec mysql bash
```

### View Environment Variables

```bash
# View all environment variables in a container
docker-compose exec airflow-apiserver env

# View specific variable
docker-compose exec airflow-apiserver printenv AIRFLOW__CORE__EXECUTOR
```

## 📦 Python Package Management

### Install Additional Packages

1. Add package to `requirements.txt`
2. Restart Airflow services:

```bash
docker-compose restart airflow-apiserver airflow-scheduler airflow-worker
```

Or rebuild:

```bash
docker-compose up -d --build airflow-apiserver airflow-scheduler airflow-worker
```

### Check Installed Packages

```bash
docker-compose exec airflow-apiserver pip list
docker-compose exec airflow-apiserver pip show <package-name>
```

## 🌐 Network & Connectivity

### Test Kafka from Airflow

```bash
docker-compose exec airflow-apiserver python3 << EOF
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=['kafka:29092'])
producer.send('test-topic', b'Hello from Airflow!')
producer.close()
print("Message sent successfully!")
EOF
```

### Test MySQL from Airflow

```bash
docker-compose exec airflow-apiserver python3 << EOF
import pymysql
conn = pymysql.connect(host='mysql', user='airflow', password='airflow', database='airflow_db')
cursor = conn.cursor()
cursor.execute("SELECT VERSION()")
print(f"MySQL version: {cursor.fetchone()[0]}")
conn.close()
EOF
```

## 📊 Performance Optimization

### Airflow Configuration

Edit `config/airflow.cfg`:

```ini
[core]
# Increase parallelism
parallelism = 32
max_active_tasks_per_dag = 16

[scheduler]
# Adjust scheduler performance
scheduler_heartbeat_sec = 5
min_file_process_interval = 30
```

### MySQL Optimization

```sql
-- Check table sizes
SELECT
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)"
FROM information_schema.TABLES
WHERE table_schema = 'airflow_db'
ORDER BY (data_length + index_length) DESC;

-- Optimize table
OPTIMIZE TABLE sensor_readings;
```

## 📝 Common Configuration Files

### Airflow Connection URI

```python
# MySQL
mysql+mysqldb://airflow:airflow@mysql/airflow_db

# Kafka (in Python)
bootstrap_servers=['kafka:29092']
```

### Environment Variables Reference

```bash
# Airflow
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=mysql+mysqldb://user:pass@mysql/db

# MySQL
MYSQL_USER=airflow
MYSQL_PASSWORD=airflow
MYSQL_DATABASE=airflow_db

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
```

---

**💡 Pro Tip**: Bookmark this file for quick reference during development!
